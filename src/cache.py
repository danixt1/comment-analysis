from src.comment import Comment
import string
import hashlib
import json
from datetime import datetime
from pathlib import Path
chars = string.ascii_letters + string.digits

def makeHash(f = None):
    if f:
        sha1 = hashlib.sha1(f.encode('utf-8'))
        return sha1.hexdigest()
    import random
    return ''.join(random.choice(chars) for _ in range(10))

class Cache:
    def __init__(self):
        self.cache = {}
        self.timestamp =int(datetime.now().timestamp())
        path = Path("cache")
        path.mkdir(exist_ok=True)     
        self.path = path

    def _makeCache(self, fromConfig,t):
        hashValue = makeHash(json.dumps(fromConfig, sort_keys=True))
        path = self.path / f"{self.timestamp}-{hashValue}-{t}.json"
        path.touch(exist_ok=True)
        return path
    
    def addFromCollection(self, comments: list[Comment], collectorConfig:dict):
        path = self._makeCache(collectorConfig,'collector')
        dicts = [x.asdict() for x in comments]
        with open(path, "w") as f:
            f.write(json.dumps(dicts, sort_keys=True))

    def addData(self,data,processConfig:dict):
        path = self._makeCache(processConfig,'data_process')
        with open(path, "w") as f:
            f.write(str(data))
    def get(self,config:dict):
        hashValue = makeHash(json.dumps(config, sort_keys=True))
        matchedFiles:list[Path] = []
        for path in self.path.iterdir():
            name = path.name.split('-')
            if hashValue == name[1]:
                matchedFiles.append(path)
        selected =None
        if len(matchedFiles) == 0:
            return None
        for matched in matchedFiles:
            timestamp = int(matched.name.split('-')[0])
            if not selected:
                selected = matched
            elif timestamp > int(selected.name.split('-')[0]):
                selected = matched
        if not selected:
            return None
        data = json.loads(selected.read_text())
        typeCache = selected.name.split('-')[2]
        if typeCache == 'collector.json':
            comments = [Comment(**x) for x in data]
            return comments
        if typeCache == 'data_process.json':
            return data