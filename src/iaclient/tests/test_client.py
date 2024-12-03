from ..promptInfo import PromptInfo, setPromptsPath
from ..client import IAClient
from ...comment import Comment,CommentScorer
from ..requestProcess import RequestProcess
from typing import List

class FakeClient(IAClient):

    def __init__(self,retData):
        super().__init__("test-client")
        self.countReqs = 0
        self.expectedLot = [0,0]
        self.actPrompt =0
        self.retData = retData
        self.comments = None
    def _separateCommentsBatch(self,comments: List[Comment]) -> List[List[Comment]]:
        self.comments = comments
        lot1 = comments[::2]
        lot2 = comments[1::2]
        self.expectedLot[0] =len(lot1)
        self.expectedLot[1] = len(lot2)
        return [lot1,lot2]
    def _generatePrompt(self,comments: List[Comment]):
        assert len(comments) == self.expectedLot[self.actPrompt], "Don't have the expected quantity of comments to the lot"
        self.actPrompt+=1
        firstCmt = comments[0]
        return PromptInfo('test1' if str(firstCmt) == 'prompt1' else 'test2')
    def _makeRequestToAi(self,prompt:str,request:RequestProcess):
        self.countReqs+=1
        request.setData(self.retData).setTokensInput(2).setTokensOutput(5)

def test_client_flux():
    setPromptsPath("src/iaclient/tests/prompt")
    client = FakeClient([{"behavior":"neutral"},{"behavior":"happy"},{"behavior":"angry"}])
    comments = [Comment('def','comment','test') for x in range(6)]
    result = client.analyze(comments)
    assert client.countReqs == 2
    assert len(result['requests']) == 2
    assert len(result['batchs']) == 2
    assert result['tokens']['output'] == 10
    assert result['tokens']['input'] == 4
    assert client.countReqs == 2

def test_client_with_auto_test():
    setPromptsPath("src/iaclient/tests/prompt")
    rets = [
        {"behavior":"neutral"},{"behavior":"happy"},{"behavior":"angry"},
    ]
    TOTAL_COMMENTS_PASSED = 4
    TOTAL_AUTO_TESTS_PERCENTAGE = 0.50
    TOTAL_COMMENT_SCORER_EXPECTED = 2
    TOTAL_COMMENTS_EXPECTED = TOTAL_COMMENTS_PASSED + (TOTAL_AUTO_TESTS_PERCENTAGE * TOTAL_COMMENTS_PASSED)
    client = FakeClient(rets)
    comments = [Comment('def', 'comment', 'test') for x in range(TOTAL_COMMENTS_PASSED)]
    client.useAutoTest(TOTAL_AUTO_TESTS_PERCENTAGE)
    result = client.analyze(comments)
    assert client.countReqs == 2
    assert len(client.comments) == TOTAL_COMMENTS_EXPECTED
    assert len([x for x in client.comments if isinstance(x,CommentScorer)]) == TOTAL_COMMENT_SCORER_EXPECTED
    assert 'score' in result