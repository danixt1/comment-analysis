from src.comment import Comment
from src.aiclient.promptInfo import PromptInfo

from .client import AiClient,BatchbucketManager,FilterBatchByType
from .requestProcess import RequestProcess

import logging
import os
import json
import google.generativeai as genai
logger = logging.getLogger(__name__)

COMMENT_LEN_LIMIT = 10000
schema = {
    "type":"ARRAY",
    "items":{
        "type":"OBJECT",
        "properties":{
            "spam":{"type":"BOOLEAN"},
            "behavior":{
                "type":"STRING",
                "format":"enum",
                "enum":["positive","negative","neutral","question"]
            },
            "problems":{"type":"ARRAY","nullable":True,"items":{"type":"STRING"}}
        }
    }
}
class SplitBatchsByToken:
    def __init__(self,model,limit):
        self.model = model
        self.limit = limit
    def __call__(self, batch,comment,data):
        if "totalTokens" not in data:
            data["totalTokens"] = 0
        tokens = self.model.count_tokens(str(comment)).total_tokens
        data["totalTokens"] += tokens
        if data["totalTokens"] > self.limit:
            data["totalTokens"] = tokens
            return True
        return False
    
class GeminiClient(AiClient):
    KNOW_PROBLEMS = ['delivery','damaged']
    def __init__(self,model = "gemini-1.5-flash",prefix:str = None):
        super().__init__('google:'+model)
        prefix = prefix + '_' if prefix else ''
        genai.configure(api_key=os.getenv(prefix+'GEMINI_API_KEY'))

        self.model = genai.GenerativeModel(model)
        self.generation_config=genai.GenerationConfig(
            response_mime_type="application/json", response_schema=schema
        )
    
    def _separateCommentsBatch(self, comments: list[Comment]) -> list[list[Comment]]:
        bucket = BatchbucketManager(SplitBatchsByToken(self.model,COMMENT_LEN_LIMIT))
        bucket.addBulkRules(FilterBatchByType("worker"))
        bucket.addComments(comments)
        return bucket.getBatchs(True)
    
    def _generatePrompt(self, comments: list[Comment]) -> PromptInfo:
        prompt = PromptInfo('worker' if comments[0].type == 'worker' else 'default')
        formatedComments ="".join([f"<comment>{str(x)}</comment>\n" for x in comments])
        if comments[0].type == 'worker':
            return prompt.format(formatedComments)
        return prompt.format(self.KNOW_PROBLEMS,formatedComments)
    
    def _makeRequestToAi(self, prompt,request:RequestProcess):
        result = self.model.generate_content(
            prompt,
            generation_config=self.generation_config
        )
        data = json.loads(result.text)
        return request.setData(data).setTokensInput(result.usage_metadata.prompt_token_count).setTokensOutput(result.usage_metadata.candidates_token_count)
    