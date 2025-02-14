from .outputBase import OutputBase
from src.managerBase import ManagerBase
from .managerInstanceable import initInstanceables
class OutputManager(ManagerBase):
    
    def __init__(self):
        super().__init__()
        self._items: list[OutputBase] = []
    
    def output(self,comments,processResults:list):
        for output in self._items:
            output.sendData(comments,processResults)
    
initInstanceables(OutputManager)