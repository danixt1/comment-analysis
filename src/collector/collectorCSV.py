from src.comment import Comment
from .collectorBase import CollectorBase
from .collectorManager import CollectorManager
import os.path as path
import csv


class CollectorCSV(CollectorBase):
    def __init__(self,path,delimiter = ',',header = None,encoding = 'utf-8') -> None:
        super().__init__()
        self.csvPath = path
        self.delimiter = delimiter
        self.header = header

    def checkConnection(self):
        return path.exists(self.csvPath)
    
    def collect(self) -> list[Comment]:
        comments = []
        header = self.header
        with open(self.csvPath,newline='',encoding='utf-8') as fileCSV:
            csvReader = csv.reader(fileCSV,delimiter=self.delimiter)
            if(not header):
                header = next(csvReader)
            for data in csvReader:
                commentDict = {}
                for index in range(len(header)):
                    dataCell = data[index]
                    commentDict[header[index]] = dataCell
                if not "origin" in commentDict:
                    commentDict["origin"] = "CSV"
                comments.append(Comment.createFromDict(commentDict))
        return comments
    
CollectorManager.registerCollector("CSV", CollectorCSV)