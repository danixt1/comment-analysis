# Analyze and extract information from comments

This project have the purpose to analyze comments from workers and users, and extract relevant data using LLMS.

For now only gemini is supported.

The actual supported output is mongoDB.

# Installing
Get the pip installation need using:
```shell
python analyzer.py deps
```
The returned pip is related to the pipeline in `config.json`

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