from src.adapters import BaseAdapter
from src.schemas import AdapterConfig
import openai
import os

class OpenAIAdapter(BaseAdapter):
    def __init__(self, config: AdapterConfig):
        super().__init__(config)
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def predict(self, query: str, context: str = None) -> str:
        messages = []
        
        # Load system prompt or use default
        system_content = "You are a helpful assistant."
        if self.config.prompt_template_path and os.path.exists(self.config.prompt_template_path):
            with open(self.config.prompt_template_path, 'r') as f:
                system_content = f.read()
        
        # Prepare context if provided
        user_content = query
        if context:
            user_content = f"Context: {context}\n\nQuestion: {query}"
            
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        return response.choices[0].message.content
