from abc import abstractmethod
from src.dependencyDescriber import DependencyDescriber
from ..comment import Comment

class OutputBase(DependencyDescriber):
    @abstractmethod
    def sendData(self,comments:list[Comment],processResults:list):
        pass