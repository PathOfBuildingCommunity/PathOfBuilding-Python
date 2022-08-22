"""
Import dialog

Open a dialog for importing a character.
"""

import urllib3
from qdarktheme.qtpy.QtWidgets import QDialog

from dlg_Import import Ui_Dialog
from pob_config import *
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
        self.http = urllib3.PoolManager()

        self.setupUi(self)
        self.comboChar_History.clear()
        self.comboChar_History.addItems(self.config.accounts())
        self.comboChar_History.setCurrentText(self.config.last_account_name)
        self.lineedit_Account.setText(self.config.last_account_name)

        self.btn_Close.clicked.connect(self.close_dialog)
        self.btn_StartImport.clicked.connect(self.start_import)
        self.lineedit_Account.returnPressed.connect(self.start_import)
        self.comboChar_History.currentTextChanged.connect(self.change_account_name)

    @Slot()
    def close_dialog(self):
        print("close_dialog")
        self.done(0)

    @Slot()
    def change_account_name(self, text):
        self.lineedit_Account.setText(text)

    @Slot()
    def start_import(self):
        print("start_import")
        realm = realm_list.get(self.combo_Realm.currentText(), "pc")
        account = self.lineedit_Account.text()
        print(account)
        url = f"{realm['hostName']}character-window/get-characters?accountName={account}&realm={realm['realmCode']}"
        response = self.http.request('GET', url, headers=http_headers)
        print(response.status, vars(response))
        print(response.data.decode('utf-8'))
        return_json=response.data.decode('utf-8')
        print(type(return_json))
