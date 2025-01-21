from src.managerBase import ManagerBase

PREFIX = 'src.output.'
def initInstanceables(managerClass:ManagerBase):
    
    managerClass.addInstanceable('graphic',(PREFIX + 'outputGraphic','OutputGraphic'))
    managerClass.addInstanceable('mongodb',(PREFIX + 'outputMongoDb','OutputMongoDb'))