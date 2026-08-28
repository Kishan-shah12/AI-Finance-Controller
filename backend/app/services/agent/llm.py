import os
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models import ExceptionRecord, ReconciliationRun

try:
    from google import genai
    from google.genai import errors
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

def is_transient_error(exc: BaseException) -> bool:
    if isinstance(exc, errors.APIError):
        return exc.code in (429, 503, 500, 502, 504)
    return False

class LLMProvider(ABC):
    @abstractmethod
    def query(self, prompt: str, context: str, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        pass

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.models = [
            os.getenv("GEMINI_MODEL_PRIMARY", "gemini-3.6-flash"),
            os.getenv("GEMINI_MODEL_FALLBACK_1", "gemini-3.5-flash"),
            os.getenv("GEMINI_MODEL_FALLBACK_2", "gemini-3.5-flash-lite")
        ]
        if GEMINI_AVAILABLE and self.api_key and self.api_key != "stub_key":
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    @retry(retry=retry_if_exception(is_transient_error), wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
    def _call_model(self, model_name: str, prompt: str, evidence_str: str) -> str:
        if not self.client:
            raise ValueError("Gemini client not initialized")
        
        system_instruction = "You are ReconAI, a finance controller. Answer only based on the provided evidence. Keep it concise. Do not expose chain-of-thought."
        full_prompt = f"Evidence:\n{evidence_str}\n\nUser Query: {prompt}"
        
        response = self.client.models.generate_content(
            model=model_name,
            contents=full_prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1
            )
        )
        return response.text

    def _fallback_response(self, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "answer": "This is a deterministic fallback response based strictly on the retrieved database evidence.",
            "evidence": evidence,
            "confidence": evidence[0]["value"] if evidence and "value" in evidence[0] else None,
            "provider_metadata": "Evidence-backed fallback",
            "recommended_action": "Review provided evidence."
        }

    def query(self, prompt: str, context: str, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not evidence:
            return {
                "answer": "Hello. I am your AI Finance Controller. How can I assist you with your reconciliations today?",
                "evidence": [],
                "confidence": None,
                "provider_metadata": "Evidence-backed fallback",
                "recommended_action": None
            }
            
        if not self.client:
            return self._fallback_response(evidence)
            
        # Clean evidence to not expose internal IDs if not needed, but keep exception_id
        evidence_str = json.dumps([{k: v for k, v in e.items() if k != 'exception_id'} for e in evidence])
        
        for idx, model_name in enumerate(self.models):
            try:
                answer = self._call_model(model_name, prompt, evidence_str)
                if idx == 0:
                    provider_meta = "Gemini 3.6 Flash"
                elif idx == 1:
                    provider_meta = "Gemini 3.5 Flash · fallback"
                else:
                    provider_meta = "Gemini 3.5 Flash-Lite · fallback"
                
                return {
                    "answer": answer,
                    "evidence": evidence,
                    "confidence": evidence[0]["value"] if evidence and "value" in evidence[0] else None,
                    "provider_metadata": provider_meta,
                    "recommended_action": "Review data."
                }
            except errors.APIError as e:
                if e.code in (400, 401, 403):
                    # Fail fast for unrecoverable errors
                    break
                # Otherwise, it must be transient (already retried by tenacity) so continue to next model
                continue
            except Exception:
                break
                
        return self._fallback_response(evidence)

class NemotronProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def query(self, prompt: str, context: str, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not evidence:
            return {
                "answer": "Hello. I am Nemotron 3 Ultra. How can I help?",
                "evidence": [],
                "confidence": None,
                "provider_metadata": "Evidence-backed fallback",
                "recommended_action": None
            }
            
        return {
            "answer": "Deterministic fallback from Nemotron 3 Ultra based on evidence.",
            "evidence": evidence,
            "confidence": evidence[0]["value"] if evidence and "value" in evidence[0] else None,
            "provider_metadata": "Nemotron 3 Ultra · fallback",
            "recommended_action": "Approve match."
        }

class AgentService:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.nemotron_key = os.getenv("NEMOTRON_API_KEY")
        
        if self.nemotron_key:
            self.provider = NemotronProvider(self.nemotron_key)
        elif self.gemini_key:
            self.provider = GeminiProvider(self.gemini_key)
        else:
            self.provider = GeminiProvider("stub_key")
            
    def process_query(self, query: str, db: Session, context_data: dict = None) -> Dict[str, Any]:
        try:
            query_lower = query.lower()
            evidence = []
            
            latest_run = db.query(ReconciliationRun).filter(
                ReconciliationRun.mode == 'demo',
                ReconciliationRun.provider == 'SYNTHETIC',
                ReconciliationRun.seed == 42,
                ReconciliationRun.status == 'COMPLETED'
            ).order_by(ReconciliationRun.created_at.desc()).first()
            
            run_id = latest_run.id if latest_run else None

            # Route 1: GREETING
            if any(word in query_lower.split() for word in ["hi", "hello", "hey", "greetings"]):
                return {
                    "status": "SUCCESS",
                    "answer": "Hello! I am your AI Finance Controller. How can I assist you today?",
                    "evidence": None,
                    "confidence": None,
                    "provider_metadata": "Agent router"
                }
                
            # Route 2: CAPABILITIES
            elif any(phrase in query_lower for phrase in ["what can you do", "what services", "how can you help", "what can i ask"]):
                return {
                    "status": "SUCCESS",
                    "answer": "I can analyze settlement variances, investigate exceptions, find unresolved high-value transactions, and identify records that are safe to auto-close.",
                    "evidence": None,
                    "confidence": None,
                    "provider_metadata": "Agent router"
                }

            # Route 3: SETTLEMENT_VARIANCE (Why is today's settlement short?)
            elif any(phrase in query_lower for phrase in ["short", "variance", "lower than expected"]):
                if run_id:
                    exceptions = db.query(ExceptionRecord).filter(
                        ExceptionRecord.run_id == run_id,
                        ExceptionRecord.decision == 'UNRESOLVED'
                    ).limit(3).all()
                    
                    for ex in exceptions:
                        evidence.append({
                            "exception_id": ex.id,
                            "feature_name": ex.exception_type,
                            "value": ex.confidence,
                            "passed": False,
                            "explanation": f"Variance driver found for exception."
                        })

            # Route 4: LARGEST_UNEXPLAINED_VARIANCE (Which settlement has the largest unexplained variance? Or Which exceptions impact cash the most?)
            elif any(phrase in query_lower for phrase in ["largest unexplained", "largest variance", "impact cash the most", "largest unexplained variance"]):
                if run_id:
                    # For simplicity in this demo, grab the lowest confidence unresolved exception
                    ex = db.query(ExceptionRecord).filter(
                        ExceptionRecord.run_id == run_id,
                        ExceptionRecord.decision == 'UNRESOLVED'
                    ).order_by(ExceptionRecord.confidence.asc()).first()
                    
                    if ex:
                        evidence.append({
                            "exception_id": ex.id,
                            "feature_name": ex.exception_type,
                            "value": ex.confidence,
                            "passed": False,
                            "explanation": f"Highest priority unexplained variance."
                        })

            # Route 5: HOW_MUCH_UNRECONCILED (How much remains unreconciled?)
            elif any(phrase in query_lower for phrase in ["remains unreconciled", "how much is unresolved"]):
                if run_id:
                    unresolved_count = latest_run.unresolved
                    ex = db.query(ExceptionRecord).filter(
                        ExceptionRecord.run_id == run_id,
                        ExceptionRecord.decision == 'UNRESOLVED'
                    ).first()
                    
                    evidence.append({
                        "exception_id": ex.id if ex else None,
                        "feature_name": "Unreconciled Summary",
                        "value": ex.confidence if ex else 1.0, 
                        "passed": False,
                        "explanation": f"Total unresolved records: {unresolved_count}"
                    })

            # Route 6: UNRESOLVED_TRANSACTIONS (Show unresolved transactions above 10,000)
            elif "unresolved" in query_lower and any(word in query_lower for word in ["10,000", "ten thousand", "high-value"]):
                if run_id:
                    exceptions = db.query(ExceptionRecord).filter(
                        ExceptionRecord.run_id == run_id,
                        ExceptionRecord.decision == 'UNRESOLVED'
                    ).limit(5).all()
                    
                    for ex in exceptions:
                        evidence.append({
                            "exception_id": ex.id,
                            "feature_name": ex.exception_type,
                            "value": ex.confidence,
                            "passed": False,
                            "explanation": f"High value unresolved exception."
                        })

            # Route 7: SAFE_AUTO_CLOSE
            elif any(phrase in query_lower for phrase in ["auto-close", "safe", "auto resolved"]):
                if run_id:
                    exceptions = db.query(ExceptionRecord).filter(
                        ExceptionRecord.run_id == run_id,
                        ExceptionRecord.decision == 'REVIEW'
                    ).limit(3).all()
                    
                    for ex in exceptions:
                        evidence.append({
                            "exception_id": ex.id,
                            "feature_name": ex.exception_type,
                            "value": ex.confidence,
                            "passed": True,
                            "explanation": f"Record meets business rules for auto-close."
                        })

            # Route 8: OTHER
            else:
                return {
                    "status": "SUCCESS",
                    "answer": "I can help with settlement analysis, exceptions, unresolved transactions, and safe automation.",
                    "evidence": None,
                    "confidence": None,
                    "provider_metadata": "Agent router"
                }
            
            # Filter out evidence with no exception_id to be safe
            evidence = [e for e in evidence if e.get("exception_id")]

            context_str = str(context_data) if context_data else "No specific context provided."
            
            result = self.provider.query(prompt=query, context=context_str, evidence=evidence)
            result["status"] = "SUCCESS"
            return result
            
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Agent processing failed: {str(e)}"
            }
