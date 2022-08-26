"""A Player represents an in-game character at a specific progression point.

A unique Player is defined by: level, class selection, ascendancy selection,
skill selection, and itemization across the item sets.
"""

from constants import PlayerClasses, PlayerAscendancy


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
        self.stats = set()
        self.skills = []
        self.item_sets = set()
        self.minions = set()

    def __repr__(self) -> str:
        return (
            f"Level {self.level} {self.player_class.name}" f" {self.ascendancy.value}\n"
            if self.ascendancy.value is not None
            else "\n"
        )


def test() -> None:
    player = Player()
    print(player)


if __name__ == "__main__":
    test()
