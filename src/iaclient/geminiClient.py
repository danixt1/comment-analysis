from src.comment import Comment
from src.iaclient.promptInfo import PromptInfo
from src.iaclient.responseInfo import ResponseInfo
from .client import IAClient
from typing import List

import logging
import os
import json
logger = logging.getLogger(__name__)
COMMENT_LEN_LIMIT = 9000
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
    def __init__(self):
        super().__init__(os.getenv("GOOGLE_MODEL") or 'gemini/flash-1.5')
        import google.generativeai as genai
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

        self.model = genai.GenerativeModel("gemini-1.5-flash")

        self.generation_config=genai.GenerationConfig(
            response_mime_type="application/json", response_schema=schema
        )
    def _separateCommentsBatch(self, comments: List[Comment]) -> List[List[Comment]]:
        batchs = []
        partionWorkers = {"len":0,"comments":[]}
        partionClients = {"len":0,"comments":[]}

        for comment in comments:
            partion = partionWorkers if comment.msgType == 'worker' else partionClients
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
        prompt = PromptInfo('workers') if comments[0].msgType == 'worker' else PromptInfo('default')
        return prompt.format(self.KNOW_PROBLEMS,"\nNEXT-COMMENT\n".join([str(x) for x in comments]))
    def _makeRequestToAi(self, comments: List[Comment], prompt) -> ResponseInfo:
        response = ResponseInfo()
        result = self.model.generate_content(
            prompt,
            generation_config=self.generation_config
        )
        self._reportCost(result.usage_metadata.total_token_count)
        data = json.loads(result.text)
        return response.setData(data)
    