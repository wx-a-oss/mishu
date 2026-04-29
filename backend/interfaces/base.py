from abc import ABC, abstractmethod


class BaseInterface(ABC):
    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def stop(self):
        pass
