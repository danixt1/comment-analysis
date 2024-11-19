import sys

# Get command line arguments (excluding script name)
args = sys.argv[1:]

CTXS = ["start", "install"]
config = None
def getCmdIndex(abrev,ext):
    if '-'+abrev in args:
        return args.index('-'+abrev)
    if '--'+ext in args:
        return args.index('--'+ext)
    return None
def haveCmd(abrev, ext):
    return not getCmdIndex(abrev, ext) == None
HELP = """Usage: analyzer [start|install] [cmds]
Options:
  -h, --help     display this help and exit

  start          start execution with the instructions in config.json

  deps        output the pip install command with the dependencies of the project
  -c --config    set the config file to by used."""
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

if 'start' in args:
    import src.pipeline as pipeline
    pipeline.run(config)
    exit()
if 'deps' in args:
    import src.installer as install
    install.run(config)
    exit()