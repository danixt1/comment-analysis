from abc import ABC, abstractmethod
from ..comment import Comment

class OutputBase(ABC):
    @abstractmethod
    def sendData(self,comments:list[Comment]):
        pass