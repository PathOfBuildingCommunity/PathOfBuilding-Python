#

from functools import cached_property
from math import floor

from Dependency import Dependency, addDependency

class Player(Dependency):
    def __init__(self, level, strength):
        self.modDB = dict()
        self._level = level
        self._start_strength = strength
        self._flat_strength = 0
        self._more_strength = 0
        self._inc_strength = 0
        self._flat_life = 0
        self._more_life = 0
        self._inc_life = 0
        self._base_health = None
        self._max_health = None
        self._base_strength = None
        self._max_strength = None

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

    @cached_property
    def base_health(self):
        print("Base Health calculated")
        return 38 + self.level * 12 + floor(self.max_strength / 2) + self.flat_life

    @cached_property
    def max_health(self):
        print("Max Health calculated")
        return self.base_health * (1 + self.inc_life / 100) * (1 + self.more_life / 100)

    @cached_property
    def base_strength(self):
        print("Base Strength calculated")
        return self._start_strength + self._flat_strength

    @cached_property
    def max_strength(self):
        print("Max Strength calculated")
        return self.base_strength * (1 + self.inc_strength / 100) * (1 + self.more_strength / 100)

    @property
    def level(self):
        return self._level

    @property
    def start_strength(self):
        return self._start_strength

    @property
    def flat_life(self):
        return self._flat_life

    @property
    def more_life(self):
        return self._more_life

    @property
    def inc_life(self):
        return self._inc_life

    @property
    def flat_strength(self):
        return self._flat_strength

    @property
    def more_strength(self):
        return self._more_strength

    @property
    def inc_strength(self):
        return self._inc_strength

def test():
    player = Player(1, 20)
    print(f"{player.max_health}")

    player.level = 5
    print(f"{player.max_health}")

    player.more_life = 100
    print(f"{player.max_health}")

    player.flat_strength = 100
    print(f"{player.max_health}")

if __name__ == "__main__":
    test()
