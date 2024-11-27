import hashlib
import json
from datetime import datetime
from pathlib import Path

def makeHash(f):
    sha1 = hashlib.sha1(f.encode('utf-8'))
    return sha1.hexdigest()

class Cache:
    timestamp =int(datetime.now().timestamp())

    def __init__(self,subpath:str = None,prefix = None,actPath = None):
        self.cache = {}
        self.prefix = prefix
        self.n = 0
        if actPath:
            self.path = Path(actPath)
            return

        path = Path("cache")
        if subpath:
            path.mkdir(exist_ok=True) 
            path = path / subpath
            path.mkdir(exist_ok=True)    
        self.path = path
    def cacheWithPrefix(self,prefix):
        if isinstance(prefix, (dict, list)):
            prefix =makeHash(json.dumps(prefix, sort_keys=True))
        return Cache(prefix=prefix,actPath=self.path)
    def _makeCache(self, fromInput):
        filename = str(self.timestamp)
        if self.prefix:
            filename += f"-{self.prefix}"
        if fromInput:
            hashValue = makeHash(json.dumps(fromInput, sort_keys=True))
            filename += f"-{hashValue}"
        else:
            filename += f"-{self.n}"
            self.n += 1
        path = self.path / filename
        path.touch(exist_ok=True)
        return path
    def add(self,data, inputData:dict = None):
        path = self._makeCache(inputData)
        with open(path, "w") as f:
            f.write(json.dumps(data, sort_keys=True))

    def deleteExpiredCache(self,expireTime):
        expiredIn = self.timestamp - expireTime
        for path in self.path.iterdir():
            if path.is_dir():
                continue
            timestamp = 0
            try:
                timestamp = int(path.name.split('-')[0])
            except:
                continue
            if timestamp < expiredIn:
                path.unlink()
    def _getNewer(self, data:list):
        selected = data[0]
        timestamp = selected[0]
        for actTimestamp,fileHash,matched in data:
            if timestamp < actTimestamp:
                timestamp = actTimestamp
                selected = matched
        return selected
    
    def _getFromPrefix(self):
        matchedFiles:list = []
        actTimestamp = 0
        ret = []
        for path in self.path.iterdir():
            part = 0
            data = path.name.split('-')
            if(len(data) == 3):
                part = int(data.pop())
            if(len(data) != 2):
                continue
            data[0] = int(data[0])
            timestamp,fileHash = data
            if self.prefix == fileHash and timestamp >= actTimestamp:
                if timestamp > actTimestamp:
                    actTimestamp = timestamp
                    matchedFiles = []
                matchedFiles.append([part, path])
        if len(matchedFiles) == 0:
            return None
        matchedFiles.sort(key=lambda x: x[0])
        for _,path in matchedFiles:
            data = json.loads(path.read_text())
            ret.extend(data)
        return ret
    def get(self,inputData:dict = None):
        if not inputData:
            return self._getFromPrefix()