import json
from openai import OpenAI

import os

from src.aiclient._aiclient.schema import CommentsAnalyzeResults
from src.aiclient.promptInfo import PromptModifier
from src.aiclient.requestProcess import RequestProcess
from .client import KNOW_PROBLEMS, AiClient, Batch, BatchBucketManager, BatchRules, FilterItemByType, SplitBatchByCharLimit

class OpenAIClient(AiClient):
    baseName="openai"
    def __init__(self, tolerance=2,model="",env="OPENAI_API_KEY",base_url = None):
        super().__init__(self.baseName+":"+model, tolerance)
        apiKey = os.environ.get(env)
        self.client = OpenAI(base_url=base_url,api_key=apiKey)
        self.model = model
    def _separateCommentsBatch(self) -> BatchBucketManager:
        bucket = BatchBucketManager(SplitBatchByCharLimit(10000))
        bucket.addBatchRule(BatchRules('worker').addRules(FilterItemByType("worker")))
        return bucket
    
    def _generatePrompt(self, comments: Batch) -> PromptModifier:
        return PromptModifier(comments.name).addKnowProblems(KNOW_PROBLEMS['product' if comments.name == 'default' else 'company'])
    
    def _makeRequestToAi(self, prompt,request:RequestProcess):
        response = self.client.beta.chat.completions.parse(
            messages=[{"role":"system","content":prompt}],
            model=self.model,
            response_format=CommentsAnalyzeResults)
        return request.\
            setData(json.loads(response.choices[0].message.content)).\
            setTokensInput(response.usage.prompt_tokens).\
            setTokensOutput(response.usage.completion_tokens)