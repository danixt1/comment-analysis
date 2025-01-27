from src.managerBase import ManagerBase
PREFIX = 'src.aiclient.'
def initInstanceables(managerClass:ManagerBase):

    managerClass.addInstanceable('gemini',(PREFIX+'geminiClient','GeminiClient'))