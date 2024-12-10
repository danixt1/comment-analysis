from .collectorDBAPI import CollectorDBAPI
import os
class CollectorWordPress(CollectorDBAPI):
    def __init__(self,database:str,host:str,prefix:str = None,port:str = "3306",connector = "mysql+mysqlconnector",where:str = None) -> None:
        prefix = prefix + '_' or ''
        user = os.getenv(prefix+'WP_USERNAME','')
        password = os.getenv(prefix+'WP_PASSWORD','')
        self.url = f"{connector}://{user}:{password}@{host}:{port}/{database}"
        mapping = [('comment_content','message'),("comment_date_gmt",'timestamp','gmt')]
        super().__init__(self.url,"wp_comments",mapping=mapping,where=where)