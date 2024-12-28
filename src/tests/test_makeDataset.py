from src.datasets.makeDataset import makeData,makeCSV
import csv
from datetime import datetime

def test_make_all_variations_from_data():
    res = makeData(1000,searchIn=[{
        "lang":"en",
        "tags":["product","generic"],
        "messages":["excelent [test1|test2]",'good'],
        "behavior":"positive"
    }])
    res = [x['message'] for x in res]
    res.sort()
    assert len(res) == 3
    assert res == ['excelent test1','excelent test2','good']

def test_make_dataset_with_limit():
    res = makeData(10,searchIn=[{
        "lang":"en",
        "tags":["product","generic"],
        "messages":["excelent [test1|test2|another|other|other initial] and [have this|and this| and that]",'good'],
        "behavior":"positive"
    },
    {
        "lang":"en",
        "tags":["product","generic"],
        "messages":["bad [test|test2|test3]",'bad quality',],
        "behavior":"negative"
    }],maxPositives=0.7)
    assert len(res) == 10
    assert len([x for x in res if x['expected']['behavior'] == 'positive']) == 7
    assert len([x for x in res if x['expected']['behavior'] == 'negative']) == 3

def test_tag_system():
    res = makeData(10,searchIn=[{
        "lang":'en',
        "tags":["no"],
        "messages":["NO [a1|a2|a3] and [b1|b2|b3]"],
        "behavior":"negative"
    },
    {
        "lang":"en",
        "tags":['ok'],
        "message":"OK",
        "behavior":"negative"
    }],exclude_tags=['no'])
    assert len(res) == 1
    assert res[0]['message'] == 'OK'
def test_timestamp():
    start =int(datetime(2020,1,1).timestamp() * 1000)
    end = int(datetime(2020, 5, 2).timestamp() * 1000)
    res = makeData(3,searchIn=[{
        "lang":'en',
        "tags":["test"],
        "messages":["test1",'test2','test3'],
        "behavior":"negative"
    }
    ],timestamps=(start,end))
    assert len(res) == 3
    assert len([x for x in res if 'timestamp' in x]) == 3
    assert all([x['timestamp'] >= start and x['timestamp'] <= end for x in res]), 'Invalid timestamp'

def test_make_csv(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("data")
    makeCSV(str(tmp_path / 'data.csv'),useData=[{
        "lang":"en",
        "tags":["product","generic"],
        "messages":["excelent [test1|test2]",'good'],
        "behavior":"positive"
    }])
    with open(str(tmp_path / 'data.csv')) as f:
        reader = csv.reader(f)
        res = [x[0] for x in reader]
        res.sort()
        assert len(res) == 4
        assert res == ['excelent test1','excelent test2','good','message']

def test_make_csv_with_timestamp(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("data")
    start =int(datetime(2020,1,1).timestamp() * 1000)
    end = int(datetime(2020, 5, 2).timestamp() * 1000)

    makeCSV(str(tmp_path / 'dataTimestamp.csv'),useData=[{
        "lang":"en",
        "tags":["product","generic"],
        "messages":["excelent [test1|test2]",'good'],
        "behavior":"positive"
    }],config={'timestamps':(start,end),'limit':100})

    with open(str(tmp_path / 'dataTimestamp.csv')) as f:
        reader = csv.reader(f)
        readedData = [x for x in reader]
        assert len(readedData) == 4
        res = [x[3] for x in readedData]
        assert all([int(x) >= start and int(x) <= end for x in res[1::]]), 'Invalid timestamp'