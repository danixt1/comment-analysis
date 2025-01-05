from src.output.graphics.intervalMaker import DateInterval,LegendInterval,addValidItemsByDate,daiIyIter,monthIter,weekIter
from datetime import datetime
import random

def test_validItemsByDate_dailyIter():
    dates = [(2020,1,1),(2020, 1, 2),(2020, 1, 2),(2020, 1, 3),(2020, 1, 4),(2020, 1, 7)]
    data = [1,'22',2,3,4,5]
    banch = IterTestBanch(dates,data)
    banch.addValidItemsByDate(daiIyIter)
    banch.assertResult( [[1],['22',2],[3],[4],[],[],[5]] )


def test_validItemsByDate_weekIter():
    dates = [(2024,4,3),(2024,4,5),(2024,4,7),(2024,4,9),(2024,4,22)]
    data = ['w1','w1.2','w1.3','w2','w4']
    banch = IterTestBanch(dates, data)
    banch.addValidItemsByDate(weekIter)
    banch.assertResult([['w1', 'w1.2', 'w1.3'], ['w2'], [], ['w4']])

def test_validItemsByDate_monthIter():
    dates = [(2019, 12, 1),(2019,12,23),(2020,1,2),(2020,3,5),(2020,3,12)]
    data = ['month12','month12.2',1,2,3]
    banch = IterTestBanch(dates, data)
    banch.addValidItemsByDate(monthIter)
    banch.assertResult([['month12','month12.2'],[1],[],[2,3]])

def test_DateInterval_month():
    INITIAL_MONTH = 2
    #dates from 2020/02/01 to 2020/12/01
    dates = [datetime(2020,x,1) for x in range(INITIAL_MONTH,11 + INITIAL_MONTH)]

    #Add two more dates in march making position 1 to by expected to have 3 datas
    dates.append(datetime(2020, 3, 3))
    dates.append(datetime(2020, 3, 8))

    #Add two more month to test when the interval not is in the same year
    dates.append(datetime(2021, 1, 15))
    dates.append(datetime(2021, 4, 16))
    #Remove the date from April making expected a gape in position two of interval

    dates.remove(dates[2])
    data = [{"ref":x.month,"day":x.day} for x in dates]
    dates = [x.timestamp() for x in dates]
    datesWithInterval = list(zip(dates,data))

    random.shuffle(datesWithInterval)

    intervalMaker = DateInterval(datesWithInterval,"month",timestampInSeconds=True)
    intervals = intervalMaker.getIntervals()
    counts = [len(x) for x in intervals]
    assert counts == [1, 3, 0, 1, 1, 1, 1, 1, 1, 1, 1,1,0,0,1]
    actMonth = INITIAL_MONTH
    for index in range(len(intervals)):
        datas = intervals[index]

        for data in datas:
            assert data["ref"] == actMonth, "Incorrect month"
        actMonth += 1
        if actMonth > 12:
            actMonth = 1
    #Check the order and if the values is passed correct.
    assert [x['day'] for x in intervals[1]] == [1,3,8],"Incorrect expected values"

def test_DateInterval_week():
    # Day is 9(Monday) what is the start of the 2 second week(in python default behavior) the first week MUST NOT exist in output.
    # Days 10,15 is in the same week of 12 making the first value equal 3
    # From day 17 to 30 have one week gap(0).
    # Day 1 of 2025(Wednesday) need to continue the week of day 30 in 2024 making the final value 2
    # The others weeks need to be desconsidered
    dates = [datetime(2024, 12, 9),datetime(2024, 12, 10),datetime(2024,12,15),datetime(2024,12,17),datetime(2024,12,30),datetime(2025,1,1)]

    data = [{"ref":x.month,"day":x.day} for x in dates]
    dates = [x.timestamp() for x in dates]
    datesWithInterval = list(zip(dates,data))

    random.shuffle(datesWithInterval)
    intervalMaker = DateInterval(datesWithInterval,"week",timestampInSeconds=True)
    intervals = intervalMaker.getIntervals()
    counts = [len(x) for x in intervals]
    assert counts == [3, 1, 0, 2]
    assert intervals[3][1] == {"ref":1,"day":1}
    assert intervals[0][0] == {"ref":12,"day":9}
    assert intervals[0][1] == {"ref":12,"day":10}

def test_LegendInterval_month():
    intervalMaker = makeBasicLegendInterval([datetime(2020, 1, 1),datetime(2020,4,1)],"month")
    assert [str(x.month) + "/2020" for x in intervalMaker.getLegends()] == [str(x) + "/2020" for x in range(1,13)]
    
def add0(x):
    return "0"+str(x) if x < 10 else str(x)
def datesArr(*args):
    return [datetime(*x) for x in args]
class IterTestBanch:
    def __init__(self,dates:list[tuple],data:list):
        self._dates = [datetime(*x) for x in dates]
        self._data = data
    def addValidItemsByDate(self, iterFn,jumps = 1):
        self.results = []
        datesWithInterval = list(zip(self._dates, self._data))
        addValidItemsByDate(datesWithInterval,self.results,iterFn,self._dates[0],self._dates[-1],jumps)
    def assertResult(self, expected):
        assert self.results == expected

def makeBasicLegendInterval(dates,granularity):
    dates = [datetime(2020, 1, 1),datetime(2020,12,1)]
    data = [{"ref":x.month,"day":x.day} for x in dates]
    dates = [x.timestamp() for x in dates]
    datesWithInterval = list(zip(dates, data))
    random.shuffle(datesWithInterval)
    return DateInterval(datesWithInterval,granularity, timestampInSeconds=True)