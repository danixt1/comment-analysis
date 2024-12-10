import pytest
from ..collectorDBAPI import CollectorDBAPI
from sqlalchemy import create_engine, text
from datetime import datetime
sql_query = """
CREATE TABLE "comments" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER,
    author_id INTEGER,
    content TEXT,
    date_gmt TEXT DEFAULT "2024-05-23 10:20:45"
);
INSERT INTO comments (post_id, author_id, content) VALUES (1, 1, 'This a test comment');
INSERT INTO comments (post_id, author_id, content) VALUES (1, 2, 'This is another test comment');
INSERT INTO comments (post_id, author_id, content) VALUES (2, 2, 'expected message');
"""

@pytest.fixture(scope="session")
def db_url(tmp_path_factory):
    db_path = tmp_path_factory.mktemp('DBAPI') / 'collectorDBAPI.db'
    eng = create_engine(f"sqlite:///{str(db_path)}")
    with eng.connect() as conn:
        for sqlCmd in sql_query.split(';'):
            if sqlCmd.strip():
                conn.execute(text(sqlCmd))
        conn.commit()
    return f"sqlite:///{str(db_path)}"

def test_simple_mapping(db_url):
    convert_date_gmt = lambda date_str: int(datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
    collector = CollectorDBAPI(db_url,"comments",[("content","message"),("date_gmt","timestamp",convert_date_gmt)])
    data = collector.collect()
    assert len(data) == 3
    assert data[0].message == "This a test comment"
    assert data[0].timestamp == convert_date_gmt("2024-05-23 10:20:45")

def test_where_condition(db_url):
    collector = CollectorDBAPI(db_url, "comments", [("content", "message")], where="post_id=2")
    data = collector.collect()
    assert len(data) == 1
    assert data[0].message == "expected message"