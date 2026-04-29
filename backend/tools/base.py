from abc import ABC, abstractmethod


class BaseTool(ABC):
    name: str
    description: str
    parameters: dict

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        pass

    def get_schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }
