from src.aiclient.promptInfo import PromptModifier

from .client import AiClient,BatchBucketManager,FilterItemByType,SplitBatchsByToken,BatchRules, requestSchemaOpenAI,KNOW_PROBLEMS,Batch
from .requestProcess import RequestProcess

import logging
import os
import json
import google.generativeai as genai
logger = logging.getLogger(__name__)

COMMENT_LEN_LIMIT = 10000
    
class GeminiClient(AiClient):
    def __init__(self,model = "gemini-1.5-flash",env='GEMINI_API_KEY'):
        super().__init__('google:'+model)
        genai.configure(api_key=os.getenv(env))

        self.model = genai.GenerativeModel(model)
        self.generation_config=genai.GenerationConfig(
            response_mime_type="application/json", response_schema=requestSchemaOpenAI
        )
    
    def _separateCommentsBatch(self) -> BatchBucketManager:
        bucket = BatchBucketManager(SplitBatchsByToken(lambda text: self.model.count_tokens(text).total_tokens,COMMENT_LEN_LIMIT))
        bucket.addBatchRule(BatchRules('worker').addRules(FilterItemByType("worker")))
        return bucket
    
    def _generatePrompt(self, comments: Batch) -> PromptModifier:
        return PromptModifier(comments.name).addKnowProblems(KNOW_PROBLEMS['product' if comments.name == 'default' else 'company']) #prompt.format(KNOW_PROBLEMS["product"],formatedComments)
    
    def _makeRequestToAi(self, prompt,request:RequestProcess):
        result = self.model.generate_content(
            prompt,
            generation_config=self.generation_config
        )
        data = json.loads(result.text)
        return request.setData(data).setTokensInput(result.usage_metadata.prompt_token_count).setTokensOutput(result.usage_metadata.candidates_token_count)
    