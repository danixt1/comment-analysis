from src.managerBase import ManagerBase

def initInstanceables(managerClass:ManagerBase):

    from .outputMongoDb import OutputMongoDb

    managerClass.addInstanceable('mongodb',OutputMongoDb)