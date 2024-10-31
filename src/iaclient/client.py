from clientObserver import ClientObserver
from abc import ABC, abstractmethod
from responseInfo import ResponseInfo
from clientObserver import ClientObserver
import logging
import time
from comment import Comment
logger = logging.getLogger(__name__)
import hashlib

# TODO make a folder to put the base prompts and save the SHA1 from the prompts
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
        self.used_tokens = 0
        self.observer = ClientObserver()
        self.clientName = clientName

    def _reportCost(self,tokens: int) -> None:
        """Call this function to report the cost of tokens from the request"""
        self.used_tokens += tokens

    @abstractmethod
    def _separateCommentsBatch(self,comments: list[Comment], type_comments: str) -> list[list[Comment]]:
        """Receive the data to divide in batchs to send to the AI.
            Divide the data to avoid hallucinations.

            Args:
                comments: comments to process
            return the comments batchs to process.
        """
        pass
    @abstractmethod
    def _generatePrompt(self,comments,type_comments:str) ->str:
        pass
    @abstractmethod
    def _makeRequestToAi(self,comments,prompt)->ResponseInfo:
        pass
    # TODO make possibility to do async
    def analyze(self,comments: list[Comment],type_comments) ->list:
        generatedData = []
        observer = self.observer

        observer.initializedAnalysis(comments)
        observer.notify("init")

        batchs = self._separateCommentsBatch(comments,type_comments)
        observer.notify("batchs")
        def requestData(batch: list[Comment]):
            prompt = self._generatePrompt(self,batch,type_comments)
            observer.promptSetted(prompt)
            response = self._makeRequestToAi(batch,prompt)
            if response.isSuccessful():
                generatedData.extend(response.getData())
                return "ok"
            error,msg = response.getError()
            if error in ["timeout","connection"]:
                logger.warn(f"client {self.clientName}:failed requesting api data, error:{error}, msg:{msg}, retrying...")
                return "retry"
            data = response.getData()
            for index in range(len(data)):
                message = batch[index]
                msgData = data[index]
                # TODO continue here, attach the SHA1 to the message
                message.attachInfo(msgData,self.clientName,"<SHA-1>")
        for batch in batchs:
            maxRetrys = 4
            retry = 0
            while(requestData(batch) == "retry"):
                time.sleep(1)
                retry+=1
                if retry == maxRetrys:
                    logger.error(f"client {self.clientName}:MAX RETRY REACHED")
                    return
    
    def attachObserver(self,observer: ClientObserver):
        self.observer = observer