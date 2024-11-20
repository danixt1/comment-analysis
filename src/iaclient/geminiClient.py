from src.comment import Comment
from src.iaclient.promptInfo import PromptInfo

from .client import IAClient
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
class GeminiClient(IAClient):
    KNOW_PROBLEMS = ['delivery','damaged']
    def __init__(self,model = "gemini-1.5-flash"):
        super().__init__('google:'+model)
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

        self.model = genai.GenerativeModel(model)

        self.generation_config=genai.GenerationConfig(
            response_mime_type="application/json", response_schema=schema
        )
    def _separateCommentsBatch(self, comments: list[Comment]) -> list[list[Comment]]:
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
    def _generatePrompt(self, comments: list[Comment]) -> PromptInfo:
        prompt = PromptInfo('worker' if comments[0].type == 'worker' else 'default')
        formatedComments ="".join([f"<comment>{str(x)}</comment>" for x in comments])
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
    