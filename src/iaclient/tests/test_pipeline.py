from src.iaclient.pipeline import PipeRunner,Pipe

def test_simplerunner():
    runner = PipeRunner()
    runned = [False,False,False]
    def first():
        runned[0] = True
    def second():
        runned[1] = True
    def third():
        runned[2] = True
    pipeRules = Pipe('test').add(first).add(second).add(third)
    runner.addPipe(pipeRules)
    runner.execute()
    assert all(runned)
    assert [x.__name__ for x in runner.executionList] == ['first','second','third']

def test_beforeRule():
    runner = PipeRunner()
    def first():
        pass
    def other():
        pass
    pipe1 = Pipe('test').add(first)
    pipe2 = Pipe('test2').before('first',other)
    runner.addPipe(pipe1).addPipe(pipe2)
    runner.execute()
    assert ['other','first'] == [x.__name__ for x in runner.executionList]