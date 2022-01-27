#!/usr/bin/env python3

"""
Tree Class

[class] Tree
    [str] version
    [set] All Nodes (addressable by Node ID)
    [set] Allocated Nodes (addressable by Node ID)
"""

_VERSION_ = "3.17"


class Tree:
    def __init__(self, version: str = _VERSION_) -> None:
        self.version = version
        self.tree_nodes = set()
        self.allocated_nodes = set()

    def __repr__(self) -> str:
        ret_str = f"[TREE]: version '{self.version}'\n"
        return ret_str


def test() -> None:
    tree = Tree()
    print(tree)


if __name__ == "__main__":
    test()
