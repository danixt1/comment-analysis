from src.aiclient.openai import OpenAIClient

class OpenrouterClient(OpenAIClient):
    baseName="openrouter"
    def __init__(self, tolerance=2,model="",env="OPENROUTER_API_KEY"):
        super().__init__(model=model,env=env,base_url="https://openrouter.ai/api/v1",tolerance=tolerance)