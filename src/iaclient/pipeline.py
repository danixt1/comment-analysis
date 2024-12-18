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
    def finish(self):
        self._finish = True

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
    
class PipeInstanciable(RulesAccess):
    """Pipe instantiate only by call from controller.
    
    When called create a new sub pipe. rules added with `before` and `after` is added on calling in."""
    def __init__(self, pipeName):

        super().__init__(pipeName)

import inspect
import asyncio

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
    
class PipeRunner:

    def __init__(self):
        self._pipes:dict[str,Pipe] = {}
        self.executionList = []
        self.data = {'lastReturn':None}
        self.controller =  Controller()

    def addPipe(self, pipe:Pipe):
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
            self._fnWrapper(pipe._onPipesCreated)
        self._makePipe()

    def _generatorExecute(self):
        self._initPipe()
        for fn in self.executionList:
            if inspect.iscoroutinefunction(fn):
                yield {'type':'async','data':(lambda: self._fnWrapper(fn), self._asyncCallback())}
                continue
            
            newRes = self._fnWrapper(fn)
            if not newRes == None:
                self.data['lastReturn'] = newRes
            if self.controller._finish:
                break
        yield {'type':'finish','data':self.data['lastReturn']}

    def execute(self):
        ret = None
        for ret in self._generatorExecute():
            pass
        return ret['data']
    
    def _asyncCallback(self):
        def callback(data):
            self.data.update(data)
        return callback

    def _makePipe(self):
        rulesAdd:list[Rule] = []
        rulesLinked:dict[str,Rule] = {}
        execList = []
        for pipe in self._pipes.values():
            if not self._fnWrapper(pipe._activate):
                continue
            for rule in pipe.rules:
                rule.fn._origin = rule.pipe
                if rule.mode == RuleMode.MODE_ADD:
                    rulesAdd.append(rule)
                    continue
                value = rule.linked
                if value not in rulesLinked:
                    rulesLinked[value] = []
                rulesLinked[value].append(rule)
        for rule in rulesAdd:
            execList.append(rule.fn)
            self._addLinkeds(rule, execList, rulesLinked)
        self.executionList = execList

    def _addLinkeds(self, rule:Rule, execList:list,rulesLinked:dict[str,list[Rule]]):
        fnName = rule.fn.__name__
        if fnName not in rulesLinked:
            return
        links = rulesLinked[fnName]
        for ruleLinked in links:
            n = 1 if ruleLinked.mode == RuleMode.MODE_AFTER else 0
            execList.insert(execList.index(rule.fn) + n, ruleLinked.fn)
            self._addLinkeds(ruleLinked, execList, rulesLinked)

    def _fnWrapper(self,fn):
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
    