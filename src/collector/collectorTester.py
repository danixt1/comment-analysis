from src.comment import Comment
from .collectorBase import CollectorBase
from src.datasets.makeDataset import makeData

class CollectorTester(CollectorBase):
    def __init__(self,limit=100,gmts=None,timestamps=None,exclude_tags = None,seed = None):
        super().__init__()
        self.timestamps = timestamps
        self.limit = limit
        self.exclude_tags = exclude_tags
        self.seed = seed
        if gmts:
            self._convertGmtToTimestamp(gmts)

    def _convertGmtToTimestamp(self,gmts):
        if not isinstance(gmts, tuple) and not isinstance(gmts, list):
            raise TypeError("gmts must be tuple or list")
        if not len(gmts) == 2:
            raise ValueError("gmts must contains 2 values")
        
        from datetime import datetime
        timestamps = []
        for gmt in gmts:
            if not isinstance(gmt, str):
                raise TypeError("gmts must be str")
            timeStr = "%Y-%m-%d"
            if gmt.find(":") != -1:
                timeStr += " %H:%M:%S"
            timestamps.append(int(datetime.strptime(gmt, timeStr).timestamp() * 1000))
        self.timestamps = timestamps

    def collect(self):
        data = makeData(self.limit,timestamps=self.timestamps,exclude_tags=self.exclude_tags,seed=self.seed)
        comments:list[Comment] = []
        for actData in data:
            del actData['expected']
            comments.append(Comment(**actData))
        return comments