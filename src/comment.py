class Comment:
    def __init__(self,message:str,msgType:str = None,origin:str = None,id:str | int | None= None,timestamp = None,process = None,**kwargs):
        local_id = kwargs.get('local_id')
        self.timestamp = timestamp
        self.id = id or kwargs.get('origin_id')
        self.message =message
        self.type =msgType or kwargs.get('type')
        self.origin = origin
        self.localId =local_id or hash(str(self.origin) + str(self.id) + self.message)
        self.process = process or []
        self.haveAdditionalData = len(self.process) > 0
    def __str__(self):
        return self.message
    @staticmethod
    def createFromDict(dictData:dict):
        import warnings
        warnings.warn(
            "createFromDict is deprecated and will be removed in a future version",
            DeprecationWarning,
            stacklevel=2)
        
        check = lambda cond,fals: dictData[cond] if cond in dictData else fals
        if not "message" in dictData:
            raise KeyError("Expected message property")
        if not "origin" in dictData:
            raise KeyError("origin need to by specified")
        return Comment(
            dictData['message'],
            check('type',"comment"),
            dictData['origin'],
            check('id',None),
            check('timestamp',None),
            check('process',None)
        )
    def getLastProcess(self):
        if len(self.process) == 0:
            return None
        return self.process[-1]
    def attachInfo(self,info,processName:str,process_id:int):
        self.haveAdditionalData = True
        self.process.append({"name":processName,"data":info,"process_id":process_id})
    
    def __iter__(self):
        self.dict = self.toDict()
        return iter(self.dict.items())

    def getData(self):
        if len(self.process) == 0:
            return None
        return self.process[-1]['data']
    
    def asdict(self):
        return self.toDict()
    def toDict(self):
        return {
            "origin_id":self.id,
            "local_id":self.localId,
            "message":self.message,
            "timestamp":self.timestamp,
            "type":self.type,
            "origin":self.origin,
            "process":self.process
        }