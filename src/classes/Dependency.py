#

from itertools import chain

_dependencies = {}
_dependent_vars = set()

def addDependency(dep1: str, dep2: str):
    global _dependencies, _dependent_vars
    if dep1 in _dependencies.keys():
        if not dep2 in _dependencies[dep1]:
            _dependencies[dep1].append(dep2)
    else:
        _dependencies[dep1] = [dep2]
    _dependent_vars = set(chain.from_iterable(_dependencies.values()))

class Dependency:
    def _reset_dependent_vars(self, name):
        for var in _dependencies[name]:
            super().__delattr__(f"{var}")
            if var in _dependencies:
                self._reset_dependent_vars(var)

    def __setattr__(self, name, value):
        global _dependencies, _dependent_vars
        if name in _dependent_vars:
            raise AttributeError("Cannot set this value.")
        if name in _dependencies:
            self._reset_dependent_vars(name)
            name = f"_{name}"
        super().__setattr__(name, value)