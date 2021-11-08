#

from functools import cached_property
from math import floor

from Dependency import Dependency, addDependency

class Player(Dependency):
    def __init__(self, level, strength):
        self._level = level
        self._strength = strength
        self._flat_life = 0
        self._more_life = 0
        self._inc_life = 0
        self._base_health = None
        self._max_health = None

        addDependency("level", "base_health")
        addDependency("strength", "base_health")
        addDependency("flat_life", "base_health")
        addDependency("base_health", "max_health")
        addDependency("more_life", "max_health")
        addDependency("inc_life", "max_health")

    @cached_property
    def base_health(self):
        print("Base Health calculated")
        return 38 + self.level * 12 + floor(self.strength / 2) + self.flat_life

    @cached_property
    def max_health(self):
        print("Max Health calculated")
        return self.base_health * (1 + self.inc_life / 100) * (1 + self.more_life / 100)

    @property
    def level(self):
        return self._level

    @property
    def strength(self):
        return self._strength

    @property
    def flat_life(self):
        return self._flat_life

    @property
    def more_life(self):
        return self._more_life

    @property
    def inc_life(self):
        return self._inc_life

def test():
    player = Player(1, 20)
    print(f"{player.max_health}")

    player.level = 5
    print(f"{player.max_health}")
    
    player.more_life = 100
    print(f"{player.max_health}")

    player.flat_life = 100
    print(f"{player.max_health}")

if __name__ == "__main__":
    test()