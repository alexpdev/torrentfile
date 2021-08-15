import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFileDialog,
                             QHBoxLayout, QLabel, QLineEdit, QSpacerItem,
                             QMainWindow, QMenu, QMenuBar, QPlainTextEdit,
                             QPushButton, QToolButton, QWidget, QFormLayout,
                             QStatusBar)

from torrentfile.metafile import TorrentFile
from torrentfile.utils import Bendecoder, path_stat

"""
Graphical Extension for Users who prefer a GUI over CLI.
"""

class Window(QMainWindow):
    """
    Window MainWindow of GUI extension interface.

    Subclass:
        QMainWindow (QWidget): PyQt6 QMainWindow
    """

    labelRole = QFormLayout.ItemRole.LabelRole
    fieldRole = QFormLayout.ItemRole.FieldRole
    spanRole = QFormLayout.ItemRole.SpanningRole

    stylesheet = """QMainWindow {
        background-color: #525252;
        }"""

    def __init__(self, parent=None, app=None):
        """
        __init__ Constructor for Window class.

        Args:
            parent (QWidget, optional): The current Widget's parent. Defaults to None.
            app (QApplication, optional): Controls the GUI application. Defaults to None.
        """
        super().__init__(parent=parent)
        self.app = app
        self.menubar = MenuBar(parent=self)
        self.statusbar = QStatusBar(parent=self)
        self.central = QWidget(parent=self)
        self.icon = QIcon("./assets/torrent-icon.png")
        self.setObjectName("Mainwindow")
        self.setWindowTitle("Torrentfile Tools")
        self.setWindowIcon(self.icon)
        self.setMenuBar(self.menubar)
        self.setStatusBar(self.statusbar)
        self.setCentralWidget(self.central)
        self.setStyleSheet(self.stylesheet)
        self._setupUI()

    def _setupUI(self):
        """
        _setupUI Internal function for setting up UI elements.
        """
        self.resize(450, 450)
        self.formLayout = QFormLayout(self.central)
        self.central.setLayout(self.formLayout)

        self.hlayout1 = QHBoxLayout()
        self.hlayout2 = QHBoxLayout()
        self.path_label = Label("Path", parent=self)
        self.path_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.path_input = LineEdit(parent=self)
        self.path_input.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.browse_button = BrowseButton(parent=self)
        self.hlayout1.addWidget(self.path_input)
        self.hlayout1.addWidget(self.browse_button)
        self.formLayout.setWidget(0, self.labelRole, self.path_label)
        self.formLayout.setLayout(0, self.fieldRole, self.hlayout1)

        self.created_by_label = Label("Created By:", parent=self)
        self.created_by_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.created_by_input = LineEdit(parent=self)
        self.created_by_input.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.formLayout.setWidget(1, self.labelRole, self.created_by_label)
        self.formLayout.setWidget(1, self.fieldRole, self.created_by_input)

        self.source_label = Label("Source:", parent=self)
        self.source_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.source_input = LineEdit(parent=self)
        self.source_input.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.formLayout.setWidget(2, self.labelRole, self.source_label)
        self.formLayout.setWidget(2, self.fieldRole, self.source_input)

        self.comment_label = Label("Comment:", parent=self)
        self.comment_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.comment_input = LineEdit(parent=self)
        self.comment_input.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.formLayout.setWidget(3, self.labelRole, self.comment_label)
        self.formLayout.setWidget(3, self.fieldRole, self.comment_input)

        self.announce_label = Label("Trackers:", parent=self)
        self.announce_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.announce_input = TextEdit(parent=self)
        self.formLayout.setWidget(4, self.labelRole, self.announce_label)
        self.formLayout.setWidget(4, self.fieldRole, self.announce_input)

        self.piece_length_label = Label("Piece Length:", parent=self)
        self.piece_length_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.piece_length = ComboBox(parent=self)
        self.private = QCheckBox("Private Tracker",parent=self)
        self.private.setStyleSheet("QCheckBox {color: #e1e7f6; font-size: 11pt;}")
        self.spacer = QSpacerItem(50,0)
        self.hlayout2.addWidget(self.piece_length)
        self.hlayout2.addItem(self.spacer)
        self.hlayout2.addWidget(self.private)
        self.formLayout.setWidget(5, self.labelRole, self.piece_length_label)
        self.formLayout.setLayout(5, self.fieldRole, self.hlayout2)

        self.submit_button = SubmitButton("Create Torrent", parent=self)
        self.formLayout.setWidget(6, self.spanRole, self.submit_button)

        self.hlayout1.setObjectName(u"hlayout1")
        self.formLayout.setObjectName(u"formLayout")
        self.hlayout2.setObjectName("hlayout2")
        self.submit_button.setObjectName("submit_button")
        self.private.setObjectName("private")
        self.path_label.setObjectName("path_label")
        self.path_input.setObjectName("path_input")
        self.piece_length.setObjectName("piece_length")
        self.piece_length_label.setObjectName("piece_length_label")
        self.source_label.setObjectName("source_label")
        self.source_input.setObjectName("source_input")
        self.announce_input.setObjectName("announce_input")
        self.announce_label.setObjectName("announce_label")
        self.comment_input.setObjectName("comment_input")
        self.comment_label.setObjectName("comment_label")
        self.created_by_label.setObjectName("created_by_label")
        self.created_by_input.setObjectName("created_by_input")
        self.browse_button.setObjectName("browse_button")
        self.statusbar.setObjectName(u"statusbar")

    def apply_settings(self, result):
        """
        apply_settings Activated by MenuBar action to import from external file.

        Args:
            result (dict): Data retreived from external file.
        """
        d = result[0]
        info = d["info"]
        trackers = d["announce"]
        piece_length = info["piece length"]
        self.announce_input.appendPlainText(trackers)

        if "source" in info:
            source = info["source"]
            self.source_input.insert(source)

        if "comment" in info:
            comment = info["comment"]
            self.comment_input.insert(comment)

        if "created by" in info:
            created_by = info["created by"]
            self.created_by_input.insert(created_by)

        if "private" in info:
            if info["private"]:
                self.private.setChecked()

        val_kb = str(int(piece_length) // 1024)
        val_mb = str(int(piece_length) // (1024 ** 2))

        for i in range(self.piece_length.count()):
            if val_kb in self.piece_length.itemText(i):
                self.piece_length.setCurrentIndex(i)
                break
            elif val_mb in self.piece_length.itemText(i):
                self.piece_length.setCurrentIndex(i)
                break
        return


class BrowseButton(QToolButton):
    """
    BrowseButton ToolButton for activating filebrowser.

    Subclass:
        QToolButton : PyQt6 Button Widget
    """

    stylesheet = """
        QPushButton {
            border-color: #F80;
            border-width: 1px;
            border-style: solid;
            color: #000;
            padding: 4px;
            background-color: #ddd;
        }
        QPushButton::hover{
            background-color: #ced;
        }"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        """
        __init__ public constructor for BrowseButton Class.
        """
        self.setText("...")
        self.window = parent
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pressed.connect(self.browse)

    def browse(self):
        """
        browse Action performed when user presses button.

        Opens File/Folder Dialog.

        Returns:
            str: Path to file or folder to include in torrent.
        """
        caption = "Choose File or Root Folder"
        path = QFileDialog.getExistingDirectory(parent=self.window, caption=caption)
        self.window.path_input.insert(str(path))
        _, size, piece_length = path_stat(path)

        if piece_length < (2**20):
            val = f"{piece_length//(2**10)}KB"

        else:
            val = f"{piece_length//(2**20)}MB"

        for i in range(self.window.piece_length.count()):
            if self.window.piece_length.itemText(i) == val:
                self.window.piece_length.setCurrentIndex(i)
                break
        return size


class SubmitButton(QPushButton):
    """
    SubmitButton Button to signal finished setup options.

    Subclass:
        QPushButton
    """

    stylesheet = """
        QPushButton {
            border-width: 4px;
            border-style: outset;
            border-top-color: #999999;
            border-left-color: #999999;
            border-right-color: #707070;
            border-bottom-color: #707070;
            border-bottom-width: 2px;
            border-radius: 8px;
            padding: 3px;
            margin: 3px;
            color: #fff;
            background-color: #575757;
        }
        QPushButton::hover{
            border-top-color: #b4b4b4;
            border-left-color: #929292;
            border-right-color: #7f7f7f;
            border-bottom-color: #737373;
            background-color: #8d8d8d;
            color: #fff;
        }"""

    def __init__(self, text, parent=None):
        """
        __init__ Public Constructor for Submit Button.

        Args:
            text (str): Text displayed on the button itself.
            parent (QWidget, optional): This Widget's parent. Defaults to None.
        """
        super().__init__(text, parent=parent)
        self._text = text
        self.window = parent
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setText(text)
        self.setStyleSheet(self.stylesheet)
        self.pressed.connect(self.submit)

    def submit(self):
        """
        submit Action performed when user presses Submit Button.
        """
        window = self.window
        # Gather Information from other Widgets.
        path = window.path_input.text()
        private = 1 if window.private.isChecked() else 0
        source = window.source_input.text()
        # at least 1 tracker input is required
        announce = window.announce_input.toPlainText()
        announce = announce.split("\n")
        # Calculates piece length if not specified by user.
        created_by = window.created_by_input.text()
        piece_length = window.piece_length.currentText()

        val, denom = piece_length.split(" ")

        if denom == "KB":
            val = int(val) * 1024

        elif denom == "MB":
            val = int(val) * (1024 ** 2)

        comment = window.comment_input.text()

        torrentfile = TorrentFile(
            path=path,
            private=private,
            source=source,
            announce=announce,
            created_by=created_by,
            piece_length=val,
            comment=comment,
        )
        torrentfile.assemble()
        try:
            save_dir = os.getenv("HOME")
        except:
            save_dir = os.getenv("USERPROFILE")
        save_file = os.path.join(save_dir, os.path.basename(path) + ".torrent")
        save_location = QFileDialog.getSaveFileName(
            parent=window, caption="Save Location", directory=save_file
        )
        torrentfile.write(save_location)
        print("success")


class Label(QLabel):
    """
    Label Identifier for Window Widgets.

    Subclass:
        QLabel
    """

    stylesheet = """QLabel {
        color: #fff;
        padding: 3px;
    }"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent=parent)
        self.setStyleSheet(self.stylesheet)
        font = self.font()
        font.setBold(True)
        font.setPointSize(12)
        self.setFont(font)


class LineEdit(QLineEdit):

    stylesheet = """QLineEdit {
        border-color: #3a3a3a;
        border-width: 1px;
        border-radius: 4px;
        border-style: inset;
        padding: 0 8px;
        color: #fff;
        background: #646464;
        selection-background-color: #bbbbbb;
        selection-color: #3c3f41;
    }"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._parent = parent
        self.setStyleSheet(self.stylesheet)


class TextEdit(QPlainTextEdit):

    stylesheet = """QPlainTextEdit {
        color: #0F0;
        background-color: #2a2a2a;
    }"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._parent = parent
        self.setBackgroundVisible(True)
        self.setStyleSheet(self.stylesheet)


class ComboBox(QComboBox):

    stylesheet = """
        QCombobox {
            margin: 10px;
        }
        QComboBox QAbstractItemView {
            padding: 4px;
            background-color: #444;
            color: #FFF;
            border: 1px solid brown;
        }
        QCombobox QLineEdit {
            margin: 10px;
        }"""

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent=parent)
        self.args = args
        self.kwargs = kwargs
        self.setStyleSheet(self.stylesheet)
        self.addItem("")
        for exp in range(14, 24):
            if exp < 20:
                item = str((2 ** exp) // (2**10)) + "KB"
            else:
                item = str((2 ** exp) // (2**20)) + "MB"
            self.addItem(item)
        self.setEditable(False)


class Menu(QMenu):

    stylesheet = """
        QMenu {
            color: #dfdbd2;
            background-color: #41403b;
        }
        QMenu::item {
            color: #dfdbd2;
            border-color: #2a2a2c;
            padding:4px 10px 4px 20px;
            border-style: solid;
            border-width: 3px;
        }
        QMenu::item:selected {
            color:#FFF;
            background-color: #e16c36;
            border-style:solid;
            border-width:3px;
            padding:4px 7px 4px 17px;
            border-bottom-color:#af5530;
            border-top-color:#d95721;
            border-right-color:#cd5a2e;
            border-left-color:#fd9c71;
        }"""

    def __init__(self,text,parent=None):
        super().__init__(text,parent=parent)
        self.menubar = parent
        self.txt = text
        font = self.font()
        self.setObjectName(text)
        font.setPointSize(10)
        self.setFont(font)
        self.setStyleSheet(self.stylesheet)



class MenuBar(QMenuBar):

    stylesheet = """
        QMenuBar {
	        color: #dfdbd2;
	        background-color: #41403b;
        }
        QMenuBar::item {
            padding:5px;
            color: #dfdbd2;
            background-color: #41403b;
        }
        QMenuBar::item:selected {
            color: #FFF;
            padding:2px;
            padding-bottom:0px;
            border-width:3px;
            border-bottom-width:0px;
            border-top-right-radius:4px;
            border-top-left-radius:4px;
            border-style:solid;
            background-color: #41403b;
            border-top-color: #2a2a2c;
            border-right-color: #2f2f2c;
            border-left-color: #27272c;
        }"""

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent=parent)
        self.args = args
        self.window=parent
        self.kwargs = kwargs
        self.setStyleSheet(self.stylesheet)
        self.file_menu = Menu("File")
        self.options_menu = Menu("Options")
        self.help_menu = Menu("Help")
        self.addMenu(self.file_menu)
        self.addMenu(self.options_menu)
        self.addMenu(self.help_menu)
        self.actionExit = QAction(self.window)
        self.actionLoad = QAction(self.window)
        self.actionAbout = QAction(self.window)
        self.actionExit.setText("Exit")
        self.actionLoad.setText("Load Torrent")
        self.actionAbout.setText("About")
        self.file_menu.addAction(self.actionExit)
        self.options_menu.addAction(self.actionLoad)
        self.help_menu.addAction(self.actionAbout)
        self.actionExit.triggered.connect(self.exit_app)
        self.actionLoad.triggered.connect(self.load)
        self.actionAbout.triggered.connect(self.about_qt)
        self.actionExit.setObjectName("actionExit")
        self.actionAbout.setObjectName("actionAbout")
        self.actionLoad.setObjectName("actionLoad")

    def about_qt(self):
        self.window.app.aboutQt()

    def exit_app(self):
        self.parent().app.exit()

    def load(self):
        fname = QFileDialog.getOpenFileName(self, "Select File", "/", "*.torrent")
        decoder = Bendecoder()
        data = open(fname[0], "rb").read()
        results = decoder.decode(data)
        self.parent().apply_settings(results)

class Application(QApplication):
    def __init__(self, args=None):
        if not args:
            args = sys.argv
        super().__init__(args)

def start():
    app = Application()
    window = Window(parent=None, app=app)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    start()
