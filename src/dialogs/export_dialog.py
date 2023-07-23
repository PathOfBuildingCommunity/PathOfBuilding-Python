"""
Import dialog

Open a dialog for importing a character.
"""

import urllib3, re, requests
import xml.etree.ElementTree as ET
import pyperclip

from qdarktheme.qtpy.QtWidgets import QDialog
from qdarktheme.qtpy.QtCore import Qt, Slot, QTimer

from views.dlgBuildExport import Ui_BuildExport
from pob_config import Config, decode_base64_and_inflate, deflate_and_base64_encode, print_a_xml_element, unique_sorted
from build import Build
from constants import get_http_headers, post_http_headers, website_list
from ui_utils import html_colour_text, set_combo_index_by_text


class ExportDlg(Ui_BuildExport, QDialog):
    """Export dialog"""

    def __init__(self, _build: Build, _config: Config, parent=None):
        super().__init__(parent)
        self.build = _build
        self.config = _config
        self.http = urllib3.PoolManager()
        self.build_as_astring = ET.tostring(self.build.root, encoding="utf8")
        self.code = deflate_and_base64_encode(self.build_as_astring).decode("utf8")

        # UI Commands below this one
        self.setupUi(self)
        self.lineEdit_Code.setText(self.code)
        self.groupBox_PasteBin.setHidden(True)
        for site in website_list.keys():
            if website_list[site].get("postUrl", "P0B") != "P0B":
                self.combo_ShareSite.addItem(site)

        self.lineEdit_DevKey.setText(self.config.pastebin_dev_api_key)
        self.lineEdit_UserKey.setText(self.config.pastebin_user_api_key)

        self.btn_Copy.clicked.connect(self.copy_button)
        self.btn_Share.clicked.connect(self.share_button)
        self.combo_ShareSite.currentTextChanged.connect(self.share_site_changed)
        self.lineEdit_DevKey.textChanged.connect(self.update_DevKey)
        self.lineEdit_UserKey.textChanged.connect(self.update_UserKey)
        # self.combo_ShareSite.setCurrentText("pastebin.com")

        QTimer.singleShot(50, self.on_show)  # waits for this to finish until gui displayed

    @property
    def status(self):
        """status label text. Needed so we can have a setter"""
        return self.label_Status.text()

    @status.setter
    def status(self, text):
        """Add to the status label"""
        self.label_Status.setText(text)

    @Slot()
    def on_show(self):
        """Actions for when the window is shown"""
        self.lineEdit_Code.selectAll()
        self.lineEdit_Code.setFocus()

    @Slot()
    def share_site_changed(self, _text):
        self.groupBox_PasteBin.setHidden(_text != "pastebin.com")

    @Slot()
    def copy_button(self):
        pyperclip.copy(self.lineEdit_Code.text())

    def share_button(self):
        response = None
        try:
            website = self.combo_ShareSite.currentText()
            website_info = website_list[website]
            url = website_info["postUrl"]
            params = website_info.get("postFields","").replace("CODE", self.code)
            print("url", url)
            print("params", params)

            match website:
                case "pastebin.com":
                    # Ref: https://pastebin.com/asRbutde
                    data = self.get_pastebin_data(website_info, "Path of Building - Python")
                    response = requests.post(url, headers=get_http_headers, timeout=12.0, data=data)
                case "pobb.in":
                    response = requests.post(url, headers=get_http_headers, timeout=12.0, data=self.code)
                case "poe.ninja":
                    response = requests.post(url, params=params, headers=get_http_headers, timeout=6.0)

            # print the response text (the content of the requested file):
            print("response.text", response.text)
            print("response", response)
            print(f"response, {response.reason} ({response.status_code}).")
            if response.status_code == 200:
                code_url = website_info.get("codeOut","")
                self.lineEdit_Code.setText(f"{code_url}{response.text}")
                self.on_show()
            else:
                self.status = html_colour_text(
                    "RED", f"Error retrieving 'Data': {response.reason} ({response.status_code})."
                )
        except requests.RequestException as e:
            self.status = html_colour_text(
                "RED", f"Error retrieving 'Data': {response.reason} ({response.status_code})."
            )
            print(f"Error retrieving 'Data': {e}.")
            return

    def get_pastebin_data(self, site_info, title):
        """Get properly formed data for PasteBin"""
        api_dev_key = self.lineEdit_DevKey.text()
        api_dev_key = api_dev_key == "" and site_info["api_dev_key"]
        api_user_key = self.lineEdit_DevKey.text()
        return {
            "api_option": "paste",
            "api_dev_key": api_dev_key,
            "api_paste_code": self.code,
            "api_paste_name": title,
            "api_paste_expire_date": "1Y",
            "api_user_key": api_user_key,
            "api_paste_format": "python",
        }

    @Slot()
    def share_site_changed(self, _text):
        self.groupBox_PasteBin.setHidden(_text != "pastebin.com")

    @Slot()
    def update_DevKey(self, _text):
        """Update config"""
        self.config.pastebin_dev_api_key = self.lineEdit_DevKey.text()

    @Slot()
    def update_UserKey(self, _text):
        """Update config"""
        self.config.pastebin_user_api_key = self.lineEdit_UserKey.text()
