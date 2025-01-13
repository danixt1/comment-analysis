from datetime import datetime, timedelta
import calendar
from dateutil.rrule import rrule, MONTHLY,WEEKLY,DAILY,YEARLY

class DateInterval():

    def __init__(self,dataWithTimestamp:list,granularity:str = None,timestampInSeconds = False):
        n = 1 if timestampInSeconds else 1000
        self._argsLegend = {}
        self._dates = dataWithTimestamp
        self._dates.sort(key=lambda x: x[0])
        self._dates:list[tuple[datetime,object]] = [(datetime.fromtimestamp(x[0] / n),x[1]) for x in self._dates]
        self.intervals = []
        start = self._dates[0][0]
        end = self._dates[-1][0]
        self.jumps = 1
        self.startDate:datetime = start
        self.endDate:datetime = end

        if granularity is None:
            granularity =getGranularity(start,end)

        self.granularity = granularity

        if granularity == "day":
            self._initIter(daiIyIter)
        elif granularity == "week":
            self._initIter(weekIter)
        elif granularity == "month":
            self._initIter(monthIter)
        else:
            raise Exception('invalid granularity')

    def _initIter(self,iterFn):
        addValidItemsByDate( self._dates, self.intervals,iterFn, self.startDate, self.endDate, self.jumps)            
    
    def _makeIntervals(self,quant):
        self.intervals = [[] for _ in range(quant)]

    def setLegendKwargs(self, **kwargs):
        self._argsLegend = kwargs
    
    def getIntervals(self):
        return self.intervals
    
    def getLegends(self):
        return LegendInterval(self,**self._argsLegend,granularity=self.granularity).getLegends()

def add0(num):
    return "0" + str(num) if num < 10 else str(num)

class LegendInterval():

    def __init__(self, dateInterval:DateInterval,limit = 12,minLegends = 6,granularity:str = None):
        self.legends = []
        self.intervals = dateInterval.intervals
        self.startDate = dateInterval.startDate
        self.endDate = dateInterval.endDate
        self.granularity = getGranularity(self.startDate,self.endDate) if not granularity else granularity

        granularity = self.granularity
        if granularity == "day":
            self._legendDay()
        elif granularity == "week":
            self._legendWeek()
        elif granularity == "month":
            self._legendMonth()
        else:
            raise Exception('invalid granularity')

    def _legendYear(self):
        startYear = self.startDate.year
        endYear = self.endDate.year

        self.legends = [str(startYear + i) for i in range(endYear - startYear)]

    def _legendMonth(self,jumpMonths = 1):
        legends = []

        for date in monthIter(self.startDate,self.endDate,jumpMonths):
            legends.append(date.replace(day=1))
        legends[0] = self.startDate
        legends[-1] = datetime(self.endDate.year, self.endDate.month, 1)
        self.legends = legends
    def _legendWeek(self):
        legends = []
        for date in weekIter(self.startDate, self.endDate, 1):
            legends.append(date)
        self.legends = legends

    def _legendDay(self):

        startDate = self.startDate
        endDate = self.endDate

        for date in daiIyIter(startDate, endDate, 1):
            self.legends.append(date)

    def getLegends(self):
        return self.legends
def getGranularity(start,end):
    diffDays = (end - start).days
    if diffDays < 30:
        return "day"
    elif diffDays < 90:
        return "week"
    else:
        return "month"

def addValidItemsByDate(fromDateObjects,insertIn:list,iterFn,startDate,EndDate,jumps = 1):
        lastPos = 0
        for date in iterFn(startDate, EndDate,jumps):
            toInsert = []
            actDate,item = fromDateObjects[lastPos]
            if actDate > date:
                insertIn.append(toInsert)
                continue
            while lastPos < len(fromDateObjects):
                actDate,item = fromDateObjects[lastPos]
                if actDate > date:
                    break
                toInsert.append(item)
                lastPos += 1
            insertIn.append(toInsert)
    
def daiIyIter(start,end,jumpDays):
    startDate = datetime(start.year, start.month, start.day)
    endDate = datetime(end.year, end.month, end.day)
    actJump = 0
    for date in rrule(freq=DAILY, dtstart=startDate, until=endDate):
        actJump += 1
        if actJump == jumpDays:
            actJump = 0
        else:
            continue
        yield datetime(date.year, date.month, date.day, 23, 59, 59)
def weekIter(start,end,jumpWeeks):
    def addWeekDays(date):
        return  6 - calendar.weekday(date.year,date.month,date.day)
    startDate = datetime(start.year, start.month, start.day)
    endDate = datetime(end.year, end.month, end.day) + timedelta(days= addWeekDays(end))

    for date in rrule(freq=WEEKLY, dtstart=startDate, until=endDate, interval=jumpWeeks):
        yield datetime(date.year, date.month, date.day, 23, 59, 59) + timedelta(days=addWeekDays(date))

def monthIter(start,end,jumpMonths):
    # set the initial data to day 1 to avoid skip of date. See (RFC 3.3.10): https://dateutil.readthedocs.io/en/stable/rrule.html
    startDate = datetime(start.year, start.month, 1)
    endDate = datetime(end.year, end.month, 1)

    for date in rrule(freq=MONTHLY, dtstart=startDate, until=endDate, interval=jumpMonths,):
        yield datetime(date.year,date.month,getLastDayOfMonth(date),23,59,59)

def yeaIter(start, end,jump):
    startDate = datetime(start.year, 1, 1, 2)
    endDate = datetime(end.year, 1, 1, 2)

    for date in rrule(freq=YEARLY, dtstart=startDate, until=endDate):
        yield datetime(date.year, 12, 31, 23, 59, 59)
        
def getLastDayOfMonth(date):
    return calendar.monthrange(date.year, date.month)[1]