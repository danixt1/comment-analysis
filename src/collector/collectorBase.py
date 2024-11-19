from abc import abstractmethod
from src.dependencyDescriber import DependencyDescriber
from ..comment import Comment

class CollectorBase(DependencyDescriber):
    @abstractmethod
    def collect(self) -> list[Comment]:
        pass