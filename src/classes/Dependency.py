#

from itertools import chain

_dependencies = {}
_dependent_vars = set()

def addDependency(dep1: str, dep2: str):
    global _dependencies, _dependent_vars
    if dep1 in _dependencies.keys():
        if not dep2 in _dependencies[dep1]:
            _dependencies[dep1].append(dep2)
            #print(f"Appending DEP: {dep1} -> {dep2}")
    else:
        _dependencies[dep1] = [dep2]
        #print(f"Adding DEP: {dep1} -> {dep2}")
    _dependent_vars = set(chain.from_iterable(_dependencies.values()))
    #print("DV: \n", _dependent_vars)

def getDependentVars():
    return _dependent_vars

def getDependencies():
    return _dependencies

class Dependency:
    def _reset_dependent_vars(self, name: str):
        #print(f"DEP\n{_dependencies}")
        for var in _dependencies[name]:
            #print(f"Resetting: {var} (due to {name})")
            try:
                super().__delattr__(f"{var}")
            except:
                #print(f"FAIL")
                pass
            if var in _dependencies:
                self._reset_dependent_vars(var)

    def __setattr__(self, name: str, value):
        global _dependencies, _dependent_vars
        if name in _dependent_vars:
            raise AttributeError("Cannot set this value.")
        if name in _dependencies:
            self._reset_dependent_vars(name)
            name = f"_{name}"
        #print(f"Setting {name} to {value}")
        super().__setattr__(name, value)
