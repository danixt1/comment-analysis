from src.output.graphics.intervalMaker import DateInterval
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