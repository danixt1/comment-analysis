from pathlib import Path

promptPath =Path("prompts")
prompts = [{"name":txt.name[:-4],data:txt.read_text(encoding="utf-8")} for txt in promptPath.glob("*.txt")]
jsonFile = promptPath / "prompt.json"
def createJsonFile():
    jsonFile.name

if not jsonFile.exists():
    createJsonFile()

class PromptInfo:
    """ Get the text and hash from the specified prompt, prompt name is the prompt file without the extension"""
    def __init__(self,promptName):
        self.hash = ""
        self.prompt = ""
    def __str__(self):
        return self.prompt