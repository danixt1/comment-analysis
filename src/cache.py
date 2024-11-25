import hashlib
import json
from datetime import datetime
from pathlib import Path

def makeHash(f):
    sha1 = hashlib.sha1(f.encode('utf-8'))
    return sha1.hexdigest()

class Cache:
    timestamp =int(datetime.now().timestamp())
    def __init__(self,subpath:str):
        self.cache = {}
        path = Path("cache")
        path.mkdir(exist_ok=True) 
        path = path / subpath
        path.mkdir(exist_ok=True)    
        self.path = path

    def _makeCache(self, fromConfig):
        hashValue = makeHash(json.dumps(fromConfig, sort_keys=True))
        path = self.path / f"{self.timestamp}-{hashValue}.json"
        path.touch(exist_ok=True)
        return path
    
    def add(self, config:dict,data):
        path = self._makeCache(config)
        with open(path, "w") as f:
            f.write(json.dumps(data, sort_keys=True))

    def deleteExpiredCache(self,expireTime):
        expiredIn = self.timestamp - expireTime
        for path in self.path.iterdir():
            timestamp = int(path.name.split('-')[0])
            if timestamp < expiredIn:
                path.unlink()

    def get(self,config:dict):
        hashValue = makeHash(json.dumps(config, sort_keys=True)) + '.json'
        matchedFiles:list = []
        for path in self.path.iterdir():
            data = path.name.split('-')
            if(len(data) != 2):
                continue
            data[0] = int(data[0])
            timestamp,fileHash = data
            if hashValue == fileHash:
                matchedFiles.append([timestamp,fileHash,path])
        selected =None
        if len(matchedFiles) == 0:
            return None
        timestamp = matchedFiles[0][0]
        for actTimestamp,fileHash,matched in matchedFiles:
            if not selected:
                selected = matched
            elif timestamp < actTimestamp:
                timestamp = actTimestamp
                selected = matched
        if not selected:
            return None
        data = json.loads(selected.read_text())
        return data