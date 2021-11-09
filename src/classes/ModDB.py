#

from Modifiers import Modifier

class ModifierDatabase:
    def __init__(self):
        self.clear()

    def addEntry(self, entry: Modifier):
        name = entry.name
        type = entry.type
        if name not in self.db.keys():
            self.db[name] = dict()
        if type not in self.db[name].keys():
            self.db[name][type] = [entry]
        else:
            if not entry in self.db[name][type]:
                self.db[name][type].append(entry)

    def getBase(self, name: str):
        retVal = 0
        if name in self.db.keys() and "BASE" in self.db[name].keys():
            for entry in self.db[name]["BASE"]:
                retVal += entry.getValue()
            return retVal
        return 0

    def getFlat(self, name: str):
        retVal = 0
        if name in self.db.keys() and "FLAT" in self.db[name].keys():
            for entry in self.db[name]["FLAT"]:
                retVal += entry.getValue()
            return retVal
        return 0

    def getInc(self, name: str):
        retVal = 0
        if name in self.db.keys() and "INC" in self.db[name].keys():
            for entry in self.db[name]["INC"]:
                retVal += entry.getValue()
            return retVal
        return retVal

    def getMore(self, name: str):
        retVal = 0
        if name in self.db.keys() and "MORE" in self.db[name].keys():
            for entry in self.db[name]["MORE"]:
                retVal += entry.getValue()
            return retVal
        return retVal

    def clear(self):
        self.db = dict()

def test():
    db = ModifierDatabase()
    mod1 = Modifier("Health", "BASE", 12, "", { "type": "Multiplier", "var": "Level" })
    mod2 = Modifier("Health", "BASE", 13, "")
    db.addEntry(mod1)
    db.addEntry(mod2)
    import pprint
    pprint.pprint(db.db)

    print("BASE: " + str(db.getBase("Health")))

if __name__ == "__main__":
    test()
