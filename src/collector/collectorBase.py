from abc import ABC,abstractmethod
from ..comment import Comment

class CollectorBase(ABC):
    @abstractmethod
    def collect(self) -> list[Comment]:
        pass