from .clientObserver import ClientObserver
from abc import ABC, abstractmethod
from .promptInfo import PromptInfo
from .responseInfo import ResponseInfo
import logging
import time
from ..comment import Comment

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
        self.used_tokens = 0
        self.observers:list[ClientObserver] = []
        self.clientName = clientName
        logger.debug(f'initializing IA client {clientName}')

    def _reportCost(self,tokens: int) -> None:
        """Call this function to report the cost of tokens from the request"""
        self.used_tokens += tokens

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
    def _makeRequestToAi(self,prompt:PromptInfo)->ResponseInfo:
        pass
    # TODO make possibility to do async
    def analyze(self,comments: list[Comment]):
        observers = self.observers
        
        batchs = self._separateCommentsBatch(comments)
        batchs = [x for x in batchs if len(x)]
        for obs in observers:
            obs.notify_batchs_generated(batchs)

        def requestData(batch: list[Comment],prompt: PromptInfo):
            logger.debug(f"client {self.clientName}:requesting analyze for batch with {len(batch)} comments...")
            response = self._makeRequestToAi(str(prompt))
            for obs in observers:
                obs.notify_ai_response(response)
            if not response.isSuccessful():
                error,msg = response.getError()
                if error in ["timeout","connection"]:
                    logger.warning(f"client {self.clientName}:Failed requesting api data, error:{error}, msg:{msg}, retrying...")
                    return "retry"
                logger.error(f"client {self.clientName}:Critical error process finished, error {error}, mgs:{msg}")
                return False
            data = response.getData()
            for index in range(len(data)):
                message,msgData = batch[index],data[index]
                for obs in observers:
                    obs.notify_data_added_to_comment(data,message)
                message.attachInfo(msgData,self.clientName,prompt.hash)
            return True

        for batch in batchs:
            maxRetrys = 4
            retry = 0
            prompt = self._generatePrompt(batch)
            for obs in observers:
                obs.notify_new_prompt_generated(prompt)
            resultInfo = requestData(batch,prompt)
            while(resultInfo == "retry"):
                time.sleep(1)
                retry+=1
                if retry == maxRetrys:
                    logger.error(f"client {self.clientName}:MAX RETRY REACHED")
                    for obs in observers:
                        obs.notify_max_retrys_reached(batch,prompt)
                    return False
            if not resultInfo:
                return False
        return True
    
    def addObserver(self,observer: ClientObserver):
        self.observer = observer
__all__ = ["IaClient"]