from src.managerBase import ManagerBase

def initInstanceables(managerClass:ManagerBase):

    from .geminiClient import GeminiClient

    managerClass.addInstanceable('gemini',GeminiClient)
    