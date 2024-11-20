from dotenv import load_dotenv
load_dotenv()

from src.collector.collectorManager import CollectorManager
from src.iaclient.clientManager import ClientManager
from src.output.outputManager import OutputManager
import logging


def run(path:str | None = None):
    if path == None:
        path = 'config.json'
    config = {}
    logging.basicConfig(level=logging.INFO)
    with open(path,'r') as f:
        import json
        config = json.load(f)

    collector = CollectorManager.initWithConfig(config['collector'])
    processor = ClientManager.initWithConfig(config['processing'])
    output = OutputManager.initWithConfig(config['output'])

    comments = collector.collect()
    result =processor.analyze(comments)
    output.output(comments,result)