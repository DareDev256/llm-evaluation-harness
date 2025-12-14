from src.adapters import BaseAdapter
from src.schemas import AdapterConfig
import httpx
import os

class HTTPRAGAdapter(BaseAdapter):
    def __init__(self, config: AdapterConfig):
        super().__init__(config)
        self.base_url = config.base_url or os.getenv("RAG_API_URL")

    def predict(self, query: str, context: str = None) -> str:
        # Context is ignored here as the RAG system retrieves its own context
        url = f"{self.base_url}/query"
        payload = {"text": query} # Adapting to the expected RAG API format
        
        # RAG API Key if needed
        headers = {}
        api_key = os.getenv("RAG_API_KEY")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        with httpx.Client(timeout=self.config.timeout) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            # Assuming getting answer from 'answer' field
            return data.get("answer", str(data))
