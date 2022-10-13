"""
Represents and manages one Spec in the XML.
"""
import xml.etree.ElementTree as ET
import base64
import re

from constants import default_spec, PlayerClasses, _VERSION_str
from pob_config import print_call_stack, print_a_xml_element


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
        self.set_mastery_effects_from_string(self.xml_spec.get("masteryEffects", ""))

        self.nodes = []
        self.extended_hashes = []
        self.set_nodes_from_string(self.xml_spec.get("nodes", "0"))

        # Table of jewels equipped in this tree
        # Keys are node IDs, values are items
        self.jewels = {}

        # if there are no sockets there, we don't mind. We'll create an empty one when saving
        sockets = _spec.find("Sockets")
        if sockets is not None:
            for socket in sockets.findall("Socket"):
                node_id = int(socket.get("nodeId", 0))
                item_id = int(socket.get("itemId", 0))
                # There are files which have been saved poorly and have empty jewel sockets saved as sockets ...
                # with itemId zero. This check filters them out to prevent dozens of invalid jewels
                if item_id > 0:
                    self.jewels[node_id] = item_id

    @property
    def title(self):
        return self.xml_spec.get("title", "Default")

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
        :param new_class_id: PlayerClasses or int: importing from json sets using an int
        :return: N/A
        """
        if type(new_class_id) == int:
            self.xml_spec.set("classId", f"{new_class_id}")
        else:
            self.xml_spec.set("classId", f"{new_class_id.value}")

    @property
    def ascendClassId(self):
        return int(self.xml_spec.get("ascendClassId", 0))

    @ascendClassId.setter
    def ascendClassId(self, new_ascend_class_id):
        """
        :param new_ascend_class_id: int
        :return: N/A
        """
        self.xml_spec.set("ascendClassId", f"{new_ascend_class_id}")

    def ascendClassId_str(self):
        """Return a string of the current Ascendancy"""
        # get a list of ascendancies from the current tree's json
        _class = self.build.current_tree.classes[self.classId]
        ascendancies = [_ascendancy["name"] for _ascendancy in _class["ascendancies"]]
        # insert the class name for when ascendClassId == 0
        ascendancies.insert(0, self.classId_str())
        # Return the current ascendancy's name
        return ascendancies[self.ascendClassId]

    @property
    def treeVersion(self):
        return self.xml_spec.get("treeVersion", _VERSION_str)

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
            return None
        return xml_url.text.strip()

    @URL.setter
    def URL(self, new_url):
        """
        :param new_url: str
        :return: N/A
        """
        if new_url == "":
            return
        xml_url = self.xml_spec.find("URL")
        if xml_url is None:
            xml_url = ET.Element("URL")
            self.xml_spec.append(xml_url)
        xml_url.text = new_url

    def set_nodes_from_url(self):
        """
        This function sets the nodes from the self.URL property. This allows us to set the URL for legacy purposes
        without actually disturbing the node information we have.

        :return: N/A
        """
        if self.URL is None:
            return
        m = re.search(r"http.*passive-skill-tree/(.*/)?(.*)", self.URL)

        # check the validity of what was passed in
        # group(1) is None or a version
        # group(2) is always the encoded string, with any variables
        if m is not None:
            self.treeVersion = m.group(1) is None and _VERSION_str or m.group(1)
            # output[0] will be the encoded string and the rest will variable=value, which we don't care about (here)
            output = m.group(2).split("?")
            decoded_str = base64.b64decode(output[0], "-_")
            # print(type(decoded_str), decoded_str)
            # print(f"decoded_str: {len(decoded_str)},", "".join("{:02x} ".format(x) for x in decoded_str))

            # the decoded_str is 0 based, so every index will be one smaller than the equivalent in lua
            if decoded_str and len(decoded_str) > 7:
                version = int.from_bytes(decoded_str[0:4], "big")
                print(f"Valid tree found, {version}")

                self.classId = decoded_str[4]
                self.ascendClassId = version >= 4 and decoded_str[5] or 0

                nodes_start = version >= 4 and 7 or 6
                nodes_end = version >= 5 and 7 + (decoded_str[6] * 2) or -1
                # print("nodes_start, end", nodes_start, nodes_end)
                decoded_nodes = decoded_str[nodes_start:nodes_end]
                # print(f"nodes: {len(nodes)},", "".join('{:02x} '.format(x) for x in nodes))
                # print("")

                # now decode the nodes structure to numbers
                self.nodes = []
                for i in range(0, len(decoded_nodes), 2):
                    # print(
                    #     i,
                    #     " ".join("{:02x}".format(x) for x in decoded_nodes[i : i + 2]),
                    #     int.from_bytes(decoded_nodes[i : i + 2], "big"),
                    # )
                    self.nodes.append(int.from_bytes(decoded_nodes[i : i + 2], "big"))

                if version < 5:
                    self.masteryEffects = {}
                    return

                cluster_count = decoded_str[nodes_end]
                cluster_start = nodes_end + 1
                cluster_end = cluster_count == 0 and cluster_start or cluster_start + (cluster_count * 2)
                # print("cluster_start, end", cluster_start, cluster_end, cluster_count)
                if cluster_count > 0:
                    decoded_cluster_nodes = decoded_str[cluster_start:cluster_end]
                    # cluster_nodes = decoded_str[cluster_start:cluster_start+(cluster_count * 2)]
                    # print(f"decoded_cluster_nodes: {len(decoded_cluster_nodes)},", ''.join('{:02x} '.format(x) for x in decoded_cluster_nodes))
                    # now decode the cluster nodes structure to numbers
                    for idx in range(0, len(decoded_cluster_nodes), 2):
                        # print(''.join('{:02x} '.format(x) for x in cluster_nodes[idx:idx + 2]))
                        # print(idx, int.from_bytes(decoded_cluster_nodes[idx : idx + 2], "big") + 65536)
                        self.nodes.append(int.from_bytes(decoded_cluster_nodes[idx : idx + 2], "big") + 65536)

                mastery_count = decoded_str[cluster_end]
                if mastery_count > 0:
                    mastery_start = cluster_end + 1
                    mastery_end = mastery_count == 0 and mastery_start or mastery_start + (mastery_count * 4)
                    # print("mastery_start, end", mastery_start, mastery_end, mastery_count)
                    decoded_mastery_nodes = decoded_str[mastery_start:mastery_end]
                    # print(f"decoded_mastery_nodes: {len(decoded_mastery_nodes)},", ''.join('{:02x} '.format(x) for x in decoded_mastery_nodes))
                    # now decode the mastery nodes structure to numbers
                    for idx in range(0, len(decoded_mastery_nodes), 4):
                        # print(''.join('{:02x} '.format(x) for x in decoded_mastery_nodes[idx:idx + 4]))
                        # print(idx, int.from_bytes(decoded_mastery_nodes[idx:idx+2], "big"))
                        m_id = int.from_bytes(decoded_mastery_nodes[idx + 2 : idx + 4], "big")
                        m_effect = int.from_bytes(decoded_mastery_nodes[idx : idx + 2], "big")
                        # print(m_id, m_effect)
                        self.masteryEffects[m_id] = m_effect

    def set_mastery_effects_from_string(self, new_effects):
        """
        masteryEffects is a string of {paired numbers}. Turn it into a dictionary [int1] = int2

        :param new_effects: str
        :return:
        """
        if new_effects != "":
            # get a list of matches
            effects = re.findall(r"{(\d+),(\d+)}", new_effects)
            for effect in effects:
                self.masteryEffects[int(effect[0])] = int(effect[1])

    def get_mastery_effect(self, node_id):
        """return one node id from mastery effects"""
        return self.masteryEffects.get(node_id, -1)

    def set_mastery_effect(self, node_id, effect_id):
        """add one node id from mastery effects"""
        self.masteryEffects[node_id] = int(effect_id)

    def remove_mastery_effect(self, node_id):
        """remove one node id from mastery effects"""
        try:
            del self.masteryEffects[node_id]
        except KeyError:
            pass

    def list_assigned_effects_for_mastery_type(self, node_list):
        """
        Get a list of effects assigned for a given mastery type (eg: "Life Mastery").

        :param node_list: list: A list of node id's
        :return: list of effects already assigned.
        """
        pass

    def set_nodes_from_string(self, new_nodes):
        """
        Turn the string list of numbers into a list of numbers
        :param new_nodes: str
        :return: N/A
        """
        if new_nodes:
            self.nodes = [int(node) for node in new_nodes.split(",")]
            # self.nodes = new_nodes.split(",")

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

        sockets = self.xml_spec.find("Sockets")
        if sockets is not None:
            self.xml_spec.remove(sockets)
        sockets = ET.Element("Sockets")
        self.xml_spec.append(sockets)
        if len(self.jewels) > 0:
            for node_id in self.jewels.keys():
                sockets.append(ET.fromstring(f'<Socket nodeId="{node_id}" itemId="{self.jewels[node_id]}"/>'))

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
