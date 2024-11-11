from .outputBase import OutputBase
from src.managerBase import ManagerBase

class OutputManager(ManagerBase):
    
    def __init__(self):
        self.items: list[OutputBase] = []
    
    def output(self,comments):
        for output in self.items:
            output.sendData(comments)