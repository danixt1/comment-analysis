from ..managerBase import ManagerBase
import pytest


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
    
@pytest.fixture(scope="session")
def FakeManagerClass():
    class FakeManager(ManagerBase):
        called = False
        def __init__(self,customProp) -> None:
            super().__init__()
            assert customProp == 'work'
            FakeManager.called = True

    return FakeManager

def test_manager_init(FakeManagerClass):
    FakeManagerClass.addInstanceable('test1', Fake1)
    FakeManagerClass.addInstanceable('test2', Fake2)
    manager = FakeManagerClass.initWithConfig({
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

    assert FakeManagerClass.called, "FakeManager was not initialized"
    assert Fake2.called, "Fake2 was not initialized"
    assert len(manager._builders) == 2

def test_manager_with_lambda(FakeManagerClass):
    makeCalled = False
    def makeFake2(config):
        nonlocal makeCalled
        assert "test" in config
        assert config['test'] == 'ok'
        makeCalled = True
        return Fake2()
    FakeManagerClass.addInstanceable('faker', makeFake2)
    manager = FakeManagerClass.initWithConfig({
        "customProp": "work",
        "data":[
            {
                "name": "faker",
                "test": "ok"
            }
        ]
    })
    assert len(manager._builders) == 1
    assert makeCalled, "fn makeFake2 was not called"