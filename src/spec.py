"""
Represents one Spec in the XML.
"""
import xml.etree.ElementTree as ET
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

        # masteryEffects is string of {paired numbers}
        # we'll turn it into a list of lists [paired numbers]
        self.masteryEffects = []
        str_mastery_effects = self.xml_spec.get("masteryEffects", "")
        if str_mastery_effects != "":
            for effect in str_mastery_effects.split("},"):
                self.masteryEffects.append([effect.replace("{", "").replace("}", "")])

        self.nodes = {}
        str_nodes = self.xml_spec.get("nodes", "0")
        if str_nodes:
            self.nodes = str_nodes.split(",")

        self.Sockets = _spec.find("Sockets")
        if self.Sockets is None:
            self.Sockets = self.def_spec.find("Sockets")

    @property
    def title(self):
        return self.xml_spec.get("title", self.def_spec.get("title"))

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

        :param new_class_id: PlayerClasses:
        :return: N/A
        """
        self.xml_spec.set("classId", f"{new_class_id.value}")

    @property
    def ascendClassId(self):
        return int(self.xml_spec.get("ascendClassId", 0))

    def ascendClassId_str(self):
        """Return a string of the current Ascendancy"""
        # get a list of ascendancies from the current tree's json
        _class = self.build.current_tree.classes[self.classId]
        ascendancies = [_ascendancy["name"] for _ascendancy in _class["ascendancies"]]
        ascendancies.insert(0, self.classId_str())
        return ascendancies[self.ascendClassId]

    @ascendClassId.setter
    def ascendClassId(self, new_ascend_class_id):
        """

        :param new_ascend_class_id: int
        :return: N/A
        """
        self.xml_spec.set("title", f"{new_ascend_class_id}")

    @property
    def treeVersion(self):
        return self.xml_spec.get("treeVersion", self.def_spec.get("treeVersion"))

    @treeVersion.setter
    def treeVersion(self, new_version):
        """

        :param new_version: str
        :return:
        """
        self.xml_spec.set("title", new_version)

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

    def save(self):
        """
        Save anything that can't be a property, like Nodes,sockets

        :return:
        """
        if len(self.nodes) > 0:
            self.xml_spec.set("nodes", ",".join(f"{node}" for node in self.nodes))
        # put masteryEffects back into a string of {number,number},{number,number}
        str_mastery_effects = ",".join(
            f"{{{','.join(f'{number}' for number in pair)}}}" for pair in self.masteryEffects
        )
        self.xml_spec.set("masteryEffects", str_mastery_effects)
