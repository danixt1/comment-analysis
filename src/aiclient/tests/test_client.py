from ..promptInfo import PromptInfo, setPromptsPath
from ..client import AiClient, BatchbucketManager,RuleBatchType
from ...comment import Comment,CommentScorer
from ..requestProcess import RequestProcess
from typing import List

class FakeClient(AiClient):

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

class FakeClientAutoRetryTest(AiClient):
    def __init__(self, responses, batchs = None,tolerance=2):
        self.batchs = batchs
        self.responses = responses
        self.actRes = 0
        self.promptHistoric = []
        super().__init__("test-retry",tolerance=tolerance)
    def _separateCommentsBatch(self, comments):
        return [comments] if self.batchs is None else self.batchs
    def _generatePrompt(self, comments):
        self.promptHistoric.append(len(comments))
        return PromptInfo('test1' if str(comments[0]) == 'prompt1' else 'test2')
    def _makeRequestToAi(self, prompt, request):
        if self.actRes >= len(self.responses):
            raise Exception("No more responses")
        request.setData(self.responses[self.actRes]).setTokensInput(1).setTokensOutput(3)
        self.actRes +=1
    

def test_client_flux():
    setPromptsPath("src/aiclient/tests/prompt")
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
    setPromptsPath("src/aiclient/tests/prompt")
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

def test_client_auto_retry_on_missing_data():
    # Make one request to analyze 5 comments but the AI only return the answer of 3 comments.
    # is expected a second request to two final comments who not is processed in first request.
    setPromptsPath("src/aiclient/tests/prompt")
    responses = [
        [{"behavior":"neutral"},{"behavior":"happy"},{"behavior":"happy"}],
        [{"behavior":"angry"},{"behavior":"angry"}]
    ]
    comments = [Comment('def','comment','test') for _ in range(5)]
    client = FakeClientAutoRetryTest(responses)
    result = client.analyze(comments)
    # First try with the 5 comments, after only returning 3 comment try the two left.
    assert client.promptHistoric == [5,2]
    assert client.actRes == 2
    assert all([comment.getData() for comment in comments]), "Returned comments without data"
    assert comments[4].getData()['behavior'] == 'angry'
    assert comments[1].getData()['behavior'] == 'happy'

def test_client_auto_retry_on_hallucination():
    setPromptsPath("src/aiclient/tests/prompt")
    responses = [
        [{'behavior':'angry'},{'behavior':'happy'},{'behavior':'happy'},{'behavior':'neutral'},{'behavior':'angry'},{'behavior':'happy'}],
        [{'behavior':'happy'},{'behavior':'angry'}],
        [{'behavior':'neutral'},{'behavior':'angry'}]
    ]
    comments = [Comment('def','comment','test') for _ in range(4)]
    client = FakeClientAutoRetryTest(responses,tolerance=3)
    result = client.analyze(comments)

    assert client.promptHistoric == [4,2,2]
    assert client.actRes == 3
    assert all([comment.getData() for comment in comments]), "Returned comments without data"
    assert comments[1].getData()['behavior'] == 'angry'
    assert comments[2].getData()['behavior'] == 'neutral'

def test_batchs_render():
    group =BatchbucketManager()
    comments = [Comment('test','group1') for _ in range(5)]
    comments.extend([Comment('test', 'group2') for _ in range(3)])
    def ruleMakeNewBatch(batch:list[Comment],comment:Comment,data:dict):
        return len(batch) == 2
    group.addBulkRules(bucketRule=RuleBatchType('group1'),makeNewBatch=ruleMakeNewBatch)
    group.addComments(comments)
    assert len(group.buckets) == 1
    assert [len(x) for x in group.getBatchs(False)] == [2,2,1]