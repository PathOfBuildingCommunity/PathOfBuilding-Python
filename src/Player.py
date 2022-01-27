#!/usr/bin/env python3

"""
Player Class

[class] Player
     [enum] Class Selection
     [enum] Ascendancy Selection
     [set] Stats (e.g. Str/Dex/Int, Hit/Crit, Life/Mana,
                  Block/Spell Block/Evade/Dodge, etc.)
     [set] Item Sets
         [per slot ref] Item
     [optional set] Minions
"""

from Enumerations import PlayerClasses, PlayerAscendancies


class Player:
    def __init__(
        self,
        player_class: PlayerClasses = PlayerClasses.SCION,
        ascendancy: PlayerAscendancies = PlayerAscendancies.NONE,
        level: int = 1,
    ) -> None:
        self.player_class = player_class
        self.ascendancy = ascendancy
        self.level = level
        self.stats = set()
        self.item_sets = set()
        self.minions = set()

    def __repr__(self) -> str:
        ret_str = f"Level {self.level} {self.player_class.name}"
        ret_str += f" {self.ascendancy.value}\n" if self.ascendancy.value else "\n"
        return ret_str


def test() -> None:
    player = Player()
    print(player)


if __name__ == "__main__":
    test()
