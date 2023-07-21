"""
Import dialog

Open a dialog for importing a character.
"""
import json, re, requests
from hashlib import sha1
import xml.etree.ElementTree as ET
from pprint import pprint

from qdarktheme.qtpy.QtWidgets import QDialog
from qdarktheme.qtpy.QtCore import Qt, Slot

from views.dlgBuildImport import Ui_BuildImport
from constants import valid_websites, website_list, http_headers
from pob_config import (
    Config,
    decode_base64_and_inflate,
    deflate_and_base64_encode,
    unique_sorted,
)
from pob_file import write_json
from build import Build
from ui_utils import html_colour_text, set_combo_index_by_text

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

        :param _build: A pointer to the currently loaded build
        :param _config: A pointer to the settings
        :param _skills_ui: pointer to the ItemsUI() class for item saving
        :param parent: A pointer to MainWindowUI
        """
        super().__init__(parent)
        self.build = _build
        self.config = _config
        self.win = parent
        # validation variable for importing a PoB build
        self.pob_base64_encoded = False
        # validation variable for importing a PoB build via url (type is the result of a re.search)
        self.pob_valid_url = None
        # validation variable for importing a poeplanner json
        self.poep_json_import = False

        # A temporary variable to hold the account list of characters.
        # Needs to be sharable so trigger functions can access it
        self.account_json = None

        """ when a character has been chosen to download, this will hold the items and passive tree data"""
        self.character_data = None
        """ when build sharing is used, then the result will be an xml string"""
        self.xml = None

        self.setupUi(self)
        self.fill_character_history()
        if self.build.last_account_hash:
            acct_hash = self.build.last_account_hash
            for idx in range(self.combo_Account_History.count()):
                if acct_hash == sha1(self.combo_Account_History.itemText(idx).encode("utf-8")).hexdigest():
                    self.combo_Account_History.setCurrentIndex(idx)
                    self.lineedit_Account.setText(self.combo_Account_History.currentText())
                    break

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
        self.combo_Account_History.currentTextChanged.connect(self.change_account_name)
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

    def test_import_text_for_poeplanner_json(self, text):
        """
        Validate that this text is from poeplanner.com. json import must have at least these components (see below)
        :param text: str: text to test
        :return: boolean; True if test passes.
        """
        bad_text = "P 0 B"
        try:
            text_json = json.loads(text)
            return (
                int(text_json.get("version", "0")) > 0
                and text_json.get("calculatedStats", bad_text) != bad_text
                and text_json.get("equipment", bad_text) != bad_text
                and text_json.get("helpedBandit", bad_text) != bad_text
                and text_json.get("skills", bad_text) != bad_text
                and text_json.get("tree", bad_text) != bad_text
            )
        except (KeyError, json.decoder.JSONDecodeError):
            return False

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
        self.test_import_text_for_poeplanner_json(text)
        # Test for various formats
        self.pob_base64_encoded = decode_base64_and_inflate(text) is not None
        self.poep_json_import = self.test_import_text_for_poeplanner_json(text)
        # get the website and the code as separate 'group' variables
        #   (1) is the website and (2) is the code (not used here)
        self.pob_valid_url = re.search(r"http[s]?://([a-z0-9.\-]+)/(.*)", text)
        if (
            (self.pob_valid_url is not None and self.pob_valid_url.group(1) in valid_websites)
            or self.pob_base64_encoded
            or self.poep_json_import
        ):
            self.btn_ImportBuildSharing.setEnabled(True)
        else:
            self.pob_base64_encoded = False
            self.poep_json_import = False
            self.pob_valid_url = None

    @Slot()
    def import_from_code(self, text):
        """
        Import the whole character's data
        Attempt to break up the text in lineedit control into a meaningful url to see if it's a url
        that we support *OR* if it's a validate import code *OR* that is is a valid json from poeplanner.com
        Close dialog if successful
        :return: N/A
        """
        text = self.lineedit_BuildShare.text().strip()
        if text == "":
            return
        if self.combo_Import.currentData() == "NEW":
            self.win.build_new()

        # Test for various formats
        # self.pob_valid_url is set in validate_build_sharing_text
        if self.pob_valid_url is not None:
            # if the text was a meaninful url and it was a supported url, let's get the code
            response = None
            try:
                website = self.pob_valid_url.group(1)
                url_code = self.pob_valid_url.group(2)
                url = website_list[website]["downloadURL"].replace("CODE", url_code)
                response = requests.get(url, headers=http_headers, timeout=6.0)
                code = decode_base64_and_inflate(response.content)
            except requests.RequestException as e:
                self.status = html_colour_text(
                    "RED", f"Error retrieving 'Data': {response.reason} ({response.status_code})."
                )
                print(f"Error retrieving 'Data': {e}.")
                return
        elif self.pob_base64_encoded:
            # decode the string and return a possibly valid code.
            code = decode_base64_and_inflate(text)
        elif self.poep_json_import:
            # import the json for better or worse. No errors. Just do it.
            self.import_all_from_poep_json(json.loads(text))
            self.done(0)
            return
        else:
            # If we can't get a resolution, return with a standard error.
            code = None

        if code is None:
            self.status = html_colour_text("RED", f"Code failed to decode.")
            print(f"Code failed to decode.")
            return
        else:
            self.xml = ET.ElementTree(ET.fromstring(code))
            self.done(0)

    def import_all_from_poep_json(self, poep_json):
        """

        :param poep_json: json object:
        :return:
        import doesn't have socket, corruption, influence info.
        import doesn't have separate craft info. It is linked in with explicits.
        import doesn't have unique names for Magic and normal items. This makes it difficult for the system to
            assign the correct slot
        """
        # self.import_passive_tree_jewels_selected()
        self.win.items_ui.load_from_poep_json(
            poep_json["equipment"],
            "Imported from poeplanner",
            True,
        )
        # self.import_skills_selected()

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
        self.build.import_passive_tree_jewels_ggg_json(
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
        self.win.items_ui.load_from_ggg_json(
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
        skillset = self.build.import_gems_ggg_json(self.character_data.get("items"))
        self.win.skills_ui.load(self.build.skills)
        self.win.combo_SkillSet.setCurrentIndex(skillset - 1)
        self.btn_Close.setFocus()

    @Slot()
    def change_account_name(self, text):
        """Set Account lineedit based on combo_Account_History"""
        self.config.last_account_name = text
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

        def find_matching_standard_league(league):
            """
            :param: str: non standard league name, but function will still work if a Standard league name is used.
            :return: str
            """
            # Find a Standard league name for a given league name
            # Reference https://api.pathofexile.com/league?realm=pc
            if "Hardcore" in league:
                return "Hardcore"
            elif "HC SSF" in league:
                # includes Ruthless "HC SSF R "
                return "SSF Hardcore"
            elif "SSF" in league:
                # Any non HardCore SSF's - includes Ruthless "SSF R "
                return "SSF Standard"
            else:
                # normal league and ruthless league (Sanctum, Ruthless Sanctum)
                return "Standard"

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
            self.status = html_colour_text(
                "RED", f"Error retrieving 'Account': {response.reason} ({response.status_code})."
            )
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
            # Try to find the league that this character was imported from, if available
            # combo_League's trigger will fill out combo_CharList
            if self.build.last_league:
                set_combo_index_by_text(self.combo_League, self.build.last_league)
                if self.combo_League.currentText() != self.build.last_league:
                    # Current league may not exist any more, try move to the equivalent standard league
                    standard_league = find_matching_standard_league(self.build.last_league)
                    set_combo_index_by_text(self.combo_League, standard_league)
                    if self.combo_League.currentText() != standard_league:
                        # Give up and select the first
                        self.combo_League.setCurrentIndex(0)
                    else:
                        self.build.last_league = self.combo_League.currentText()
            if self.build.last_character_hash:
                char_hash = self.build.last_character_hash
                for idx in range(self.combo_CharList.count()):
                    if char_hash == sha1(self.combo_CharList.itemText(idx).encode("utf-8")).hexdigest():
                        self.combo_CharList.setCurrentIndex(idx)
                        break
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
        self.build.last_character_hash = sha1(char_name.encode("utf-8")).hexdigest()
        self.build.last_account_hash = sha1(account_name.encode("utf-8")).hexdigest()
        self.build.last_league = self.combo_League.currentText()
        self.build.last_realm = self.combo_Realm.currentText()

        realm_code = realm_list.get(self.combo_Realm.currentText(), "pc")
        params = {
            "accountName": account_name,
            "character": char_name,
            "realm": realm_code,
        }

        # get passive tree
        passive_tree = None
        response = None
        try:
            url = f"{realm_code['hostName']}character-window/get-passive-skills"
            response = requests.get(url, params=params, headers=http_headers, timeout=6.0)
            passive_tree = response.json()
        except requests.RequestException as e:
            print(f"Error retrieving 'Passive Tree': {e}.")
            self.status = html_colour_text(
                "RED", f"Error retrieving 'Passive Tree': {response.reason} ({response.status_code})."
            )
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
            self.status = html_colour_text(
                "RED", f"Error retrieving 'Items': {response.reason} ({response.status_code})."
            )
            print(vars(response))

        # lets add the jewels and items together
        for idx, jewel in enumerate(passive_tree.get("items", [])):
            items["items"].insert(idx, jewel)
        char_info = items.get("character", None)
        self.character_data = {
            "tree": passive_tree,
            "items": items,
            "character": char_info,
        }
        # pprint(passive_tree)
        # write_json("builds/" + char_name + "_items.json", items)

    def fill_character_history(self):
        self.combo_Account_History.clear()
        self.combo_Account_History.addItems(self.config.accounts())
        set_combo_index_by_text(self.combo_Account_History, self.config.last_account_name)
        self.lineedit_Account.setText(self.config.last_account_name)
