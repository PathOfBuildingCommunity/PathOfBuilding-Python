#

from functools import cached_property
from math import floor

from Dependency import Dependency, getDependencies
from ModDB import ModifierDatabase
from Modifiers import Modifier

class Player(Dependency):
    def __init__(self, level, strength):
        self.modDB = ModifierDatabase()
        self._level = level

        '''
        addDependency("level", "base_health")
        addDependency("start_strength", "base_strength")
        addDependency("flat_strength", "base_strength")
        addDependency("base_strength", "max_strength")
        addDependency("more_strength", "max_strength")
        addDependency("inc_strength", "max_strength")
        addDependency("max_strength", "base_health")
        addDependency("flat_life", "base_health")
        addDependency("base_health", "max_health")
        addDependency("more_life", "max_health")
        addDependency("inc_life", "max_health")
        '''

        self.addMod(Modifier("Health", "BASE", 12, "Base Per Level", { "type": "Multiplier", "var": "Level" }))
        self.addMod(Modifier("Health", "BASE", 0.5, "Base Per Strength", { "type": "Multiplier", "var": "Max_Strength"}))
        self.addMod(Modifier("Strength", "BASE", strength, "Starting"))

    def addMod(self, mod: Modifier):
        self.modDB.addEntry(mod)
        attr = f"{mod.type.lower()}_{mod.name.lower()}"
        try:
            self.__delattr__(f"{attr}")
        except:
            #print("FAIL")
            pass
        if attr in getDependencies():
            self._reset_dependent_vars(attr)

    @cached_property
    def base_health(self):
        ret = 38 + self.level * 12 + floor(self.max_strength / 2) + self.flat_health
        print(f"BASE Health calculated: {ret}")
        return ret

    @cached_property
    def max_health(self):
        ret = floor(self.base_health * (1 + self.inc_health / 100) * (1 + self.more_health / 100))
        print(f"Total Health calculated: {ret}")
        return ret

    @cached_property
    def base_strength(self):
        ret = self.modDB.getBase("Strength")
        print(f"BASE Strength calculated: {ret}")
        return ret

    @cached_property
    def max_strength(self):
        ret = floor((self.base_strength + self.flat_strength) * (1 + self.inc_strength / 100) * (1 + self.more_strength / 100))
        print(f"Total Strength calculated: {ret}")
        return ret

    @property
    def level(self):
        return self._level

    @cached_property
    def flat_health(self):
        ret = self.modDB.getFlat("Health")
        print(f"FLAT Health calculated: {ret}")
        return ret

    @cached_property
    def more_health(self):
        ret = self.modDB.getMore("Health")
        print(f"MORE Health calculated: {ret}")
        return ret

    @cached_property
    def inc_health(self):
        ret = self.modDB.getInc("Health")
        print(f"INC Health calculated: {ret}")
        return ret

    @cached_property
    def flat_strength(self):
        ret = self.modDB.getFlat("Strength")
        print(f"FLAT Strength calculated: {ret}")
        return ret

    @cached_property
    def more_strength(self):
        ret = self.modDB.getMore("Strength")
        print(f"MORE Strength calculated: {ret}")
        return ret

    @cached_property
    def inc_strength(self):
        ret = self.modDB.getInc("Strength")
        print(f"INC Strength calculated: {ret}")
        return ret

def test():
    player = Player(1, 20)
    #print(f"{player.base_health}\n")
    print(f"{player.max_health}\n")

    player.level = 5
    print(f"{player.max_health}\n")

    player.addMod(Modifier("Health", "MORE", 100, ""))
    print(f"{player.max_health}\n")

    player.addMod(Modifier("Strength", "FLAT", 100, ""))
    player.addMod(Modifier("Strength", "INC", 30, ""))
    player.addMod(Modifier("Strength", "MORE", 15, ""))
    player.addMod(Modifier("Health", "FLAT", 500, ""))
    #print(f"{player.max_strength}\n")
    print(f"{player.max_health}\n")

if __name__ == "__main__":
    test()
