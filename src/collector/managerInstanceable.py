from src.managerBase import ManagerBase

PREFIX = 'src.collector.'

def initInstanceables(managerClass:ManagerBase):
    
    managerClass.addInstanceable("csv", (PREFIX +'collectorCSV','CollectorCSV'))
    managerClass.addInstanceable("dbapi",(PREFIX +'collectorDBAPI','CollectorDBAPI'))
    managerClass.addInstanceable("wordpress", (PREFIX +'collectorWordPress','CollectorWordPress'))
    managerClass.addInstanceable("tester", (PREFIX+'collectorTester','CollectorTester'))