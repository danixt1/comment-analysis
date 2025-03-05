from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId
from src.comment import Comment
from .outputBase import OutputBase
from contextlib import contextmanager

class OutputMongoDb(OutputBase):
    def __init__(self,host:str,db:str="behavior-analysis",port:str | int = "27017",user:str = '', password:str = '',collections:dict[str,str] = None):
        if collections is None:
            collections = {
                "process":'process',
                "comments":'comments'
            }
        if "comments" not in collections:
            raise Exception("Collection comments not found, pass `comments` in collections parameter")
        if not isinstance(collections["comments"],str):
            raise Exception("Collection comments must be a string")
        if isinstance(port,int):
            port = str(port)
        self.url = f"mongodb://{user}:{password}@{host}:{port}/" if user != '' else f"mongodb://{host}:{port}/"
        self.config = {
            'db': db,
            'process_collection': collections["process"] if "process" in collections and collections["process"] != "" else None,
            'comments_collection': collections["comments"]
        }
    @contextmanager
    def connection(self):
        try:
            self.connect()
            yield
        except PyMongoError as e:
            raise Exception(f"Database operation failed: {str(e)}")
        except Exception as e:
            raise e
        finally:
            if hasattr(self, 'client'):
                self.client.close()

    def connect(self):
        config = self.config
        self.client = MongoClient(self.url)
        db = self.client[config['db']]
        self.comments_collection = db[config['comments_collection']]
        self.process_collection = db[config['process_collection']] if config['process_collection'] is not None else None
        return True
    
    def sendData(self, comments: list[Comment],processResults:list):
        with self.connection():
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
                if comment['local_id'] not in comments_id:
                    continue
                comment['_id'] = comments_id[comment['local_id']]
                del comment['local_id']
                for processInfo in comment['process']:
                    processInfo['process_id'] = process_id[processInfo['process_id']]
            self.comments_collection.insert_many(toInsert)
            if self.process_collection:
                self.process_collection.insert_many(processResults)