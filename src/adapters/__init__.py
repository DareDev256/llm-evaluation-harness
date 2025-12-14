from abc import ABC, abstractmethod
from src.schemas import AdapterConfig

class BaseAdapter(ABC):
    def __init__(self, config: AdapterConfig):
        self.config = config

    @abstractmethod
    def predict(self, query: str, context: str = None) -> str:
        """Given a query and optional context, return the model output."""
        pass
