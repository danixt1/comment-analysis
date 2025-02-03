from .clientObserver import ClientObserver
from .promptInfo import PromptInfo
from .process import Process
from .requestProcess import RequestProcess
from ..comment import Comment
import logging
from abc import ABC,abstractmethod

logger = logging.getLogger(__name__)


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
    def __init__(self,clientName):
        self.observers:list[ClientObserver] = []
        self.clientName = clientName
        self.autoTestPercentage = 0
        logger.info(f'initializing IA client {clientName}')
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
                                       requestGenerateData,requestAttachData,requestEnd,
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

        for batch, prompt, index in reqInfos:
            data.update({'batch':batch,'prompt':prompt,'index':index})
            requestGenerateData(data,resultFn)
            requestAttachData(data, resultFn)
            scorerRemoveScorerFromRequest(data, resultFn)
            cacheSaveRequestComments(data, resultFn)
            requestEnd(data, resultFn)
        process.finish()
        return process.toDict()
    
    def addObserver(self,observer: ClientObserver):
        self.observer = observer
        