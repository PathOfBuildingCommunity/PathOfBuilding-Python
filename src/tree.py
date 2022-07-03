"""This class represents an instance of the Passive Tree for a given Build.

Multiple Trees can exist in a single Build (at various progress levels;
at different Jewel/Cluster itemisations, etc.)

A Tree is tied to a Version of the Tree as released by GGG and thus older Trees
need to be supported for backwards compatibility reason.
"""

_VERSION = "3.17"


class Tree:
    def __init__(self, version: str = _VERSION) -> None:
        self.version = version
        self.tree_nodes = set()
        self.allocated_nodes = set()

    def __repr__(self) -> str:
        return f"[TREE]: version '{self.version}'"


def test() -> None:
    tree = Tree()
    print(tree)


if __name__ == "__main__":
    test()
