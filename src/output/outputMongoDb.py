from pymongo import MongoClient

from src.comment import Comment
from .outputBase import OutputBase

class OutputMongoDb(OutputBase):
    def __init__(self,host,db="behavior-analysis",port = "27017",user = '', password = '',
                 process_collection = 'behavior-analysis-process',
                 comments_collection = 'behavior-analysis-collection'):
        self.url = f"mongodb://{user}:{password}@{host}:{port}/" if user != '' else f"mongodb://{host}:{port}/"
        self.config = {
            'db': db,
            'process_collection': process_collection,
            'comments_collection': comments_collection
        }
        
    def connect(self):
        config = self.config
        self.client = MongoClient(self.url)
        db = self.client[config['db']]
        self.comments_collection = db[config['comments_collection']]
        self.process_collection = db[config['process_collection']]
        return True
    def sendData(self, comments: list[Comment],processResults:list):
        self.connect()
        toInsert = [dict(comment) for comment in comments]
        self.comments_collection.insert_many(toInsert)
        self.process_collection.insert_many([x.toDict() for x in processResults])