from ..comment import Comment

def test_generate_simple_dict():
    _id = 1
    message = 'msgTest'
    msgType = 'comment'
    comment = Comment(_id,message,msgType)
    inList = dict(comment)
    expected = makeBasicDict(_id,message,msgType)
    assert inList == expected, "Comment don't generate the expected dict"

def test_generate_dict_with_process_info():
    from time import time
    _id = 1
    message = 'msgTest'
    msgType = 'comment'

    prcName = 'testProcess/1.0'
    fakeHash = 'fawqh'
    comment = Comment(_id,message,msgType)
    comment.attachInfo({'spam':False},prcName,fakeHash)
    expected = makeBasicDict(_id,message,msgType)
    expected['data'] = {'spam':False}
    expected['process'] = [{
        'name':prcName,
        'hash':fakeHash,
        'timestamp':int(time() * 1000)
    }]
    assert expected == dict(comment)
    
def test_get_message_using_str():
    _id = 1
    message = 'msgTest'
    msgType = 'comment'
    comment = Comment(_id,message,msgType)
    assert message == str(comment)

def makeBasicDict(_id = 1,message = 'msgTest',msgType = 'comment'):
    return {
        "id":_id,
        "message":message,
        "type":msgType,
        "origin":"",
        "process":[],
        "data":{}
    }