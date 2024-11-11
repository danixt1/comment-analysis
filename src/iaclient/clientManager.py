from .client import IAClient
from src.managerBase import ManagerBase
from src.comment import Comment
from .managerInstanceable import initInstanceables

class ClientManager(ManagerBase):
    def __init__(self) -> None:
        super().__init__()
        self._items:list[IAClient] = []

    def analyze(self,comments:list[Comment]):
        for client in self._items:
            client.analyze(comments)
    
initInstanceables(ClientManager)