#!/usr/bin/env python3

"""
Build Class

[class] Build
    [ref] Tree
    [ref] Player
"""

import Tree
import Player


class Build:
    def __init__(self, name: str = "temp") -> None:
        self.name = name
        self.tree_ref = Tree.Tree()
        self.player_ref = Player.Player()

    def __repr__(self) -> str:
        ret_str = f"[BUILD]: '{self.name}'\n"
        ret_str += f"{self.tree_ref}"
        ret_str += f"{self.player_ref}"
        return ret_str


def test() -> None:
    build = Build()
    print(build)


if __name__ == "__main__":
    test()
