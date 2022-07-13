"""
Build Class

The build class is the top-level class encompassing all attributes and
parameters defining a build. It is defined by a specific Tree and Player
instance at time of evaluation.

The intent is that there is only one Build for a character. There might be
numerous Passive Trees (at various Player Levels, or various Cluster Jewels)
associated with a Player.
"""

import Tree
import Player


class Build:
    def __init__(self, name: str = "temp") -> None:
        self.name = name
        self.tree = Tree.Tree()
        self.player = Player.Player()

    def __repr__(self) -> str:
        ret_str = f"[BUILD]: '{self.name}'\n"
        ret_str += f"{self.tree}"
        ret_str += f"{self.player}"
        return ret_str


def test() -> None:
    build = Build()
    print(build)


if __name__ == "__main__":
    test()
