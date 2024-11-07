from src.collector.collectorBase import CollectorBase
class CollectorManager:
    def __init__(self,skipOnFailure = False):
        self._collectors:list[CollectorBase] = []
        self.skipOnFailure = skipOnFailure

    def addCollector(self,collector:CollectorBase):
        self._collectors.append(collector)

    def collect(self):
        collected = []
        for collector in self._collectors:
            if not self.skipOnFailure:
                collected.extend(collector.collect())
            try:
                collected.extend(collector.collect())
            except:
                continue
        return collected
    