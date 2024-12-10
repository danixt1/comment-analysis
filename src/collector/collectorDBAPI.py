from src.comment import Comment
from .collectorBase import CollectorBase
from sqlalchemy import create_engine, text

def convert_date_gmt(date_str):
    from datetime import datetime
    return int(datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)

mappingsFns = {
    "gmt":convert_date_gmt
}
class CollectorDBAPI(CollectorBase):

    def __init__(self,dbUrl:str,table:str, mapping:list,where:str = None) -> None:
        super().__init__()
        self.engine = create_engine(dbUrl)
        self.table = table
        self.mapping = mapping
        self.where = where or ''
    
    def collect(self) -> list[Comment]:
        collumsToGet = [x[0] for x in self.mapping]
        commentRef = [x[1] for x in self.mapping]
        comments = []
        where = " WHERE " + self.where + ';' if self.where else ';'
        with self.engine.connect() as conn:
            result = conn.execute(text(f'SELECT {",".join(collumsToGet)} FROM {self.table}' + where))
            allResults = result.all()
            for row in allResults:
                dictComments = {}
                for index in range(len(commentRef)):
                    prop = commentRef[index]
                    valueToSet = row[index]
                    if len(self.mapping[index]) == 3:
                        fnInfo = self.mapping[index][2]
                        if isinstance(fnInfo,str):
                            try:
                                fnInfo =  mappingsFns[fnInfo]
                            except KeyError as err:
                                err.add_note("collector.dbapi:supported mapping fns is: "+str(mappingsFns.keys()))
                                raise err
                        valueToSet = fnInfo(valueToSet)
                    dictComments[prop] = valueToSet

                if not 'origin' in dictComments:
                    dictComments['origin'] = "SQL:"+self.table
                comments.append(Comment(**dictComments))
        return comments
    