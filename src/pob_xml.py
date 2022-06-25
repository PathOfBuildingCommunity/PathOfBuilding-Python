"""
Functions for reading and writing xml

"""

import os
import xmltodict


def read_xml(filename):
    file_ptr = None
    ordered_dict = None
    if os.path.exists(filename):
        try:
            file_ptr = open(filename, "r")
            xml_content = file_ptr.read()
            ordered_dict = xmltodict.parse(xml_content)
        except:
            print("Unable to open file %s" % filename)
        finally:
            file_ptr.close()
    return ordered_dict


def write_xml(filename, ordered_dict):
    file_ptr = None
    try:
        file_ptr = open(filename, "w")
        xml_content = xmltodict.unparse(ordered_dict, pretty=True)
        file_ptr.write(xml_content)
    except:
        print("Unable to write file %s" % filename)
    finally:
        file_ptr.close()
