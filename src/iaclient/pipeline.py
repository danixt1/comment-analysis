from dataclasses import dataclass

MODE_ADD = 0
MODE_BEFORE = 1
MODE_AFTER = 2

@dataclass
class Rule:
    fn:callable
    pipe:str
    mode:int
    linked:str = None

class Pipe:
    def __init__(self,pipeName:str,activator:callable = None):
        self._before = {}
        self._after = {}
        self._added = []
        self.rules:list[Rule] = []
        self._activate =activator if activator else lambda *args, **kwargs: True
        self._onPipesCreated = lambda *args, **kwargs: None
        self.pipeName = pipeName

    def activator(self,func:callable):
        self._activate = func
        return self
    
    def before(self,nameFn:str,func:callable):
        rule = Rule(func, self.pipeName, MODE_BEFORE,nameFn)
        self.rules.append(rule)
        return self
    
    def after(self,nameFn:str,func:callable):
        rule = Rule(func, self.pipeName, MODE_AFTER, nameFn)
        self.rules.append(rule)
        return self
        
    def add(self,func:callable):
        rule = Rule(func, self.pipeName, MODE_ADD)
        self.rules.append(rule)
        return self
    
    def onPipesCreated(self, func):
        self._onPipesCreated = func
        return self
    
import inspect
class PipeRunner:

    def __init__(self):
        self._pipes:dict[str,Pipe] = {}
        self.executionList = []
        self.data = {}
    def addPipe(self, pipe:Pipe):
        self._pipes[pipe.pipeName] = pipe
        return self
    
    def execute(self):
        for pipe in self._pipes.values():
            pipe._onPipesCreated(self,pipe, self._pipes)
        self._makePipe()
        for fn in self.executionList:
            self._fnWrapper(fn)
            
    def _makePipe(self):
        rulesAdd:list[Rule] = []
        rulesLinked:list[Rule] = {}
        execList = []
        for pipe in self._pipes.values():
            if not self._fnWrapper(pipe._activate):
                continue
            for rule in pipe.rules:
                rule.fn._origin = rule.pipe
                if rule.mode == MODE_ADD:
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

    def _addLinkeds(self, rule:Rule, execList:list,rulesLinked):
        fnName = rule.fn.__name__
        if fnName not in rulesLinked:
            return
        links = rulesLinked[fnName]
        for ruleLinked in links:
            n = 1 if ruleLinked.mode == MODE_AFTER else 0
            execList.insert(execList.index(rule.fn) + n, ruleLinked.fn)
            self._addLinkeds(ruleLinked, execList, rulesLinked)

    def _fnWrapper(self,fn):
        props = list(inspect.signature(fn).parameters.keys())
        args = []
        for prop in props:
            if prop == 'data':
                args.append(self.data)
                continue
            if prop == 'pipes':
                args.append(self._pipes)
                continue
            if prop == 'args' or prop == 'kwargs':
                continue
            args.append(self.data[prop])
        return fn(*args)
    