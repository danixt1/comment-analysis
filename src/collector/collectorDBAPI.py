from src.comment import Comment
from .collectorBase import CollectorBase
from sqlalchemy import create_engine, text
class CollectorDBAPI(CollectorBase):

    def __init__(self,dbUrl:str,table:str, mapping:list) -> None:
        super().__init__()
        self.engine = create_engine(dbUrl)
        self.table = table
        self.mapping = mapping
    
    def collect(self) -> list[Comment]:
        collumsToGet = [x[0] for x in self.mapping]
        commentRef = [x[1] for x in self.mapping]
        comments = []
        with self.engine.connect() as conn:
            result = conn.execute(text(f'select {",".join(collumsToGet)} from {self.table}'))
            allResults = result.all()
            for row in allResults:
                dictComments = {}
                for index in range(len(commentRef)):
                    prop = commentRef[index]
                    valueToSet = row[index]
                    dictComments[prop] = valueToSet
                if not 'origin' in dictComments:
                    dictComments['origin'] = "SQL:"+self.table
                comments.append(Comment.createFromDict(dictComments))
        return comments