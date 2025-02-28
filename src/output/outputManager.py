from .outputBase import OutputBase
from src.managerBase import ManagerBase
from .managerInstanceable import initInstanceables

import logging
logger = logging.getLogger(__name__)

class OutputManager(ManagerBase):
    
    def __init__(self):
        super().__init__()
        self._items: list[OutputBase] = []
    
    def output(self,comments,processResults:list):
        logger.info("calling {} output{}".format(len(self._items), "s" if len(self._items) > 1 else ""))
        for output in self._items:
            output.sendData(comments,processResults)
        logger.info("output done.")
initInstanceables(OutputManager)