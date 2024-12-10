from .collectorDBAPI import CollectorDBAPI

class CollectorWordPress(CollectorDBAPI):
    def __init__(self,database:str,user:str,password:str,host:str,port:str = "3306",connector = "mysql+mysqlconnector",where:str = None) -> None:
        self.url = f"{connector}://{user}:{password}@{host}:{port}/{database}"
        mapping = [('comment_content','message'),("comment_date_gmt",'timestamp','gmt')]
        super().__init__(self.url,"wp_comments",mapping=mapping,where=where)