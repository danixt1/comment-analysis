from src.output.graphics.intervalMaker import DateInterval,LegendInterval
from datetime import datetime
import random

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
    intervalMaker = makeBasicLegendInterval([datetime(2020, 1, 1),datetime(2020,12,1)],"month")
    assert intervalMaker.getLegends() == [add0(x) + "/2020" for x in range(1,13)]

def test_LegendInterval_2_month():
    intervalMaker = makeBasicLegendInterval([datetime(2020, 1, 1), datetime(2020,12,1)], "month")
    legendInterval = LegendInterval(intervalMaker, 6)
    assert legendInterval.getLegends() == [add0(x) + "/2020" for x in range(1, 13, 2)]
    
def add0(x):
    return "0"+str(x) if x < 10 else str(x)

def makeBasicLegendInterval(dates,granularity):
    dates = [datetime(2020, 1, 1),datetime(2020,12,1)]
    data = [{"ref":x.month,"day":x.day} for x in dates]
    dates = [x.timestamp() for x in dates]
    datesWithInterval = list(zip(dates, data))
    random.shuffle(datesWithInterval)
    return DateInterval(datesWithInterval,granularity, timestampInSeconds=True)