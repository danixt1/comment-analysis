from ..datasets import helper
textdata="""# message
{}
# type
{}
# behavior
{}
# spam It should NOT interfere in the test
{}
# problems
{}
# comment
{}
 """


baseComment = ["test","comment","neutral","false",0,"it's a test"]
def test_return_data_without_none():
    comment = list(baseComment)
    text = textdata.format(*comment)
    res = helper.extractDataFrom(text)
    assert all(not x == None for x in res.values())
def test_return_data_with_none_in_type():
    comment = list(baseComment)
    comment[1] = 'invalid type'
    text = textdata.format(*comment)
    res = helper.extractDataFrom(text)
    nones = [x for x in res.values() if x == None]
    assert res['type'] == None, "expected type to be none returned:"+res['type']
    assert len(nones) == 1, "expected only one None value"