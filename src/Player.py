"""
Player Class

The Player represents an in-game character at a specific point in their
leveling progress.

A unique Player is defined by: level, class selection, ascendancy selection,
skill selection, and itemization across the item sets.
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
        self.skills = list()
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
