#Gemini client test
from dotenv import load_dotenv
load_dotenv()

from src.comment import Comment
import json
from src.iaclient.geminiClient import GeminiClient
client = GeminiClient()
comments = [
    Comment(1,'Produto excelente nada a reclamar!','comment'),
    Comment(2,'Veio com pedaço danificado e ainda atrasou a entrega...','comment'),
    Comment(3,'Gente a loja test abre domingo???','social')]
client.analyze(comments)
for comment in comments:
    print(json.dumps(dict(comment), indent=4))