from src.comment import Comment
from src.iaclient.promptInfo import PromptInfo
from src.iaclient.responseInfo import ResponseInfo
from .client import IAClient
from .clientManager import ClientManager
from typing import List

import logging
import os
import json
import time
logger = logging.getLogger(__name__)
COMMENT_LEN_LIMIT = 1000
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
class GeminiClient(IAClient):
    KNOW_PROBLEMS = ['delivery','damaged']
    def __init__(self,model = "gemini-1.5-flash"):
        super().__init__('google:'+model)
        import google.generativeai as genai
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

        self.model = genai.GenerativeModel(model)

        self.generation_config=genai.GenerationConfig(
            response_mime_type="application/json", response_schema=schema
        )
    def _separateCommentsBatch(self, comments: List[Comment]) -> List[List[Comment]]:
        batchs = []
        partionWorkers = {"len":0,"comments":[]}
        partionClients = {"len":0,"comments":[]}

        for comment in comments:
            partion = partionWorkers if comment.type == 'worker' else partionClients
            msgLen = len(str(comment))
            if msgLen + partion['len'] > COMMENT_LEN_LIMIT:
                batchs.append(partion['comments'])
                partion['comments'] = []
                partion['len'] = 0
            partion['len'] += msgLen
            partion['comments'].append(comment)
        batchs.append(partionClients['comments'])
        batchs.append(partionWorkers['comments'])

        return batchs
    def _generatePrompt(self, comments: List[Comment]) -> PromptInfo:
        prompt = PromptInfo('worker') if comments[0].type == 'worker' else PromptInfo('default')
        return prompt.format(self.KNOW_PROBLEMS,"\n\n---------NEXT-COMMENT-------\n\n".join([str(x) for x in comments]))
    def _makeRequestToAi(self, prompt) -> ResponseInfo:
        response = ResponseInfo()
        result = self.model.generate_content(
            prompt,
            generation_config=self.generation_config
        )
        self._reportCost(result.usage_metadata.total_token_count)
        data = json.loads(result.text)
        time.sleep(3)
        return response.setData(data)
    
ClientManager.registerClient("gemini",GeminiClient)