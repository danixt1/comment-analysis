#Gemini client test
from dotenv import load_dotenv
load_dotenv()

from src.comment import Comment
import json
from src.iaclient.geminiClient import GeminiClient
client = GeminiClient()
comments = [
    Comment('Produto excelente nada a reclamar!','comment','test'),
    Comment('Veio com pedaço danificado e ainda atrasou a entrega...','comment','test'),
    Comment('Gente a loja test abre domingo???','social','test')
]
client.analyze(comments)
for comment in comments:
    print(json.dumps(dict(comment), indent=4))