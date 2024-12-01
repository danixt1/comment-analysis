from pymongo import MongoClient
from bson import ObjectId
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
        process_id = {}
        comments_id = {}

        for process in processResults:
            process_db_id = ObjectId()
            process_id[process['id']] = process_db_id
            process['_id'] = process_db_id
            del process['id']
            for batch in process['batchs']:
                for index in range(len(batch['comments_id'])):
                    comment_db_id = ObjectId()
                    comment_local_id = batch['comments_id'][index]
                    batch['comments_id'][index] = comment_db_id

                    comments_id[comment_local_id] = comment_db_id

        for comment in toInsert:
            comment['_id'] = comments_id[comment['local_id']]
            del comment['local_id']
            for processInfo in comment['process']:
                processInfo['process_id'] = process_id[processInfo['process_id']]
        self.comments_collection.insert_many(toInsert)
        self.process_collection.insert_many(processResults)