from src.collector.collectorManager import CollectorManager
from src.iaclient.clientManager import ClientManager
from src.output.outputManager import OutputManager

def run(path = None):
    if path == None:
        path = 'config.json'
    config = {}
    with open(path,'r') as f:
        import json
        config = json.load(f)

    collector = CollectorManager.initWithConfig(config['collector'])
    processor = ClientManager.initWithConfig(config['processing'])
    output = OutputManager.initWithConfig(config['output'])

    deps = []
    deps.extend(collector.dependencies())
    deps.extend(processor.dependencies())
    deps.extend(output.dependencies())
    finalCmd = 'pip install '+ ' '.join(deps)
    print(finalCmd)