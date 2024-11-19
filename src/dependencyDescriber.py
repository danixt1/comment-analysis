from abc import ABC,abstractmethod

class DependencyDescriber(ABC):
    """
    DependencyDescribe is an abstract class that describes the dependencies of a module.
    """
    def hasAllDependencies(self)->bool:
        """
        Checks if the dependencies are met.
        Returns True if the dependencies are met, False otherwise.
        """
        try:
            self._initDependecies()
            return True
        except ModuleNotFoundError:
            return False
    @abstractmethod
    def _initDependecies(self):
        pass
    @abstractmethod
    def dependencies(self)->str|list[str]:
        """
        Returns the dependencies of the module.
        """
        pass