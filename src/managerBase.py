from abc import ABC
from src.cache import Cache

def raiseInvalStr(obj, propName):
    if not propName in obj:
        raise KeyError(propName + ' not found in config')
    if not isinstance(obj[propName], str):
        raise TypeError(propName + ' must be a string')
    
class ManagerBase(ABC):
    
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls._builders = {}
    def __init__(self) -> None:
        super().__init__()
        self._items = []

    def add(self, obj):
        self._items.append(obj)
    
    @classmethod
    def addInstanceable(cls,name, instanceable):
        cls._builders[name] = (lambda config: instanceable(**config)) if isinstance(instanceable,type) else instanceable
    
    @classmethod
    def initWithConfig(cls,config,cache:Cache):
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

            if not name in cls._builders:
                raise KeyError(f'instance "{name}" not found in instanceables list, supported:{",".join(cls._builders.keys())}.')
            item = cls._builders[name](instanceConfig)
            item._cache = cache.cacheWithPrefix(instanceConfig)
            instance.add(item)
        return instance