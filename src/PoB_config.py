import sys, os
import PoB_xml

# Default config incase the settings file doesn't exist
_config = {'PathOfBuilding': {'Misc': {'@theme': 'light', '@slotOnlyTooltips': 'true', '@showTitlebarName': 'true', '@showWarnings': 'true', '@defaultCharLevel': '1', '@nodePowerTheme': 'RED/BLUE', '@connectionProtocol': 'nil', '@thousandsSeparator': ',', '@betaTest': 'false', '@decimalSeparator': '.', '@defaultGemQuality': '0', '@showThousandsSeparators': 'true', '@buildSortMode': 'NAME'}}}
exeDir = os.path.dirname(os.path.abspath(sys.argv[0]))
buildPath = os.path.join(exeDir, "builds")
if not os.path.exists(buildPath):
    os.makedirs(buildPath)

# colorCodes = {
# 	NORMAL = "^xC8C8C8",
# 	MAGIC = "^x8888FF",
# 	RARE = "^xFFFF77",
# 	UNIQUE = "^xAF6025",
# 	RELIC = "^x60C060",
# 	GEM = "^x1AA29B",
# 	PROPHECY = "^xB54BFF",
# 	CURRENCY = "^xAA9E82",
# 	CRAFTED = "^xB8DAF1",
# 	CUSTOM = "^x5CF0BB",
# 	SOURCE = "^x88FFFF",
# 	UNSUPPORTED = "^xF05050",
# 	WARNING = "^xFF9922",
# 	TIP = "^x80A080",
# 	FIRE = "^xB97123",
# 	COLD = "^x3F6DB3",
# 	LIGHTNING = "^xADAA47",
# 	CHAOS = "^xD02090",
# 	POSITIVE = "^x33FF77",
# 	NEGATIVE = "^xDD0022",
# 	OFFENCE = "^xE07030",
# 	DEFENCE = "^x8080E0",
# 	SCION = "^xFFF0F0",
# 	MARAUDER = "^xE05030",
# 	RANGER = "^x70FF70",
# 	WITCH = "^x7070FF",
# 	DUELIST = "^xE0E070",
# 	TEMPLAR = "^xC040FF",
# 	SHADOW = "^x30C0D0",
# 	MAINHAND = "^x50FF50",
# 	MAINHANDBG = "^x071907",
# 	OFFHAND = "^xB7B7FF",
# 	OFFHANDBG = "^x070719",
# 	SHAPER = "^x55BBFF",
# 	ELDER = "^xAA77CC",
# 	FRACTURED = "^xA29160",
# 	ADJUDICATOR = "^xE9F831",
# 	BASILISK = "^x00CB3A",
# 	CRUSADER = "^x2946FC",
# 	EYRIE = "^xAAB7B8",
# 	CLEANSING = "^xF24141",
# 	TANGLE = "^x038C8C",
# 	CHILLBG = "^x151e26",
# 	FREEZEBG = "^x0c262b",
# 	SHOCKBG = "^x191732",
# 	SCORCHBG = "^x270b00",
# 	BRITTLEBG = "^x00122b",
# 	SAPBG = "^x261500",
# 	SCOURGE = "^xFF6E25",
# }
# colorCodes.STRENGTH = colorCodes.MARAUDER
# colorCodes.DEXTERITY = colorCodes.RANGER
# colorCodes.INTELLIGENCE = colorCodes.WITCH
#
# colorCodes.LIFE = colorCodes.MARAUDER
# colorCodes.MANA = colorCodes.WITCH
# colorCodes.ES = colorCodes.SOURCE
# colorCodes.WARD = colorCodes.RARE
# colorCodes.EVASION = colorCodes.POSITIVE
# colorCodes.RAGE = colorCodes.WARNING
# colorCodes.PHYS = colorCodes.NORMAL

def readConfig():
    global _config
    settingsFile = os.path.join(exeDir, "settings.xml")
    if os.path.exists(settingsFile):
        cfg = PoB_xml.readXML(settingsFile)

def writeConfig():
    global _config
    PoB_xml.writeXML(os.path.join(exeDir, "settings.xml"), _config)
