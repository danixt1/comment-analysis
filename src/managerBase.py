from abc import ABC,abstractmethod


def raiseInvalStr(obj, propName):
    if not propName in obj:
        raise KeyError(propName + ' not found in config')
    if not isinstance(obj[propName], str):
        raise TypeError(propName + ' must be a string')
    
class ManagerBase(ABC):
    _builders = {}

    def __init__(self) -> None:
        super().__init__()
        self._items = []

    @staticmethod
    @abstractmethod
    def _getBaseClass():
        pass

    def add(self, obj):
        self._items.append(obj)
    
    @classmethod
    def addInstanceable(cls,name, instanceable):
        baseClass =  cls._getBaseClass()
        ManagerBase._builders[name] = (lambda config: instanceable(**config)) if issubclass(instanceable, baseClass) else instanceable
    
    @classmethod
    def initWithConfig(cls,config):
        if not 'data' in config:
            raise KeyError('data not found in config')
        data = config['data']
        del config['data']
        if not isinstance(data, list):
            raise TypeError('data must be a array')
        instance = cls(**config)
        
        for instanceConfig in data:
            if not isinstance(instanceConfig, dict):
                raise TypeError('data must be a object')
            raiseInvalStr(instanceConfig, 'name')
            name = instanceConfig['name'].lower()
            del instanceConfig['name']

            if not name in ManagerBase._builders:
                raise KeyError('instance not found in instanceables list, supported:'+",".join(cls._builders.keys()) + '.')
            item = ManagerBase._builders[name](instanceConfig)
            instance.add(item)
        return instance