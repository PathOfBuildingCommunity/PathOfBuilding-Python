"""
File Dialog

Open a dialog for Opening or Saving a character.
"""

import glob, os, re

from qdarktheme.qtpy.QtWidgets import QDialog, QListWidgetItem, QWidget
from qdarktheme.qtpy.QtCore import Qt, Slot

from build import Build
from constants import ColourCodes
from dialogs.popup_dialogs import yes_no_dialog
from pob_config import Config
from pob_file import read_xml_as_dict
from ui.dlgBrowseFile import Ui_BrowseFile
from widgets.ui_utils import html_colour_text


class BrowseFileDlg(Ui_BrowseFile, QDialog):
    """File dialog"""

    def __init__(self, _build: Build, _config: Config, task, parent=None):
        super().__init__(parent)
        self.build = _build
        self.config = _config
        self.selected_file = ""
        self.triggers_connected = False
        self.Save = task == "Save"
        self.Open = task == "Open"

        # UI Commands below this one
        self.setupUi(self)
        self.setWindowTitle(f"{self.windowTitle()} - {task}")

        self.btnClose.clicked.connect(self.close)
        self.btnOpenSave.clicked.connect(self.file_chosen)
        self.list_Files.itemClicked.connect(self.list_file_clicked)

        self.btnOpenSave.setText(f"&{task}")
        for idx in range(0, self.hLayout_SaveAs.count()):
            self.hLayout_SaveAs.itemAt(idx).widget().setHidden(self.Open)

        self.list_Files.set_delegate()
        self.list_Files_width = self.list_Files.width()
        self.max_filename_width = 100

        self.change_dir(self.config.build_path)  # connects triggers

    # Overridden function
    def resizeEvent(self, event):
        """
        Work out how many chanracters can fit in the listbox. One character is 7.3 pixels (ish)
        Width of the four spaces plus the "Level nnn Elementalist (vn)" is 31
        :param event:
        :return: N/A
        """
        self.list_Files_width = self.list_Files.width()
        self.max_filename_width = int(self.list_Files_width / 7.3) - 31
        # forcibly refill the list box by calling the only function with trigger controls
        self.change_dir(self.lineEdit_CurrDir.text())
        QDialog.resizeEvent(self, event)

    def connect_triggers(self):
        if self.triggers_connected:
            return
        self.list_Files.itemDoubleClicked.connect(self.list_file_double_clicked)
        self.lineEdit_CurrDir.textChanged.connect(self.current_dir_changed)
        self.lineEdit_CurrDir.editingFinished.connect(self.editing_finished)
        self.triggers_connected = True

    def disconnect_triggers(self):
        if not self.triggers_connected:
            return
        self.list_Files.itemDoubleClicked.disconnect(self.list_file_double_clicked)
        self.lineEdit_CurrDir.textChanged.disconnect(self.current_dir_changed)
        self.lineEdit_CurrDir.editingFinished.disconnect(self.editing_finished)
        self.triggers_connected = False

    def get_file_info(self, filename, max_length):
        """
        Open the xml and get the class information, level and version. Format a line for display on the listbox.
        Take into account the maximum width of the listbox and trim names as needed.

        :param filename: name of file in current directory
        :param max_length: int: of the longest name
        :return: str, str: "", "" if invalid xml, or colourized name and class name
        """
        xml_file = read_xml_as_dict(filename)
        xml_build = xml_file.get("PathOfBuilding", {}).get("Build", {})
        if xml_build != {}:
            name = os.path.splitext(filename)[0]
            # Get the maximum length of a name, trimming it ifneed be
            name = len(name) > self.max_filename_width and (name[: self.max_filename_width] + "..") or name
            # Create a spacer string of the correct length to right justify the class info
            spacer = (min(max_length, self.max_filename_width) - len(name) + 4) * " "

            # The information on the right
            version = xml_build.get("@version", "1")
            level = xml_build.get("@level", "1")
            class_name = xml_build.get("@className", "1")
            ascend_class_name = xml_build.get("@ascendClassName", "None")
            _class = ascend_class_name == "None" and class_name or ascend_class_name
            text = f" Level {level} {_class} (v{version})"

            colour = ColourCodes[class_name.upper()].value
            normal = ColourCodes["NORMAL"].value
            return (
                f'<pre style="color:{normal};">{name}{spacer}<span style="color:{colour};">{text}</span></pre>',
                class_name,
            )
        else:
            return "", ""

    def fill_list_box(self, this_dir):
        """

        :param this_dir:
        :return:
        """
        self.list_Files.clear()
        self.lineEdit_CurrDir.setText(this_dir)
        dirs = [name for name in os.listdir(this_dir) if os.path.isdir(os.path.join(this_dir, name))]
        # add in parent directory if we aren't at the top, ie: C:\ or /
        if os.path.dirname(os.getcwd()) != "/":
            self.add_path_to_listbox("..", "..", "", True)
        for name in dirs:
            self.add_path_to_listbox(f"{name}", f"{name}", "", True)

        # name = self.get_file_info("_test.xml2")
        # self.add_path_to_listbox(name, False)
        # self.label.setText(name)
        files_grabbed = glob.glob("*.xml") + glob.glob("*.xml2")
        # Don't use listBox's sort method as it puts the directories at the bottom
        files_grabbed.sort()
        # find longest name
        max_length = max([len(s) for s in files_grabbed])
        for filename in files_grabbed:
            text, class_name = self.get_file_info(filename, max_length)
            if text != "":
                self.add_path_to_listbox(filename, text, class_name, False)

    def add_path_to_listbox(self, filename, _text, class_name, is_dir):
        """

        :param filename: name of file in current directory
        :param _text: The name of the file, class name and verions (with colours).
        :param class_name: The class name (for tooltip colour).
        :param is_dir: True if a directory
        :return: QListWidgetItem: the item added.
        """
        if is_dir:
            lwi = QListWidgetItem(html_colour_text("NORMAL", f"[{_text}]"))
            # If _name is .., then add the parent directory, else the subdirectory
            path = _text == ".." and os.pardir or _text
            _path = os.path.abspath(os.path.join(self.lineEdit_CurrDir.text(), path))
            lwi.setToolTip(os.path.basename(_path))
        else:
            lwi = QListWidgetItem(_text)
            _path = os.path.abspath(os.path.join(self.lineEdit_CurrDir.text(), filename))
            lwi.setToolTip(f"<nobr>{html_colour_text(class_name, filename)}</nobr>")
        lwi.setWhatsThis(_path)
        self.list_Files.addItem(lwi)
        return lwi

    @Slot()
    def file_chosen(self):
        path = self.list_Files.currentItem().whatsThis()
        save_name = self.lineEdit_SaveAs.text()
        if self.Save:
            if save_name == "":
                return
            else:
                extension = os.path.splitext(save_name)[1]
                if extension == "":
                    extension = self.rBtn_v2.isChecked() and "xml2" or "xml"
                    save_name = f"{save_name}.{extension}"
                if os.path.exists(save_name):
                    if not yes_no_dialog(self, "Overwrite file", f"{save_name} exists. Overwrite"):
                        return
                self.selected_file = os.path.join(self.lineEdit_CurrDir.text(),save_name)
                print("file_chosen", self.selected_file)
        else:
            print("file_chosen", path)
            if "[" in self.list_Files.currentItem().text():  # is_dir
                self.change_dir(path)
            else:
                self.selected_file = path
        self.accept()

    @Slot()
    def current_dir_changed(self, new_dir):
        # print(f"current_dir_changed {new_dir}")
        self.change_dir(new_dir)

    def change_dir(self, new_dir):
        # print(f"change_dir {new_dir}")
        self.disconnect_triggers()
        if os.path.exists(new_dir):
            os.chdir(new_dir)
            self.lineEdit_CurrDir.setText(new_dir)
            self.fill_list_box(new_dir)
        self.list_Files.setFocus()
        self.connect_triggers()

    def editing_finished(self):
        # print("editing_finished", self.lineEdit_CurrDir.text())
        # forcibly refill the list box by calling the only function with trigger controls
        self.change_dir(self.lineEdit_CurrDir.text())

    @Slot()
    def list_file_clicked(self, item: QListWidgetItem):
        # print("list_file_clicked")
        if "[" in item.text():  # is_dir
            return
        else:
            self.lineEdit_SaveAs.setText(re.sub('<[^<]+?>', '', item.toolTip()))

    @Slot()
    def list_file_double_clicked(self, item: QListWidgetItem):
        # print("list_file_double_clicked")
        if "[" in item.text():  # is_dir
            self.change_dir(item.whatsThis())
        else:
            # do something interesting, like return with the information
            self.file_chosen()
