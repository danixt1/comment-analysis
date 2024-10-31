import time
class Comment:
    def __init__(self,commentId:int,message:str,msgType:str):
        self.message = message
        self.msgType = msgType
        self.commentId = commentId
        self.data = {process:[]}
        self.haveAdditionalData = False
    def __str__(self):
        return self.message
    def attachInfo(self,info,processName:str,actualHash:str):
        self.haveAdditionalData = True
        self.data.update(info)
        self.data.process.append({name:processName,actualHash:str,timestamp: int(time.time() * 1000)})
