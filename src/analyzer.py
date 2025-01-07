import sys

# Get command line arguments (excluding script name)
args = sys.argv[1:]

CTXS = ["start", "install"]
config = None
filepath = None
limit = 30
def getCmdIndex(abrev,ext):
    if '-'+abrev in args and abrev:
        return args.index('-'+abrev)
    if '--'+ext in args:
        return args.index('--'+ext)
    return None

def haveCmd(abrev, ext):
    return not getCmdIndex(abrev, ext) == None
HELP = f"""Usage: analyzer [start|deps] [cmds]
Options:
  -h, --help     display this help and exit

  start        start execution with the instructions in config.json

  deps         output the pip install command with the dependencies of the project
  -c --config   set the config file to by used in command generation.
     --sudo     add "sudo" to the start of the command.
  -i --install  run pip install.

  dataset      automatic build CSV datasets.
  -p --path     path with the dataset file to output the CSV data
  -l --limit    limit of data to generate (default {limit})"""
# Check if no arguments are provided
if len(args) == 0:
    print(HELP)
    exit()

if haveCmd('h', 'help'):
    print(HELP)
    exit()

configCmd = getCmdIndex('c','config')
if not configCmd == None:
    config = args[configCmd + 1]
    args.remove(config)

filePathCmd = getCmdIndex('p','path')
if filePathCmd is not None:
    filepath = args[filePathCmd + 1]
    args.remove(filepath)

limitCmd = getCmdIndex('l', 'limit')
if limitCmd is not None:
    limit = args[limitCmd + 1]
    args.remove(limit)

if 'start' in args:
    import src.pipeline as pipeline
    pipeline.run(config)
    exit()

if 'deps' in args:
    import src.dependency as deps
    deps.run(config,haveCmd('','sudo'),haveCmd('i', 'install'))
    exit()

if 'dataset' in args:
    import src.datasets.makeDataset as dataset
    if filepath is None:
        print("Please provide a path to the dataset file")
        exit()
    dataset.makeCSV(filepath,{'limit':limit})
    exit()