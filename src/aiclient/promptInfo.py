from pathlib import Path
from src.comment import Comment
import hashlib

indexs = []
prompts = []
class ExtractData:
    def __init__(self,file:Path) -> None:
        self.name = file.name[:-4]
        indexs.append(self.name)
        #self.lastModify = int(file.stat().st_mtime * 1000)
        self.text = file.read_text(encoding="utf-8")
        self.hash = self.makeHash()
    def makeHash(self) -> str:
        sha1 = hashlib.sha1(self.text.encode('utf-8'))
        return sha1.hexdigest()
    
class PromptInfo:
    """ Get the text and hash from the specified prompt, prompt name is the prompt file without the extension"""
    def __init__(self,promptName:str):
        promptId = indexs.index(promptName)
        prompt = prompts[promptId]
        self.hash = prompt.hash
        self.prompt = prompt.text
    def __str__(self):
        return self.prompt
    def format(self,**ops):
        self.prompt = self.prompt.format(**ops)
        return self
class PromptModifier:
    def __init__(self,prompt:str):
        promptInfo = PromptInfo(prompt)
        self.promptInfo = promptInfo
        self.comments = ""
        self.problems = ""
    def addComments(self, comments:list[Comment],open = "<comment>",close = "</comment>"):
        promptComments = ([str(x) for x in comments])
        promptComments = [open + x + close for x in promptComments]
        self.comments = "\n".join(promptComments)
        return self
    def addKnowProblems(self, problems:list[str]):
        self.problems = ",".join(problems)
        return self
    def generatePrompt(self):
        return self.promptInfo.format(comments=self.comments, problems=self.problems)
    def __str__(self):
        return str(self.generatePrompt())
def setPromptsPath(path):
    indexs.clear()
    prompts.clear()
    promptPath =Path(path)
    prompts.extend([ExtractData(txt) for txt in promptPath.glob("*.txt")])
setPromptsPath("src/aiclient/prompts")