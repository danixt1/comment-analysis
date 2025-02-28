from dotenv import load_dotenv
load_dotenv()

from src.collector.collectorManager import CollectorManager
from src.aiclient.clientManager import ClientManager
from src.output.outputManager import OutputManager
from src.cache import Cache
import logging


def run(path:str | None = None):
    if path == None:
        path = 'config.json'
    config = {}
    logging.basicConfig(level=logging.INFO)
    with open(path,'r') as f:
        import json
        config = json.load(f)

    expireCacheTime = config['expireCacheTime'] if 'expireCacheTime' in config else 60*60*24
    mainCache = Cache('1.0')
    if expireCacheTime > 0:
        mainCache.deleteExpiredCache(expireCacheTime)
    if 'cache' in config and config['cache'] == False:
        mainCache = None
        logging.info('Cache is disabled')
    else:
        logging.info('Cache is enabled')
    logging.info('Starting pipeline')
    collector = CollectorManager.initWithConfig(config['collector'],mainCache)
    processor = ClientManager.initWithConfig(config['processing'],mainCache)
    output = OutputManager.initWithConfig(config['output'],mainCache)
    logging.info('Pipeline started!')
    logging.info('Starting analyze')
    comments = collector.collect()
    result =processor.analyze(comments)
    output.output(comments,result)
    logging.info('Analyze finished!')