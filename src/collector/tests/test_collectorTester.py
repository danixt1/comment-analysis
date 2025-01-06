from ..collectorTester import CollectorTester
from datetime import datetime
def test_basic_collector():
    collector = CollectorTester(10)
    comments = collector.collect()
    assert len(comments) == 10

def test_with_gmt():
    start = int(datetime(2020, 10, 4).timestamp() * 1000)
    end = int(datetime(2021, 10, 5, 12, 23, 42).timestamp() * 1000)
    collector = CollectorTester(10, gmts=('2020-10-04','2021-10-05 12:23:42'))
    comments = collector.collect()
    assert len(comments) == 10
    for comment in comments:
        assert comment.timestamp >= start 
        assert comment.timestamp <= end