from ..promptInfo import PromptModifier, setPromptsPath
from ..client import AiClient, BatchBucketManager,FilterItemByType,BatchRules,SplitBatch,Batch
from ..analyzeStructure import scorerAddToBatch
from ...comment import Comment,CommentScorer
from ..requestProcess import RequestProcess
from unittest.mock import patch

class SplitBatchFalseAlways(SplitBatch):
    def __call__(self, batch, comment, data):
        return False
class FakeClient(AiClient):

    def __init__(self,retData):
        super().__init__("test-client")
        self.countReqs = 0
        self.expectedLot = [0,0]
        self.actPrompt =0
        self.retData = retData
        self.comments = None
    def _separateCommentsBatch(self) -> BatchBucketManager:
        bucket = BatchBucketManager(SplitBatchFalseAlways())
        bucket.addBatchRule(BatchRules("lot1").addRules(FilterItemByType('lot1')))
        bucket.addBatchRule(BatchRules("lot2").addRules(FilterItemByType('lot2')))
        return bucket
    def analyze(self, comments, resultFn=None):
        self.comments = comments
        lot1 = comments[::2]
        lot2 = comments[1::2]
        for comment in lot1:
            comment.type = 'lot1'
        for comment in lot2:
            comment.type = 'lot2'
        self.expectedLot[0] =len(lot1)
        self.expectedLot[1] = len(lot2)
        return super().analyze(comments, resultFn)
    def _generatePrompt(self,comments: Batch):
        assert len(comments) == self.expectedLot[self.actPrompt], "Don't have the expected quantity of comments to the lot"
        self.actPrompt+=1
        return PromptModifier('test1' if comments.name == "lot1" else 'test2').addComments(comments).addKnowProblems(['pr1','pr2','otherpr'])
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
    def _separateCommentsBatch(self):
        bucker = BatchBucketManager(lambda x,y,z: False)
        if self.batchs is not  None:
            bucker.batchs = self.batchs
        return bucker
    def _generatePrompt(self, comments):
        self.promptHistoric.append(len(comments))
        return PromptModifier('test1' if str(comments[0]) == 'prompt1' else 'test2')
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

@patch('src.aiclient.analyzeStructure.scorerAddToBatch')
def test_client_with_auto_test(mock_scorer):
    setPromptsPath("src/aiclient/tests/prompt")
    rets = [
        {"behavior":"neutral"},{"behavior":"happy"},{"behavior":"angry"},
    ]
    TOTAL_COMMENTS_PASSED = 4
    TOTAL_AUTO_TESTS_PERCENTAGE = 0.50
    TOTAL_COMMENT_SCORER_EXPECTED = 2
    TOTAL_COMMENTS_EXPECTED = TOTAL_COMMENTS_PASSED + (TOTAL_AUTO_TESTS_PERCENTAGE * TOTAL_COMMENTS_PASSED)
    originalFn = scorerAddToBatch
    def sideEffectScorer(data,resultFn):
        ret = originalFn(data, resultFn)
        comments = [x for xs in data['batchs'] for x in xs]
        assert len(comments) == TOTAL_COMMENTS_EXPECTED
        assert len([x for x in comments if isinstance(x,CommentScorer)]) == TOTAL_COMMENT_SCORER_EXPECTED
        return ret
    mock_scorer.side_effect = sideEffectScorer
    client = FakeClient(rets)
    comments = [Comment('def', 'comment', 'test') for x in range(TOTAL_COMMENTS_PASSED)]
    client.useAutoTest(TOTAL_AUTO_TESTS_PERCENTAGE)
    result = client.analyze(comments)

    assert client.countReqs == 2
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
    client.analyze(comments)
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
    client.analyze(comments)

    assert client.promptHistoric == [4,2,2]
    assert client.actRes == 3
    assert all([comment.getData() for comment in comments]), "Returned comments without data"
    assert comments[1].getData()['behavior'] == 'angry'
    assert comments[2].getData()['behavior'] == 'neutral'

def test_batchBucketManager():
    import random
    class SplitBatchWhen2(SplitBatch):
        def __call__(self, batch, comment, data):
            return len(batch) == 2
    group =BatchBucketManager()
    batchRule = BatchRules()\
        .addRules(FilterItemByType('group1'))\
        .addRules(SplitBatchWhen2())
    comments = [Comment('test','group1') for _ in range(5)]
    comments.extend([Comment('test', 'group2') for _ in range(3)])
    random.shuffle(comments)
    group.addBatchRule(batchRule)
    group.addComments(comments)
    assert len(group.buckets) == 1
    assert [len(x) for x in group.getBatchs()] == [2,2,1,3]
    assert [len(x) for x in group.defBatchs] == [3]

def test_prompt_formating():
    setPromptsPath("src/aiclient/tests/prompt")
    class FakeAiClientPromptTest(AiClient):
        def __init__(self):
            super().__init__("test")
        def _generatePrompt(self, comments: Batch):
            return PromptModifier('min').addKnowProblems(['pr1','pr2'])
        def _separateCommentsBatch(self):
            return BatchBucketManager(lambda x, y, z: False)
        def _makeRequestToAi(self, prompt, request):
            assert prompt == "problems:pr1,pr2 ,prompts: <comment>hi</comment>\n<comment>other hi</comment>"
            return request.setData([{'behavior':'happy'},{'behavior':'angry'}]).setTokensInput(2).setTokensOutput(5)
    comments = [Comment('hi'), Comment('other hi')]
    client = FakeAiClientPromptTest()
    client.analyze(comments)