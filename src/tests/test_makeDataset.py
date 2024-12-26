from src.datasets.makeDataset import makeData,makeCSV
import csv
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