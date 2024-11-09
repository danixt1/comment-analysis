import pytest
from ..collectorDBAPI import CollectorDBAPI
from sqlalchemy import create_engine, text

sql_query = """
CREATE TABLE "comments" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER,
    author_id INTEGER,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO comments (post_id, author_id, content) VALUES (1, 1, 'This a test comment');
INSERT INTO comments (post_id, author_id, content) VALUES (1, 2, 'This is another test comment');
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
    collector = CollectorDBAPI(db_url,"comments",[("content","message"),("created_at","timestamp")])
    data = collector.collect()
    assert len(data) == 2
    assert data[0].message == "This a test comment"