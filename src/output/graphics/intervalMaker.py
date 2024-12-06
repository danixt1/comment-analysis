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

        if granularity is None:
            diffDays = (end - start).days
            if diffDays < 30:
                granularity = "day"
            elif diffDays < 90:
                granularity = "week"
            else:
                granularity = "month"

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