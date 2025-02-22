from src.aiclient.clientManager import ClientManager
from src.aiclient.analyzeStructure import scorerAddToBatch
from src.aiclient.client import AiClient, BatchBucketManager, SplitBatchByCharLimit,Batch
from src.aiclient.promptInfo import PromptInfo, setPromptsPath
from src.comment import Comment, CommentScorer
from unittest.mock import patch

class FakeClient(AiClient):
    def __init__(self):
        super().__init__('fake-client')
        self.comments = []
    def _generatePrompt(self, comments):
        return PromptInfo('test1')
    def _makeRequestToAi(self, prompt, request):
        request.setData([{"behavior":"happy"}] * 3).setTokensInput(2).setTokensOutput(5)
    def _separateCommentsBatch(self):
        return BatchBucketManager(SplitBatchByCharLimit(9999999))
    def analyze(self, comments, resultFn=None):
        res = super().analyze(comments, resultFn)
        self.comments = comments
        return res
ClientManager.addInstanceable('test',('src.aiclient.tests.test_clientManager','FakeClient'))

@patch('src.aiclient.analyzeStructure.scorerAddToBatch')
def test_clientManagerWithScorer(mock_scorer):
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
    original_mock = scorerAddToBatch
    def testScorer(data,retFn):
        res = original_mock(data, retFn)
        batchs:list[Batch] = data['batchs']
        assert len(batchs) == 1, "Expected only one batch of comments"
        batch:Batch = batchs[0]
        assert len(batch) == 3, "Expected 3 comments in the batch (1 for the scorer)"
        assert any([isinstance(comment,CommentScorer) for comment in batch]), "CommentScorer not detected"
        return res
    mock_scorer.side_effect = testScorer
    manager = ClientManager.initWithConfig(config)
    manager.analyze([Comment('test'),Comment('test2')])
    assert len(manager._items) == 1

    mock_scorer.assert_called()