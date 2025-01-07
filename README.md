# Analyze and extract information from comments

This project have the purpose to analyze comments from workers and users, and extract relevant data behavior using LLMS.

Some features:

* Multiple source collection.
* Support to confidence system to test the quality of results generated.
* extraction of behavior detected in the message.
* extract problems detected in the message.

# Installing

Get the pip installation need using:
```shell
python analyzer.py deps
```
The returned pip is related to the pipeline in `config.json`.

is possible to pass **-i** in deps to install.

dev:
```shell
pip install pytest
```

# Running

run `python analyzer.py start`

# Collectors
## CSV

Properties:
- **header**: if not present use the first collum as header.
- **delimiter**: default is a comma.
- **encoding**: default is utf-8.

```json
{
    "path":"dataset.csv",
    "delimiter":",",
    "header":["message","type","timestamp"],
    "encoding":"utf-8"
}
```
## DBAPI

connect to a various types of SQL DB.

```json
{
    "dbUrl":"<connector>://user:password@<host>:<port>/<database>",
    "table":"table_name",
    "mapping":[
        ["collum_name_with_comment","message"],
        ["created_at","timestamp"]
    ],
    "where":"created_at > 1675438212000"
}
```
to pass the password more safe you can replace a part of url and store in .env


ex:
```env
DB_PASSWORD=password
DB_USER=user 
```

and in `dbUrl` passing **mysql+mysqlconnector://DB_USER:DB_PASSWORD@localhost:3306/mydatabase**
the `DB_USER` and `DB_PASSWORD` gonna by replaced by .env config

>obs: the *deps* command look for what connector you are using and try to add to list of dependencies.

# Processing

## Gemini

```json
{
    "name":"gemini",
    "model":"<MODEL>(optional)"
}
```
Pass the api key in the .env as **GEMINI_API_KEY**

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

## Graphic

Output one image with graphics showing informations from the comments.

```json
{
    "name":"graphic",
    "granularity":"(optional)day|week|month",
    "filename":"(optional)output",
    "lang:":"(optional)en|pt"
}
```