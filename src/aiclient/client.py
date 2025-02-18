from typing import Callable
from .clientObserver import ClientObserver
from .promptInfo import PromptInfo
from .process import Process
from .requestProcess import RequestProcess
from ..comment import Comment
import logging
from abc import ABC,abstractmethod

logger = logging.getLogger(__name__)

KNOW_PROBLEMS = {
    "product":["delivery","damaged","sue","quality","violated","missing-part","llm-poison"],
    "company":["salary","overwork","infrastructure","culture","management","harassment","llm-poison"]
}
class FilterBatchByType():
    def __init__(self,commentType):
        self.commentType = commentType
    def __call__(self, comment:Comment):
        return comment.type == self.commentType
    
class SplitBatchsByToken:
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
    
class SplitBatchByCharLimit:
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
    
class BatchbucketManager():
    """Class to create batchs, every batch is one prompt/request to the AI client"""
    def __init__(self,createRule = None,returnNoGroupComments = True):
        self.batchs = []
        self.defBatchs = [[]]
        self.buckets = []
        self.noGroupComments = returnNoGroupComments
        self.makeNewBatchDefRule = createRule
        if not self.makeNewBatchDefRule:
            self.makeNewBatchDefRule = SplitBatchByCharLimit(5000)
        self.defData = {}
    def addBucketRules(self,bucketRule:Callable[[Comment],bool],makeNewBatch:Callable[[list[Comment],Comment,dict],bool]|None = None,initialData:dict = {}):
        """Make a bucket of batchs with the comments approved by the function `bucketRule`.<br>
        The quantity of comments by batch is defined by `makeNewBatch` every time True is returned a new batch is created.
        
        Parameters:
        bucketRule (Callable[[Comment],bool]):receive 1 arg with a Comment object, return `True` to add the comment to the this bucket\
        or false to try the next group.
        makeNewBatch (Callable): optional function, receive three args `batch` a array of comments representing the actual batch to send,\
        ,`comment` the actual comment object who is trying to be inserted in the batch, and\
        `data` a dict from the generator to keep info after the run, if returned true a new batch is generated and the comment is added to the new batch.
        initialData (dict): the dict to by passed to `makeNewBatch`"""
        batchs = [[]]
        self.batchs.append(batchs)
        self.buckets.append({"bucketRule":bucketRule,"makeNewBatch":makeNewBatch or self.makeNewBatchDefRule,"data":initialData,"batchs":batchs})

    def addComments(self,comments:list[Comment]):
        """Add a list of comments to the batchs, the comments are added in the first group that the `bucketRule` return true."""
        for comment in comments:
            self.addComment(comment)

    def addComment(self, comment:Comment):
        """Add a comment to the batchs, the comment is added in the first group that the `bucketRule` return true."""
        for group in self.buckets:
            if group['bucketRule'](comment):
                batchs:list[list[Comment]] = group['batchs']
                actBatch = batchs[-1]
                makeNewBatchFn = group['makeNewBatch']
                data = group['data']
                if makeNewBatchFn(actBatch,comment,data):
                    batchs.append([comment])
                else:
                    actBatch.append(comment)
                return
        actBatch = self.defBatchs[-1]
        makeNewBatchFn = self.makeNewBatchDefRule
        data = self.defData
        if makeNewBatchFn(actBatch, comment, data):
            self.defBatchs.append([comment])
        else:
            actBatch.append(comment)

    def getBatchs(self,includesCommentWithoutBucket = None):
        """Return batchs of comments created by buckets"""
        if includesCommentWithoutBucket is None:
            includesCommentWithoutBucket = self.noGroupComments
        createdBatchs = []
        for group in self.buckets:
            createdBatchs.extend(group['batchs'])
        if len(self.defBatchs) > 0 and includesCommentWithoutBucket:
            createdBatchs.extend(self.defBatchs)
        return createdBatchs
requestSchemaOpenAI = {
    "type":"ARRAY",
    "items":{
        "type":"OBJECT",
        "properties":{
            "spam":{"type":"BOOLEAN"},
            "behavior":{
                "type":"STRING",
                "format":"enum",
                "enum":["positive","negative","neutral","question"]
            },
            "problems":{"type":"ARRAY","nullable":True,"items":{"type":"STRING"}}
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
    def _separateCommentsBatch(self,comments: list[Comment]) -> list[list[Comment]]:
        """Receive the data to divide in batchs to send to the AI.
            Divide the data to avoid hallucinations.

            Args:
                comments: comments to process
            return the comments batchs to process.
        """
        pass
    @abstractmethod
    def _generatePrompt(self,comments:list[Comment]) ->PromptInfo:
        pass
    @abstractmethod
    def _makeRequestToAi(self,prompt:PromptInfo,request:RequestProcess):
        pass

    def analyze(self,comments: list[Comment],resultFn = None):
        from .analyzeStructure import (ResultEnum,cacheActive,cacheGetCachedComments,cacheSaveRequestComments,
                                       batchGenerateBatch,batchPrepareBatchsToProcess,
                                       requestGenerateData,requestAttachData,requestEnd,requestTryFixError,
                                       scorerAdd,scorerRemoveScorerFromRequest)
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
        scorerAdd(data, resultFn)
        batchGenerateBatch(data, resultFn)
        batchPrepareBatchsToProcess(data, resultFn)
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
        