from ..comment import Comment

def test_generate_simple_dict():
    _id = 1
    message = "msgTest"
    msgType = 'comment'
    comment = Comment(_id,message,msgType)
    inList = dict(comment)
    expected = {
        "id":_id,
        "message":message,
        "type":msgType,
        "origin":"",
        "process":[],
        "data":{}
    }
    assert inList == expected, "Comment don't generate the expected dict"