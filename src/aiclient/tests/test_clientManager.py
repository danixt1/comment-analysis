from src.aiclient.clientManager import ClientManager
from src.aiclient.client import AiClient
from src.aiclient.promptInfo import PromptInfo, setPromptsPath
from src.comment import Comment, CommentScorer

class FakeClient(AiClient):
    def __init__(self):
        super().__init__('fake-client')
        self.comments = []
    def _generatePrompt(self, comments):
        return PromptInfo('test1')
    def _makeRequestToAi(self, prompt, request):
        request.setData([{"behavior":"happy"}] * 3).setTokensInput(2).setTokensOutput(5)
    def _separateCommentsBatch(self, comments):
        self.comments = comments
        return [comments]
    
ClientManager.addInstanceable('test',('src.aiclient.tests.test_clientManager','FakeClient'))

def test_clientManagerWithScorer():
    setPromptsPath("src/aiclient/tests/prompt")
    config = {
        "data":[
            {
                "scorer":{
                    'percentage':50
                },
                "name":"test"
            }
        ]
    }
    manager = ClientManager.initWithConfig(config)
    manager.analyze([Comment('test'),Comment('test2')])
    assert len(manager._items) == 1
    fakeClient = manager._items[0]
    assert len(fakeClient.comments) == 3
    assert len([x for x in fakeClient.comments if isinstance(x,CommentScorer)]) == 1