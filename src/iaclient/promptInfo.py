from pathlib import Path
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
    def format(self,*ops):
        self.prompt = self.prompt.format(*ops)
        return self
    
def setPromptsPath(path):
    indexs.clear()
    prompts.clear()
    promptPath =Path(path)
    prompts.extend([ExtractData(txt) for txt in promptPath.glob("*.txt")])
setPromptsPath("src/iaclient/prompts")