import subprocess
import time
from .requestProcess import RequestProcess

def get_git_commit():
    try:
        # Get the current git commit hash
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()
        return commit
    except subprocess.CalledProcessError:
        return None
commit = get_git_commit() or "Unknown"

class Process:
    idCount = 0
    def __init__(self, name):
        self.name = name
        self.commit = commit
        self.startTimestamp = int(round(time.time() * 1000))
        self.id = Process.idCount
        self.tokensInput = 0
        self.tokensOutput = 0
        self.batchs = []
        self.requests = []
        Process.idCount += 1
        
    def addBatch(self, prompt,comments):
        batch = {
            "promptHash":prompt.hash,
            "tokens": {
                "input":0,
                "output":0
            },
            "comments_id":[comment.id for comment in comments],
            "successfulRequest":None
        }
        self.batchs.append(batch)
        return len(self.batchs) - 1
    def getRequest(self,request:RequestProcess,pos:int):
        reqInfo = {
            "success":not request.data == None,
            "batch_pos":pos
        }
        self.requests.append(reqInfo)
        if request.data == None:
            reqInfo["error"] = request.error
            return
        batch = self.batchs[pos]
        batch["successfulRequest"] = len(self.requests) - 1

        tokensInput = request.tokensInput or 0
        tokensOutput = request.tokensOutput or 0

        batch["tokens"] = {
            "input":request.tokensInput,
            "output":request.tokensOutput
        }
        self.tokensInput += tokensInput
        self.tokensOutput += tokensOutput
    def finish(self):
        self.endTimestamp = int(round(time.time() * 1000))
    def toDict(self):
        return {
            "id": self.id,
            "name": self.name,
            "commit": self.commit,
            "timestamp":{
                "start":self.startTimestamp,
                "end":self.endTimestamp
            },
            "tokens":{
                "input":self.tokensInput,
                "output":self.tokensOutput
            },
            "requests": self.requests,
            "batchs": self.batchs
        }