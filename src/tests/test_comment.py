from ..comment import Comment

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