"""
Import dialog

Open a dialog for importing a character.
"""

import urllib3

from qdarktheme.qtpy.QtWidgets import QDialog

from dlg_BuildExport import Ui_BuildExport
from pob_config import Config
from build import Build


class ExportDlg(Ui_BuildExport, QDialog):
    """Export dialog"""

    def __init__(self, _build: Build, _config: Config, parent=None):
        super().__init__(parent)
        self.build = _build
        self.config = _config
        self.http = urllib3.PoolManager()

        self.setupUi(self)
