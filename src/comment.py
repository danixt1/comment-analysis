import time
#TODO make id being hashs
#TODO make a variable to reference the external ids connections.
class Comment:
    _actId =0
    def __init__(self,message:str,msgType:str,origin:str,process = None,timestamp = None):
        self.timestamp = timestamp
        self.message =message
        self.type =msgType
        self.id = Comment._actId
        self.origin = origin
        self.process = process or []
        self.haveAdditionalData = len(self.process) > 0
        Comment._actId += 1
    def __str__(self):
        return self.message
    @staticmethod
    def createFromDict(dictData:dict):
        check = lambda cond,fals: dictData[cond] if cond in dictData else fals
        if not "message" in dictData:
            raise KeyError("Expected message property")
        if not "origin" in dictData:
            raise KeyError("origin need to by specified")
        return Comment(
            dictData['message'],
            check('type',"comment"),
            dictData['origin'],
            check('process',None),
            check('timestamp',None)
        )

    def attachInfo(self,info,processName:str,process_id:int):
        self.haveAdditionalData = True
        self.process.append({"name":processName,"data":info,"process_id":process_id})
    
    def __iter__(self):
        self.dict = self.toDict()
        return iter(self.dict.items())

    def toDict(self):
        return {
            "id":self.id,
            "message":self.message,
            "timestamp":self.timestamp,
            "type":self.type,
            "origin":self.origin,
            "process":self.process
        }