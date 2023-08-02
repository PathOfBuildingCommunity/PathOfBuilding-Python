import xml.etree.ElementTree as ET
from pathlib import Path
import sys, re

sys.path.insert(1, "../")

from item import Item
from pob_file import read_xml, write_xml, read_json

base_items = read_json("../data/base_items.json")

templates = []
t_xml = read_xml("rare_templates_flat.xml")
_xml_root = t_xml.getroot()
for xml_item in t_xml.getroot().findall("Item"):
    new_item = Item(base_items)
    new_item.load_from_xml(xml_item)
    new_item.rarity = "RARE"
    templates.append(new_item)
new_xml = ET.ElementTree(ET.fromstring("<?xml version='1.0' encoding='utf-8'?><RareTemplates></RareTemplates>"))
new_root = new_xml.getroot()
for item in templates:
    # we don't want to add extra work for when we are manually updating uniques.xml
    item_xml = item.save_v2()
    item_xml.attrib.pop("rarity", None)
    new_root.append(item_xml)
write_xml("../data/rare_templates.xml.new", new_xml)
