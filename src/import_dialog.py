"""
Import dialog

Open a dialog for importing a character.
"""
import re

import requests
import pprint
from qdarktheme.qtpy.QtWidgets import QDialog

from dlg_Import import Ui_Dialog
from pob_config import *
import pob_file
from build import Build

realm_list = {
    "PC": {
        "realmCode": "pc",
        "hostName": "https://www.pathofexile.com/",
        "profileURL": "account/view-profile/",
    },
    "Xbox": {
        "realmCode": "xbox",
        "hostName": "https://www.pathofexile.com/",
        "profileURL": "account/xbox/view-profile/",
    },
    "PS4": {
        "realmCode": "sony",
        "hostName": "https://www.pathofexile.com/",
        "profileURL": "account/sony/view-profile/",
    },
    "Garena": {
        "realmCode": "pc",
        "hostName": "https://web.poe.garena.tw/",
        "profileURL": "account/view-profile/",
    },
    "Tencent": {
        "realmCode": "pc",
        "hostName": "https://poe.game.qq.com/",
        "profileURL": "account/view-profile/",
    },
}


class ImportDlg(Ui_Dialog, QDialog):
    """Import dialog."""

    def __init__(self, _build: Build, _config: Config, parent=None):
        super().__init__(parent)
        self.build = _build
        self.config = _config
        # A temporary variable to hold the account list of characters.
        # Needs to be sharable so trigger functions can access it
        self.account_json = None

        """ when a character has been chosen to download, this will hold the itmes and passive tree data"""
        self.character_data = None
        """ when buid sharing is used, then the result will be an xml string"""
        self.xml = None

        self.setupUi(self)
        self.fill_character_history()
        self.grpbox_CharImport.setVisible(False)

        self.btn_Close.clicked.connect(self.close_dialog)
        self.btn_StartImport.clicked.connect(self.download_character_information)
        self.btn_ImportAll.clicked.connect(self.import_all)
        self.btn_ImportBuildSharing.clicked.connect(self.import_from_code)
        self.lineedit_Account.returnPressed.connect(self.download_character_information)
        self.lineedit_BuildShare.textChanged.connect(self.validate_build_sharing_text)
        self.comboChar_History.currentTextChanged.connect(self.change_account_name)
        self.combo_League.currentTextChanged.connect(self.change_league_name)

    @Slot()
    def close_dialog(self):
        self.done(0)

    @Slot()
    def validate_build_sharing_text(self):
        self.btn_ImportBuildSharing.setEnabled(False)
        text = self.lineedit_BuildShare.text().strip()
        if text == "":
            return
        # Attempt to break up the text in lineedit control into a meaningful url.
        # get the website and the code as separate 'group' variables
        #   (1) is the website and (2) is the code (not used here)
        m = re.search(r'http[s]?://(.*)/(.*)$', text)
        if (m is not None and m.group(1) in valid_websites) or decode_base64_and_inflate(text) is not None:
            self.btn_ImportBuildSharing.setEnabled(True)

    @Slot()
    def import_from_code(self, text):
        """Import the whole character's data"""
        print("import_from_code")
        text = self.lineedit_BuildShare.text().strip()
        if text == "":
            return
        # Attempt to break up the text in lineedit control into a meaningful url.
        # get the website and the code as separate 'group' variables
        #   (1) is the website and (2) is the code
        m = re.search(r'http[s]?://(.*)/(.*)$', text)
        if m is not None and m.group(1) in valid_websites:
            # if the text was a meaninful url and it was a supported url, let's get the code
            try:
                url = website_list[m.group(1)]["downloadURL"].replace("CODE", m.group(2))
                response = requests.get(url, headers=http_headers, timeout=6.0)
                code = decode_base64_and_inflate(response.content)
                print("import_from_code", code)
            except requests.RequestException as e:
                print(f"Error retrieving data: {e}.")
                return
        else:
            # check the code is valid
            code = decode_base64_and_inflate(text)

        if code is not None:
            # code is an xml string
            # tree = ET.ElementTree(ET.fromstring(code))
            # print_a_xml_element(tree.getroot())
            self.xml = ET.ElementTree(ET.fromstring(code))

    @Slot()
    def import_all(self, text):
        """Import the whole character's data from PoE web site"""
        print("import_all")
        # download the data if one of the other buttons hasn't done it yet.
        if self.character_data is None:
            self.download_character_data()

    @Slot()
    def change_account_name(self, text):
        """Set Account lineedit based on comboChar_History"""
        self.lineedit_Account.setText(text)

    @Slot()
    def change_league_name(self, text):
        """
        Fill the combo_CharList with character names based on league
        :param text: current text of the league comboBox. "" will occur on .clear()
        :return: N/A
        """
        if self.account_json is None:
            return
        self.character_data = None
        self.combo_CharList.clear()
        if text == "All" or text == "":
            self.combo_CharList.addItems([char["name"] for char in self.account_json])
        else:
            # ToDo: is there a list comprehension way of doing this or is this the best way ?
            for char in self.account_json:
                if char["league"] == text:
                    self.combo_CharList.addItem(char["name"])

    @Slot()
    def download_character_information(self):
        """
        React to the 'Start' button by getting a list of characters and setting.
        :return: N/A
        """
        account_name = self.lineedit_Account.text()
        try:
            realm_code = realm_list.get(self.combo_Realm.currentText(), "pc")
            url = f"{realm_code['hostName']}character-window/get-characters"
            params = {"accountName": account_name, "realm": realm_code}
            response = requests.get(url, params=params, headers=http_headers, timeout=6.0)
            self.account_json = response.json()
            # self.account_json = pob_file.read_json("c:/Users/peter/Downloads/get-characters-xyllywyt.json")
        except requests.RequestException as e:
            print(f"Error retrieving account: {e}.")
            return
        if self.account_json:
            # add this account to account history
            self.config.last_account_name = account_name
            self.config.add_account(account_name)

            # turn on controls and fill them
            self.grpbox_CharImport.setVisible(True)
            self.combo_League.clear()
            self.combo_League.addItem("All")
            self.combo_League.addItems(unique_sorted([char["league"] for char in self.account_json]))

    def download_character_data(self):
        """
        Given the account and character is chosen, download the data and decode
        Do not load into build. Let the button procedures do their thing.
        Called by the button procedures
        """
        self.character_data = None
        account_name = self.lineedit_Account.text()
        char_name = self.combo_CharList.currentText()
        realm_code = realm_list.get(self.combo_Realm.currentText(), "pc")
        params = {"accountName": account_name, "character": char_name, "realm": realm_code}

        # get passive tree
        passive_tree = None
        try:
            url = f"{realm_code['hostName']}character-window/get-passive-skills"
            response = requests.get(url, params=params, headers=http_headers, timeout=6.0)
            passive_tree = response.json()
            # passive_tree = {'hashes': [487, 1203, 1325, 2913, 4378, 5152, 5197, 5233, 6289, 6446, 6580, 7162, 7285, 9695, 10143, 12247, 13009, 14056, 15405, 17201, 17735, 18025, 19711, 20010, 20551, 21435, 22285, 22356, 24083, 24914, 25011, 25933, 26523, 26866, 29547, 29933, 31471, 33287, 33740, 34031, 34400, 35859, 37800, 39725, 40653, 41472, 42009, 42293, 42800, 44429, 44606, 44908, 45696, 46910, 48287, 48438, 48807, 49109, 49254, 49806, 50288, 50862, 53118, 53793, 54340, 55485, 55649, 55676, 56001, 56359, 58449, 61198, 61262, 61471, 62017, 62817, 63649, 64587, 65034], 'hashes_ex': [], 'mastery_effects': ['4079782931', '3928020036', '4219298227'], 'items': [], 'jewel_data': {}}
            print(type(passive_tree))
        except requests.RequestException as e:
            print(f"Error retrieving account: {e}.")
            print(vars(response))

        # get items
        items = None
        try:
            url = f"{realm_code['hostName']}character-window/get-items"
            response = requests.get(url, params=params, headers=http_headers, timeout=6.0)
            items = response.json()
            print(type(items))
        except requests.RequestException as e:
            print(f"Error retrieving account: {e}.")
            print(vars(response))
        # items =

        # pprint.pprint(passive_tree)
        # pprint.pprint(items)
        self.character_data = {"tree": passive_tree, "items":  items}

    def fill_character_history(self):
        self.comboChar_History.clear()
        self.comboChar_History.addItems(self.config.accounts())
        self.comboChar_History.setCurrentText(self.config.last_account_name)
        self.lineedit_Account.setText(self.config.last_account_name)
