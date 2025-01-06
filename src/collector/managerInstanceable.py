from src.managerBase import ManagerBase

def initInstanceables(managerClass:ManagerBase):

    from .collectorCSV import CollectorCSV
    from .collectorDBAPI import CollectorDBAPI
    from .collectorWordPress import CollectorWordPress
    from .collectorTester import CollectorTester
    
    managerClass.addInstanceable("csv", CollectorCSV)
    managerClass.addInstanceable("dbapi",CollectorDBAPI)
    managerClass.addInstanceable("wordpress", CollectorWordPress)
    managerClass.addInstanceable("tester", CollectorTester)