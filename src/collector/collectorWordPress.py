from datetime import datetime
from .collectorDBAPI import CollectorDBAPI

class CollectorWordPress(CollectorDBAPI):
    def __init__(self,database:str,user:str,password:str,host:str,port:str = "3306",connector = "mysql+mysqlconnector") -> None:
        convert_date_gmt = lambda date_str: int(datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
        super().__init__(f"{connector}://{user}:{password}@{host}:{port}/{database}",
                         "wp_comments",
                         [('comment_content','message'),("comment_date_gmt",'timestamp',convert_date_gmt)])
    