from pathlib import Path
import hashlib
import os
indexs = []
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
    
promptPath =Path(os.environ["PROMPTS_PATH"] if "PROMPTS_PATH" in os.environ else "prompts")
prompts = [ExtractData(txt) for txt in promptPath.glob("*.txt")]

class PromptInfo:
    """ Get the text and hash from the specified prompt, prompt name is the prompt file without the extension"""
    def __init__(self,promptName):
        promptId = indexs.index(promptName)
        prompt = prompts[promptId]
        self.hash = prompt.hash
        self.prompt = prompt.text
    def __str__(self):
        return self.prompt