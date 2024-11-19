from src.comment import Comment
from .collectorBase import CollectorBase

class CollectorDBAPI(CollectorBase):

    def __init__(self,dbUrl:str,table:str, mapping:list) -> None:
        super().__init__()
        self.dbUrl = dbUrl
        self.table = table
        self.mapping = mapping
    
    def _initDependecies(self):
        from sqlalchemy import create_engine
        self.engine = create_engine(self.dbUrl)
    def dependencies(self) -> str | list[str]:
        deps = ['SQLAlchemy']
        dbUrl = self.dbUrl
        mapping = [
                ['mysql+mysqlconnector','mysql-connector-python'],
                ['mysql+mysqldb','mysqlclient'],
                ['mysql+pymysql','PyMySQL'],
                ['mssql+pyodbc','pyodbc'],
                ['oracle://','cx_oracle'],
                ['oracle+oracledb','oracledb']
        ]
        for m in mapping:
            if dbUrl.startswith(m[0]):
                deps.append(m[1])
                break
        return deps
    def collect(self) -> list[Comment]:
        from sqlalchemy import text

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
                    if len(self.mapping[index]) == 3:
                        valueToSet = self.mapping[index][2](valueToSet)
                        
                    dictComments[prop] = valueToSet
                if not 'origin' in dictComments:
                    dictComments['origin'] = "SQL:"+self.table
                comments.append(Comment.createFromDict(dictComments))
        return comments
    