from dataclasses import dataclass
import enum

class RuleMode(enum.Enum):
    MODE_ADD = 1
    MODE_BEFORE = 2
    MODE_AFTER = 3

@dataclass
class Rule:
    fn:callable
    pipe:str
    mode:RuleMode
    linked:str = None

class Controller:
    def __init__(self):
        self._finish = False
        self._instance = []
    def finish(self):
        self._finish = True
    def instancePipe(self,name:str,additionalData = {}):
        self._instance.append((name, additionalData))

class RulesAccess:
    def __init__(self):
        self.rules:list[Rule] = []

    def getRules(self):
        return self.rules
    def _addRules(self,rule:Rule):
        self.rules.append(rule)

class RulesInsertion(RulesAccess):

    def __init__(self,ruleName:str):
        super().__init__()
        self._ruleName = ruleName

    def before(self,nameFn:str,func:callable):
        rule = Rule(func, self._ruleName, RuleMode.MODE_BEFORE,nameFn)
        self._addRules(rule)
        return self
    
    def after(self,nameFn:str,func:callable):
        rule = Rule(func, self._ruleName, RuleMode.MODE_AFTER, nameFn)
        self._addRules(rule)
        return self
        
    def add(self,*funcs:callable):
        for func in funcs:
            rule = Rule(func, self._ruleName, RuleMode.MODE_ADD)
            self._addRules(rule)
        return self
    
class Pipe(RulesInsertion):
    def __init__(self,pipeName:str,activator:callable = None):
        self._activate =activator if activator else lambda *args, **kwargs: True
        self._onPipesCreated = lambda *args, **kwargs: None
        self.pipeName = pipeName
        super().__init__(pipeName)

    def activator(self,func:callable):
        self._activate = func
        return self
    
    def onPipesCreated(self, func):
        self._onPipesCreated = func
        return self
    
class PipeInstanciable(RulesInsertion):
    """Pipe instantiate only by call from controller.
    
    When called create a new sub pipe. rules added with `before` and `after` is added on calling in."""
    def __init__(self, pipeName):

        super().__init__(pipeName)

import inspect
import asyncio
from functools import wraps

class AsyncTaskBucket:
    def __init__(self):
        self._bucket = []
    def add(self, fn,callback):
        self._bucket.append((fn,callback))

    def execute(self):
        data = asyncio.run(self._executeAsync())
        for dataWithCallback in data:
            dataWithCallback[1](dataWithCallback[0])

    async def _executeAsync(self):
        tasksWithCallback:list[tuple[asyncio.Task,callable]] = []
        async with asyncio.TaskGroup() as tg:
            for fn in self._bucket:
                tasksWithCallback.append((tg.create_task(fn[0]()),fn[1]))
        dataWithCallback:list[tuple[any,callable]] = []
        for taskWithCallback in tasksWithCallback:
            dataWithCallback.append((taskWithCallback[0].result(), taskWithCallback[1]))
        return dataWithCallback
    
def addLinkedsRules(rule:Rule, execList:list,rulesLinked:dict[str,list[Rule]]):
    fnName = rule.fn.__name__
    if fnName not in rulesLinked:
        return
    links = rulesLinked[fnName]
    for ruleLinked in links:
        n = 1 if ruleLinked.mode == RuleMode.MODE_AFTER else 0
        execList.insert(execList.index(rule.fn) + n, ruleLinked.fn)
        addLinkedsRules(ruleLinked, execList, rulesLinked)  

def makePipeline(pipes:list[Pipe],wrapper):
    rulesAdd:list[Rule] = []
    rulesLinked:dict[str,Rule] = {}
    execList = []
    ignoreAdd = False
    for pipe in pipes:
        if isinstance(pipe, PipeInstanciable):
            ignoreAdd = True
        elif not wrapper(pipe._activate):
            continue
        for rule in pipe.rules:
            rule.fn._origin = rule.pipe
            if rule.mode == RuleMode.MODE_ADD:
                if ignoreAdd and not isinstance(pipe,PipeInstanciable):
                    continue
                rulesAdd.append(rule)
                continue
            value = rule.linked
            if value not in rulesLinked:
                rulesLinked[value] = []
            rulesLinked[value].append(rule)
    for rule in rulesAdd:
        execList.append(rule.fn)
        addLinkedsRules(rule, execList, rulesLinked)
    return execList

class PipeRunner:

    def __init__(self,executionList = []):
        self._pipes:dict[str,Pipe] = {}
        self.executionList = executionList
        self.subExecList = {}
        self.data = {'lastReturn':None}
        self._instances = {}
        self.controller =  Controller()

    def createPipe(self,name:str,activator = None):
        pipe = Pipe(name, activator)
        self.addPipe(pipe)
        return pipe
    
    def createInstanciablePipe(self, name:str):
        pipe = PipeInstanciable(name)
        self._instances[pipe._ruleName] = pipe
        return pipe
    
    def addPipe(self, pipe):
        if isinstance(pipe, PipeInstanciable):
            self._instances[pipe._ruleName] = pipe
            return self
        self._pipes[pipe.pipeName] = pipe
        return self
    
    def executeWithAsyncBucket(self,bucket:AsyncTaskBucket):
        ret = {'data':None}
        for ret in self._generatorExecute():
            if ret['type'] == 'async':
                bucket.add(ret['data'][0], ret['data'][1])
                yield
        yield ret['data']
        
    def _initPipe(self):
        for pipe in self._pipes.values():
            pipe._onPipesCreated._origin = pipe.pipeName
            self._executeFnWithWrapper(pipe._onPipesCreated)
        self._makeMainPipe()

    def _generatorExecute(self):
        self._initPipe()
        for fn in self.executionList:
            if inspect.iscoroutinefunction(fn):
                yield {'type':'async','data':(lambda: self._executeFnWithWrapper(fn), self._asyncCallback())}
                continue
            
            newRes = self._executeFnWithWrapper(fn)
            if not newRes == None:
                self.data['lastReturn'] = newRes
            if self.controller._finish:
                break

            for instanceName,data in self.controller._instance:
                subRunner = PipeRunner(self.subExecList[instanceName])
                subRunner.data.update(self.data)
                subRunner.data.update(data)
                for subRet in subRunner._generatorExecute():
                    if subRet['type'] == 'finish':
                        self.data['lastReturn'] = subRet['data']
                        
                    if subRet['type'] == 'async':
                        yield subRet
        yield {'type':'finish','data':self.data['lastReturn']}

    def execute(self):
        ret = None
        for ret in self._generatorExecute():
            if ret['type'] == 'async':
                res = asyncio.run(ret['data'][0]())
                ret['data'][1](res)
        return ret['data']
    
    def _asyncCallback(self):
        def callback(data):
            self.data.update(data)
        return callback

    def _makeMainPipe(self):
        if(len(self.executionList)):
            return
        execListInstances = {}
        mainPipes = self._pipes.values()
        for namePipe,pipe in self._instances.items():
            pipes = [pipe]
            pipes.extend(mainPipes)
            execListInstances[namePipe] = makePipeline(pipes, self._executeFnWithWrapper)
        self.subExecList = execListInstances
        self.executionList = makePipeline(mainPipes,self._executeFnWithWrapper)
 
    def _fnWrapper(self,fn):
        @wraps(fn)
        def wrapper():
            return self._executeFnWithWrapper(fn)
        return wrapper
    
    def _executeFnWithWrapper(self,fn):
        params = inspect.signature(fn).parameters
        props = list(params.keys())
        args = []
        ops = {
            'pipe':lambda:args.append(self._pipes[fn._origin]),
            'data':lambda:args.append(self.data),
            'pipes':lambda:args.append(self._pipes),
            'controller':lambda:args.append(self.controller)
        }
        for prop in props:
            if params[prop].kind in [inspect.Parameter.VAR_KEYWORD, inspect.Parameter.VAR_POSITIONAL]:
                continue
            if prop in ops:
                ops[prop]()
            else:
                args.append(self.data[prop])
        return fn(*args)
    def __repr__(self):
        return 'Pipeline:\n\n' + 'Execution order:' + ", ".join([x.__name__ + '('+x._origin +')' for x in self.executionList]) + '.'