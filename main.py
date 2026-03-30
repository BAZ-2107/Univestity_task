 # -*- coding: utf-8 -*-


import sqlite3
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import sys
import os
import shutil


class Window(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()
        uic.loadUi("ui/main.ui", self)
        self.setupUI()

    def setupUI(self):
        self.arr = []
        self.show_author = None
        self.show_help = None
        self.about_action.triggered.connect(self.__open_author)
        self.help_action.triggered.connect(self.__open_help)
        self.add_string.clicked.connect(self.__add_line)
        self.del_string.clicked.connect(self.__del_line)

    def __open_author(self):
        self.show_author = Author(self)
        self.show_author.show()

    def __open_help(self):
        self.show_help = Help(self)
        self.show_help.show()

    def __add_line(self):
        n = self.table.rowCount()
        self.table.insertRow(n)
        item = QTableWidgetItem(f"x_{n + 1}")
        item2 = QTableWidgetItem(f"f_{n + 1}(x)")
        self.table.setItem(n, 0, item)
        self.table.setItem(n, 1, item2)

    def __del_line(self):
        n = self.table.rowCount()
        if n > 0:
            self.table.removeRow(n - 1)

    def __save_system(self):
        n = self.table.rowCount()
        if n:
            pass

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Close):
            self.close()
        elif event.matches(QKeySequence.New):
            self.__add_line()
        elif event.matches(QKeySequence.Cut):
            self.__del_line()
        elif event.matches(QKeySequence.Undo):
            self.__open_author()
        elif event.matches(QKeySequence.Save):
            self.__save_system()


class Author(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__()
        uic.loadUi("ui/about.ui", self)
        self.setupUI()

    def setupUI(self):
        self.label.setPixmap(QPixmap("images/photo2"))

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Close):
            self.close()


class Help(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__()
        uic.loadUi("ui/help.ui", self)
        self.setupUI()

    def setupUI(self):
        self.textBrowser.setText(open("txt/help.txt", encoding="utf-8", mode='r').read())

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Close):
            self.close()


# catch errors
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

if __name__ == "__main__":
    # show interface
    app = QApplication(sys.argv)
    form = Window()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())