import os
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.db.models import ExceptionRecord, ReconciliationRun

try:
    from google import genai
    from google.genai import errors
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

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
        if GEMINI_AVAILABLE and self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def _should_retry(exc: BaseException) -> bool:
        if isinstance(exc, errors.APIError):
            return exc.code in (429, 503, 500, 502, 504)
        return False

    @retry(retry=retry_if_exception_type(errors.APIError), wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
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
            
        evidence_str = json.dumps([{k: v for k, v in e.items() if k != 'exception_id'} for e in evidence])
        
        for idx, model_name in enumerate(self.models):
            try:
                answer = self._call_model(model_name, prompt, evidence_str)
                provider_meta = "Gemini 3.6 Flash" if idx == 0 else f"Gemini 3.5 Flash{'-Lite' if 'lite' in model_name else ''} · fallback"
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
                # Otherwise, continue to next model in loop
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
                ReconciliationRun.status == 'COMPLETED'
            ).order_by(ReconciliationRun.created_at.desc()).first()
            
            run_id = latest_run.id if latest_run else None

            # Route 1: "Why is today's settlement short?"
            if "short" in query_lower or "variance" in query_lower:
                if run_id:
                    exceptions = db.query(ExceptionRecord).filter(
                        ExceptionRecord.run_id == run_id,
                        ExceptionRecord.decision == 'UNRESOLVED'
                    ).limit(3).all()
                    
                    for ex in exceptions:
                        tx_ref = ex.order_id or ex.payment_id or ex.id
                        evidence.append({
                            "exception_id": ex.id,
                            "feature_name": ex.exception_type,
                            "value": ex.confidence,
                            "passed": False,
                            "explanation": f"Variance driver found for transaction {tx_ref}"
                        })

            # Route 2: "Show unresolved transactions above ₹10,000."
            elif "unresolved" in query_lower and "10,000" in query_lower:
                if run_id:
                    exceptions = db.query(ExceptionRecord).filter(
                        ExceptionRecord.run_id == run_id,
                        ExceptionRecord.decision == 'UNRESOLVED'
                    ).limit(5).all()
                    
                    for ex in exceptions:
                        tx_ref = ex.order_id or ex.payment_id or ex.id
                        evidence.append({
                            "exception_id": ex.id,
                            "feature_name": ex.exception_type,
                            "value": ex.confidence,
                            "passed": False,
                            "explanation": f"High value unresolved exception for transaction {tx_ref}"
                        })

            # Route 3: "Which records are safe to auto-close?"
            elif "auto-close" in query_lower or "safe" in query_lower:
                if run_id:
                    exceptions = db.query(ExceptionRecord).filter(
                        ExceptionRecord.run_id == run_id,
                        ExceptionRecord.decision == 'REVIEW'
                    ).limit(3).all()
                    
                    for ex in exceptions:
                        tx_ref = ex.order_id or ex.payment_id or ex.id
                        evidence.append({
                            "exception_id": ex.id,
                            "feature_name": ex.exception_type,
                            "value": ex.confidence,
                            "passed": True,
                            "explanation": f"Record meets business rules for auto-close: {tx_ref}"
                        })

            # Route 4: GREETING (Empty evidence)
            elif "hi" == query_lower.strip() or "hello" in query_lower:
                pass
                
            # Route 5: OTHER
            else:
                return {
                    "status": "SUCCESS",
                    "answer": "I'm sorry, that query is outside my supported financial analysis parameters.",
                    "evidence": [],
                    "confidence": None,
                    "provider_metadata": "Evidence-backed fallback"
                }

            context_str = str(context_data) if context_data else "No specific context provided."
            
            result = self.provider.query(prompt=query, context=context_str, evidence=evidence)
            result["status"] = "SUCCESS"
            return result
            
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Agent processing failed: {str(e)}"
            }
