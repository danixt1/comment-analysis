from ..managerBase import ManagerBase


class FakeBaseClass:
    pass

class Fake1(FakeBaseClass):
    def __init__(self, **kwargs):
        assert 'faker' in kwargs
        assert kwargs['faker'] == 'fake1'
class Fake2(FakeBaseClass):
    called = False
    def __init__(self):
        Fake2.called = True
class FakeManager(ManagerBase):
    called = False
    def __init__(self,customProp) -> None:
        super().__init__()
        assert customProp == 'work'
        FakeManager.called = True
    @staticmethod
    def _getBaseClass():
        return FakeBaseClass
FakeManager.addInstanceable('test1', Fake1)
FakeManager.addInstanceable('test2', Fake2)
def test_manager_init():
    manager = FakeManager.initWithConfig({
        "customProp": "work",
        "data":[
            {
                "name": "test1",
                "faker": "fake1"
            },
            {
                "name": "test2",
            }
        ]
    })
    assert FakeManager.called, "FakeManager was not initialized"
    assert Fake2.called, "Fake2 was not initialized"
    assert len(manager._builders) == 2