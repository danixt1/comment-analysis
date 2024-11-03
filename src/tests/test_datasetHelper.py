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