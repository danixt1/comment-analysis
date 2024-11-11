from .client import IAClient
from src.managerBase import ManagerBase
from src.comment import Comment
from .managerInstanceable import initInstanceables

import logging
logger = logging.getLogger(__name__)

class ClientManager(ManagerBase):
    def __init__(self) -> None:
        super().__init__()
        self._items:list[IAClient] = []

    def analyze(self,comments:list[Comment]):
        logger.info("analyzing {} comments with {} AIClient.".format(len(comments), len(self._items)))
        processors = []
        for client in self._items:
            processors.append(client.analyze(comments))
        return processors
    
initInstanceables(ClientManager)