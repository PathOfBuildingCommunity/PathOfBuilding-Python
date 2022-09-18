    """
    A class to encapsulate one item
    """

class Item:

    def __init__(self, _slot=None) -> None:
        """
        Initialise defaults
        :param _slot: where this item is worn/carried.
        """
        self._slot = _slot

        # this is not always available from the json character download
        self.level_req = 0

        self.rarity = "NORMAL"
        self.title = ""
        self.name = ""
        self.base_name = ""
        self.ilevel = 0
        self.quality = 0
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
        self.limits = 0
        self.implicitMods = []
        self.explicitMods = []
        self.full_explicitMods_list = []
        self.craftedMods = []
        self.enchantMods = []

    def load_from_xml(self, desc, debug_lines=False):
        """
        Load internal structures from the build object's xml

        :param desc: The lines of the item
        :param debug_lines: Temporary to debug the process
        :return: N/A
        """
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
            if m is not None:
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
                    case "LevelReq":
                        self.level_req = int(m.group(2))
                    case "Limited to":
                        self.limits = int(m.group(2))
                    case "Implicits":
                        # implicits, if any
                        for idx in range(int(m.group(2))):
                            line = lines.pop(line_idx)
                            self.implicitMods.append(Mod(line))
                        explicits_idx = line_idx
                        break
                self.properties[m.group(1)] = m.group(2)
            else:
                # skip this line
                line_idx += 1
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
                for var in m.group(1).split(","):
                    if var == self.curr_variant:
                        self.explicitMods.append(mod)
            else:
                self.explicitMods.append(mod)

        if debug_lines:
            _debug("b", len(lines), lines)
        # 'normal' and Magic ? objects and flasks only have one line (either no title or no base name)
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

    def save(self, _id, debug_print=False):
        """
        Save internal structures back to a xml object

        :param:   debug_print: bool, temporary whilst items are being developed
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
        print(self.properties)
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

        if debug_print:
            print(f"{text}\n\n")
        return ET.fromstring(f'<Item id="{_id}">{text}</Item>')

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
            tip += f'<br/>{html_colour_text(influence_colours[influence], influence)}'
        tip += "</th></tr>"
        if self.level_req > 0:
            tip += f"<tr><td>Requires Level <b>{self.level_req}</b></td></tr>"
        if self.limits > 0:
            tip += f"<tr><td>Limited to: <b>{self.limits}</b></td></tr>"
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
