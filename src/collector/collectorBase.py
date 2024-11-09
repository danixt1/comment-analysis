from abc import ABC,abstractmethod
from ..comment import Comment

class CollectorBase(ABC):
    @abstractmethod
    def collect() -> list[Comment]:
        pass