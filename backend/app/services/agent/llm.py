import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class LLMProvider(ABC):
    @abstractmethod
    def query(self, prompt: str, context: str) -> Dict[str, Any]:
        pass

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        # In a real implementation, we would initialize the google.generativeai client here
        
    def query(self, prompt: str, context: str) -> Dict[str, Any]:
        # Stub implementation
        return {
            "answer": "This is a response from Gemini based on the evidence provided.",
            "evidence": [{"feature_name": "Context Length", "value": 1.0, "passed": True, "explanation": "Context was provided"}],
            "confidence": 0.95,
            "recommended_action": "Review data."
        }

class NemotronProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def query(self, prompt: str, context: str) -> Dict[str, Any]:
        # Stub implementation
        return {
            "answer": "This is a response from Nemotron 3 Ultra based on the evidence.",
            "evidence": [{"feature_name": "Context Matching", "value": 0.98, "passed": True, "explanation": "Strong context alignment"}],
            "confidence": 0.98,
            "recommended_action": "Approve match."
        }

class AgentService:
    def __init__(self):
        # Fallback to unavailable if no keys are provided, per user instructions
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.nemotron_key = os.getenv("NEMOTRON_API_KEY")
        
        self.provider = None
        if self.nemotron_key:
            self.provider = NemotronProvider(self.nemotron_key)
        elif self.gemini_key:
            self.provider = GeminiProvider(self.gemini_key)
            
    def process_query(self, query: str, context_data: dict = None) -> Dict[str, Any]:
        if not self.provider:
            return {
                "status": "AGENT_UNAVAILABLE",
                "message": "AI Finance Controller is not configured."
            }
            
        try:
            # Prepare context
            context_str = str(context_data) if context_data else "No specific context provided."
            
            # Execute query
            result = self.provider.query(prompt=query, context=context_str)
            result["status"] = "SUCCESS"
            return result
            
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Agent processing failed: {str(e)}"
            }
