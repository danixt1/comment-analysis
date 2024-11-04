import time
class Comment:
    def __init__(self,commentId:int,message:str,msgType:str,data = {},origin="",process = [],dictData = {}):
        check = lambda cond,fals: dictData[cond] if cond in dictData else fals
        self.message =check("message",message)
        self.msgType =check("type",msgType)
        self.id = check("id",commentId)
        self.data = check('data',data)
        self.origin = check("origin",origin)
        self.process = check("process",process)
        self.haveAdditionalData = len(process) > 0
    def __str__(self):
        return self.message
    def attachInfo(self,info,processName:str,actualHash:str):
        self.haveAdditionalData = True
        self.data.update(info)
        self.process.append({"name":processName,"hash":actualHash,"timestamp": int(time.time() * 1000)})
    
    def __iter__(self):
        self.dict = self.toDict()
        return iter([(x,self.dict[x]) for x in self.dict.keys()])

    def toDict(self):
        return {
            "id":self.id,
            "message":self.message,
            "type":self.msgType,
            "origin":self.origin,
            "process":self.process,
            "data":self.data
        }