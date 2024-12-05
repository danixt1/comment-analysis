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
            self._dailyInterval()#TODO testing
        elif granularity == "week":

            weeks = calendar.monthcalendar(start.year,start.month)
            print(weeks)
            #weekIndex = weeks.index([x for x in weeks if start.day in x][0]) + 1#this is the location of the first week
            actMonth = start.month
            actYear = start.year
            totalMonths = (end.year - start.year) * 12 + (end.month - start.month) + 1
            #self.intervals = [[] for _ in range(len(weeks) - weekIndex)]
            lastData = 0
            for i in range(totalMonths):
                currentWeeks =calendar.monthcalendar(actYear, actMonth)
                lenWeeks = len(currentWeeks)
                startFrom = len(self.intervals)

                if currentWeeks[0][0] == 0:#if the day is 0 its because continuation the last week
                    startFrom -= 1
                    lenWeeks -= 1
                self.intervals.extend([[] for _ in range(lenWeeks)])

                for dataIndex in range(lastData, len(self._dates)):
                    date,data = self._dates[dataIndex]
                    if date.month == actMonth and date.year == actYear:

                        for weekIndex in range(lenWeeks):
                            if date.day in currentWeeks[weekIndex]:
                                finalPos = weekIndex + startFrom
                                self.intervals[finalPos].append(data)
                                lastData = dataIndex + 1
                    else:
                        break
                actMonth += 1
                if actMonth > 12:
                    actMonth = 1
                    actYear += 1
            #print(len(weeks) - weekIndex)
            #mode 1 if the first value is 0 then skip this week because its continuation from the before else if it is the start week
            #raise NotImplementedError()
            #self.intervals = [[]] * int(diffDays / 7)
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