from ..promptInfo import PromptInfo, setPromptsPath
from ..client import IAClient
from ...comment import Comment
from ..responseInfo import ResponseInfo
from typing import List

class FakeClient(IAClient):

    def __init__(self):
        super().__init__("test-client")
        self.countReqs = 0

    def _separateCommentsBatch(self,comments: List[Comment]) -> List[List[Comment]]:
        lot1 = comments[::2]
        lot2 = comments[1::2]
        return [lot1,lot2]
    def _generatePrompt(self,comments: List[Comment]):
        assert len(comments) == 3, "expected only 3 comments after being separated"
        firstCmt = comments[0]
        return PromptInfo('test1' if str(firstCmt) == 'prompt1' else 'test2')
    def _makeRequestToAi(self,prompt:str)->ResponseInfo:
        self.countReqs+=1
        if(self.countReqs > 2):
            raise Exception('Expected only 2 requests to AI')
        assert prompt.startswith('<FIRST_TEST>') if self.countReqs == 1 else prompt.startswith('<SECOND_TEST>')
        response = ResponseInfo()
        response.setData([{"behavior":"neutral"},{"behavior":"happy"},{"behavior":"angry"}])
        return response
def test_client_flux():
    setPromptsPath("src/iaclient/tests/prompt")
    client = FakeClient()
    comments = [Comment('def','comment','test') for x in range(6)]
    comments[0].message = "prompt1"
    assert client.analyze(comments)
    assert client.countReqs == 2