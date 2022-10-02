"""
Represents and manages one Spec in the XML.
"""
import xml.etree.ElementTree as ET
import re

from constants import default_spec, PlayerClasses


class Spec:
    def __init__(self, build, _spec=None) -> None:
        """
        Represents one Spec in the XML. Most simple settings are properties.

        :param _spec: the spec from the XML, or None for a new Spec (probably should never happen)
        """
        self.build = build
        self.def_spec = ET.fromstring(default_spec)
        if _spec is None:
            _spec = self.def_spec
        self.xml_spec = _spec

        # remove editedNodes if found
        ed = self.xml_spec.find("EditedNodes", None)
        if ed is not None:
            self.xml_spec.remove(ed)

        self.masteryEffects = {}
        self.set_masteryEffects_from_string(self.xml_spec.get("masteryEffects", ""))

        self.nodes = []
        self.extended_hashes = []
        self.set_nodes_from_string(self.xml_spec.get("nodes", "0"))

        self.Sockets = _spec.find("Sockets")
        if self.Sockets is None:
            self.Sockets = self.def_spec.find("Sockets")

    @property
    def title(self):
        return self.xml_spec.get("title")

    @title.setter
    def title(self, new_title):
        self.xml_spec.set("title", new_title)

    @property
    def classId(self):
        return PlayerClasses(int(self.xml_spec.get("classId", PlayerClasses.SCION.value)))

    def classId_str(self):
        """Return a string of the current Class"""
        return self.classId.name.title()

    @classId.setter
    def classId(self, new_class_id):
        """
        :param new_class_id: PlayerClasses or int: importing fromjson sets using an int
        :return: N/A
        """
        if type(new_class_id) == int:
            self.xml_spec.set("classId", f"{new_class_id}")
        else:
            self.xml_spec.set("classId", f"{new_class_id.value}")

    @property
    def ascendClassId(self):
        return int(self.xml_spec.get("ascendClassId", 0))

    def ascendClassId_str(self):
        """Return a string of the current Ascendancy"""
        # get a list of ascendancies from the current tree's json
        _class = self.build.current_tree.classes[self.classId]
        ascendancies = [_ascendancy["name"] for _ascendancy in _class["ascendancies"]]
        # insert the class name for when ascendClassId == 0
        ascendancies.insert(0, self.classId_str())
        # Return the current ascendancy's name
        return ascendancies[self.ascendClassId]

    @ascendClassId.setter
    def ascendClassId(self, new_ascend_class_id):
        """
        :param new_ascend_class_id: int
        :return: N/A
        """
        self.xml_spec.set("ascendClassId", f"{new_ascend_class_id}")

    @property
    def treeVersion(self):
        return self.xml_spec.get("treeVersion", self.def_spec.get("treeVersion"))

    @treeVersion.setter
    def treeVersion(self, new_version):
        """
        :param new_version: str
        :return:
        """
        self.xml_spec.set("treeVersion", new_version)

    @property
    def URL(self):
        xml_url = self.xml_spec.find("URL")
        if xml_url is None:
            xml_url = self.def_spec.find("URL")
            self.xml_spec.append(xml_url)
        return xml_url.text.strip()

    @URL.setter
    def URL(self, new_url):
        """
        :param new_url: str
        :return:
        """
        xml_url = self.xml_spec.find("URL")
        xml_url.text = new_url

    def set_masteryEffects_from_string(self, new_effects):
        """
        masteryEffects is string of {paired numbers}. Turn it into a dictionary [int1] = int2

        :param new_effects: str
        :return:
        """
        if new_effects != "":
            # get a list of matches
            effects = re.findall(r"{(\d+),(\d+)}", new_effects)
            for effect in effects:
                self.masteryEffects[int(effect[0])] = int(effect[1])

    def set_nodes_from_string(self, new_nodes):
        """
        Turn the string list of numbers into a list of numbers
        :param new_nodes: str
        :return: N/A
        """
        if new_nodes:
            self.nodes = new_nodes.split(",")

    def set_extended_hashes_from_string(self, new_nodes):
        """
        Turn the string list of numbers into a list of numbers
        :param new_nodes: str
        :return: N/A
        """
        if new_nodes:
            self.nodes = new_nodes.split(",")

    def save(self):
        """
        Save anything that can't be a property, like Nodes,sockets

        :return:
        """
        if len(self.nodes) > 0:
            self.xml_spec.set("nodes", ",".join(f"{node}" for node in self.nodes))

        # put masteryEffects back into a string of {number,number},{number,number}
        str_mastery_effects = ""
        for effect in self.masteryEffects.keys():
            str_mastery_effects += f"{{{effect},{self.masteryEffects[effect]}}},"
        self.xml_spec.set("masteryEffects", str_mastery_effects.rstrip(","))

    def load_from_json(self, title, json_tree, json_character):
        """
        Import the tree (and later the jewels)

        :param title: str: New title
        :param json_tree: json import of tree and jewel data
        :param json_character: json import of the character information
        :return: N/A
        """
        self.nodes = json_tree.get("hashes", "0")
        self.extended_hashes = json_tree.get("hashes_ex", [])
        # for the json import, this is a list of large ints (https://www.pathofexile.com/developer/docs/reference)
        #   with the modulo remainder being "the string value of the mastery node skill hash"
        #   with the quotient being "the value is the selected effect hash"
        for effect in json_tree.get("mastery_effects", []):
            self.masteryEffects[int(effect) % 65536] = int(effect) // 65536
        self.title = title
        self.classId = json_character.get("classId", 0)
        self.ascendClassId = json_character.get("ascendancyClass", 0)
        # write nodes and stuff to xml
        self.save()
