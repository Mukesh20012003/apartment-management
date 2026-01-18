from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime

class BaseEvent(ABC):
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.timestamp = datetime.utcnow().isoformat()
        self.event_type = self.__class__.__name__

    @abstractmethod
    def publish(self):
        """Publish to message broker"""
        pass
