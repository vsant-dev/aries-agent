from abc import (abstractmethod)

class Agent:
    @abstractmethod
    async def start(self):
        raise NotImplementedError()
    
    @abstractmethod
    async def stop(self):
        raise NotImplementedError()

    @abstractmethod
    async def get_invite(self, use_did_exchange: bool):
        raise NotImplementedError()

    @abstractmethod
    async def receive_invite(self, invite):
        raise NotImplementedError()