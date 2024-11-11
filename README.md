# Analyze and extract information from comments

This project have the purpose to analyze comments from workers and users, and extract relevant data using LLMS.

TODO: make caching system.

# TODO: new system to save the state of process
Instead of passing the process information in `process` property, pass a id of the process, with this logic is possible to add much more details of how the process runned.

The process object:
```json
{
    "id":"INT: unique id, passed to the comment to refer the proccess",
    "name":"STRING: process name",
    "branch":"STRING: The git hash branch when this proccess has runned",
    "timestamps":{
        "start":"INT: timestamp of the start of the proccess",
        "end":"INT: timestamp of the end of the process"
    },
    "tokens":{
        "input":"INT: the total tokens usage in input to run this proccess",
        "output":"INT: total tokens of output generated"
    },
    "batchs":[
        {
            "comment":"STRING(optional): comment passed from the proccess to give more context of this batch",
            "promptHash":"STRING: the base hash of used prompt to generate the results",
            "comments":"ARRAY<INT>: the id of the comments added to that batch",
            "tokens":{
                "input":"INT: the total tokens usage in input to run this batch",
                "output":"INT: total tokens of output generated"
            },
            "successfulRequest":"INT|NULL:pass the position from \"requests\" property where ended with success or NULL if not ended with success."
        }
    ],
    "requests":[
        {
            "relatedBatch":"INT:get the batch anexed with the request maded to the AI",
            "success":"BOOL: return if this request has ended successfull",
            "error":"(optional)ENUM<TIMEOUT|SERVER_PROBLEM|INVALID_AI_RESPONSE|INVALID_RESPONSE|REQUEST_LIMIT|AUTHENTICATION_FAILED>: pass the error occorrured in the request"
        }
    ],
    "commentsDiscarded":"ARRAY<INT>: comment's discarted from analyze by proccess choice."
}
```

>Temporary removed requirements.txt(unstable) use:
```shell
pip install google-generativeai python-dotenv mysql-connector-python SQLAlchemy pymongo
```
dev:
```shell
pip install pytest
```

# Usage mapping:
collectorDBAPI = SQLAlchemy #if using only sqlite
collectorMySql = mysql-connector-python SQLAlchemy
geminiClient = google-generativeai