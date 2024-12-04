from src.comment import Comment
from datetime import datetime
import calendar

class DateInterval():

    def __init__(self,dataWithTimestamp:list,granularity:str = None,timestampInSeconds = False):
        n = 1 if timestampInSeconds else 1000
        self._dates = dataWithTimestamp
        self._dates.sort(key=lambda x: x[0])
        self._dates = [[datetime.fromtimestamp(x[0] / n),x[1]] for x in self._dates]
        self.intervals = []
        start = self._dates[0][0]
        end = self._dates[-1][0]

        self.startDate = start
        self.endDate = end

        diffDays = (end - start).days
        if granularity is None:
            if diffDays < 30:
                granularity = "daily"
            elif diffDays < 90:
                granularity = "week"
            else:
                granularity = "month"

        if granularity == "daily":
            self._dailyInterval()#TODO testing
        elif granularity == "week":
            raise NotImplementedError()
            self.intervals = [[]] * int(diffDays / 7)
            steps = 604800
        elif granularity == "month":
            self._montlyInterval()
        else:
            raise Exception('invalid granularity')

    def _dailyInterval(self):
        start = self.startDate
        end = self.endDate
        daysPassed = (end - start).days
        self.intervals = [[] for _ in range(daysPassed)]

        for date,comment in self._dates:
            diffFromStart = (date - start).days
            self.intervals[diffFromStart].append(comment)
        
    def _montlyInterval(self):
        start = self.startDate
        end = self.endDate
        
        monthsPassed = (end.year - start.year) * 12 + (end.month - start.month) + 1
        self._makeIntervals(monthsPassed)
        lastPos = 0
        monthInYear = start.month
        for i in range(monthsPassed):
            lastPos = self._stepEveryMonth(lastPos,monthInYear,i)
            if monthInYear == 12:
                monthInYear = 1
                continue
            monthInYear += 1

    def _stepEveryMonth(self,actPos:int,actMonth,indexIntervals):
        actInterval = self.intervals[indexIntervals]
        for date,comment in self._dates[actPos::]:
            if date.month == actMonth:
                actPos += 1
                actInterval.append(comment)
            else:
                break
        return actPos
    
    def _makeIntervals(self,quant):
        self.intervals = [[] for _ in range(quant)]
    def getIntervals(self):
        return self.intervals