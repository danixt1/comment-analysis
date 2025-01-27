from .client import AiClient
from src.managerBase import ManagerBase
from src.comment import Comment
from .managerInstanceable import initInstanceables

import logging
logger = logging.getLogger(__name__)

class ClientManager(ManagerBase):
    def __init__(self,scorer = None) -> None:
        super().__init__()
        self._items:list[AiClient] = []
        self._scorerPercentage = 0
        if scorer:
            if not 'percentage' in scorer:
                raise KeyError("scorer must have a percentage value (0 - 100)")
            self._scorerPercentage =1/ 100 * scorer['percentage']

    def analyze(self,comments:list[Comment]):
        logger.info("analyzing {} comments with {} AIClient.".format(len(comments), len(self._items)))
        processors = []
        for client in self._items:
            if self._scorerPercentage and not client.isUsingAutoTest():
                client.useAutoTest(self._scorerPercentage)
            processors.append(client.analyze(comments))
        return processors
    
    @classmethod
    def _beforeCreate(cls, config: dict):
        data = config['scorer'] if 'scorer' in config else None
        if data:
            del config['scorer']
            return {'scorer':data}

    @classmethod
    def _afterCreate(cls, item:AiClient, config: dict,data:dict):
        if 'scorer' in data:
            percentage = data['scorer']['percentage']
            percentage = (1 / 100) * percentage
            item.useAutoTest(percentage)
            
initInstanceables(ClientManager)