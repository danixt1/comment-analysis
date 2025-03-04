from src.managerBase import ManagerBase
PREFIX = 'src.aiclient.'
def initInstanceables(managerClass:ManagerBase):

    managerClass.addInstanceable('gemini',(PREFIX+'geminiClient','GeminiClient'))
    managerClass.addInstanceable('openrouter',(PREFIX+ 'openrouterClient','OpenrouterClient'))
    managerClass.addInstanceable('openai',(PREFIX + 'openai','OpenAIClient'))