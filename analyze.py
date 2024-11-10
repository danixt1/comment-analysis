from src.collector.collectorManager import CollectorManager
from src.iaclient.clientManager import ClientManager
from src.output.outputManager import OutputManager
import logging
config = {}
logging.basicConfig(level=logging.DEBUG)
with open('config.json','r') as f:
    import json
    config = json.load(f)

collector = CollectorManager.initWithConfig(config['collector'])
processor = ClientManager.initWithConfig(config['processing'])
output = OutputManager.initWithConfig(config['output'])

comments = collector.collect()
processor.analyze(comments)
output.output(comments)