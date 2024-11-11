# Analyze and extract information from comments

This project have the purpose to analyze comments from workers and users, and extract relevant data using LLMS.

For now only gemini is supported.

The actual supported output is mongoDB.

# Installing
>Temporary removed requirements.txt(unstable) use:

```shell
pip install google-generativeai python-dotenv mysql-connector-python SQLAlchemy pymongo
```
dev:
```shell
pip install pytest
```

# Running

1. configure the pipeline in `config.json`.
2. configure GEMINI_API_KEY in env.
3. run `python analyze`

# Collectors

## DBAPI
connect to a SQL DB.

```json
{
    "dbUrl":"<connector>://<user>:<password>@<host>:<port>/<database>",
    "table":"table_name",
    "mapping":[
        ["collum_name_with_comment","message"],
        ["created_at","timestamp"]
    ]
}
```
### connector:
* mysql+mysqlconnector : need `mysql-connector-python`
* postgresql+psycopg2: need `psycopg2`

# Processing

## Gemini

```json
{
    "name":"gemini",
    "model":"<MODEL>(optional)"
}
```

# Output 

## mongoDB

```json
{
    "name":"mongodb",
    "host":"localhost",
    "db":"behavior-analysis(default)",
    "port":"27017(default)",
    "user":"(optional)",
    "password":"",
    "process_collection":"behavior-analysis-process.(default)",
    "comments_collection":"behavior-analysis-collection.(default)"
}
```

# Dependency Usage mapping:

Show where every dependency is being used.

collectorDBAPI = SQLAlchemy #if using only sqlite
collectorMySql = mysql-connector-python SQLAlchemy
geminiClient = google-generativeai