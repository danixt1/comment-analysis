from abc import ABC,abstractmethod
from ..comment import Comment

class CollectorBase(ABC):
    @abstractmethod
    def collect(self) -> list[Comment]:
        pass

    def collectUsingCache(self):
        if not hasattr(self, '_cache'):
            return self.collect()
        cache = self._cache
        cached = cache.get()
        if cached:
            return [Comment(**x) for x in cached]
        result = self.collect()
        cache.add([x.asdict() for x in result])
        return result