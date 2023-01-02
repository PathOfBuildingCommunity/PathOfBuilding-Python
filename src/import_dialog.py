"""
Import dialog

Open a dialog for importing a character.
"""
import re
import requests
import xml.etree.ElementTree as ET
from pprint import pprint

from qdarktheme.qtpy.QtWidgets import QDialog
from qdarktheme.qtpy.QtCore import Qt, Slot

from dlg_BuildImport import Ui_BuildImport
from constants import valid_websites, website_list, http_headers
from pob_config import Config, decode_base64_and_inflate, deflate_and_base64_encode, unique_sorted
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


class ImportDlg(Ui_BuildImport, QDialog):
    """Import dialog"""

    def __init__(self, _build: Build, _config: Config, parent):
        """

        :param _build: A pointer of the build
        :param _config: A pointer to the settings
        :param _skills_ui: pointer to the ItemsUI() class for item saving
        :param parent: A pointer to MainWindowUI
        """
        super().__init__(parent)
        self.build = _build
        self.config = _config
        self.win = parent

        # A temporary variable to hold the account list of characters.
        # Needs to be sharable so trigger functions can access it
        self.account_json = None

        """ when a character has been chosen to download, this will hold the items and passive tree data"""
        self.character_data = None
        """ when build sharing is used, then the result will be an xml string"""
        self.xml = None

        self.setupUi(self)
        self.fill_character_history()

        self.combo_Import.setItemData(0, "THIS")
        self.combo_Import.setItemData(1, "NEW")

        self.btn_Close.clicked.connect(self.close_dialog)
        self.btn_StartImport.clicked.connect(self.download_character_information)
        self.btn_ImportAll.clicked.connect(self.import_all_selected)
        self.btn_TreeJewels.clicked.connect(self.import_passive_tree_jewels_selected)
        self.btn_Items.clicked.connect(self.import_items_selected)
        self.btn_Skills.clicked.connect(self.import_skills_selected)
        self.btn_ImportBuildSharing.clicked.connect(self.import_from_code)
        self.lineedit_Account.returnPressed.connect(self.download_character_information)
        self.lineedit_BuildShare.textChanged.connect(self.validate_build_sharing_text)
        self.comboAccount_History.currentTextChanged.connect(self.change_account_name)
        self.combo_League.currentTextChanged.connect(self.change_league_name)
        self.combo_Import.currentTextChanged.connect(self.change_import_selection_data)
        self.lineedit_BuildShare.setFocus()

    @property
    def status(self):
        """status label text. Needed so we can have a setter"""
        return self.label_Status.text()

    @status.setter
    def status(self, text):
        """Add to the status label"""
        self.label_Status.setText(text)

    @Slot()
    def close_dialog(self):
        self.done(0)

    @Slot()
    def validate_build_sharing_text(self):
        """
        Attempt to break up the text in lineedit control into a meaningful url to see if it's a url
        that we support *OR* if it's a valid import code. Turn on the import button if needed.
        :return: N/A
        """
        self.btn_ImportBuildSharing.setEnabled(False)
        text = self.lineedit_BuildShare.text().strip()
        if text == "":
            return
        # get the website and the code as separate 'group' variables
        #   (1) is the website and (2) is the code (not used here)
        m = re.search(r"http[s]?://([a-z0-9.\-]+)/(.*)", text)
        if (m is not None and m.group(1) in valid_websites) or decode_base64_and_inflate(text) is not None:
            self.btn_ImportBuildSharing.setEnabled(True)

    @Slot()
    def import_from_code(self, text):
        """
        Import the whole character's data
        Attempt to break up the text in lineedit control into a meaningful url to see if it's a url
        that we support *OR* if it's a validate import code.
        Close dialog if successful
        :return: N/A
        """
        text = self.lineedit_BuildShare.text().strip()
        if text == "":
            return
        if self.combo_Import.currentData() == "NEW":
            self.win.build_new()
        # Attempt to break up the text in lineedit control into a meaningful url.
        # get the website and the code as separate 'group' variables
        #   (1) is the website and (2) is the code
        m = re.search(r"http[s]?://([a-z0-9.\-]+)/(.*)", text)
        if m is not None and m.group(1) in valid_websites:
            # if the text was a meaninful url and it was a supported url, let's get the code
            response = None
            try:
                url = website_list[m.group(1)]["downloadURL"].replace("CODE", m.group(2))
                response = requests.get(url, headers=http_headers, timeout=6.0)
                code = decode_base64_and_inflate(response.content)
            except requests.RequestException as e:
                self.status = f"Error retrieving 'Data': {response.reason} ({response.status_code})."
                print(f"Error retrieving 'Data': {e}.")
                return
        else:
            # check the code is valid
            code = decode_base64_and_inflate(text)

        if code is None:
            self.status = f"Code failed to decode."
            print(f"Code failed to decode.")
            return
        else:
            self.xml = ET.ElementTree(ET.fromstring(code))
            self.done(0)

    @Slot()
    def import_all_selected(self):
        """Import the whole character's data from PoE web site"""
        # print("import_all_selected")
        self.import_passive_tree_jewels_selected()
        self.import_items_selected()
        self.import_skills_selected()

    @Slot()
    def import_passive_tree_jewels_selected(self):
        """Import the character's data from PoE web site"""
        # print("import_passive_tree_jewels_selected")
        # download the data if one of the other buttons hasn't done it yet.
        if self.character_data is None:
            self.download_character_data()
        if self.check_DeleteJewels.isChecked():
            # ToDo: Do something clever to remove jewels
            pass
        self.build.import_passive_tree_jewels_json(
            self.character_data.get("tree"), self.character_data.get("character")
        )
        self.btn_Close.setFocus()

    @Slot()
    def import_items_selected(self):
        """Import the character's items from PoE web site"""
        # print("import_items_selected")
        # download the data if one of the other buttons hasn't done it yet.
        if self.character_data is None:
            self.download_character_data()
        json_character = self.character_data.get("character")
        # A lot of technology is built into the ItemsUI() class, lets reuse that
        self.win.items_ui.load_from_json(
            self.character_data["items"],
            f'Imported {json_character.get("name", "")}',
            self.check_DeleteItems.isChecked(),
        )
        # force everything back to xml format
        self.win.items_ui.save()
        self.btn_Close.setFocus()

    @Slot()
    def import_skills_selected(self):
        """Import the character's skills from PoE web site"""
        # print("import_skills_selected")
        # download the data if one of the other buttons hasn't done it yet.
        if self.character_data is None:
            self.download_character_data()
        if self.check_DeleteSkills.isChecked():
            # ToDo: Do something clever to remove skills. Later when you have Manage Skill Sets dialog working
            pass
        skillset = self.build.import_gems_json(self.character_data.get("items"))
        self.win.skills_ui.load(self.build.skills)
        self.win.combo_SkillSet.setCurrentIndex(skillset - 1)
        self.btn_Close.setFocus()

    @Slot()
    def change_account_name(self, text):
        """Set Account lineedit based on comboAccount_History"""
        self.lineedit_Account.setText(text)
        self.character_data = None

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
    def change_import_selection_data(self, text):
        """
        React to the user changing the combo_Import.

        :param text: str: Not used
        :return:
        """
        match self.combo_Import.currentData():
            case "NEW":
                self.check_DeleteJewels.setEnabled(False)
                self.check_DeleteItems.setEnabled(False)
                self.check_DeleteSkills.setEnabled(False)
            case "THIS":
                self.check_DeleteJewels.setEnabled(True)
                self.check_DeleteItems.setEnabled(True)
                self.check_DeleteSkills.setEnabled(True)

    @Slot()
    def download_character_information(self):
        """
        React to the 'Start' button by getting a list of characters and settings (not data).

        :return: N/A
        """
        account_name = self.lineedit_Account.text()
        self.grpbox_CharImport.setEnabled(True)
        response = None
        try:
            realm_code = realm_list.get(self.combo_Realm.currentText(), "pc")
            url = f"{realm_code['hostName']}character-window/get-characters"
            params = {"accountName": account_name, "realm": realm_code}
            response = requests.get(url, params=params, headers=http_headers, timeout=6.0)
            self.account_json = response.json()
        except requests.RequestException as e:
            self.status = f"Error retrieving 'Account': {response.reason} ({response.status_code})."
            print(f"Error retrieving 'Account': {e}.")
            print(vars(response))
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
            self.combo_League.setFocus()

    def download_character_data(self):
        """
        Given the account and character is chosen, download the data and decode
        Do not load into build. Let the button procedures do their thing.
        Called by the button procedures
        """
        if self.combo_Import.currentData() == "NEW":
            self.win.build_new()
        self.character_data = None
        account_name = self.lineedit_Account.text()
        char_name = self.combo_CharList.currentText()
        realm_code = realm_list.get(self.combo_Realm.currentText(), "pc")
        params = {"accountName": account_name, "character": char_name, "realm": realm_code}

        # get passive tree
        passive_tree = None
        response = None
        try:
            url = f"{realm_code['hostName']}character-window/get-passive-skills"
            response = requests.get(url, params=params, headers=http_headers, timeout=6.0)
            passive_tree = response.json()
        except requests.RequestException as e:
            print(f"Error retrieving 'Passive Tree': {e}.")
            self.status = f"Error retrieving 'Passive Tree': {response.reason} ({response.status_code})."
            print(vars(response))

        # get items
        items = None
        response = None
        try:
            url = f"{realm_code['hostName']}character-window/get-items"
            response = requests.get(url, params=params, headers=http_headers, timeout=6.0)
            items = response.json()
        except requests.RequestException as e:
            print(f"Error retrieving 'Items': {e}.")
            self.status = f"Error retrieving 'Items': {response.reason} ({response.status_code})."
            print(vars(response))

        # lets add the jewels and items together
        for idx, jewel in enumerate(passive_tree.get("items", [])):
            items["items"].insert(idx, jewel)
        char_info = items.get("character", None)
        self.character_data = {"tree": passive_tree, "items": items, "character": char_info}
        # pprint(passive_tree)

    def fill_character_history(self):
        self.comboAccount_History.clear()
        self.comboAccount_History.addItems(self.config.accounts())
        self.comboAccount_History.setCurrentText(self.config.last_account_name)
        self.lineedit_Account.setText(self.config.last_account_name)
