from .clientObserver import ClientObserver
from abc import ABC,abstractmethod
from .promptInfo import PromptInfo
from .process import Process
from .requestProcess import RequestProcess
from ..comment import Comment,CommentScorer

import logging
import time

logger = logging.getLogger(__name__)


class IAClient(ABC):
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

    def __fromCache(self,comments:list[Comment]):
        cached = self._cache.get()
        if not cached:
            return comments
        cached = {id:data for id,data in cached}
        ret = []
        for comment in comments:
            localId = comment.localId
            if localId in cached:
                comment.process.append(cached[localId])
                continue
            ret.append(comment)
        return ret
    
    def __addToCache(self,comments:list[Comment]):
        cache = []
        for index in range(len(comments)):
            process = comments[index].getLastProcess()
            if process == None:
                continue
            cache.append([comments[index].localId,process])
        self._cache.add(cache)

    # TODO make possibility to do async
    def analyze(self,comments: list[Comment]):
        process = Process(self.clientName)
        observers = self.observers

        # Get From cache
        if hasattr(self, "_cache"):
            comments = self.__fromCache(comments)
            if len(comments) == 0:
                logger.info(f"client {self.clientName}:all comments already processed")
                process.finish()
                return process
        
        # Create auto test comments
        if self.autoTestPercentage:
            from src.datasets.makeDataset import makeData
            quantity = int(len(comments) * self.autoTestPercentage) or 1
            distribuition = int(len(comments) / quantity)
            tests = makeData(quantity)
            tests = [CommentScorer(**x) for x in tests]
            comments = [x for x in comments]
            testIndex =0
            for i in range(len(comments) -1,0,-distribuition):
                comments.insert(i, tests[testIndex])
                testIndex+=1 

        batchs = self._separateCommentsBatch(comments)
        batchs = [x for x in batchs if len(x)]
        for obs in observers:
            obs.notify_batchs_generated(batchs)

        def requestData(batch: list[Comment],prompt: PromptInfo,index:int):
            logger.info(f"client {self.clientName}:requesting analyze for batch with {len(batch)} comments...")
            requestData = RequestProcess( prompt, batch)
            self._makeRequestToAi(str(prompt),requestData)
            if requestData.error:
                requestData.finish()
                process.getRequest(requestData, index)
                error,msg = requestData.error
                if error in ["timeout","connection"]:
                    logger.warning(f"client {self.clientName}:Failed requesting api data, error:{error}, msg:{msg}, retrying...")
                    return "retry"
                logger.error(f"client {self.clientName}:Critical error process finished, error {error}, mgs:{msg}")
                return False
            
            data = requestData.data
            if len(data) > len(batch):
                requestData.setHallucinationError("Returned more data than the expected")
                requestData.finish()
                return False
            for i in range(len(data)):
                message,msgData = batch[i],data[i]
                for obs in observers:
                    obs.notify_data_added_to_comment(data,message)
                message.attachInfo(msgData,self.clientName,process.id)

            # Get Score and remove CommentScorer from comments
            if self.autoTestPercentage:
                scores = []
                for x in batch:
                    if isinstance(x, CommentScorer):
                        scores.append(x.getScore())
                if len(scores) > 0:
                    requestData.setScore(scores)
                    logger.info(f"client {self.clientName}:score for batch {index} is {requestData.score.totalScore}")
                batch = [x for x in batch if not isinstance(x, CommentScorer)]

            if hasattr(self, "_cache"):
                self.__addToCache(batch if self.autoTest else batch)

            requestData.finish()
            process.getRequest(requestData, index)
            return True

        for batch in batchs:
            maxRetrys = 4
            retry = 0
            prompt = self._generatePrompt(batch)
            index = process.addBatch(prompt,batch)
            for obs in observers:
                obs.notify_new_prompt_generated(prompt)
            resultInfo = requestData(batch,prompt,index)
            while(resultInfo == "retry"):
                time.sleep(1 + retry)
                retry+=1
                if retry == maxRetrys:
                    logger.error(f"client {self.clientName}:MAX RETRY REACHED")
                    for obs in observers:
                        obs.notify_max_retrys_reached(batch,prompt,index)
                    break
                resultInfo = requestData(batch,prompt,index)
        process.finish()
        return process.toDict()
    
    def addObserver(self,observer: ClientObserver):
        self.observer = observer
__all__ = ["IaClient"]