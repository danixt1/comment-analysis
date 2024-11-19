from ..collectorWordPress import CollectorWordPress
from sqlalchemy import create_engine, text
import pytest
from datetime import datetime
sql_query = """
CREATE TABLE "wp_comments" (
	"comment_ID"	INTEGER PRIMARY KEY,
	"comment_post_ID"	INTEGER,
	"comment_author"	TEXT,
	"comment_author_email"	TEXT,
	"comment_author_url"	TEXT,
	"comment_author_IP"	TEXT,
	"comment_date"	TEXT,
	"comment_date_gmt"	TEXT,
	"comment_content"	TEXT,
	"comment_karma"	INTEGER,
	"comment_approved"	TEXT,
	"comment_agent"	TEXT,
	"comment_type"	TEXT,
	"comment_parent"	INTEGER,
	"user_id"	INTEGER
);
INSERT INTO "wp_comments" VALUES (1,1,'Author Name','author@example.com','','127.0.0.1','2023-05-01 12:00:00','2023-05-01 12:00:00','test1',0,'1','','comment',0,0);
INSERT INTO "wp_comments" VALUES (2,1, 'Author Name', 'author@example.com', '', '127.0.0.1', '2023-05-01 12:00:00', '2023-05-01 12:00:00', 'test2', 0, '1', '', 'comment', 0, 0);
"""

@pytest.fixture(scope="session")
def db_url(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("collector_wordpress") / "test.db"
    eng = create_engine(f"sqlite:///{db_path}")
    with eng.connect() as conn:
        for sqlCmd in sql_query.split(';'):
            if sqlCmd.strip():
                conn.execute(text(sqlCmd))
        conn.commit()
    return f"sqlite:///{db_path}"

def test_collectorWordPress(db_url):
    convert_date_gmt = lambda date_str: int(datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
    collector = CollectorWordPress('', '','','',connector='sqlite')
    collector.dbUrl = db_url
    collector._initDependecies()
    data = collector.collect()

    assert len(data) == 2
    assert data[0].message == "test1"
    assert data[1].message == "test2"
    assert data[0].timestamp == convert_date_gmt("2023-05-01 12:00:00")