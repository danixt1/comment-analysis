from src.collector.collectorBase import CollectorBase
import logging

logger = logging.getLogger(__name__)

class CollectorManager:
    collectorInit = {}

    @staticmethod
    def registerCollector(name:str, fn):
        CollectorManager.collectorInit[name] = (lambda config: fn(**config)) if issubclass(fn, CollectorBase) else fn

    def __init__(self,skipOnFailure = False):
        self._collectors:list[CollectorBase] = []
        self.skipOnFailure = skipOnFailure

    def addCollector(self,collector:CollectorBase):
        self._collectors.append(collector)
    @staticmethod
    def initWithConfig(config):
        manager = CollectorManager(config.get("skipOnFailure", False))
        fns = CollectorManager.collectorInit
        for collectorConfig in config.get("collectors", []):
            if not 'name' in collectorConfig:
                raise Exception("Collector name not specified")
            name = collectorConfig['name']
            del collectorConfig['name']
            logger.debug(f"Initializing collector {name}")
            if not name in fns:
                raise Exception(f"Collector {name} not registered. know options:"
                                +",".join(fns.keys()) + '.')
            manager.addCollector(fns[name](collectorConfig))
        return manager
    
    def collect(self):
        collected = []
        logger.info(f"Collecting comments from {len(self._collectors)} collectors.")
        for collector in self._collectors:
            if not self.skipOnFailure:
                collected.extend(collector.collect())
                continue
            try:
                collected.extend(collector.collect())
            except:
                continue
        return collected
    