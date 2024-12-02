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
    res = makeData(4,searchIn=[{
        "lang":"en",
        "tags":["product","generic"],
        "messages":["excelent [test1|test2|another|other] and [have this|and this| and that]",'good'],
        "behavior":"positive"
    },
    {
        "lang":"en",
        "tags":["product","generic"],
        "messages":["bad [test|test2|test3]",'bad quality',],
        "behavior":"negative"
    }])
    assert len(res) == 4
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