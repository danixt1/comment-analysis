# Analyze and extract information from comments

This project have the purpose to analyze comments from workers and users, and extract relevant data using LLMS.

TODO: make caching system.


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