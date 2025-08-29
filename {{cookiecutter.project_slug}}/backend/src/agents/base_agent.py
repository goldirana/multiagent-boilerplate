from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.is_active = False
    
    @abstractmethod
    def process(self, input_data: dict) -> dict:
        """Process input and return response"""
        pass
    
    def start(self):
        """Start the agent"""
        self.is_active = True
        return f"{self.name} started"
    
    def stop(self):
        """Stop the agent"""
        self.is_active = False
        return f"{self.name} stopped"
