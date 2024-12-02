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

class CommentScorer(Comment):
    def __init__(self,expected:dict, **kwargs):
        super().__init__(**kwargs)
        self.expected = expected
        self.result = None

    def getScore(self):
        if self.result is None:
            return None
        score = 0
        maxScore = 0
        problemsNotDetected = []
        expected = self.expected
        result = self.result

        expectedBehavior = expected['behavior']
        expectedSpam = expected['spam']

        resultBehavior = result['behavior']
        resultSpam = result['spam'] if 'spam' in result else False
        resultProblems = result['problems'] if 'problems' in result else []

        if not expectedBehavior == '-':
            maxScore += 1
            
        if expectedBehavior == resultBehavior:
            score += 1

        if expectedSpam:
            maxScore += 1
            if resultSpam:
                score += 1

        if expected['min_problems']:
            maxScore += expected['min_problems']
            score += len(resultProblems)

        for problem in expected['problems']:
            maxScore += 1
            if problem in resultProblems:
                score += 1
            else:
                problemsNotDetected.append(problem)

        return dict(
            score=1 if maxScore == 0 else (1 /maxScore) * score,
            not_detected=problemsNotDetected,
        )
    
    def attachInfo(self, info, processName: str, process_id: int):
        self.result = info