from .outputBase import OutputBase
class OutputManager:
    _outputInit = {}

    @staticmethod
    def registerOutput(name:str, fn):
        OutputManager._outputInit[name] = (lambda config: fn(**config)) if issubclass(fn, OutputBase) else fn
    
    def __init__(self):
        self._outputs = []
    
    def addOutput(self, output:OutputBase):
        self._outputs.append(output)
    def output(self,comments):
        for output in self._outputs:
            output.sendData( comments)
    @staticmethod
    def initWithConfig(config:list):
        output = OutputManager()
        for outputConfig in config:
            name = outputConfig['name']
            del outputConfig['name']
            output.addOutput(OutputManager._outputInit[name](outputConfig))
        return output