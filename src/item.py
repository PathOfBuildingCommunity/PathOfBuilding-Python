"""
A class to encapsulate one item
"""

import xml.etree.ElementTree as ET
import re

from pob_config import _debug, index_exists, str_to_bool, bool_to_str, print_call_stack
from constants import slot_map, ColourCodes
from ui_utils import html_colour_text
from mod import Mod

influence_colours = {
    "Shaper Item": ColourCodes.SHAPER.value,
    "Elder Item": ColourCodes.ELDER.value,
    "Warlord Item": ColourCodes.ADJUDICATOR.value,
    "Hunter Item": ColourCodes.BASILISK.value,
    "Crusader Item": ColourCodes.CRUSADER.value,
    "Redeemer Item": ColourCodes.EYRIE.value,
    "Searing Exarch Item": ColourCodes.CLEANSING.value,
    "Eater of Worlds Item": ColourCodes.TANGLE.value,
}


class Item:
    def __init__(self, _base_items, _slot=None) -> None:
        """
        Initialise defaults
        :param _base_items: dict: the loaded base_items.json
        :param _slot: where this item is worn/carried.
        """
        self._slot = _slot
        # the dict from json of the all items
        self.base_items = _base_items
        # Just this item's entry from base_items
        self.base_item = None

        # this is not always available from the json character download
        self.level_req = 0

        self.id = 0
        self.rarity = "NORMAL"
        self.title = ""
        self.name = ""
        self.base_name = ""
        self.ilevel = 0
        # needs to be a string as there are entries like "Limited to: 1 Survival"
        self.limited_to = ""
        self.type = ""  # or item_class
        self.quality = 0
        # this is a string even though the value is a number, as it's easier for comparisons from the original string.
        self.curr_variant = ""
        self.unique_id = ""
        self.requires = {}
        self.influences = []
        self.two_hand = False
        self.corrupted = False
        self.fractured = None
        self.fracturedMods = None
        self.abyss_jewel = None
        self.synthesised = None
        self.sockets = ""
        self.properties = {}
        self.implicitMods = []
        # explicit mods affecting this item with current variants
        self.explicitMods = []
        # all explicit mods including all variants
        self.full_explicitMods_list = []
        self.craftedMods = []
        self.enchantMods = []
        # titles of the variants
        self.variants = []
        # I think i need to store the variants separately, for crafting. Dict of string lists, var number is index
        self.variantMods = {}

        self.evasion = 0
        self.evasion_base_percentile = 0.0
        self.energy_shield = 0
        self.energy_shield_base_percentile = 0.0
        self.armour = 0
        self.armour_base_percentile = 0.0
        self.league = ""
        self.source = ""

    def load_from_xml(self, xml, debug_lines=False):
        """
        Load internal structures from the free text version of item's xml

        :param xml: ET.element: xml of the item
        :param debug_lines: Temporary to debug the process
        :return: N/A
        """
        if xml.get("ver", "1") == "2":
            self.load_from_xml_v2(xml)
            return
        desc = xml.text
        # split lines into a list, removing any blank lines, leading & trailing spaces.
        #   stolen from https://stackoverflow.com/questions/7630273/convert-multiline-into-list
        lines = [y for y in (x.strip() for x in desc.splitlines()) if y]
        # lets get all the : separated variables first and remove them from the lines list
        # stop when we get to implicits
        explicits_idx, line_idx = (0, 0)
        # Can't use enumerate as we are changing the list as we move through
        while index_exists(lines, line_idx):
            if debug_lines:
                _debug("a", len(lines), lines)
            m = re.search(r"(.*): (.*)", lines[line_idx])
            if m is None:
                # skip this line
                line_idx += 1
            else:
                lines.pop(line_idx)
                match m.group(1):
                    case "Rarity":
                        self.rarity = m.group(2).upper()
                    case "Unique ID":
                        self.unique_id = m.group(2)
                    case "Item Level":
                        self.ilevel = m.group(2)
                    case "Selected Variant":
                        self.curr_variant = m.group(2)
                    case "Quality":
                        self.quality = m.group(2)
                    case "Sockets":
                        self.sockets = m.group(2)
                    case "Armour":
                        self.armour = m.group(2)
                    case "ArmourBasePercentile":
                        self.armour_base_percentile = m.group(2)
                    case "Energy Shield":
                        self.energy_shield = m.group(2)
                    case "EnergyShieldBasePercentile":
                        self.energy_shield_base_percentile = m.group(2)
                    case "Evasion":
                        self.evasion = m.group(2)
                    case "EvasionBasePercentile":
                        self.evasion_base_percentile = m.group(2)
                    case "LevelReq":
                        self.level_req = int(m.group(2))
                    case "League":
                        self.league = m.group(2)
                    case "Source":
                        self.source = m.group(2)
                    case "Limited to":
                        self.limited_to = m.group(2)
                    case "Variant":
                        self.variants.append(m.group(2))
                    case "Implicits":
                        # implicits, if any
                        for idx in range(int(m.group(2))):
                            line = lines.pop(line_idx)
                            self.implicitMods.append(Mod(line))
                        explicits_idx = line_idx
                        break
                self.properties[m.group(1)] = m.group(2)
        # every thing that is left, from explicits_idx, is explicits
        for idx in range(explicits_idx, len(lines)):
            line = lines.pop(explicits_idx)
            # Corrupted is not a mod, but will get caught in explicits due to crap data design
            if "Corrupted" in line:
                self.corrupted = True
                continue
            mod = Mod(line)
            self.full_explicitMods_list.append(mod)
            # check for variants and if it's our variant, add it to the smaller explicit mod list
            if "variant" in line:
                m = re.search(r"{variant:([\d,]+)}(.*)", line)
                if self.curr_variant in m.group(1).split(","):
                    self.explicitMods.append(mod)
                # for var in m.group(1).split(","):
                #     if var == self.curr_variant:
                #         self.explicitMods.append(mod)
            else:
                self.explicitMods.append(mod)

        if debug_lines:
            _debug("b", len(lines), lines)
        # 'normal' and Magic ? objects and flasks only have one line (either no title or no base name)
        # should only have the title and basename entries
        if len(lines) == 1:
            self.name = lines.pop(0)
            match self.rarity:
                case "MAGIC":
                    self.base_name = self.name
                case "NORMAL":
                    self.base_name = self.name
        else:
            self.title = lines.pop(0)
            self.base_name = lines.pop(0)
            self.name = f"{self.title}, {self.base_name}"
        if debug_lines:
            _debug("c", len(lines), lines)

        # Anything left must be something like 'Shaper Item', Requires ...
        for line in lines:
            if line in influence_colours.keys():
                self.influences.append(line)
            else:
                m = re.search(r"Requires (.*)", line)
                if m:
                    self.requires[m.group(1)] = True
                else:
                    # do something else
                    match line:
                        case _:
                            print(f"Item().load_from_xml: Skipped: {line}")
        self.base_item = self.base_items.get(self.base_name, None)
        if self.base_item is not None:
            self.type = self.base_item["type"]
        elif "Flask" in self.name:
            self.type = "Flask"
        # load_from_xml

    def load_from_json(self, _json):
        """
        Load internal structures from the downloaded json
        """
        rarity_map = {0: "NORMAL", 1: "MAGIC", 2: "RARE", 3: "UNIQUE", 9: "RELIC"}

        def get_property(_json_item, _name, _default):
            """
            Get a property from a list of property tags. Not all properties appear to be mandatory.

            :param _json_item: the gem reference from the json download
            :param _name: the name of the property
            :param _default: a default value to be used if the property is not listed/found
            :return: Either the string value if found or the _default value passed in.
            """
            for _prop in _json_item:
                if _prop.get("name") == _name and _prop.get("suffix") != "(gem)":
                    value = _prop.get("values")[0][0].replace("+", "").replace("%", "")
                    return value
            return _default

        self.base_name = _json.get("typeLine", "")
        # for magic and normal items, name is blank
        self.title = _json.get("name", "")
        self.name = f'{self.title and f"{self.title}, " or ""}{self.base_name}'
        self.unique_id = _json["id"]
        self._slot = slot_map[_json["inventoryId"]]
        self.rarity = rarity_map[int(_json.get("frameType", 0))]

        # Mods
        for mod in _json.get("explicitMods", []):
            self.full_explicitMods_list.append(Mod(mod))
        for mod in _json.get("craftedMods", []):
            self.full_explicitMods_list.append(Mod(f"{{crafted}}{mod}"))
        self.explicitMods = self.full_explicitMods_list

        for mod in _json.get("enchantMods", []):
            self.implicitMods.append(Mod(f"{{crafted}}{mod}"))
        for mod in _json.get("scourgeMods", []):
            self.implicitMods.append(Mod(f"{{crafted}}{mod}"))
        for mod in _json.get("implicitMods", []):
            self.implicitMods.append(Mod(mod))
        # for mod in _json.get("scourgeModLines", []):
        #     self.implicitMods.append(f"{{crafted}}{mod}")
        # for mod in _json.get("implicitModLines", []):
        #     self.implicitMods.append(f"{{crafted}}{mod}")

        self.properties = _json.get("properties", {})
        if self.properties:
            self.quality = get_property(_json["properties"], "Quality", "0")
        self.ilevel = _json.get("ilvl", 0)
        self.corrupted = _json.get("corrupted", False)
        self.abyss_jewel = _json.get("abyssJewel", False)
        self.fractured = _json.get("fractured", False)
        self.synthesised = _json.get("synthesised", False)
        if self.fractured:
            self.fracturedMods = _json.get("fracturedMods", None)
        if _json.get("requirements", None):
            self.level_req = int(get_property(_json["requirements"], "Level", "0"))
        # Process sockets and their grouping
        if _json.get("sockets", None) is not None:
            current_socket_group_number = -1
            socket_line = ""
            for socket in _json["sockets"]:
                this_group = socket["group"]
                if this_group == current_socket_group_number:
                    socket_line += f"-{socket['sColour']}"
                else:
                    socket_line += f" {socket['sColour']}"
                    current_socket_group_number = this_group
            # there will always be a leading space from the routine above
            self.sockets = socket_line.strip()
        """
        delve 	?bool 	always true if present
        synthesised 	?bool 	always true if present
        """
        influences = _json.get("influences", None)
        if influences is not None:
            # each entry is like 'shaper=true'
            for influence in influences:
                key = f'{influence.split("=")[0].title()} Item'
                if key in influence_colours.keys():
                    self.influences.append(key)

        self.base_item = self.base_items.get(self.base_name, None)
        if self.base_item is not None:
            self.type = self.base_item["type"]
        elif "Flask" in self.name:
            self.type = "Flask"
        # load_from_json

    def save(self):
        """
        Save internal structures back to a xml object

        :return: ET.ElementTree:
        """
        text = f"Rarity: {self.rarity}\n"
        text += self.title and f"{self.title}\n{self.base_name}\n" or f"{self.base_name}\n"
        text += f"Unique ID: {self.unique_id}\n"
        text += f"Item Level: {self.ilevel}\n"
        text += f"Quality: {self.quality}\n"
        if self.sockets:
            text += f"Sockets: {self.sockets}\n"
        text += f"LevelReq: {self.level_req}\n"
        for influence in self.influences:
            text += f"{influence}\n"
        for requirement in self.requires.keys():
            text += f"Requires {requirement}\n"
        if type(self.properties) == dict:
            for idx in self.properties.keys():
                text += f"{idx}: {self.properties[idx]}\n"
        text += f"Implicits: {len(self.implicitMods)}\n"
        for mod in self.implicitMods:
            text += f"{mod.text_for_xml}\n"
        for mod in self.full_explicitMods_list:
            text += f"{mod.text_for_xml}\n"
        if self.corrupted:
            text += "Corrupted"

        # if debug_print:
        #     print(f"{text}\n\n")
        return ET.fromstring(f'<Item id="{self.id}">{text}</Item>')

    def save_v2(self):
        """
        Save to xml in version 2

        :return: ET.element
        """

        def add_attrib_if_not_null(_xml, tag, value):
            """
            add an attribute if not 0, none, false or empty str

            :param _xml: ET.element: the xml element to add to
            :param tag: the tag name to add
            :param value:
            :return: N/A
            """
            if type(value) == str:
                if value:
                    _xml.set(tag, value)
            elif type(value) == bool:
                if value:
                    _xml.set(tag, bool_to_str(value))
            else:
                # some kind of number (int or float)
                if value != 0:
                    _xml.set(tag, f"{value}")

        xml = ET.fromstring(f'<Item ver="2" id="{self.id}"></Item>')
        xml.set("title", self.title)
        xml.set("base_name", self.base_name)
        xml.set("rarity", self.rarity)
        add_attrib_if_not_null(xml, "sockets", self.sockets)
        if self.rarity == "UNIQUE":
            add_attrib_if_not_null(xml, "league", self.league)
            add_attrib_if_not_null(xml, "source", self.source)
        add_attrib_if_not_null(xml, "unique_id", self.unique_id)
        add_attrib_if_not_null(xml, "corrupted", self.corrupted)
        # add_attrib_if_not_null(xml, "variant", self.curr_variant)
        # there is always an Attribs element, even if it is empty, which almost never happens
        attribs = ET.fromstring(f"<Attribs />")
        add_attrib_if_not_null(attribs, "evasion", self.evasion)
        add_attrib_if_not_null(attribs, "evasion_base_percentile", self.evasion_base_percentile)
        add_attrib_if_not_null(attribs, "energy_shield", self.energy_shield)
        add_attrib_if_not_null(attribs, "energy_shield_base_percentile", self.energy_shield_base_percentile)
        add_attrib_if_not_null(attribs, "armour", self.armour)
        add_attrib_if_not_null(attribs, "armour_base_percentile", self.armour_base_percentile)
        add_attrib_if_not_null(attribs, "limited_to", self.limited_to)
        add_attrib_if_not_null(attribs, "ilevel", self.ilevel)
        add_attrib_if_not_null(attribs, "level_req", self.level_req)
        xml.append(attribs)
        # there is always Implicits and Explicits elements, even if they are empty
        imp = ET.fromstring("<Implicits></Implicits>")
        for mod in self.implicitMods:
            imp.append(ET.fromstring(f"<Mod>{mod.text_for_xml}</Mod>"))
        xml.append(imp)
        exp = ET.fromstring("<Explicits></Explicits>")
        for mod in self.full_explicitMods_list:
            exp.append(ET.fromstring(f"<Mod>{mod.text_for_xml}</Mod>"))
        xml.append(exp)
        # Requires are only present if there are some
        for requirement in self.requires.keys():
            xml.append(ET.fromstring(f"<Requires>{requirement}</Requires>"))
        if len(self.variants) > 0:
            var_xml = ET.fromstring(f'<Variants current="{self.curr_variant}"></Variants>')
            for num, variant in enumerate(self.variants, 1):
                # at this point (Nov2022) 'num' isn't used but it makes reading/editing the xml a little easier
                var_xml.append(ET.fromstring(f'<Variant num="{num}">{variant}</Variant>'))
            xml.append(var_xml)
        return xml
    # save_v2

    def load_from_xml_v2(self, xml):
        """
        Fill variables from the version 2 xml

        :param the loaded xml:
        :return:
        """
        self.title = xml.get("title", "")
        # print(self.title)
        self.base_name = xml.get("base_name", "oh noes")
        # print(self.base_name)
        self.name = f'{self.title and f"{self.title}, " or ""}{self.base_name}'
        self.rarity = xml.get("rarity", "oh noes")
        self.unique_id = xml.get("unique_id", "")
        self.sockets = xml.get("sockets", "")
        self.league = xml.get("league", "")
        self.source = xml.get("source", "")
        self.corrupted = str_to_bool(xml.get("corrupted", "False"))
        # self.curr_variant = xml.get("variant", "0")
        attribs = xml.find("Attribs")
        if attribs is not None:
            self.evasion = int(attribs.get("evasion", "0"))
            self.evasion_base_percentile = float(attribs.get("evasion_base_percentile", "0.0"))
            self.energy_shield = int(attribs.get("energy_shield", "0"))
            self.energy_shield_base_percentile = float(attribs.get("energy_shield_base_percentile", "0.0"))
            self.armour = int(attribs.get("armour", "0"))
            self.armour_base_percentile = float(attribs.get("armour_base_percentile", "0.0"))
            self.limited_to = attribs.get("limited_to", "")
            self.ilevel = int(attribs.get("ilevel", "0"))
            self.level_req = int(attribs.get("level_req", "0"))
        var_xml = xml.find("Variants")
        if var_xml is not None:
            self.curr_variant = var_xml.get("current", "1")
            for variant in var_xml.findall("Variant"):
                self.variants.append(variant.text)
            # ensure the uniques load with the latest value
            if self.curr_variant == "0" and self.rarity == "UNIQUE":
                self.curr_variant = f"{len(self.variants)}"
        imp = xml.find("Implicits")
        for mod_xml in imp.findall("Mod"):
            self.implicitMods.append(Mod(mod_xml.text))
        exp = xml.find("Explicits")
        for mod_xml in exp.findall("Mod"):
            line = mod_xml.text
            mod = Mod(mod_xml.text)
            self.full_explicitMods_list.append(mod)
            # check for variants and if it's our variant, add it to the smaller explicit mod list
            if "variant" in line:
                m = re.search(r"{variant:([\d,]+)}(.*)", line)
                if self.curr_variant in m.group(1).split(","):
                    self.explicitMods.append(mod)
                # for var in m.group(1).split(","):
                #     if var == self.curr_variant:
                #         self.explicitMods.append(mod)
            else:
                self.explicitMods.append(mod)
        for requirement in xml.findall("Requires"):
            self.requires[requirement.text] = True
        # load_from_xml_v2

    def tooltip(self):
        """
        Create a tooltip. Hand crafted html anyone ?

        :return: str: the tooltip
        """
        rarity_colour = f"{ColourCodes[self.rarity].value};"
        tip = (
            f"<style>"
            f"table, th, td {{border: 1px solid {rarity_colour}; border-collapse: collapse;}}"
            f"td {{text-align: center;}}"
            f"</style>"
            f'<table width="425">'
            f"<tr><th>"
        )
        name = self.title == "" and self.base_name or self.name
        tip += html_colour_text(rarity_colour, name)
        for influence in self.influences:
            tip += f"<br/>{html_colour_text(influence_colours[influence], influence)}"
        tip += "</th></tr>"
        if self.level_req > 0:
            tip += f"<tr><td>Requires Level <b>{self.level_req}</b></td></tr>"
        if self.limited_to != "":
            tip += f"<tr><td>Limited to: <b>{self.limited_to}</b></td></tr>"
        if self.requires:
            for requirement in self.requires:
                tip += f"<tr><td>Requires <b>{requirement}</b></td></tr>"
        if len(self.implicitMods) > 0:
            tip += f"<tr><td>"
            for mod in self.implicitMods:
                tip += mod.tooltip
            # mod tooltip's always end in <br/>, remove the last one
            tip = tip[:-4]
            tip += f"</td></tr>"
        if len(self.explicitMods) > 0:
            tip += f"<tr><td>"
            for mod in self.explicitMods:
                if not mod.corrupted:
                    tip += mod.tooltip
            # mod tooltip's always end in <br/>, remove the last one
            tip = tip[:-4]
            tip += f"</td></tr>"

        if self.corrupted:
            tip += f'<tr><td>{html_colour_text("STRENGTH", "Corrupted")}</td></tr>'
        tip += f"</table>"
        return tip

    @property
    def slot(self):
        return self._slot

    @slot.setter
    def slot(self, new_slot):
        self._slot = new_slot

    @property
    def shaper(self):
        return "Shaper" in self.influences

    @property
    def elder(self):
        return "Elder" in self.influences

    @property
    def warlord(self):
        return "Warlord" in self.influences

    @property
    def hunter(self):
        return "Hunter" in self.influences

    @property
    def crusader(self):
        return "Crusader" in self.influences

    @property
    def redeemer(self):
        return "Redeemer" in self.influences

    @property
    def exarch(self):
        return "Exarch" in self.influences

    @property
    def eater(self):
        return "Eater" in self.influences
