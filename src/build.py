"""The build class encompasses all attributes and parameters defining a build.

It is defined by a specific Tree and Player instance at time of evaluation.
The intent is that there is only one Build for a character. There might be
numerous Passive Trees (at various Player Levels, or various Cluster Jewels)
associated with a Player.
"""

import os

import player
import pob_xml
import tree

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
        "Config": {},
    }
}


class Build:
    def __init__(self, name: str = "temp") -> None:
        self.name = name
        self.tree = tree.Tree()
        self.player = player.Player()
        self.filename = ""
        self.build = {}

    def __repr__(self) -> str:
        attributes = [repr(attr) for attr in (self.name, self.tree, self.player)]
        seperator = "\n"
        return f"[BUILD]: {seperator.join(attributes)}"

    def default(self):
        self.build = default_build

    def load(self, filename: str) -> None:
        try:
            self.build = pob_xml.read_xml(filename)
        except FileNotFoundError:
            # TODO: message box for failure
            self.default()
        else:
            self.filename = filename

    def save(self, filename: str) -> None:
        try:
            pob_xml.write_xml(filename, self.build)
        except FileNotFoundError:
            # TODO: message box for failure
            pass
        else:
            self.filename = filename


def test() -> None:
    build = Build()
    print(build)


if __name__ == "__main__":
    test()
