from ..promptInfo import PromptInfo, setPromptsPath
from ..client import IAClient
from ...comment import Comment
from ..requestProcess import RequestProcess
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
    def _makeRequestToAi(self,prompt:str,request:RequestProcess):
        self.countReqs+=1
        if(self.countReqs > 2):
            raise Exception('Expected only 2 requests to AI')
        assert prompt.startswith('<FIRST_TEST>') if self.countReqs == 1 else prompt.startswith('<SECOND_TEST>')
        request.setData([{"behavior":"neutral"},{"behavior":"happy"},{"behavior":"angry"}]).setTokensInput(2).setTokensOutput(5)
def test_client_flux():
    setPromptsPath("src/iaclient/tests/prompt")
    client = FakeClient()
    comments = [Comment('def','comment','test') for x in range(6)]
    comments[0].message = "prompt1"
    process = client.analyze(comments)
    result = process.toDict()
    assert len(result['requests']) == 2
    assert len(result['batchs']) == 2
    assert result['tokens']['output'] == 10
    assert result['tokens']['input'] == 4
    assert client.countReqs == 2