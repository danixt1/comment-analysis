from ..comment import Comment,CommentScorer

def test_generate_simple_dict():
    message = 'msgTest'
    msgType = 'comment'
    comment = Comment(message,msgType,'test')
    comment.localId = 0
    inList = dict(comment)
    expected = makeBasicDict(message,msgType)
    assert inList == expected, "Comment don't generate the expected dict"

def test_generate_dict_with_process_info():
    message = 'msgTest'
    msgType = 'comment'

    prcName = 'testProcess/1.0'
    comment = Comment(message,msgType,"test")
    comment.localId = 0
    comment.attachInfo({'spam':False},prcName,1)
    expected = makeBasicDict(message,msgType)
    expected['process'] = [{
        'name':prcName,
        'data':{'spam':False},
        "process_id":1
    }]
    assert expected == dict(comment)
    
def test_get_message_using_str():
    message = 'msgTest'
    msgType = 'comment'
    comment = Comment(message,msgType,'test')
    comment.localId = 0
    assert message == str(comment)

def test_commentScorer_behavior():
    data = makeBasicScoreData()
    scorer = CommentScorer(data,message="test")
    scorer.attachInfo({'spam':False,"behavior":'positive'}, 'testProcess/1.0', 1)
    assert scorer.getScore()['score'] == 1, "CommentScorer don't return the expected score"

def test_commentScorer_behavior_false():
    data = makeBasicScoreData()
    scorer = CommentScorer(data,message="test")
    scorer.attachInfo({"behavior":'negative'}, 'testProcess/1.0', 1)
    assert scorer.getScore()['score'] == 0, "CommentScorer don't return the expected score"

def test_commentScorer_spam():
    data = makeBasicScoreData()
    data['spam'] = True
    scorer = CommentScorer(data,message="test")
    scorer.attachInfo({'spam':True,"behavior":'positive'}, 'testProcess/1.0', 1)
    assert scorer.getScore()['score'] == 1, "CommentScorer don't return the expected score"

def test_commentScorer_all_problems_detected():
    problems = ['problem1','other','anotherProblem']
    data = makeBasicScoreData()
    data['problems'] = problems
    scorer = CommentScorer(data,message="test")
    scorer.attachInfo({'spam':False,"behavior":'positive','problems':problems}, 'testProcess/1.0', 1)
    assert scorer.getScore()['score'] == 1, "CommentScorer don't returned 1"

def test_commentScorer_problem_missing():
    data = makeBasicScoreData()
    data['problems'] = ['problem1','other','anotherProblem']
    data['behavior'] = '-'
    scorer = CommentScorer(data,message="test")
    scorer.attachInfo({'spam':False,"behavior":'positive','problems':['problem1','fa','anotherProblem']}, 'testProcess/1.0', 1)
    res =scorer.getScore()
    assert res['not_detected'] == ['other'], "not detected problem not is passed in output"
    assert res['score'] == 1 /3 * 2, "CommentScorer don't returned expected score"

def test_commentScorer_full():
    data = makeBasicScoreData()
    data['problems'] = ['problem1','other','anotherProblem2']
    data['spam'] = True
    scorer = CommentScorer(data,message="test")
    scorer.attachInfo({'spam':False,"behavior":'positive','problems':['problem1','fa','anotherProblem']}, 'testProcess/1.0', 1)
    res =scorer.getScore()
    assert res['not_detected'] == ['other','anotherProblem2'], "not detected problem not is passed in output"
    assert res['score'] == 1 /5 * 2, "CommentScorer don't returned 1"
def makeBasicDict(message = 'msgTest',msgType = 'comment'):
    return {
        "origin_id":None,
        "local_id":0,
        "message":message,
        "type":msgType,
        "origin":"test",
        "process":[],
        'timestamp':None
    }
def makeBasicScoreData():
    return {
        'behavior':'positive',
        'spam':False,
        'problems':[],
        'min_problems':0
    }