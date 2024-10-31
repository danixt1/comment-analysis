class ClientObserver:
    """
    Override the functions to get the state of call
    """
    def promptSetted(self,prompt:str):
        pass
    def initializedAnalysis(self,comments):
        pass
    def notify(self,type_message):
        pass