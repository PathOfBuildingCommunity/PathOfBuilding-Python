"""
Reprocess base_items.json into a smaller file with only relevant items
base_items.json and mods.json come from https://github.com/brather1ng/RePoE/tree/master/RePoE/data
    and are not included in the git repo

"""
from pathlib import Path
import json

socket_numbers = {
    "AbyssJewel": 0,
    "Amulet": 0,
    "Belt": 0,
    "Body Armour": 6,
    "Boots": 4,
    "Bow": 6,
    "Claw": 3,
    "Dagger": 3,
    "Gloves": 4,
    "Helmet": 4,
    "HybridFlask": 0,
    "Jewel": 0,
    "LifeFlask": 0,
    "ManaFlask": 0,
    "One Hand Axe": 3,
    "One Hand Mace": 3,
    "One Hand Sword": 3,
    "Quiver": 0,
    "Ring": 0,
    "Rune Dagger": 3,
    "Sceptre": 3,
    "Shield": 3,
    "Staff": 6,
    "Thrusting One Hand Sword": 3,
    "Two Hand Axe": 6,
    "Two Hand Mace": 6,
    "Two Hand Sword": 6,
    "UtilityFlask": 0,
    "Wand": 3,
    "Warstaff": 6,
}
wanted_item_classes = socket_numbers.keys()

weapon_classes = (
    "Bow",
    "Claw",
    "Dagger",
    "One Hand Axe",
    "One Hand Mace",
    "One Hand Sword",
    "Rune Dagger",
    "Sceptre",
    "Staff",
    "Thrusting One Hand Sword",
    "Two Hand Axe",
    "Two Hand Mace",
    "Two Hand Sword",
    "Wand",
    "Warstaff",
)


def read_json(filename):
    """
    Reads a json file
    :param filename: Name of xml to be read
    :returns: A dictionary of the contents of the file
    """
    _fn = Path(filename)
    if _fn.exists():
        try:
            with _fn.open("r") as json_file:
                _dict = json.load(json_file)
                return _dict
        except EnvironmentError:  # parent of IOError, OSError *and* WindowsError where available
            print(f"Unable to open {_fn}")
    return None


def write_json(filename, _dict):
    """
    Write a json file
    :param filename: Name of json to be written
    :param _dict: New contents of the file
    :returns: N/A
    """
    _fn = Path(filename)
    try:
        with _fn.open("w") as json_file:
            json.dump(_dict, json_file, indent=4)
    except EnvironmentError:  # parent of IOError, OSError *and* WindowsError where available
        print(f"Unable to write to {_fn}")


# The dictionary we will build
base_items = {}
# The dictionary of the incoming json
base_items_json = read_json("base_items.json")

for item_id in base_items_json:
    item = base_items_json[item_id]
    item_class = item["item_class"]
    name = item["name"]
    if item_class not in wanted_item_classes:
        continue
    if item["release_state"] in ("released", "unique_only"):
        for tag in ["inventory_height", "inventory_width", "visual_identity", "release_state", "name", "item_class"]:
            del item[tag]
        item["sub-type"] = item_class
        if item_class in weapon_classes:
            item["type"] = "Weapon"
        elif "Flask" in item_class:
            item["type"] = "Flask"
        else:
            item["type"] = item_class

        # create an initial set of socket colours, as no socket can be blank
        socket_number = socket_numbers[item["sub-type"]]
        if socket_number != 0:
            item["max_num_sockets"] = socket_number
            reqs = {}
            for tag in ("dexterity", "intelligence", "strength"):
                val = item.get("requirements", {})[tag]
                if val != 0:
                    new_tag = tag.replace("dexterity", "G").replace("intelligence", "B").replace("strength", "R")
                    reqs[new_tag] = item["requirements"][tag]
            if reqs:
                initial_sockets = ""
                l_r = len(reqs)
                tags = list(reqs.keys())
                for idx in range(socket_number):
                    initial_sockets += f"{tags[idx % l_r]}-"
                if initial_sockets:
                    item["initial_sockets"] = initial_sockets.rstrip("-")

        # Rename Attributes
        reqs = item["requirements"]
        if reqs:
            new_reqs = {}
            for tag in reqs:
                match tag:
                    case "dexterity":
                        new_reqs["Dex"] = reqs[tag]
                    case "intelligence":
                        new_reqs["Int"] = reqs[tag]
                    case "strength":
                        new_reqs["Str"] = reqs[tag]
                    case _:
                        new_reqs[tag] = reqs[tag]
            item["requirements"] = new_reqs
            # print(name, new_reqs)
        base_items[name] = item
    # process implicits ?

write_json("../Data/base_items.json", base_items)
