from pathlib import Path
import pytest
import csv
from ..collectorCSV import CollectorCSV

header = ['message','type']
commentsLines = [
    ["testing one","comment"],
    ["another test",'social']
]
@pytest.fixture(scope="session")
def csv_folder(tmp_path_factory):
    tmp_path_factory = tmp_path_factory.mktemp("data")
    withHeader = tmp_path_factory / "header.csv"
    withoutHeader = tmp_path_factory / "without.csv"
    with open(withHeader, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(commentsLines)
    with open(withoutHeader, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(commentsLines)
    return tmp_path_factory

def test_collect_using_header(csv_folder):
    collector = CollectorCSV(csv_folder / "header.csv")
    comments = collector.collect()
    assert len(comments) == len(commentsLines)
    commentAndType = []
    for comment in comments:
        commentAndType.append([str(comment),comment.type])
    assert commentAndType == commentsLines

def test_collect_without_header(csv_folder):
    collector = CollectorCSV(csv_folder / "without.csv",header=header)
    comments = collector.collect()
    assert len(comments) == len(commentsLines)
    messageAndType = []
    for comment in comments:
        messageAndType.append([str(comment), comment.type])
    assert messageAndType == commentsLines