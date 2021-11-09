#

from functools import cached_property
from math import floor

from Dependency import Dependency, addDependency, getDependencies
from ModDB import ModifierDatabase
from Modifiers import Modifier

class Player(Dependency):
    def __init__(self, level, strength):
        self.modDB = ModifierDatabase()
        self._level = level
        self._base_health = None
        self._max_health = None
        self._base_strength = None
        self._max_strength = None

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
        #print("REMOVING: " + f"{mod.type.lower()}_{mod.name.lower()}")
        self._reset_dependent_vars(f"{mod.type.lower()}_{mod.name.lower()}")
        self.modDB.addEntry(mod)
        #print(getDependencies())

    @cached_property
    def base_health(self):
        print("Base Health calculated")
        return 38 + self.level * 12 + floor(self.max_strength / 2) + self.flat_life

    @cached_property
    def max_health(self):
        print("Max Health calculated")
        return self.base_health * (1 + self.inc_life / 100) * (1 + self.more_life / 100)

    @property
    def base_strength(self):
        print("Base Strength calculated")
        return self.modDB.getBase("Strength")

    @cached_property
    def max_strength(self):
        print("Max Strength calculated")
        return (self.base_strength + self.flat_strength) * (1 + self.inc_strength / 100) * (1 + self.more_strength / 100)

    @property
    def level(self):
        return self._level

    @property
    def flat_life(self):
        print("Flat Health calculated")
        return self.modDB.getFlat("Health")

    @property
    def more_life(self):
        print("More Health calculated")
        return self.modDB.getMore("Health")

    @property
    def inc_life(self):
        print("Inc Health calculated")
        return self.modDB.getInc("Health")

    @property
    def flat_strength(self):
        print("Flat Strength calculated")
        return self.modDB.getFlat("Strength")

    @property
    def more_strength(self):
        print("More Strength calculated")
        return self.modDB.getMore("Strength")

    @property
    def inc_strength(self):
        print("Inc Strength calculated")
        return self.modDB.getInc("Strength")

def test():
    player = Player(1, 20)
    #print(f"{player.base_health}")
    print(f"{player.max_health}")

    player.level = 5
    print(f"{player.max_health}")

    player.addMod(Modifier("Health", "MORE", 100, ""))
    print(f"{player.max_health}")

    player.addMod(Modifier("Strength", "FLAT", 100, ""))
    print(f"{player.max_strength}")
    print(f"{player.max_health}")

if __name__ == "__main__":
    test()
