#

from Dependency import addDependency

class Mod:
    def __init__(self, name: str, type: str, value, source: str, tags: dict = {}):
        self.name = name
        self.type = type
        self.value = value
        self.source = source
        self.tags = tags
        self.process()

    def process(self):
        if 'type' in self.tags.keys() and self.tags['type'] == "Multiplier":
            addDependency(self.tags['var'].lower(), f"{self.type.lower()}_{self.name.lower()}")

def test():
    Mod("Health", "BASE", 12, "", { "type": "Multiplier", "var": "Level" })

if __name__ == "__main__":
    from Dependency import _dependencies
    test()
    print(_dependencies)
