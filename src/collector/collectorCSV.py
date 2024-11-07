from src.comment import Comment
from .collectorBase import CollectorBase
import os.path as path
import csv
class CollectorCSV(CollectorBase):
    def __init__(self,csvPath,delimiter = ',',header = None) -> None:
        super().__init__()
        self.csvPath = csvPath
        self.delimiter = delimiter
        self.header = header

    def checkConnection(self):
        return path.exists(self.csvPath)
    
    def collect(self) -> list[Comment]:
        comments = []
        header = self.header
        with open(self.csvPath,newline='') as fileCSV:
            csvReader = csv.reader(fileCSV,delimiter=self.delimiter)
            if(not header):
                header = next(csvReader)
            for data in csvReader:
                commentDict = []
                for index in range(len(header)):
                    dataCell = data[index]
                    commentDict[header[index]] = dataCell
                if not "origin" in commentDict:
                    commentDict["origin"] = "CSV"
                comments.append(Comment.createFromDict(commentDict))
        return comments