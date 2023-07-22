"""
Represents and manages one Spec in the XML.
"""
import xml.etree.ElementTree as ET
import base64
import re

from constants import bandits, default_spec, tree_versions, PlayerClasses, _VERSION, _VERSION_str
from pob_config import print_call_stack, print_a_xml_element
from dialogs.popup_dialogs import ok_dialog


class Spec:
    def __init__(self, build, _spec=None, version=_VERSION_str) -> None:
        """
        Represents one Spec in the XML. Most simple settings are properties.

        :param _spec: the spec from the XML, or None for a new Spec (probably should never happen)
        """
        self.internal_version = 6
        self.build = build
        self.def_spec = ET.fromstring(default_spec)
        if _spec is None:
            _spec = self.def_spec
            _spec.set("treeVersion", version)
        self.xml_spec = _spec

        # remove editedNodes if found
        ed = self.xml_spec.find("EditedNodes", None)
        if ed is not None:
            self.xml_spec.remove(ed)

        self.masteryEffects = {}
        self.set_mastery_effects_from_string(self.xml_spec.get("masteryEffects", ""))

        self.nodes = []
        self.ascendancy_nodes = []
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
        Set the tree version string in the XML
        :param new_version: str
        :return:
        """
        # ensure it is formatted correctly (n_nn). Remove dots and a trailing subversion
        tmp_list = re.split(r"\.|_|/", new_version)
        self.xml_spec.set("treeVersion", f"{tmp_list[0]}_{tmp_list[1]}")

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

    def b_to_i(self, byte_array, begin, end, endian, length=0):
        """Grabs end->begin bytes and returns an int"""
        if length == 0:
            return int.from_bytes(byte_array[begin:end], endian)
        else:
            return int.from_bytes(byte_array[begin : begin + length], endian)

    def import_regular_nodes(self, decoded_str, start, count, endian):
        """
        Import all the regular nodes from an URl
        :param decoded_str:
        :param start:
        :param count: This needs to be passed in as it's one byte in ggg url and two in poeplanner
        :param endian: big (ggg) or little (poeplanner)
        :return: new index
        """
        end = start + (count * 2)

        print("nodes: start, end, count", start, end, count)
        decoded_nodes = decoded_str[start:end]

        # now decode the nodes structure to numbers
        self.nodes = []
        for i in range(0, len(decoded_nodes), 2):
            # print(i, int.from_bytes(decoded_nodes[i : i + 2], endian))
            self.nodes.append(int.from_bytes(decoded_nodes[i : i + 2], endian))
        return end

    def import_cluster_nodes(self, decoded_str, start, count, endian):
        """
        Import the cluster nodes from an URL
        :param decoded_str:
        :param start:
        :param count: This needs to be passed in as it's one byte in ggg url and two in poeplanner
        :param endian: big (ggg) or little (poeplanner)
        :return: new index
        """

        end = start + (count * 2)
        print("cluster: start, end", start, end, count)
        if count > 0:
            decoded_cluster_nodes = decoded_str[start:end]
            # now decode the cluster nodes structure to numbers
            for i in range(0, len(decoded_cluster_nodes), 2):
                # print(''.join('{:02x} '.format(x) for x in cluster_nodes[i:i + 2]))
                print(i, int.from_bytes(decoded_cluster_nodes[i : i + 2], endian) + 65536)
                self.nodes.append(int.from_bytes(decoded_cluster_nodes[i : i + 2], endian) + 65536)
        return end

    def import_mastery_nodes(self, decoded_str, start, count, endian):
        """
        Import the mastery nodes from an URL
        :param decoded_str:
        :param start:
        :param count: This needs to be passed in as it's one byte in ggg url and two in poeplanner
        :param endian: big (ggg) or little (poeplanner)
        :return: new index
        """

        end = start + (count * 4)
        print("mastery: start, end, count", start, end, count)
        if count > 0:
            self.masteryEffects = {}
            decoded_mastery_nodes = decoded_str[start:end]
            # now decode the mastery nodes structure to numbers
            for i in range(0, len(decoded_mastery_nodes), 4):
                # print(''.join('{:02x} '.format(x) for x in decoded_mastery_nodes[i:i + 2]))
                # print(''.join('{:02x} '.format(x) for x in decoded_mastery_nodes[i + 2:i + 4]))
                if endian == "little":
                    # poeplanner has these two round the other way too
                    m_id = int.from_bytes(decoded_mastery_nodes[i : i + 2], endian)
                    m_effect = int.from_bytes(decoded_mastery_nodes[i + 2 : i + 4], endian)
                else:
                    m_id = int.from_bytes(decoded_mastery_nodes[i + 2 : i + 4], endian)
                    m_effect = int.from_bytes(decoded_mastery_nodes[i : i + 2], endian)
                print("id", m_id, "effect", m_effect)
                self.masteryEffects[m_id] = m_effect
                self.nodes.append(m_id)

    def import_ascendancy_nodes(self, decoded_str, start, count, endian):
        """
        Import the ascendancy nodes from an URL from poeplpanner
        :param decoded_str:
        :param start:
        :param count: This needs to be passed in as it's one byte in ggg url and two in poeplanner
        :param endian: big (ggg) or little (poeplanner)
        :return: new index
        """
        end = start + (count * 2)
        print("ascendancy: start, end, count", start, end, count)
        if count > 0:
            decoded_ascendancy_nodes = decoded_str[start:end]
            # print(f"ascendancy_nodes: {len(decoded_ascendancy_nodes)},", "".join("{:02x} ".format(x) for x in decoded_ascendancy_nodes))
            for i in range(0, len(decoded_ascendancy_nodes), 2):
                # print("".join("{:02x} ".format(x) for x in decoded_ascendancy_nodes[i : i + 2]))
                print(i, self.b_to_i(decoded_ascendancy_nodes, i, i + 2, endian))
                self.nodes.append(self.b_to_i(decoded_ascendancy_nodes, i, i + 2, endian))
        return end

    def set_nodes_from_ggg_url(self):
        """
        This function sets the nodes from the self.URL property. This allows us to set the URL for legacy purposes
        without actually disturbing the node information we have.

        :return: N/A
        """
        endian = "big"

        if self.URL is None:
            return
        m = re.search(r"http.*passive-skill-tree/(.*/)?(.*)", self.URL)

        # check the validity of what was passed in
        # group(1) is None or a version
        # group(2) is always the encoded string, with any variables
        if m is not None:
            self.treeVersion = m.group(1) is None and _VERSION_str or m.group(1)
            if self.treeVersion not in tree_versions.keys():
                ok_dialog(
                    self.build.win,
                    f"Invalid tree version: {re.sub('_', '.', self.treeVersion)}",
                    f"Valid tree versions are: {list(tree_versions.values())}",
                )
                self.treeVersion = _VERSION_str
                return
            # output[0] will be the encoded string and the rest will variable=value, which we don't care about (here)
            output = m.group(2).split("?")
            decoded_str = base64.urlsafe_b64decode(output[0])
            # print(type(decoded_str), decoded_str)
            # print(f"decoded_str: {len(decoded_str)},", "".join("{:02x} ".format(x) for x in decoded_str))

            # the decoded_str is 0 based, so every index will be one smaller than the equivalent in lua
            if decoded_str and len(decoded_str) > 7:
                version = self.b_to_i(decoded_str, 0, 4, endian)
                print(f"Valid tree found, version: {version}")

                self.classId = decoded_str[4]
                self.ascendClassId = version >= 4 and decoded_str[5] or 0

                # Nodes, Ascendancies are in here also
                idx = 6
                nodes_count = self.b_to_i(decoded_str, idx, idx + 1, endian)
                idx = self.import_regular_nodes(decoded_str, idx + 1, nodes_count, endian)

                # Clusters
                cluster_count = decoded_str[idx]
                idx = self.import_cluster_nodes(decoded_str, idx + 1, cluster_count, endian)

                # Mastery
                mastery_count = decoded_str[idx]
                mastery_start = idx + 1
                self.import_mastery_nodes(decoded_str, mastery_start, mastery_count, endian)

    def set_nodes_from_poeplanner_url(self, poep_url):
        """
        This function sets the nodes from poeplanner url.

        :return: N/A
        """
        endian = "little"

        def get_tree_version(minor):
            """Translates poeplanner internal tree version to GGG version"""
            # fmt: off
            tree_versions = { # poeplanner id: ggg version
                26: 21, 25: 20, 24: 19, 23: 18, 22: 17, 21: 16, 19: 15, 18: 14, 17: 13, 16: 12, 15: 11, 14: 10,
            }
            # fmt: on
            return tree_versions.get(minor, -1)

        if poep_url is None:
            return
        m = re.search(r"http.*poeplanner.com/(.*)", poep_url)
        # group(1) is always the encoded string
        if m is not None:
            # Remove any variables at the end (probably not required for poeplanner)
            tmp_output = m.group(1).split("?")
            encoded_str = tmp_output[0]
            del tmp_output[0]
            variables = tmp_output  # a list of variable=value or an empty list

            decoded_str = base64.urlsafe_b64decode(encoded_str)
            # print(f"decoded_str: {len(decoded_str)},", "".join("{:02x} ".format(x) for x in decoded_str))
            if decoded_str and len(decoded_str) > 10:
                # 0-1 is version ?
                version = self.b_to_i(decoded_str, 0, 2, endian)

                # 2 is ??

                # 3-6 is tree version_version
                major_version = self.b_to_i(decoded_str, 3, 4, endian)
                minor_version = get_tree_version(self.b_to_i(decoded_str, 5, 6, endian))
                self.treeVersion = minor_version < 0 and _VERSION_str or f"{major_version}_{minor_version}"
                if self.treeVersion not in tree_versions.keys():
                    ok_dialog(
                        self.build.win,
                        f"Invalid tree version: {re.sub('_', '.', self.treeVersion)}",
                        f"Valid tree versions are: {list(tree_versions.values())}",
                    )
                    self.treeVersion = _VERSION_str
                    return

                # 7 is Class, 8 is Ascendancy
                self.classId = decoded_str[7]
                self.ascendClassId = decoded_str[8]

                # 9 is Bandit
                self.build.set_bandit_by_number(decoded_str[9])

                # Nodes
                idx = 10
                nodes_count = self.b_to_i(decoded_str, idx, idx + 1, endian)
                idx = self.import_regular_nodes(decoded_str, idx + 2, nodes_count, endian)

                # Clusters
                cluster_count = self.b_to_i(decoded_str, idx, idx + 1, endian)
                idx = self.import_cluster_nodes(decoded_str, idx + 2, cluster_count, endian)

                # Ascendancy Nodes
                ascendancy_count = self.b_to_i(decoded_str, idx, idx + 1, endian)
                idx = self.import_ascendancy_nodes(decoded_str, idx + 2, ascendancy_count, endian)

                # Masteries
                mastery_count = self.b_to_i(decoded_str, idx, idx + 1, endian)
                self.import_mastery_nodes(decoded_str, idx + 2, mastery_count, endian)

    def export_nodes_to_url(self):
        endian = "big"
        byte_stream = bytearray()
        byte_stream.extend(self.internal_version.to_bytes(4, endian))
        byte_stream.append(self.classId)
        byte_stream.append(self.ascendClassId)

        # print(''.join('{:02x} '.format(x) for x in byte_stream))

        # separate the cluster nodes from the real nodes
        nodes = []
        cluster_nodes = []
        for node in sorted(self.nodes):
            if node >= 65536:
                cluster_nodes.append(node)
            else:
                nodes.append(node)

        byte_stream.append(len(nodes))
        for node in self.nodes:
            byte_stream.extend(node.to_bytes(2, endian))
        # print(''.join('{:02x} '.format(x) for x in byte_stream))

        byte_stream.append(len(cluster_nodes))
        for cluster_node in cluster_nodes:
            cluster_node -= 65536
            byte_stream.extend(cluster_node.to_bytes(2, endian))
        # print(''.join('{:02x} '.format(x) for x in byte_stream))

        byte_stream.append(len(self.masteryEffects))
        for mastery_node in self.masteryEffects:
            byte_stream.extend(self.masteryEffects[mastery_node].to_bytes(2, endian))
            byte_stream.extend(mastery_node.to_bytes(2, endian))

        # string = " ".join('{:02x}'.format(x) for x in byte_stream)
        # print(string)

        encoded_string = base64.urlsafe_b64encode(byte_stream).decode("utf-8")
        return f"https://www.pathofexile.com/passive-skill-tree/{encoded_string}"

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
        print("set_mastery_effect", node_id, effect_id)
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

    def load_from_ggg_json(self, json_tree, json_character):
        """
        Import the tree (and later the jewels)

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
        self.classId = json_character.get("classId", 0)
        self.ascendClassId = json_character.get("ascendancyClass", 0)
        # write nodes and stuff to xml
        self.save()

    def import_from_poep_json(self, json_tree):
        """
        Import the tree (and later the jewels)

        :param json_tree: json import of tree and jewel data
        :return: N/A
        """
        self.nodes = json_tree.get("selectedNodeHashes", "0")
        self.extended_hashes = json_tree.get("selectedExtendedNodeHashes", [])
        # for the json import, this is a list of:
        # { "effectHash": 28638, "masteryHash": 64128 }
        for mastery_effect in json_tree.get("selectedMasteryEffects", []):
            mastery_node = int(mastery_effect["masteryHash"])
            self.nodes.append(mastery_node)
            self.masteryEffects[mastery_node] = int(mastery_effect["effectHash"])
        self.classId = json_tree.get("classIndex", 0)
        self.ascendClassId = json_tree.get("ascendancyIndex", 0)
        # write nodes and stuff to xml
        self.save()
