import time
import logging
from .promptInfo import PromptInfo
from src.comment import Comment

logger = logging.getLogger(__name__)

class RequestProcess:
    def __init__(self, prompt:PromptInfo, comments:list[Comment]):
        self.hash = prompt.hash
        self.comments_id = [comment.id for comment in comments]
        self.start = int(round(time.time() * 1000))
        self.end = None
        self.tokensInput = None
        self.tokensOutput = None
        self.data = None
        self.error = None
        self.score = None

    def setData(self, data):
        self.data = data
        return self
    def setScore(self, scores):
        self.score = ScoreFromRequest(scores)
        return self
    def setTokensInput(self,tokens:int):
        self.tokensInput = tokens
        return self
    
    def setTokensOutput(self, tokens:int):
        self.tokensOutput = tokens
        return self
    
    def finish(self):
        if not self.end == None:
            return
        if not self.data and not self.error:
            raise Exception("No data or error set")
        self.end = int(round(time.time() * 1000))
    def setHallucinationError(self, details = ''):
        return self._setError("hallucination", details)
    def setPartialDataError(self, details = ''):
        return self._setError("partial-data", details)
    def setTimeoutError(self,details=""):
        return self._setError("timeout",details)
    
    def setConnectionError(self,details=""):
        """ Problems related to 5XX, when is server problem"""
        return self._setError("connection",details)
    
    def setAuthError(self,details):
        return self._setError("auth",details)
    
    def setUnknowError(self,details=""):
        return self._setError("unknown",details)
    
    def setBadRequest(self,details=""):
        logger.error("BAD REQUEST:",details)
        return self._setError('bad-request',details)

    def deprecationWarn(self,message = ""):
        logger.warning(f"API DEPRECATION:{message}")
        return self
    
    def _setError(self,erroType,msg):
        self.error = (erroType,msg)
        return self
class ScoreFromRequest():
    def __init__(self,scores):
        totalScore = 0
        notDetected = []
        for score in scores:
            if len(score['not_detected']) > 0:
                notDetected.extend(score['not_detected'])
            totalScore +=score['score']
        self.totalScore = totalScore / len(scores)
        self.notDetectedProblems = notDetected
    def asdict(self):
        return dict(
            totalScore = self.totalScore,
            notDetectedProblems = self.notDetectedProblems
        )