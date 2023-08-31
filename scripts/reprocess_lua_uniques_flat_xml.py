import sys

sys.path.insert(1, "../src/")

import xml.etree.ElementTree as ET

from PoB.item import Item
from PoB.settings import Settings
from PoB.pob_file import read_xml, write_xml, read_json


_settings = Settings(None, None)
base_items = read_json("../src/data/base_items.json")

# Some items have a smaller number of variants than the actaul variant lists. Whilst these need to be fixed, this will get around it.
max_variants = {"Precursor's Emblem": "7"}

uniques = {}
u_xml = read_xml("uniques_flat.xml")
for item_type in list(u_xml.getroot()):
    # print(item_type.tag)
    uniques[item_type.tag] = []
    for _item in item_type.findall("Item"):
        new_item = Item(_settings, base_items)
        new_item.load_from_xml(_item)
        new_item.rarity = "UNIQUE"
        if new_item.base_name == "Unset Ring" and new_item.sockets == "":
            new_item.sockets = "W"
        uniques[item_type.tag].append(new_item)

new_xml = ET.ElementTree(ET.fromstring("<?xml version='1.0' encoding='utf-8'?><Uniques></Uniques>"))
new_root = new_xml.getroot()
for child_tag in uniques:
    # print(child_tag)
    child_xml = ET.fromstring(f"<{child_tag} />")
    item_type = uniques[child_tag]
    for item in item_type:
        # we don't want to add extra work for when we are manually updating uniques.xml
        item.curr_variant = ""
        if item.title in max_variants.keys():
            item.max_variant = max_variants[item.title]
        item_xml = item.save_v2()
        item_xml.attrib.pop("rarity", None)
        child_xml.append(item_xml)
    new_root.append(child_xml)
write_xml("../src/data/uniques.xml.new", new_xml)

# templates = []
# t_xml = read_xml("rare_templates_flat.xml"))
# _xml_root = t_xml.getroot()
# for xml_item in t_xml.getroot().findall("Item"):
#     new_item = Item(base_items)
#     new_item.load_from_xml(xml_item)
#     new_item.rarity = "RARE"
#     templates.append(new_item)
# new_xml = ET.ElementTree(ET.fromstring("<?xml version='1.0' encoding='utf-8'?><RareTemplates></RareTemplates>"))
# new_root = new_xml.getroot()
# for item in templates:
#     item_xml = item.save_v2()
#     item_xml.attrib.pop("rarity", None)
#     new_root.append(item_xml)
# write_xml("../src/data/rare_templates.xml.new", new_xml)
