"""
A class to encapsulate one item
"""

import xml.etree.ElementTree as ET
import re

from pob_config import _debug, index_exists, str_to_bool, bool_to_str, print_call_stack
from constants import slot_map, slot_names, ColourCodes
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
    # these are ignored
    # "Synthesised Item"
    # "Fractured Item"
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
        # This item's entry from base_items
        self.base_item = None
        self._base_name = ""
        self._type = ""  # or item_class - eg weapon
        self.sub_type = ""  # or item_class - eg claw

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
        # implicit/explicit mods affecting this item with current variants
        self.implicitMods = []
        self.explicitMods = []
        # all implicit/explicit mods including all variants
        self.full_implicitMods_list = []
        self.full_explicitMods_list = []
        self.craftedMods = []
        self.enchantMods = []
        # names of the variants
        self.variant_names = []
        # dict of lists of the variant entries (EG: name, influences, etc'
        self.variant_entries = {}
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
        self.upgrade = ""
        self.radius = ""
        self.talisman_tier = 0
        # tooltip text for the item stats, not DPS. Prevent recalculating mostly static values every time the TT is read
        self.base_tooltip_text = ""

        # special dictionary/list for the rare template items that get imported into a build
        self.crafted_item = {}
        self.variant_entries_xml = None
        self.alt_variants = {}

    def load_from_ggg_json(self, _json):
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
        self.tooltip()
        # load_from_ggg_json

    def import_from_poep_json(self, _json):
        """
        Load internal structures from the downloaded json
        !!! Important note. Not everything comes through. Corrupted and Influences are two that i've noted aren't there.
        Crafts are just part of the explicits
        """
        # Example {'name': "The Poet's Pen", 'baseName': 'Carved Wand', 'uniqueName': "The Poet's Pen",
        # 'rarity': 'UNIQUE', 'quality': 20, 'baseStatRoll': 1, 'implicits': ['15% increased Spell Damage'],
        # 'explicits': ['+1 to Level of Socketed Active Skill Gems per 25 Player Levels',
        # 'Trigger a Socketed Spell when you Attack with this Weapon, with a 0.25 second Cooldown',
        # 'Adds 3 to 5 Physical Damage to Attacks with this Weapon per 3 Player Levels', '8% increased Attack Speed']}
        self.base_name = _json.get("baseName", "")
        # for magic and normal items, name is blank
        self.title = _json.get("name", "")
        self.name = f'{self.title and f"{self.title}, " or ""}{self.base_name}'
        # Slot info will only be present for equipped items
        self._slot = _json.get("slot", "")
        if self._slot != "":
            self._slot = slot_map[self._slot.title()]
        self.rarity = _json.get("rarity", "")
        self.quality = _json.get("quality", "0")
        # import doesn't have socket info
        self.sockets = self.base_item.get("initial_sockets", "")
        # import doesn't have corruption info
        # import doesn't have influence info
        # import doesn't have craft info

        # Mods
        for mod in _json.get("explicits", []):
            self.full_explicitMods_list.append(Mod(mod))
        self.explicitMods = self.full_explicitMods_list

        for mod in _json.get("enchants", []):
            self.implicitMods.append(Mod(f"{{crafted}}{mod}"))
        for mod in _json.get("scourgeMods", []):
            self.implicitMods.append(Mod(f"{{crafted}}{mod}"))
        for mod in _json.get("implicits", []):
            self.implicitMods.append(Mod(mod))

        self.tooltip()
        # load_from_ggg_json

    def load_from_xml(self, xml, debug_lines=False):
        """
        Load internal structures from the free text version of item's xml

        :param xml: ET.element: xml of the item
        :param debug_lines: Temporary to debug the process
        :return: boolean
        """

        def process_variant_entries(entry_name, prefix=""):
            """
            Process all lines for variants, return when complete. NOT USED for implicits and explicits.
            :param entry_name: str: entry name to add to variant_entries
            :param prefix: str: prefix for the entry, eg: LevelReq
            :return: The value of the last variant read, with the {variant:x} text
            """
            value = ""
            search_string = prefix and f"{prefix}:variant" or "variant"
            self.variant_entries[entry_name] = []
            _line = lines[0]
            while search_string in _line:
                lines.pop(0)
                value = re.search(r"{variant:([\d,]+)}(.*)", _line).group(2)
                self.variant_entries[entry_name].append(_line)
                _line = lines[0]
            return value

        if xml.get("ver", "1") == "2":
            return self.load_from_xml_v2(xml)
        desc = xml.text
        # split lines into a list, removing any blank lines, leading & trailing spaces.
        #   stolen from https://stackoverflow.com/questions/7630273/convert-multiline-into-list
        lines = [y for y in (x.strip(" \t\r\n") for x in desc.splitlines()) if y]
        # The first line has to be rarity !!!!
        line = lines.pop(0)
        if "rarity" not in line.lower():
            print("Error: Dave, i don't know what to do with this:\n", desc)
            return False
        m = re.search(r"(.*): (.*)", line)
        self.rarity = m.group(2).upper()
        # The 2nd line is either the title or the name of a magic/normal item. This is why Rarity is first.
        line = lines.pop(0)
        if self.rarity in ("NORMAL", "MAGIC"):
            self.base_name = line
            self.name = line
        else:
            self.title = line
            line = lines[0]
            if "variant" in line:
                self.base_name = process_variant_entries("base_name")
            else:
                self.base_name = line
                lines.pop(0)
            self.name = f"{self.title}, {self.base_name}"
        # remove any (information)
        m = re.search(r"(.*)( \(.*\))$", self.name)
        if m:
            self.name = m.group(1)

        # print(f"t: {self.title}, r: {self.rarity}")
        if debug_lines:
            _debug("begin", len(lines), lines)

        """ So the first three lines/Entries are gone, so it's game on. They can come in almost any order """
        # lets get all the : separated variables first and remove them from the lines list
        # stop when we get to implicits, or the end (eg: Tabula Rasa)
        explicits_idx, line_idx = (0, 0)
        # We can't use enumerate as we are changing the list as we move through
        while index_exists(lines, line_idx):
            if debug_lines:
                _debug("a", len(lines), lines)
            line = lines[line_idx]
            m = re.search(r"(.*): (.*)", line)
            # If no : then try to identify line. Skip if we can't deal with it.
            if m is None:
                if debug_lines:
                    _debug("m is None", line)
                if lines[line_idx] in influence_colours.keys():
                    self.influences.append(line)
                    lines.pop(line_idx)
                elif line.startswith("Requires"):
                    m = re.search(r"Requires (.*)", line)
                    for req in m.group(1).split(","):
                        if "level" in req.lower():
                            m = re.search(r"(\w+) (\d+)", f"{req}")
                            self.level_req = int(m.group(2))
                        elif "class" in req.lower():
                            m = re.search(r"(\w+) (\w+)", f"{req}")
                            self.requires["Class"] = m.group(2)
                        else:
                            m = re.search(r"(\d+) (\w+)", f"{req}")
                            self.requires[m.group(2)] = int(m.group(1))

                        # check for 'Level nnn' or 'nnn Attribute' eg '133 Int'. m.group(2) will always be the number
                        # m = re.search(r"(\w+)? (\d+) (\w+)?", f" {req} ")
                        # if m.group(1) and "level" in m.group(1).lower():
                        #     self.level_req = int(m.group(2))
                        # else:
                        #     self.requires[m.group(3)] = int(m.group(2))
                        # m = re.search(r"level (.*)", req.lower())
                        # if m is None:
                        #     self.requires[req.strip()] = True
                        # else:
                        #     self.level_req = int(m.group(1))
                    lines.pop(line_idx)
                else:
                    # skip this line
                    line_idx += 1
            else:
                lines.pop(line_idx)
                match m.group(1):
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
                    case "Upgrade":
                        self.upgrade = m.group(2)
                    case "Radius":
                        self.radius = m.group(2)
                    case "Talisman Tier":
                        self.talisman_tier = m.group(2)
                    case "Limited to":
                        self.limited_to = m.group(2)
                    case "Variant":
                        self.variant_names.append(m.group(2))
                    case "Prefix":
                        self.crafted_item.setdefault("Prefix", []).append(m.group(2))
                    case "Suffix":
                        self.crafted_item.setdefault("Suffix", []).append(m.group(2))
                    case "Implicits":
                        # implicits, if any
                        for idx in range(int(m.group(2))):
                            if debug_lines:
                                _debug("I", len(lines), lines)
                            line = lines.pop(line_idx)
                            mod = Mod(line)
                            self.full_implicitMods_list.append(mod)
                            # check for variants and if it's our variant, add it to the smaller implicit mod list
                            if "variant" in line:
                                m = re.search(r"{variant:([\d,]+)}(.*)", line)
                                if self.curr_variant in m.group(1).split(","):
                                    self.implicitMods.append(mod)
                            else:
                                self.implicitMods.append(mod)
                        explicits_idx = line_idx
                        break
                    case "Has Alt Variant":
                        self.alt_variants[1] = 0
                    case "Selected Alt Variant":
                        self.alt_variants[1] = int(m.group(2))
                    case "Has Alt Variant Two":
                        self.alt_variants[2] = 0
                    case "Selected Alt Variant Two":
                        self.alt_variants[2] = int(m.group(2))
                    case "Has Alt Variant Three":
                        self.alt_variants[3] = 0
                    case "Selected Alt Variant Three":
                        self.alt_variants[3] = int(m.group(2))
                    case "Has Alt Variant Four":
                        self.alt_variants[4] = 0
                    case "Selected Alt Variant Four":
                        self.alt_variants[4] = int(m.group(2))
                    case "Has Alt Variant Five":
                        self.alt_variants[5] = 0
                    case "Selected Alt Variant Five":
                        self.alt_variants[5] = int(m.group(2))
                self.properties[m.group(1)] = m.group(2)

        if debug_lines:
            _debug("b", len(lines), lines)
        # every thing that is left, from explicits_idx, is explicits, and some other stuff
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
            else:
                self.explicitMods.append(mod)

        if debug_lines:
            _debug("c", len(lines), lines)

        # Anything left must be something like 'Shaper Item', Requires ...
        for line in lines:
            # do something else
            match line:
                case _:
                    print(f"Item().load_from_xml: Skipped: {line} (from {self.name})")

        if debug_lines:
            _debug("end", len(lines), lines)
            print()
        self.tooltip()
        return True
        # load_from_xml

    def load_from_xml_v2(self, xml, default_rarity="oh noes"):
        """
        Fill variables from the version 2 xml

        :param xml: the loaded xml
        :param default_rarity: str: a default rarity. Useful for the uniue and rare templates
        :return: boolean
        """

        def get_variant_value(_xml, entry_name, default_value):
            """

            :param _xml: ElementTree: Part of xml to load entry from
            :param entry_name: str: entry name for variant_entries
            :param default_value: str: a suitable default value for the entry being tested
            :return: str of the entries value or the default value, or the variant value as applicable
            """
            _entry = _xml.get(entry_name, default_value)
            if _entry == "variant":
                # check which value is our variant
                for _line in self.variant_entries[entry_name]:
                    _m = re.search(r"{variant:([\d,]+)}(.*)", _line)
                    if self.curr_variant in _m.group(1).split(","):
                        return _m.group(2)
                # _m = re.search(r"({variant:.*})(.*)", self.variant_entries[entry_name][int(self.curr_variant)])
                # if _m:
                #     print("variant", entry_name, _m.group(2))
                #     return _m.group(2)
            return _entry

        self.title = xml.get("title", "")
        self.rarity = xml.get("rarity", default_rarity)

        # get all the variant information
        self.variant_entries_xml = xml.find("VariantEntries")
        if self.variant_entries_xml is not None:
            for entry in list(self.variant_entries_xml):
                self.variant_entries.setdefault(entry.tag, []).append(entry.text)
        variant_xml = xml.find("Variants")
        if variant_xml is not None:
            for variant in variant_xml.findall("Variant"):
                self.variant_names.append(variant.text)
            self.curr_variant = variant_xml.get("current", f"{len(self.variant_names)}")
            # ensure the uniques load with the latest value
            if self.curr_variant == "0" and self.rarity == "UNIQUE":
                self.curr_variant = f"{len(self.variant_names)}"
            for alt in range(1, 9):
                value = variant_xml.get(f"alt{alt}", "")
                if value != "":
                    self.alt_variants[alt] = int(value)

        """!!!! use get_variant_value() for values that need variants !!!!"""
        self.base_name = get_variant_value(xml, "base_name", "oh noes")
        self.name = f'{self.title and f"{self.title}, " or ""}{self.base_name}'
        # remove any (information)
        m = re.search(r"(.*)(\(.*\))$", self.name)
        if m:
            self.name = m.group(1)

        self.unique_id = xml.get("unique_id", "")
        self.sockets = xml.get("sockets", "")
        self.league = xml.get("league", "")
        self.source = xml.get("source", "")
        self.upgrade = xml.get("upgrade", "")
        self.corrupted = str_to_bool(xml.get("corrupted", "False"))
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
            self.quality = int(attribs.get("quality", "0"))
            self.radius = attribs.get("radius", "")
            self.talisman_tier = int(attribs.get("talisman_tier", "0"))
        # this is for crafted items
        crafted_xml = xml.find("Crafted")
        if crafted_xml is not None:
            self.crafted_item["Prefix"] = []
            for prefix in crafted_xml.findall("Prefix"):
                self.crafted_item["Prefix"].append(prefix.text)
            self.crafted_item["Suffix"] = []
            for suffix in crafted_xml.findall("Suffix"):
                self.crafted_item["Suffix"].append(suffix.text)

        influence_xml = xml.find("Influences")
        if influence_xml is not None:
            for influence in influence_xml.findall("Variant"):
                self.influences.append(influence.text)

        imp = xml.find("Implicits")
        for mod_xml in imp.findall("Mod"):
            line = mod_xml.text
            mod = Mod(mod_xml.text)
            self.full_implicitMods_list.append(mod)
            # check for variants and if it's our variant, add it to the smaller implicit mod list
            if "variant" in line:
                m = re.search(r"{variant:([\d,]+)}(.*)", line)
                if self.curr_variant in m.group(1).split(","):
                    self.implicitMods.append(mod)
            else:
                self.implicitMods.append(mod)
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
            else:
                self.explicitMods.append(mod)

        requires_xml = xml.find("Requires")
        if requires_xml is not None:
            for req in requires_xml:
                self.requires[req.tag] = req.text

        self.tooltip()
        return True
        # load_from_xml_v2

    def save(self):
        """
        Save internal structures back to a xml object. Not used.

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

    # save

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

        def save_variant_entries(_xml, entry_name, value):
            """
            Process all lines for variants, return when complete. NOT USED for implicits and explicits.

            :param _xml: ElementTree: Part of xml to save entry too
            :param entry_name: str: entry name to add to variant_entries
            :param value: str: the string representation of the value to be saved
            :return: The value of the last variant read, with the {variant:x} text
            """
            if self.variant_entries_xml is None:
                self.variant_entries_xml = ET.fromstring("<VariantEntries></VariantEntries>")
            entries = self.variant_entries.get(entry_name, None)
            if entries is None:
                xml.set(entry_name, value)
            else:
                _xml.set(entry_name, "variant")
                for entry in entries:
                    if entry != "":
                        self.variant_entries_xml.append(ET.fromstring(f"<{entry_name}>{entry}</{entry_name}>"))

        xml = ET.fromstring(f'<Item ver="2"></Item>')
        add_attrib_if_not_null(xml, "id", self.id)
        xml.set("title", self.title)
        save_variant_entries(xml, "base_name", self.base_name)

        xml.set("rarity", self.rarity)
        add_attrib_if_not_null(xml, "sockets", self.sockets)
        add_attrib_if_not_null(xml, "corrupted", self.corrupted)
        if self.rarity == "UNIQUE":
            add_attrib_if_not_null(xml, "league", self.league)
            add_attrib_if_not_null(xml, "source", self.source)
            add_attrib_if_not_null(xml, "upgrade", self.upgrade)
        add_attrib_if_not_null(xml, "unique_id", self.unique_id)

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
        add_attrib_if_not_null(attribs, "quality", self.quality)
        add_attrib_if_not_null(attribs, "radius", self.radius)
        add_attrib_if_not_null(attribs, "talisman_tier", self.talisman_tier)
        xml.append(attribs)

        # this is for crafted items
        if self.crafted_item:
            crafted = ET.fromstring(f"<Crafted></Crafted>")
            for line in self.crafted_item["Prefix"]:
                crafted.append(ET.fromstring(f"<Prefix>{line}</Prefix>"))
            for line in self.crafted_item["Suffix"]:
                crafted.append(ET.fromstring(f"<Suffix>{line}</Suffix>"))
            xml.append(crafted)

        if self.influences:
            influences = ET.fromstring(f"<Influences></Influences>")
            for influence in self.influences:
                influences.append(ET.fromstring(f"<Influence>{influence}</Influence>"))
            xml.append(influences)

        # there are always Implicits and Explicits elements, even if they are empty
        imp = ET.fromstring("<Implicits></Implicits>")
        for mod in self.full_implicitMods_list:
            imp.append(ET.fromstring(f"<Mod>{mod.text_for_xml}</Mod>"))
        xml.append(imp)
        exp = ET.fromstring("<Explicits></Explicits>")
        for mod in self.full_explicitMods_list:
            exp.append(ET.fromstring(f"<Mod>{mod.text_for_xml}</Mod>"))
        xml.append(exp)

        # Requires are only present if there are some
        if self.requires:
            requires = ET.fromstring("<Requires></Requires>")
            for req in self.requires.keys():
                requires.append(ET.fromstring(f"<{req}>{self.requires[req]}</{req}>"))
            xml.append(requires)

        if len(self.variant_names) > 0:
            var_xml = ET.fromstring(f"<Variants></Variants>")
            add_attrib_if_not_null(var_xml, "current", self.curr_variant)
            for num, variant in enumerate(self.variant_names, 1):
                # at this point (Nov2022) 'num' isn't used but it makes reading/editing the xml a little easier
                var_xml.append(ET.fromstring(f'<Variant num="{num}">{variant}</Variant>'))
            if len(self.alt_variants) > 1:
                # always write the value, even if it's 0 (that means no choice made)
                for alt in self.alt_variants.keys():
                    var_xml.set(f"alt{alt}", f"{self.alt_variants[alt]}")
            xml.append(var_xml)

        if self.variant_entries_xml:
            xml.append(self.variant_entries_xml)

        return xml

    def tooltip(self, force=False):
        """
        Create a tooltip. Hand crafted html anyone ?

        :param force: Bool. Set to true to force recalculation of TT. EG: Use for when changing variants.
        :return: str: the tooltip
        """
        if not force and self.base_tooltip_text != "":
            return
        rarity_colour = f"{ColourCodes[self.rarity].value};"
        tip = (
            f"<style>"
            f"table, th, td {{border: 1px solid {rarity_colour}; border-collapse: collapse;}}"
            f"td {{text-align: center;}}"
            f"</style>"
            f'<table width="425">'
            f"<tr><th>"
        )
        tip += html_colour_text(rarity_colour, self.name)
        for influence in self.influences:
            tip += f"<br/>{html_colour_text(influence_colours[influence], influence)}"
        tip += "</th></tr>"

        # stats
        stats = ""
        if self.type == "Weapon":
            stats += f"{self.sub_type}<br/>"
        if self.quality != 0:
            stats += f"Quality: {self.quality}%<br/>"
        if self.sockets != "":
            socket_text = ""
            for socket in self.sockets:
                if socket in "RBGAW":
                    socket_text += html_colour_text(ColourCodes[socket].value, socket)
                else:
                    socket_text += socket
            stats += f'Sockets: {socket_text.replace("-", "=")}<br/>'
        if stats:
            tip += f'<tr><td>{stats.rstrip("<br/>")}</td></tr>'

        if self.limited_to != "":
            tip += f"<tr><td>Limited to: <b>{self.limited_to}</b></td></tr>"
        reqs = ""
        if self.requires:
            print(self.title, self.level_req)
            if self.level_req > 0:
                reqs += f"Level <b>{self.level_req}</b>"
            for req in self.requires:
                val = self.requires[req]
                match req:
                    case "Int" | "Dex" | "Str":
                        reqs += f', <b>{html_colour_text(req, f"{val}")} {req}</b>'
                    case "Class":
                        reqs += f", <b>Class {html_colour_text(val.upper(), val)}</b>"
                    case _:
                        reqs += f", <b>{req}</b>"
        else:
            print(self.title, self.level_req)
            if self.level_req > 0:
                reqs += f"Level <b>{self.level_req}</b>"
        if reqs:
            tip += f'<tr><td>Requires {reqs.lstrip(", ")}</td></tr>'
        if len(self.implicitMods) > 0:
            mods = ""
            for mod in self.implicitMods:
                mods += mod.tooltip
            tip += f'<tr><td>{mods.rstrip("<br/>")}</td></tr>'
        if len(self.explicitMods) > 0:
            mods = ""
            for mod in self.explicitMods:
                if not mod.corrupted:
                    mods += mod.tooltip
            tip += f'<tr><td>{mods.rstrip("<br/>")}</td></tr>'

        if self.corrupted:
            tip += f'<tr><td>{html_colour_text("STRENGTH", "Corrupted")}</td></tr>'
        tip += f"</table>"
        # self.base_tooltip_text = tip
        return tip

    @property
    def base_name(self):
        return self._base_name

    @base_name.setter
    def base_name(self, new_name):
        self._base_name = new_name
        # remove any (information)
        m = re.search(r"(.*)( \(.*\))$", new_name)
        if m:
            new_name = m.group(1)
        # Look up base_items to get the item type
        self.base_item = self.base_items.get(new_name, None)
        if self.base_item is not None:
            self.type = self.base_item["type"]
            self.sub_type = self.base_item["sub-type"]
            self.two_hand = "twohand" in self.base_item["tags"]
            # check for any extra requires. Just attributes for now.
            reqs = self.base_item.get("requirements", None)
            if reqs:
                for tag in reqs:
                    match tag:
                        case "Dex" | "Int" | "Str":
                            val = reqs.get(tag, None)
                            # don't overwrite a current value
                            if self.requires.get(tag, None) is None and val is not None and val != 0:
                                self.requires[tag] = val
        elif "Flask" in new_name:
            self.type = "Flask"
            self.sub_type = "Flask"

        match self.type:
            case "Shield":
                self.slots = ["Weapon 2", "Weapon 2 Swap"]
            case "Weapon":
                if self.two_hand:
                    self.slots = ["Weapon 1", "Weapon 1 Swap"]
                else:
                    # Put primary weapons before alt weapons for auto filling of item slots
                    self.slots = ["Weapon 1", "Weapon 2", "Weapon 1 Swap", "Weapon 2 Swap"]
            case "Ring":
                self.slots = ["Ring 1", "Ring 2"]
            case "Flask":
                self.slots = ["Flask 1", "Flask 2", "Flask 3", "Flask 4", "Flask 5"]
            case _:
                self.slots = [self.type]

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, new_type):
        """
        Fill slot list based on type

        :param new_type:
        :return:
        """
        self._type = new_type
        # Fill slot list

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
