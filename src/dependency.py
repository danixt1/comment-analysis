from src.deps.collectors import COLLECTORS_DEPS
from src.deps.IAclients import IACLIENTS_DEPS
from src.deps.outputs import OUTPUTS_DEPS

def getDeps(depDict,configs):
    deps = []
    for config in configs['data']:
        name = config['name']
        retVal = depDict[name]
        if retVal == None:
            continue
        if callable(retVal):
            retVal = retVal(config)
        if isinstance(retVal,str):
            deps.append(retVal)
        elif isinstance(retVal, list):
            deps += retVal
        
    return deps
def run(path = None,putSudo = False):
    deps = ['python-dotenv']
    if path == None:
        path = 'config.json'
    config = {}
    with open(path,'r') as f:
        import json
        config = json.load(f)

    deps += getDeps(COLLECTORS_DEPS, config['collector'])
    deps += getDeps(IACLIENTS_DEPS, config['processing'])
    deps += getDeps(OUTPUTS_DEPS, config['output'])
    cmdStr = 'pip install '+' '.join(deps)
    if putSudo:
        cmdStr = 'sudo '+cmdStr
    print(cmdStr)