from src.deps.collectors import COLLECTORS_DEPS
from src.deps.IAclients import IACLIENTS_DEPS
from src.deps.outputs import OUTPUTS_DEPS

from src.collector.managerInstanceable import initInstanceables as collectorInstances
from src.aiclient.managerInstanceable import initInstanceables as AIClientsInstances
from src.output.managerInstanceable import initInstanceables as outputInstances

from src.managerBase import ManagerBase

class GetInstances(ManagerBase):
    @classmethod
    def getNames(cls):
        return cls._builders.keys()


def test_get_collector_dependencies():
    GetInstances._builders = {}
    collectorInstances(GetInstances)
    names = GetInstances.getNames()
    for name in names:
        assert name in COLLECTORS_DEPS, f"Collector {name} not in registred in dependency list."

def test_get_iaclient_dependencies():
    GetInstances._builders = {}
    AIClientsInstances(GetInstances)
    names = GetInstances.getNames()
    for name in names:
        assert name in IACLIENTS_DEPS, f"IAclient {name} not in registred in dependency list."

def test_get_output_dependencies():
    GetInstances._builders = {}
    outputInstances(GetInstances)
    names = GetInstances.getNames()
    for name in names:
        assert name in OUTPUTS_DEPS, f"Output {name} not in registred in dependency list."