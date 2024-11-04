import logging
logger = logging.getLogger(__name__)

class ResponseInfo:
    def __init__(self):
        self.passedData = False
        self.declaredError = False
        self._data = []
        self.error = ("none","")

    def setData(self,data):
        self._data = data
        return self
    def isSuccessful(self) -> bool:
        if not self.passedData and self.declaredError :
            raise Exception("Data not passed and error reason not passed")
        return self.declaredError
    def getData(self):
        return self._data
    def getError(self):
        return self.error
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
    def _setError(self,erroType,details=""):
        self.error(erroType,details)
        self.declaredError = True
        return self
__all__= ["ResponseInfo"]