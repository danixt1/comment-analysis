# EXPERIMENTAL
from requests import get,delete,post
from time import sleep
import os
import json
if(not "GEMINI_API" in os.environ):
    raise Exception("api key not set use SET GEMINI_API=<API_KEY>")
token = os.environ["GEMINI_API"]
BASE_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={}".format(token)
instructions = ''' -extract the behavior from the user
-the behavior can by "positive|negative|high-negative|neutral|question"
extract relevant informations from the message.
case the message is a spam define a property "spam" with value true.
case the client have described any type of problem, describe with one word the problem described.
analyze the following message:"{}"
'''
def send_new_comment(comment):
    input = {
        "contents":[
            {"parts":[{"text":instructions.format(comment)}]}
        ],
        "generationConfig":{
            "response_mime_type": "application/json" ,
            "response_schema": {
                "type":"OBJECT",
                "properties":{
                    "spam":{"type":"BOOLEAN"},
                    "behavior":{
                        "type":"STRING",
                        "format":"enum",
                        "enum":["positive","negative","neutral","high-negative","question"]
                    },
                    "problem":{"type":"STRING","nullable":True}
                }
            }
        }
    }
    req = post(BASE_API_URL,json=input)
    if req.status_code > 299:
        raise Exception("failed" + str(req.json()))
    return req.json()["candidates"][0]["content"]["parts"][0]["text"]
data = send_new_comment("Produto maravilhoso! amei, mas demorou um pouco para chegar")
print(json.dumps(data, indent=4))