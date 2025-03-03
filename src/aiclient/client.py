from typing import Callable
from .clientObserver import ClientObserver
from .promptInfo import PromptModifier, PromptInfo
from .process import Process
from .requestProcess import RequestProcess
from ..comment import Comment,CommentScorer
import logging
from abc import ABC,abstractmethod

logger = logging.getLogger(__name__)

KNOW_PROBLEMS = {
    "product":["delivery","damaged","sue","quality","violated","missing-part","llm-poison"],
    "company":["salary","overwork","infrastructure","culture","management","harassment","llm-poison"]
}

class ScorerModifier(ABC):
    """Modify the creation and the `commentScorer` created"""
    def __call__(self, comment:CommentScorer)->None:
        pass
    def exclude_tags(self)->list[str]:
        return []
class FilterItem(ABC):
    @abstractmethod
    def __call__(self, comment:Comment)->bool:
        """Return True if the comment is valid"""
        pass
    def scorerModifier(self)->None | ScorerModifier:
        return None
class SplitBatch(ABC):
    @abstractmethod
    def __call__(self, batch:list[Comment], comment:Comment, data:dict)->bool:
        """Return True if is to end the actual batch and generate a new batch, the actual comment is added to the new batch"""
        pass
class ScorerModifierByType(ScorerModifier):
    def __init__(self, commentType:str):
        self.commentType = commentType
    def __call__(self, comment:CommentScorer):
        comment.type = self.commentType

class FilterItemByType(FilterItem):
    def __init__(self,commentType):
        self.commentType = commentType

    def __call__(self, comment:Comment):
        return comment.type == self.commentType
    def scorerModifier(self):
        return ScorerModifierByType(self.commentType)
    
class SplitBatchsByToken(SplitBatch):
    def __init__(self,getTokens:Callable,tokensLimit:int):
        self.getTokens = getTokens
        self.limit = tokensLimit
    def __call__(self, batch,comment:Comment,data:dict):
        if "totalTokens" not in data:
            data["totalTokens"] = 0
        tokens = self.getTokens(str(comment))
        data["totalTokens"] += tokens
        if data["totalTokens"] > self.limit:
            data["totalTokens"] = tokens
            return True
        return False
class SplitBatchByCharLimit(SplitBatch):
    def __init__(self,charLimit):
        self.limit = charLimit

    def __call__(self, batchs,comment,data):
        if not 'chars' in data:
            data['chars'] = 0
        data['chars'] += len(str(comment))
        if data['chars'] > self.limit:
            data['chars'] = 0
            return True
        return False
class BatchRules:
    """Define the rules of the batch have 3 rules who is modifiable.
    1. `FilterItem`: define if the comment can or not by added to this batch.
    2. `SplitBatch`: used to define the end of the batch and the creation of another batch.
    3. `ScorerModifier`: used to determine the rules of creation and modify the `CommentScorer` added to this batch.
    """
    def __init__(self,name:str | None = None):
        self.splitter:SplitBatch | None = None
        self.filter:FilterItem = None
        self.scorerModifier:ScorerModifier | None = None
        self.name = name
    def addRules(self,component: SplitBatch | FilterItem | ScorerModifier):
        if isinstance(component, SplitBatch):
            self.splitter = component
        elif isinstance(component, FilterItem):
            self.filter = component
            ScorerModifier = component.scorerModifier()
            if ScorerModifier and not self.scorerModifier:
                self.scorerModifier = ScorerModifier
        elif isinstance(component, ScorerModifier):
            self.scorerModifier = component
        else:
            raise Exception("Invalid component type")
        return self
class Batch:
    def __init__(self,comments:list[Comment],rule:BatchRules = None):
        self.comments: list[Comment] = comments
        self.rule:BatchRules | None = rule
        self.name = rule.name if rule else "default"
    def __len__(self):
        return len(self.comments)

    def __getitem__(self, index) -> Comment:
        return self.comments[index]
    
    def __iter__(self):
        return iter(self.comments)

    def __str__(self):
        return str(self.comments)
    def insertCommentsScorer(self, comments:list[CommentScorer]):
        totComments = len(self.comments) - 1
        distribuition = int(totComments / len(comments)) or 1
        scorerIndex = 0
        for i in range(totComments, 0,-distribuition):
            self.comments.insert(i, comments[scorerIndex])
            scorerIndex += 1
    def removeScorers(self):
        self.comments = [x for x in self.comments if not isinstance(x, CommentScorer)]
class BatchBucketManager:
    """Class to create batchs, every batch is one prompt/request to the AI client"""
    def __init__(self, defSplitter:SplitBatch | None = None):
        self.buckets:list[dict] = []
        self.batchs:list[list[Comment]] = []
        self.defBatchs:list[list[Comment]] = [[]]
        self.defData = {}
        self.defSplitter:SplitBatch = defSplitter or SplitBatchByCharLimit(5000)
    def addBatchRule(self, rule:BatchRules,baseData = {}):
        if not rule.filter:
            raise Exception("Rule must have a filter")
        batchs = [[]]
        self.batchs.append(batchs)
        self.buckets.append({"rule":rule,"data":baseData,"batchs":batchs})
    def addComment(self, comment:Comment):
        for bucket in self.buckets:
            rule:BatchRules = bucket['rule']
            if not rule.filter(comment):
                continue
            batchs = bucket['batchs']
            data = bucket['data']
            actBatch: list[Comment] = batchs[-1]
            if rule.scorerModifier and isinstance(comment,CommentScorer):
                rule.scorerModifier(comment)
            if rule.splitter and rule.splitter(actBatch, comment, data):
                actBatch = []
                batchs.append(actBatch)
            actBatch.append(comment)
            return
        defBatchs = self.defBatchs
        actBatch: list[Comment] = defBatchs[-1]
        data = self.defData
        if self.defSplitter and self.defSplitter(actBatch, comment, data):
            actBatch = []
            defBatchs.append(actBatch)
        actBatch.append(comment)
    
    def addComments(self, comments:list[Comment]):
        for comment in comments:
            self.addComment(comment)
    def getBatchs(self)->list[Batch]:
        """Return batchs of comments created by buckets"""
        createdBatchs:list[Batch] = []
        for group in self.buckets:
            createdBatchs.extend([Batch(x,group["rule"]) for x in group['batchs'] if len(x) > 0])
        createdBatchs.extend([Batch(x) for x in self.defBatchs if len(x) > 0])
        return createdBatchs
requestSchemaOpenAI = {
    "type":"array",
    "items":{
        "type":"object",
        "properties":{
            "spam":{"type":"boolean"},
            "behavior":{
                "type":"string",
                "format":"enum",
                "enum":["positive","negative","neutral","question"]
            },
            "problems":{"type":"array","nullable":True,"items":{"type":"string"}}
        }
    }
}
class AiClient(ABC):
    """
    Processing flux:
    1. analyze: analyze is called (DON'T overide)
    2. _separateCommentsBatch: get the comments and separate in batchs
    For every batch:
        1. _generatePrompt: render prompt to AI from the batch of comments
        2. _makeRequestToAi: pass the prompt generated and request the data, expected the JSON with the comments.
    Obs: Always return the data from comments in the SAME order of the input.
    """
    def __init__(self,clientName,tolerance = 2):
        self.observers:list[ClientObserver] = []
        self.clientName = clientName
        self.autoTestPercentage = 0
        self.tolerance = tolerance
        logger.info(f'initializing AI client {clientName}')
    def useAutoTest(self,percentage = 0.20):
        self.autoTestPercentage = percentage
    def isUsingAutoTest(self):
        return self.autoTestPercentage > 0
    @abstractmethod
    def _separateCommentsBatch(self) -> BatchBucketManager:
        """Separate the comments in batchs, and the batchs is transformed in prompt.<br>
        Use the `BatchBucketManager` to 
        """
        pass
    @abstractmethod
    def _generatePrompt(self,comments:Batch) ->PromptModifier:
        pass
    @abstractmethod
    def _makeRequestToAi(self,prompt:PromptInfo,request:RequestProcess):
        pass
    def analyze(self,comments: list[Comment],resultFn = None):
        from .analyzeStructure import (ResultEnum,cacheActive,cacheGetCachedComments,cacheSaveRequestComments,
                                       batchGenerateBatch,batchPrepareBatchsToProcess,
                                       requestGenerateData,requestAttachData,requestEnd,requestTryFixError,
                                       scorerAddToBatch,scorerRemoveScorerFromRequest)
        lastResult:ResultEnum = None
        def defLastResult(x):
            nonlocal lastResult
            lastResult = x
            return x
        resultFn = resultFn if resultFn else defLastResult
        process = Process(self.clientName)
        data = {"main":self, "comments":comments,"process":process}

        cacheActive(data,resultFn)
        cacheGetCachedComments(data, resultFn)
        if lastResult == ResultEnum.STOP:
            process.finish()
            return process.toDict()
        batchGenerateBatch(data, resultFn)
        batchPrepareBatchsToProcess(data, resultFn)
        scorerAddToBatch(data, resultFn)
        reqInfos = data['request_data']
        initialReqs = len(reqInfos)
        limitReqs = int(initialReqs * self.tolerance)
        for batch, prompt, index in reqInfos:
            data.update({'batch':batch,'prompt':prompt,'index':index})
            requestGenerateData(data,resultFn)
            if lastResult == ResultEnum.ERROR:
                requestTryFixError(data, resultFn)
                if len(data['request_data']) > limitReqs:
                    logger.error(f'client {self.clientName}:Failed processing too many retrys. please try making adjust in AI or increase tolerance limit.')
                    requestEnd(data, resultFn)
                    process.finish()
                    return process.toDict()
                if lastResult == ResultEnum.ERROR or lastResult == ResultEnum.STOP:
                    if lastResult == ResultEnum.ERROR:
                        logger.error(f'Error in request {index} of {self.clientName} canceled.')
                    requestEnd(data, resultFn)
                    continue
            requestAttachData(data, resultFn)
            scorerRemoveScorerFromRequest(data, resultFn)
            cacheSaveRequestComments(data, resultFn)
            requestEnd(data, resultFn)
        process.finish()
        return process.toDict()
    
    def addObserver(self,observer: ClientObserver):
        self.observer = observer
        