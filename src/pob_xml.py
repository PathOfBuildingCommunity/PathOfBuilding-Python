"""
Functions for reading and writing xml

"""

import os
import xmltodict


# checkout
# using with statement
# with open('file_path', 'w') as file:
# 	file.write('hello world !')
# ensures proper file closure if an exception occurs


def read_xml(filename):
    file_ptr = None
    ordered_dict = None
    if os.path.exists(filename):
        try:
            file_ptr = open(filename, "r")
            xml_content = file_ptr.read()
            ordered_dict = xmltodict.parse(xml_content)
        # except:
        #     print("Unable to open file %s" % filename)
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
