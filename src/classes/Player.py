#!/usr/bin/env python3

# Player Class
#
# [class] Player
#     [enum] Class Selection
#     [enum] Ascendancy Selection
#     [dict] Stats (e.g. Str/Dex/Int, Hit/Crit, Life/Mana,
#                   Block/Spell Block/Evade/Dodge, etc.)
#     [dict] Item Slots
#         [per slot ref] Item
#     [optional list] Minions

from enum import Enum


class PlayerClasses(Enum):
    SCION = 0
    MARAUDER = 1
    RANGER = 2
    WITCH = 3
    DUELIST = 4
    TEMPLAR = 5
    SHADOW = 6


class PlayerAscendancy(Enum):
    NONE = None


class Player:
    def __init__(
        self,
        player_class: PlayerClasses = PlayerClasses.SCION,
        ascendancy: PlayerAscendancy = PlayerAscendancy.NONE,
        level: int = 1,
    ) -> None:
        self.player_class = player_class
        self.ascendancy = ascendancy
        self.level = level
        self.stats = dict()
        self.item_slots = dict()
        self.minions = dict()

    def __repr__(self) -> str:
        ret_str = f"Level {self.level} {self.player_class.name}"
        ret_str += f" {self.ascendancy.value}\n" if self.ascendancy.value else "\n"
        return ret_str


def test() -> None:
    player = Player()
    print(player)


if __name__ == "__main__":
    test()
