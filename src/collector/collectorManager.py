from src.collector.collectorBase import CollectorBase
from src.managerBase import ManagerBase

from .managerInstanceable import initInstanceables
import logging

logger = logging.getLogger(__name__)

class CollectorManager(ManagerBase):
    def __init__(self,skipOnFailure = False):
        super().__init__()
        self._items:list[CollectorBase] = []
        self.skipOnFailure = skipOnFailure
    
    def collect(self):
        collected = []
        logger.info(f"Collecting comments from {len(self._items)} collectors.")
        for collector in self._items:
            if not self.skipOnFailure:
                collected.extend(collector.collectUsingCache())
                continue
            try:
                collected.extend(collector.collectUsingCache())
            except:
                continue
        return collected
    
initInstanceables(CollectorManager)