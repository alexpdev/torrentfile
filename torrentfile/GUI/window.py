import os
import sys
from pathlib import Path
from benencoding import Bendecoder
from torrentfile.metafile import TorrentFile
from torrentfile.utils import path_stat
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

class Window(QMainWindow):

    stylesheet = """QMainWindow {
        background-color: #1e1f2f;
        }"""

    def __init__(self,parent=None,app=None):
        super().__init__(parent=parent)
        self.app = app
        self.setObjectName("Mainwindow")
        self.setStyleSheet(self.stylesheet)
        self.setWindowTitle("Torrentfile Tools")
        icon = QIcon("./assets/torrent-icon.png")
        self.setWindowIcon(icon)
        self.resize(400,400)
        self._setupUI()

    def _setupUI(self):
        self.menubar = MenuBar(parent=self)
        self.setMenuBar(self.menubar)
        self.central = QWidget(parent=self)
        self.clayout = QGridLayout()
        self.hlayout1 = QHBoxLayout()
        self.hlayout2 = QHBoxLayout()
        self.hlayout3 = QHBoxLayout()
        self.central.setLayout(self.clayout)
        self.setCentralWidget(self.central)
        self.path_label = Label("Path",parent=self)
        self.path_input = LineEdit(parent=self)
        self.browse_button = BrowseButton(parent=self)
        self.hlayout1.addWidget(self.path_input)
        self.hlayout1.addWidget(self.browse_button)
        self.path_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.path_input.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.clayout.addWidget(self.path_label,0,0,1,1)
        self.clayout.addLayout(self.hlayout1,0,1,1,1)
        self.private_label = Label("Private:",parent=self)
        self.private_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.private = QCheckBox(parent=self)
        self.piece_length_label = Label("Piece Length:",parent=self)
        self.piece_length_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.piece_length = ComboBox(parent=self)
        self.hlayout3.addWidget(self.private_label)
        self.hlayout3.addWidget(self.private)
        self.hlayout3.addWidget(self.piece_length_label)
        self.hlayout3.addWidget(self.piece_length)
        self.clayout.addLayout(self.hlayout3,1,0,1,2)
        self.size_label = Label("Total Size:",parent=self)
        self.size_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.size_result = Label("0",parent=self)
        self.size_result.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.pieces_label = Label("Pieces:",parent=self)
        self.pieces_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pieces = Label("0",parent=self)
        self.pieces.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.hlayout2.addWidget(self.size_label)
        self.hlayout2.addWidget(self.size_result)
        self.hlayout2.addWidget(self.pieces_label)
        self.hlayout2.addWidget(self.pieces)
        self.clayout.addLayout(self.hlayout2,2,0,1,2)
        self.created_by_label = Label("Created By:", parent=self)
        self.created_by_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.created_by_input = LineEdit(parent=self)
        self.created_by_input.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.clayout.addWidget(self.created_by_label,3,0,1,1)
        self.clayout.addWidget(self.created_by_input,3,1,1,1)
        self.announce_label = Label("Trackers:",parent=self)
        self.announce_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.announce_input = TextEdit(parent=self)
        self.clayout.addWidget(self.announce_label,4,0,1,1)
        self.clayout.addWidget(self.announce_input,4,1,1,1)
        self.source_label = Label("Source:",parent=self)
        self.source_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.source_input = LineEdit(parent=self)
        self.source_input.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.clayout.addWidget(self.source_label,5,0,1,1)
        self.clayout.addWidget(self.source_input,5,1,1,1)
        self.comment_label = Label("Comment:",parent=self)
        self.comment_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.comment_input = LineEdit(parent=self)
        self.comment_input.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.clayout.addWidget(self.comment_label,6,0,1,1)
        self.clayout.addWidget(self.comment_input,6,1,1,1)
        self.submit_button = SubmitButton("Create Torrent",parent=self)
        self.clayout.addWidget(self.submit_button,7,0,1,2)

    def apply_settings(self,result):
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
        val_mb = str(int(piece_length) // (1024**2))
        for i in range(self.piece_length.count()):
            if val_kb in self.piece_length.itemText(i):
                self.piece_length.setCurrentIndex(i)
                break
            elif val_mb in self.piece_length.itemText(i):
                self.piece_length.setCurrentIndex(i)
                break

    def set_path(self):
        path = QFileDialog.getExistingDirectory(parent=self,caption="choose file")
        self.path_input.insert(str(path))
        _, size, piece_length = path_stat(path)
        self.size_result.setText(str(size))
        self.pieces.setText(str(size/piece_length))


class BrowseButton(QToolButton):

    def __init__(self,parent=None):
        super().__init__(parent=parent)
        self.setText("...")
        self._parent = parent
        self.pressed.connect(self.browse)

    def browse(self):
        self._parent.set_path()


class SubmitButton(QPushButton):

    stylesheet = """
        QPushButton {
            border-style: solid;
            border-color:  red;
            border-width:  1px;
            border-radius: 4px;
            color: #fff;
            padding: 4px;
            background-color: #1e4d33;
        }
        QPushButton::hover{
            background-color: #191f74;
        }"""

    def __init__(self,text,parent=None):
        super().__init__(text,parent=parent)
        self._text = text
        self._parent = parent
        self.setText(text)
        self.setStyleSheet(self.stylesheet)
        self.pressed.connect(self.submit)

    def submit(self):
        window = self._parent
        path = window.path_input.text()
        private = 1 if window.private.isChecked() else 0
        source = window.source_input.text()
        announce = window.announce_input.toPlainText()
        announce = announce.split("\n")
        created_by = window.created_by_input.text()
        piece_length = window.piece_length.currentText()
        val, denom = piece_length.split(" ")
        if denom == "KB":
            val = int(val) * 1024
        elif denom == "MB":
            val = int(val) * (1024**2)
        comment = window.comment_input.text()
        torrentfile = TorrentFile(path=path,private=private,source=source,announce=announce,created_by=created_by,piece_length=val,comment=comment)
        torrentfile.assemble()
        try:
            save_dir = os.getenv("HOME")
        except:
            save_dir = os.getenv("USERPROFILE")
        save_file = os.path.join(save_dir,os.path.basename(path) + ".torrent")
        save_location = QFileDialog.getSaveFileName(parent=window,caption="Save Location", directory=save_file)
        torrentfile.write(save_location)
        print("success")



class Label(QLabel):

    stylesheet = """QLabel {
        color: #FAFAFA;
        margin-right: 3px;
        margin-bottom: 3px;
        padding: 3px;
    }"""

    def __init__(self,text,parent=None):
        super().__init__(text,parent=parent)
        self.setStyleSheet(self.stylesheet)
        font = self.font()
        font.setBold(True)
        font.setPointSize(12)
        self.setFont(font)


class LineEdit(QLineEdit):

    stylesheet = """QLineEdit {
        border-color: #4edff3;
        border-width: 1px;
        border-radius: 4px;
        border-style: inset;
        padding: 5px;
        color: #a9b7c6;
        background: #1e1d23;
        selection-background-color: #007b50;
        selection-color: #FFFFFF;
    }"""

    def __init__(self,parent=None):
        super().__init__(parent=parent)
        self._parent = parent
        self.setStyleSheet(self.stylesheet)


class TextEdit(QPlainTextEdit):

    stylesheet = """QTextEdit {
        border-color: #4edff3;
        border-width: 1px;
        border-radius: 4px;
        border-style: inset;
        padding: 5px;
        color: #a9b7c6;
        background: #1e1d23;
        selection-background-color: #007b50;
        selection-color: #FFFFFF;
    }"""

    def __init__(self,parent=None):
        super().__init__(parent=parent)
        self._parent = parent
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

    def __init__(self,parent=None,*args,**kwargs):
        super().__init__(parent=parent)
        self.args = args
        self.kwargs = kwargs
        self.setStyleSheet(self.stylesheet)
        self.addItem("")
        kib = 2**10
        mib = kib**2
        for exp in range(14,24):
            item = (2**exp) // kib
            suffix = "KB"
            if item >= kib:
                item = item // kib
                suffix = "MB"
            item = f"{item} {suffix}"
            self.addItem(item)
        self.setEditable(False)
        print(self.currentIndex(), repr(self.currentText()))


class MenuBar(QMenuBar):

    stylesheet = """
        QMenuBar {
            background-color: #1e1d23;
            border-bottom: 1px solid #aa2
            margin: 2px;
        }
        QMenuBar::item {
            color: #a9b7c6;
            spacing: 3px;
            padding: 1px 4px;
            background: #1e1d23;
            margin-left: 2px;
        }

        QMenuBar::item:selected {
            background:#1e1d23;
            color: #FFFFFF;
        }
        QMenu::item:selected {
            border-style: solid;
            border-top-color: transparent;
            border-right-color: transparent;
            border-left-color: #04b97f;
            border-bottom-color: transparent;
            border-left-width: 2px;
            color: #FFFFFF;
            padding-left:15px;
            padding-top:4px;
            padding-bottom:4px;
            padding-right:7px;
            background-color: #1e1d23;
        }
        QMenu::item {
            border-style: solid;
            border-top-color: transparent;
            border-right-color: transparent;
            border-left-color: transparent;
            border-bottom-color: transparent;
            border-bottom-width: 1px;
            border-style: solid;
            color: #a9b7c6;
            padding-left:17px;
            padding-top:4px;
            padding-bottom:4px;
            padding-right:7px;
            background-color: #1e1d23;
        }
        QMenu{
            background-color:#1e1d23;
        }"""

    def __init__(self,parent=None,*args,**kwargs):
        super().__init__(parent=parent)
        self.args = args
        self.kwargs = kwargs
        self.file_menu = QMenu("File")
        self.settings_menu = QMenu("Settings")
        font = self.file_menu.font()
        font.setPointSize(11)
        self.setFont(font)
        self.addMenu(self.file_menu)
        self.addMenu(self.settings_menu)
        self.load_from_file = QAction(parent=self)
        self.exit = QAction(parent=self)
        self.setStyleSheet(self.stylesheet)
        self.exit.setText("Exit")
        self.load_from_file.setText("Load from file")
        self.file_menu.addAction(self.exit)
        self.settings_menu.addAction(self.load_from_file)
        self.exit.triggered.connect(self.exit_app)
        self.load_from_file.triggered.connect(self.load)

    def exit_app(self):
        self.parent().app.exit()

    def load(self):
        filename = QFileDialog.getOpenFileName(self,"Select Torrent File",
                                                "/", "*.torrent")[0]
        decoder = Bendecoder()
        data = open(filename,"rb").read()
        results = decoder.decode(data)
        self.parent().apply_settings(results)

def start():
    app = QApplication(sys.argv)
    window = Window(parent=None,app=app)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    start()
