import sys
import os
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

class Window(QMainWindow):

    stylesheet = """QMainWindow {background-color: #1e1d23}"""

    def __init__(self,parent=None,app=None):
        super().__init__(parent=parent)
        self.app = app
        self.setObjectName("Mainwindow")
        self.setStyleSheet(self.stylesheet)
        self.setWindowTitle("Torrentfile Tools")
        icon = QIcon("./assets/torrentfileicon.png")
        self.setWindowIcon(icon)
        self.resize(400,400)
        self._setupUI()

    def _setupUI(self):
        self.menubar = MenuBar(parent=self)
        self.setMenuBar(self.menubar)
        self.central = QWidget(parent=self)
        self.central_layout = QVBoxLayout()
        self.central.setLayout(self.central_layout)
        self.setCentralWidget(self.central)
        self.import_button = ImportButton("Import Settings From File",parent=self)
        self.private_label = Label("Private")
        self.private_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.private_input = QCheckBox()
        self.piece_length_label = Label("Piece Length")
        self.piece_length_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.piece_length_input = ComboBox(parent=None)
        self.private_piecelength_layout = QHBoxLayout()
        self.private_piecelength_layout.addWidget(self.import_button)
        self.private_piecelength_layout.addWidget(self.private_label)
        self.private_piecelength_layout.addWidget(self.private_input)
        self.private_piecelength_layout.addWidget(self.piece_length_label)
        self.private_piecelength_layout.addWidget(self.piece_length_input)
        self.path_label = Label("Path")
        self.path_input = LineEdit()
        self.path_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.path_input.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.path_layout = QHBoxLayout()
        self.path_layout.addWidget(self.path_label)
        self.path_layout.addWidget(self.path_input)
        self.created_by_label = Label("Created By")
        self.created_by_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.created_by_input = LineEdit()
        self.created_by_input.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.created_by_layout = QHBoxLayout()
        self.created_by_layout.addWidget(self.created_by_label)
        self.created_by_layout.addWidget(self.created_by_input)
        self.announce_label = Label("Trackers")
        self.announce_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.announce_input = LineEdit()
        self.announce_input.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.announce_layout = QHBoxLayout()
        self.announce_layout.addWidget(self.announce_label)
        self.announce_layout.addWidget(self.announce_input)
        self.source_label = Label("Source")
        self.source_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.source_input = LineEdit()
        self.source_input.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.source_layout = QHBoxLayout()
        self.source_layout.addWidget(self.source_label)
        self.source_layout.addWidget(self.source_input)
        self.length_label = Label("Length")
        self.length_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.length_input = LineEdit()
        self.length_input.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.length_layout = QHBoxLayout()
        self.length_layout.addWidget(self.length_label)
        self.length_layout.addWidget(self.length_input)
        self.comment_label = Label("Comment")
        self.comment_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.comment_input = LineEdit()
        self.comment_input.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.comment_layout = QHBoxLayout()
        self.comment_layout.addWidget(self.comment_label)
        self.comment_layout.addWidget(self.comment_input)
        layouts = [ self.private_piecelength_layout, self.created_by_layout,
                    self.announce_layout, self.source_layout,
                    self.length_layout, self.comment_layout]
        for layout in layouts:
            self.central_layout.addLayout(layout)
        self.submit_button = QPushButton("Create Torrent")
        self.central_layout.addWidget(self.submit_button)
        self.imported = None


class ImportButton(QPushButton):
    stylesheet = """QPushButton {
        border-style: solid;
        border-color:  red;
        border-width:  1px;
        border-radius: 4px;
        color: #a9e7e6;
        padding: 8px;
        background-color: #1e4d33}"""

    def __init__(self,text,parent=None):
        super().__init__(text,parent=parent)
        self._text = text
        self._parent = parent
        self.setText(text)
        self.setStyleSheet(self.stylesheet)
        self.pressed.connect(self._import)

    def _import(self):
        filename = QFileDialog.getOpenFileName(self,"Open File", "/", "*.torrent")
        self.parent().imported = filename


class Label(QLabel):
    stylesheet = """QLabel {color: #d9d7d6}"""
    def __init__(self,text,parent=None):
        super().__init__(text,parent=parent)
        self.setStyleSheet(self.stylesheet)
        font = self.font()
        font.setPointSize(18)
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

class ComboBox(QComboBox):
    stylesheet = """QComboBox {}"""
    def __init__(self,parent=None,*args,**kwargs):
        super().__init__(parent=parent)
        self.args = args
        self.kwargs = kwargs
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


class MenuBar(QMenuBar):

    stylesheet = """
        QMenuBar {
            background-color: #1e1d23;
        }
        QMenuBar::item {
            color: #a9b7c6;
            spacing: 3px;
            padding: 1px 4px;
            background: #1e1d23;
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
        self.addMenu(self.file_menu)
        self.load_from_file = QAction("Import")
        self.exit = QAction(parent=self)
        self.setStyleSheet(self.stylesheet)
        self.exit.setText("Exit")
        self.exit.triggered.connect(self.exit_app)
        self.file_menu.addAction(self.exit)


    def exit_app(self):
        self.parent().app.exit()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window(parent=None,app=app)
    window.show()
    sys.exit(app.exec())
