from src.iaclient.pipeline import PipeRunner,Pipe

def test_argsPassing():
    runner = PipeRunner()
    runned = [False,False,False,False]
    def first(*args):
        assert len(args) == 0
        runned[0] = True
    def second(**kwargs):
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
    def first():
        pass
    def other():
        pass
    def afterOther():
        pass
    def trueFirst():
        pass
    pipe1 = Pipe('test').add(trueFirst).add(first)
    pipe2 = Pipe('test2').after('first', other)
    pipe3 = Pipe('test3').after('other', afterOther)

    runner.addPipe(pipe2).addPipe(pipe3).addPipe(pipe1).execute()

    assert ['trueFirst','first','other','afterOther'] == [x.__name__ for x in runner.executionList]

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
    pipe1 = Pipe('test').add(trueFirst,first)
    pipe2 = Pipe('test2').after('first', other).before('other', afterOther)

    runner.addPipe(pipe2).addPipe(pipe1).execute()
    assert ['trueFirst','first','afterOther','other'] == [x.__name__ for x in runner.executionList]