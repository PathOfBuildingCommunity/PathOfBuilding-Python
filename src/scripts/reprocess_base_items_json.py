"""
Reprocess base_items.json into a smaller file with only relevant items
base_items.json and mods.json come from https://github.com/brather1ng/RePoE/tree/master/RePoE/data
    and are not included in the git repo

"""
from pathlib import Path
import xml.etree.ElementTree as ET
import json

wanted_item_classes = (
    "AbyssJewel",
    "Amulet",
    "Belt",
    "Body Armour",
    "Boots",
    "Bow",
    "Claw",
    "Dagger",
    "Gloves",
    "Helmet",
    "HybridFlask",
    "Jewel",
    "LifeFlask",
    "ManaFlask",
    "One Hand Axe",
    "One Hand Mace",
    "One Hand Sword",
    "Quiver",
    "Ring",
    "Rune Dagger",
    "Sceptre",
    "Shield",
    "Staff",
    "Thrusting One Hand Sword",
    "Two Hand Axe",
    "Two Hand Mace",
    "Two Hand Sword",
    "UtilityFlask",
    "Wand",
    "Warstaff",
)
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
        base_items[name] = item
    # process implicits ?

write_json("../Data/base_items.json", base_items)
