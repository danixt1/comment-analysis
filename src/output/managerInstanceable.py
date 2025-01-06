from src.managerBase import ManagerBase

def initInstanceables(managerClass:ManagerBase):

    from .outputMongoDb import OutputMongoDb
    from .outputGraphic import OutputGraphic
    
    managerClass.addInstanceable('graphic',OutputGraphic)
    managerClass.addInstanceable('mongodb',OutputMongoDb)