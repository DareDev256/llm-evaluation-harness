from src.adapters import BaseAdapter
from src.schemas import AdapterConfig

class MockAdapter(BaseAdapter):
    def predict(self, query: str, context: str = None) -> str:
        """Deterministic mock responses."""
        q_lower = query.lower()
        
        # Check if acting as Judge
        if "provide your assessment in strict json" in q_lower:
            return '{"score": 10, "verdict": "pass", "reasons": ["Mock judge passes everything"], "confidence": 1.0}'
            
        if "capital of france" in q_lower:
            return "The capital of France is Paris [1]."
        if "fact" in q_lower:
            return "Here is a fact about AI."
        return "Mock response for query: " + query
