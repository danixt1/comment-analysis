from src.aiclient.pipeline import PipeRunner,Pipe,Controller, AsyncTaskBucket

def test_argsPassing():
    runner = PipeRunner()
    runned = [False,False,False,False]
    def first(test,*args):
        assert test == 11
        assert len(args) == 0
        runned[0] = True

    def second(test,**kwargs):
        assert test == 11
        assert len(kwargs) == 0
        runned[1] = True

    def third(test):
        assert test == 11
        runned[2] = True

    def fourth():
        runned[3] = True

    pipeRules = Pipe('test').add(first,second,third,fourth)
    runner.addPipe(pipeRules)
    runner.data['test'] = 11
    runner.execute()
    assert all(runned)
    assert [x.__name__ for x in runner.executionList] == ['first','second','third','fourth']

def test_beforeRule():
    runner = PipeRunner()
    def first():
        pass
    def other():
        pass
    def beforeOther():
        pass
    def trueFirst():
        pass
    pipe1 = Pipe('test').add(trueFirst).add(first)
    pipe2 = Pipe('test2').before('first',other)
    pipe3 = Pipe('test3').before('other', beforeOther)

    runner.addPipe(pipe1).addPipe(pipe3).addPipe(pipe2).execute()

    assert ['trueFirst','beforeOther','other','first'] == [x.__name__ for x in runner.executionList]

def test_afterRule():
    runner = PipeRunner()
    runnedNever = False
    
    def first():
        pass
    def other():
        pass
    def afterOther():
        pass
    def trueFirst():
        pass
    def neverFunc():
        nonlocal runnedNever
        runnedNever = True
        pass

    pipe1 = Pipe('test').add(trueFirst).add(first).after('doNotExistFunc',neverFunc)
    pipe2 = Pipe('test2').after('first', other)
    pipe3 = Pipe('test3').after('other', afterOther)

    runner.addPipe(pipe2).addPipe(pipe3).addPipe(pipe1).execute()
    assert ['trueFirst','first','other','afterOther'] == [x.__name__ for x in runner.executionList]
    assert not runnedNever

def test_afterPipes():
    runner = PipeRunner()
    def first():
        pass
    def second():
        pass
    def other():
        pass
    def afterPipes(pipe:Pipe,pipes:dict[str,Pipe]):
        assert 'test2' in pipes
        pipe.add(other)

    pipe1 = Pipe('test').onPipesCreated(afterPipes).add(first)
    pipe2 = Pipe('test2').add(second)
    runner.addPipe(pipe1).addPipe(pipe2).execute()
    assert ['first','other','second'] == [x.__name__ for x in runner.executionList]

def test_finish():
    runner = PipeRunner()
    executed = False
    def first():
        pass
    def second(controller:Controller):
        controller.finish()
        return 'this string'
    def third():
        nonlocal executed
        executed = True
        return False

    pipe1 = Pipe('test').add(first,second,third)
    res = runner.addPipe(pipe1).execute()
    assert ['first','second','third'] == [x.__name__ for x in runner.executionList]
    assert res == 'this string'
    assert not executed, 'third fn must not be executed, because the operation is stopped in the second fn'
    
def test_activator():
    runner = PipeRunner()
    def trueActivator1(testData:str):
        assert testData == 'test'
        return True
    def falseActivator():
        return False
    def first():
        pass
    def other():
        pass
    def cantByAdded():
        pass
    
    pipe1 = Pipe('test').add(first).activator(trueActivator1)
    pipe2 = Pipe('test2').add(other).activator(falseActivator)
    pipe3 = Pipe('test3').after('other',cantByAdded)

    runner.data['testData'] = 'test'
    runner.addPipe(pipe2).addPipe(pipe1).addPipe(pipe3).execute()
    assert ['first'] == [x.__name__ for x in runner.executionList]

def test_afterWithBefore():
    runner = PipeRunner()
    def first():
        pass
    def other():
        pass
    def afterOther():
        pass
    def trueFirst():
        pass
    runner.createPipe('test').add(trueFirst,first)
    runner.createPipe('test2').after('first', other).before('other', afterOther)

    runner.execute()
    assert ['trueFirst','first','afterOther','other'] == [x.__name__ for x in runner.executionList]

def test_AsyncTaskBucket():
    bucket = AsyncTaskBucket()
    runner = PipeRunner()
    afterRunner = False
    def first():
        pass
    async def testIt():
        return {'retAsync':'ok'}
    def afterAsync(retAsync):
        nonlocal afterRunner
        afterRunner = True
        assert retAsync == 'ok'
        return 'finished'
    
    gen = runner.addPipe(Pipe('test').add(first,testIt,afterAsync)).executeWithAsyncBucket(bucket)
    assert next(gen) == None
    assert 'retAsync' not in runner.data
    assert not afterRunner, 'afterAsync must not be executed for now'
    bucket.execute()
    assert runner.data['retAsync'] == 'ok'
    assert next(gen) == 'finished'

def test_execute_NotAfectedByAsync():
    runner = PipeRunner()
    def first():
        pass
    async def second():
        return {'a':'new-data'}
    def third(data):
        assert data['a'] == 'new-data'
        return 'finished'
    runner.createPipe('test').add(first, second, third)
    res = runner.execute()
    assert res == 'finished'
    assert runner.data['a'] == 'new-data'
    
def test_InstanciablePipe():
    runner = PipeRunner()
    executedSub = False
    def sub1(data):
        assert 'passThat' in data
        assert data['passThat'] == 'passed'
    def sub2():
        nonlocal executedSub
        executedSub = True
        return 'that'
    def neverExec1():
        assert False, "It should never being executed"
    def main1(controller:Controller):
        controller.instancePipe('sub',{'passThat':'passed'})
    def main2(data):
        assert not 'passThat' in data, 'data passed to sub pipeline not is isolated in main execution'
        assert data['lastReturn'] == 'that'
    def beforesub2():
        pass
    runner.createPipe('test').add(main1,main2).before('sub2', beforesub2)
    runner.createInstanciablePipe('sub').add(sub1, sub2)
    runner.createInstanciablePipe('never').add(neverExec1)
    runner.execute()
    assert ['main1','main2'] == [x.__name__ for x in runner.executionList]
    assert ['sub1','beforesub2','sub2'] == [x.__name__ for x in runner.subExecList['sub']]
    assert ['neverExec1'] == [x.__name__ for x in runner.subExecList['never']]
    assert executedSub, "Instanciable pipeline is called but don't run"