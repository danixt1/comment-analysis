from datetime import datetime
import calendar
from dateutil.rrule import rrule, MONTHLY

class DateInterval():

    def __init__(self,dataWithTimestamp:list,granularity:str = None,timestampInSeconds = False):
        n = 1 if timestampInSeconds else 1000
        self._argsLegend = {}
        self._dates = dataWithTimestamp
        self._dates.sort(key=lambda x: x[0])
        self._dates = [[datetime.fromtimestamp(x[0] / n),x[1]] for x in self._dates]
        self.intervals = []
        start = self._dates[0][0]
        end = self._dates[-1][0]

        self.startDate:datetime = start
        self.endDate:datetime = end

        if granularity is None:
            diffDays = (end - start).days
            if diffDays < 30:
                granularity = "day"
            elif diffDays < 90:
                granularity = "week"
            else:
                granularity = "month"

        self.granularity = granularity

        if granularity == "day":
            self._dailyInterval()
        elif granularity == "week":
            self._weekInterval()
        elif granularity == "month":
            self._montlyInterval()
        else:
            raise Exception('invalid granularity')
        
    def _weekInterval(self):
        start = self.startDate
        end = self.endDate

        actMonth = start.month
        actYear = start.year

        currentWeeks =calendar.monthcalendar(actYear, actMonth)

        startPosition = 0
        for week in currentWeeks:
            if start.day in week:
                break
            startPosition += 1
        currentWeeks = currentWeeks[startPosition:]

        totalMonths = (end.year - start.year) * 12 + (end.month - start.month)
        lastData = self._stepWeek( actYear,actMonth, currentWeeks, 0)
        for _ in range(totalMonths):
            actMonth += 1
            if actMonth > 12:
                actMonth = 1
                actYear += 1

            currentWeeks =calendar.monthcalendar(actYear, actMonth)
            continueFromLastWeek = currentWeeks[0][0] == 0
            lastData = self._stepWeek(actYear,actMonth,currentWeeks,lastData,continueFromLastWeek)

        removeLastClearIndex = len(self.intervals)
        for i in range(len(self.intervals)-1,-1,-1):
            if len(self.intervals[i]) == 0:
                removeLastClearIndex = i
            else:
                break
        self.intervals = self.intervals[:removeLastClearIndex]
    
    def _stepWeek(self,actYear,actMonth,currentWeeks,lastData, continueFromLastWeek = False):
            lenWeeks = len(currentWeeks)
            startFrom = len(self.intervals)
            if continueFromLastWeek:
                lenWeeks -=1
                startFrom -=1
            lastDataPos = lastData
            self.intervals.extend([[] for _ in range(lenWeeks)])

            for dataIndex in range(lastData, len(self._dates)):
                date,data = self._dates[dataIndex]
                if date.month == actMonth and date.year == actYear:

                    for weekIndex in range(lenWeeks):
                        if date.day in currentWeeks[weekIndex]:
                            finalPos = weekIndex + startFrom
                            self.intervals[finalPos].append(data)
                            lastDataPos =  dataIndex + 1
                            break
                else:
                    return lastDataPos
            return lastDataPos
                
    def _dailyInterval(self):
        start = self.startDate
        end = self.endDate
        daysPassed = (end - start).days
        self.intervals = [[] for _ in range(daysPassed)]

        for date,comment in self._dates:
            diffFromStart = (date - start).days
            self.intervals[diffFromStart].append(comment)
        
    def _montlyInterval(self,jumps = 1):
        lastPassedDateIndex = 0

        for date in rruleMonthIter(self.startDate,self.endDate,jumps):
            lastPassedDateIndex = self._stepEveryMonth(lastPassedDateIndex, date.month)

    def _stepEveryMonth(self,actPos:int,actMonth):
        actInterval = []
        for date,data in self._dates[actPos::]:
            if date.month == actMonth:
                actPos += 1
                actInterval.append(data)
            else:
                break
        self.intervals.append(actInterval)
        return actPos
    
    def _makeIntervals(self,quant):
        self.intervals = [[] for _ in range(quant)]

    def setLegendKwargs(self, **kwargs):
        self._argsLegend = kwargs
    
    def getIntervals(self):
        return self.intervals
    
    def getLegends(self):
        return LegendInterval(self,**self._argsLegend).getLegends()

def add0(num):
    return "0" + str(num) if num < 10 else str(num)

class LegendInterval():

    def __init__(self, dateInterval:DateInterval,limit = 12,minLegends = 6):
        self.legends = []
        self.intervals = dateInterval.intervals
        self.startDate = dateInterval.startDate
        self.endDate = dateInterval.endDate

        startDate= self.startDate
        endDate = self.endDate

        diffYears = endDate.year - startDate.year

        def checkOthers():
            totalMonths = endDate.month - startDate.month + 1
            if totalMonths > minLegends:
                self._legendMonth(jumpMonths = totalMonths // limit)
            else:
                totalDays = (endDate - startDate).days
                if totalDays > minLegends:
                    self._legendDay()
                else:
                    self._legendHour()

        if diffYears > 0:
            if diffYears > minLegends:
                self._legendYear()
            else:
                checkOthers()
        else:
            checkOthers()

    def _legendYear(self):
        startYear = self.startDate.year
        endYear = self.endDate.year

        self.legends = [str(startYear + i) for i in range(endYear - startYear)]

    def _legendMonth(self,jumpMonths = 1):
        legends = []

        for date in rruleMonthIter(self.startDate,self.endDate,jumpMonths):
            legends.append(f"{add0(date.month)}/{date.year}")

        self.legends = legends

    def _legendDay(self):
        startDate = self.startDate
        endDate = self.endDate

        startDay = startDate.day
        endDay = endDate.day

        if startDate.month == endDate.month:
            self.legends = [add0(startDay + i) for i in range(endDay - startDay)]
            return
        actDay = startDate.day
        actMonth = startDate.month
        totalDays = (endDate - startDate).days
        for _ in range(totalDays):
            self.legends.append(f"{add0(actDay)}/{add0(actMonth)}")
            actDay += 1
            if actDay > calendar.monthrange(startDate.year, actMonth)[1]:
                actDay = 1
                actMonth += 1
                if actMonth > 12:
                    actMonth = 1
    
    def _legendHour(self):
        startHour = self.startDate.hour
        endHour = self.endDate.hour
        self.legends = [add0(startHour + i) for i in range(endHour - startHour)]

    def getLegends(self):
        return self.legends

def rruleMonthIter(start,end,intervals):
    # Solution to RFC 3.3.10 more in: https://dateutil.readthedocs.io/en/stable/rrule.html

    startDate = datetime(start.year, start.month, 1, 2)
    endDate = datetime(end.year, end.month, 1, 2)

    for date in rrule(freq=MONTHLY, dtstart=startDate, until=endDate, interval=intervals):
        yield date