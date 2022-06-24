import xmltodict, os


def readXML(filename):
    filePtr = None
    orderedDict = None
    if os.path.exists(filename):
        try:
            filePtr = open(filename, "r")
            xml_content = filePtr.read()
            orderedDict = xmltodict.parse(xml_content)
        except:
            print("Unable to open file %s" % filename)
        finally:
            filePtr.close()
    return orderedDict


def writeXML(filename, orderedDict):
    filePtr = None
    try:
        filePtr = open(filename, "w")
        xml_content = xmltodict.unparse(orderedDict, pretty=True)
        filePtr.write(xml_content)
    except:
        print("Unable to write file %s" % filename)
    finally:
        filePtr.close()
