from datetime import datetime
from src.comment import Comment
from .collectorBase import CollectorBase
from .collectorDBAPI import CollectorDBAPI
from .collectorManager import CollectorManager

class CollectorWordPress(CollectorBase):
    def __init__(self,database:str,user:str,password:str,host:str,port:str = "3306",connector = "mysql+mysqlconnector") -> None:
        super().__init__()
        self.url = f"{connector}://{user}:{password}@{host}:{port}/{database}"
    def collect(self) -> list[Comment]:
        convert_date_gmt = lambda date_str: int(datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
        mapping = [('comment_content','message'),("comment_date_gmt",'timestamp',convert_date_gmt)]
        table = "wp_comments"
        self.collector = CollectorDBAPI(self.url,table,mapping)
        return self.collector.collect()

CollectorManager.registerCollector("wordpress", CollectorWordPress)