#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
IHM for generating names
Select a folder where dictionnaries are saved
Choose dictionnary in combobox
Click "Next" button to generate a new names based on the dictionnary selected
The following will be displayed :
- "Most common" name for the selected dictionnary
- Latin version of the name generated
- Approximate katakana version of the name generated
"""

import sys
import os
from threading import Timer

from PyQt4.QtGui import *

from romkan import to_roma, to_katakana

from word_generator import WordGenerator

class Main(QMainWindow):
    """
    Main IHM
    """

    # pylint: disable=too-many-instance-attributes
    # We need all those buttons

    def __init__(self):
        QMainWindow.__init__(self, None)
        self.generators = {}
        self.counts = {}
        self.mc = {}
        self.ngg = None
        self.path = ""

        self.folder_path = QLineEdit()
        self.folder_select = QPushButton("Select Folder")
        self.files_list = QComboBox()
        self.most_common = QLabel("None")
        self.next_btn = QPushButton("Next")
        self.romanji_res = QLabel("None")
        self.katakana_res = QLabel("None")

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        tmp_widget = QWidget()
        folder_layout = QHBoxLayout()

        self.setCentralWidget(main_widget)

        folder_layout.addWidget(self.folder_select)
        folder_layout.addWidget(self.folder_path)

        main_widget.setLayout(main_layout)
        tmp_widget.setLayout(folder_layout)

        main_layout.addWidget(tmp_widget)
        main_layout.addWidget(self.files_list)
        main_layout.addWidget(self.most_common)
        main_layout.addWidget(self.next_btn)
        main_layout.addWidget(self.romanji_res)
        main_layout.addWidget(self.katakana_res)

        self.next_btn.clicked.connect(self.nxt)
        self.folder_select.clicked.connect(self.get_folder)
        self.folder_path.textChanged.connect(self.uplist)
        self.files_list.currentIndexChanged.connect(self.open_wg)
        self.folder_path.setText("Names")

        self.sizeHint()
        self.show()

    def open_wg(self):
        """ Initiate new name generator opening
        Will Displayed Laoding information
        """
        self.next_btn.setText("Loading ...")
        self.next_btn.setEnabled(False)
        Timer(0.1, self._open_wg).start()

    def _open_wg(self):
        """ Open new name generator when selecting new dictionnary """
        filename = os.path.join(str(self.path), str(self.files_list.currentText()))
        if filename in self.generators:
            self.ngg = self.generators[filename]
        else:
            name_gen = WordGenerator()
            self.counts[filename] = name_gen.proba_count(filename)
            self.ngg = name_gen.gen_word(ignore_dict=False)
            self.generators[filename] = self.ngg
            try:
                self.mc[filename] = name_gen.most_common()
            except Exception as e:
                self.mc[filename] = "Error"
        self.most_common.setText(self.mc[filename])

        self.next_btn.setText("Next")
        self.next_btn.setEnabled(True)
        self.next_btn.clicked.emit(True)

    def nxt(self):
        """ Generate new name and displays it """
        name = next(self.ngg)
        k = to_roma(name)
        if k != name:
            self.romanji_res.setText(k)
            self.katakana_res.setText(name)
        else:
            self.romanji_res.setText(name)
            name = name.replace('l', 'r')
            name = name.replace('c', 'k')
            katakana = to_katakana(name.lower())
            self.katakana_res.setText(katakana)


    def get_folder(self):
        """ Pops out folder selection dialog and updates dictionnary list """
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.folder_path.setText(str(path))
        self.uplist()

    def uplist(self):
        """ Update Dictionnary list """
        if not os.path.isdir(self.folder_path.text()):
            return
        self.path = self.folder_path.text()
        folder = str(self.path)
        choices = [f for f in os.listdir(folder)
                   if os.path.isfile(os.path.join(folder, f)) and not f.startswith('.')]
        self.files_list.clear()
        self.files_list.addItems(sorted(choices))

if __name__ == "__main__":
    APP = QApplication(sys.argv)
    MYAPP = Main()
    MYAPP.show()
    sys.exit(APP.exec_())
