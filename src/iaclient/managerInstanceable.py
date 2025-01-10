from src.managerBase import ManagerBase
PREFIX = 'src.iaclient.'
def initInstanceables(managerClass:ManagerBase):

    managerClass.addInstanceable('gemini',(PREFIX+'geminiClient'))