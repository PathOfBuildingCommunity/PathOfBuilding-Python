"""
Build Class

The build class is the top-level class encompassing all attributes and
parameters defining a build. It is defined by a specific Tree and Player
instance at time of evaluation.

The intent is that there is only one Build for a character. There might be
numerous Passive Trees (at various Player Levels, or various Cluster Jewels)
associated with a Player.
"""

import sys
import os

import Tree
import Player
import pob_xml

default_build = {
    "PathOfBuilding": {
        "Build": {
            "version": "p1",
            "level": "1",
            "targetVersion": "3_0",
            "pantheonMajorGod": "None",
            "bandit": "None",
            "className": "Templar",
            "ascendClassName": "Inquisitor",
            "mainSocketGroup": "5",
            "viewMode": "NOTES",
            "pantheonMinorGod": "None",
        },
        "Import": {
            "lastAccountHash": "c80de930a45ad8c2ad7ca55c18682fc5a64eb85a",
            "lastRealm": "PC",
            "lastCharacterHash": "5ea56ce0e8798eb62dbac4a1dbec23f435637af6",
        },
        "Calcs": {},
        "Skills": {},
        "Tree": {},
        "Notes": "",
        "TreeView": {
            "searchStr": "",
            "zoomY": "245.25",
            "showHeatMap": "false",
            "zoomLevel": "2",
            "showStatDifferences": "true",
            "zoomX": "-54.5",
        },
        "Items": {},
        "Config": {}
    }
}


class Build:
    def __init__(self, name: str = "temp") -> None:
        self.name = name
        self.tree = Tree.Tree()
        self.player = Player.Player()
        self.filename = ""
        self.build = dict()

    def __repr__(self) -> str:
        ret_str = f"[BUILD]: '{self.name}'\n"
        ret_str += f"{self.tree}"
        ret_str += f"{self.player}"
        return ret_str

    def new_build(self):
        self.build = default_build

    def load_build(self, filename):
        if os.path.exists(filename):
            self.build = pob_xml.read_xml(filename)
            # print(self.build)
        if self.build is None:
            # message box for failure
            self.new_build()
        else:
            self.filename = filename

    def save_build(self, filename):
        self.filename = filename
        pob_xml.write_xml(filename, self.build)


def test() -> None:
    build = Build()
    print(build)


if __name__ == "__main__":
    test()
