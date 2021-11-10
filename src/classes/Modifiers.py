#

from Dependency import addDependency, _dependencies
from math import floor

class Modifier:
    def __init__(self, name: str, type: str, value, source: str, conditionals: set = set(), tags: dict = {}):
        self.name = name
        self.type = type
        self.value = value
        self.source = source
        self.conditionals = conditionals
        self.tags = tags
        self.process()

    def process(self):
        if 'type' in self.tags.keys() and self.tags['type'] == "Multiplier":
            addDependency(self.tags['var'].lower(), f"{self.type.lower()}_{self.name.lower()}")
        addDependency(f"{self.type.lower()}_{self.name.lower()}", f"max_{self.name.lower()}")
        #print(self)

    def getValue(self, caller = None):
        if caller:
            #print(f"getting var: {self.name}:{self.type}")
            if 'type' in self.tags.keys() and self.tags['type'] == "Multiplier":
                var = f"{self.tags['var'].lower()}"
                l = caller.__getattribute__(var)
                #print(f"{var}: {l}")
                return floor(self.value * l)
            return self.value
        return self.value

    def __repr__(self):
        ret = f"{self.name}:{self.type}\n"
        ret += f"Value: {self.value}\n"
        ret += f"{self.tags} -- {self.source}"
        return ret

def test():
    m = Modifier("Health", "BASE", 12, "", tags = { "type": "Multiplier", "var": "Level" })
    print(m)

if __name__ == "__main__":
    test()
