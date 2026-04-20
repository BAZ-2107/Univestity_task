 # -*- coding: utf-8 -*-


import sqlite3
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import sys
import os
import json
import time
import shutil
from datetime import datetime
import sympy as sp
from scipy.integrate import solve_ivp
import numpy as np


class Window(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()
        uic.loadUi("ui/main.ui", self)
        self.setupUI()

    def setupUI(self):
        self.arr = []
        self.show_author = None
        self.show_help = None
        self.show_save_system = None
        self.warning = None

        self.save_system_action.triggered.connect(self.__open_save_system)
        self.load_system_action.triggered.connect(self.__load_system)

        self.about_action.triggered.connect(self.__open_author)
        self.help_action.triggered.connect(self.__open_help)
        self.add_string.clicked.connect(self.__add_line)
        self.del_string.clicked.connect(self.__del_line)
        self.solve_system.clicked.connect(self.__solve_expression)
        self.__load_system(True)

    def __open_author(self):
        self.show_author = Author()
        self.show_author.show()

    def __open_help(self):
        self.show_help = Help()
        self.show_help.show()

    def __solve_expression(self):
        try:
            n = self.table.rowCount()
            equations = [self.table.item(i, 1).text() for i in range(n)]
            variables = sp.symbols(" ".join(f"x{i + 1}" for i in range(n)))
            exprs = list()
            initial = list(map(float, list(self.table.item(i, 3).text() for i in range(n))))
            for_p0 = list()
            dicct = dict((x, y) for x, y in zip(variables, initial))
            for eq in equations:
                lf, rg = eq.split('=')
                exprs.append(sp.sympify(lf) - sp.sympify(rg))
                for_p0.append(exprs[-1].subs(dicct))
            jacobian = sp.Matrix([exprs]).jacobian(variables)
            if jacobian.det().simplify() == 0:
                QMessageBox.warning(self, "Вырожденность якобиана", "Якобиан введенной системы равен нулю. Решить данную систему невозможно")
            else:
                inverse_jacobian = jacobian.inv()
                p0 = sp.Matrix(for_p0)
                system = -inverse_jacobian * p0
                f = sp.lambdify(variables, system, 'numpy')
                t_span = (0, 1)
                t_eval = np.linspace(0, 1, self.point_count.value())
                def ode_system(t, y):
                    result = f(*y)
                    return np.array(result).flatten()
    
    
                solution = solve_ivp(ode_system, t_span, t_eval=t_eval, y0=initial, method=self.method.currentText())
                t, y = solution.t, solution.y
                #print(solution)
                self.table2.clear()
                self.table2.setRowCount(n)
                fact_t_points = len(t)
                self.table2.setColumnCount(fact_t_points)
                self.table2.setVerticalHeaderLabels(["x" + str(i + 1) for i in range(n)])
                self.table2.setHorizontalHeaderLabels([f"{elem:.4f}" for elem in t_eval])
                for j in range(fact_t_points):
                    for i in range(n):
                        item = QTableWidgetItem(f"{y[i][j]:.4f}")
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                        self.table2.setItem(i, j, item)
                #norm_points = list(np.linalg.norm(i) for i in zip(y))
                #print(norm_points)
                #print("y__________", list(zip(y)))
        except Exception as message:
            print(message)
            self.statusbar.showMessage("При вычислении произошла ошибка")

    def __load_system(self, for_run=False):
        if for_run:
            answer = "user_files/default.json"
        else:
            answer, _ = QFileDialog.getOpenFileName(self, "Выбор файла", "user_files", "JSON Files (*.json)")
        if answer:
            try:
                with open(answer, 'r') as fille:
                    data = json.load(fille)
                n = len(data)
                self.table.setRowCount(0)
                for i in range(n):
                    self.__add_line()
                    st_i = str(i)
                    self.table.setItem(i, 1, QTableWidgetItem(data[st_i][0]))
                    self.table.setItem(i, 3, QTableWidgetItem(data[st_i][1]))
                self.statusbar.showMessage(f"Система из файла {answer} успешно загружена")
            except Exception as m:
                self.statusbar.showMessage(f"Не удалось обработать файл: {answer}")

    def __add_line(self):
        n = self.table.rowCount()
        self.table.insertRow(n)
        item1 = QTableWidgetItem(f"f{n + 1}(x)=g{n + 1}(x)")
        item2 = QTableWidgetItem(f"f_{n + 1}(x)=0")
        item3 = QTableWidgetItem(f"(x{n + 1})0")
        item4 = QTableWidgetItem(f"0")
        self.table.setItem(n, 0, item1)
        self.table.item(n, 0).setFlags(self.table.item(n, 0).flags() & ~Qt.ItemIsEditable)
        self.table.setItem(n, 1, item2)
        self.table.setItem(n, 2, item3)
        self.table.item(n, 2).setFlags(self.table.item(n, 2).flags() & ~Qt.ItemIsEditable)
        self.table.setItem(n, 3, item4)
        self.statusbar.showMessage(f"Добавлена {n + 1}-я строка")

    def __del_line(self):
        n = self.table.rowCount()
        if n > 0:
            self.table.removeRow(n - 1)
            self.statusbar.showMessage(f"Удалена {n}-я строка")

    def __open_save_system(self):
        n = self.table.rowCount()
        if n > 0:
            self.show_save_system = SaveSystem(self)
            self.show_save_system.show()

    def saving_system(self):
        n = self.table.rowCount()
        arr = dict((i, [self.table.item(i, 1).text(), self.table.item(i, 3).text()]) for i in range(n))
        st = str(datetime.now())
        st = st[:st.find('.')].replace(':', '.')
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить", f"user_files/{st}.json", "JSON Files (*.json)")
        if path:
            with open(path, "w") as fille:
                json.dump(arr, fille)
            self.statusbar.showMessage(f"Система была сохранена в файл: {path}")

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Close):
            self.close()
        elif event.matches(QKeySequence.New):
            self.__add_line()
        elif event.matches(QKeySequence.Cut):
            self.__del_line()
        elif event.matches(QKeySequence.Open):
            self.__load_system()
        elif event.matches(QKeySequence.Undo):
            self.__open_author()
        elif event.matches(QKeySequence.Save):
            self.__open_save_system()


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


class SaveSystem(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__()
        uic.loadUi("ui/for_save_system.ui", self)
        self.setupUI(*args, **kwargs)

    def setupUI(self, *args, **kwargs):
        self.parent = args[0]
        self.parent.setDisabled(True)
        self.yes.clicked.connect(self.button_pressed)
        self.no.clicked.connect(self.button_pressed)
        self.__fill_table()

    def __fill_table(self):
        table = self.parent.table
        n = table.rowCount()
        self.tablle.setRowCount(n)
        for i in range(n):
            item1 = QTableWidgetItem(table.item(i, 1).text())
            self.tablle.setItem(i, 0, item1)
            item2 = QTableWidgetItem(table.item(i, 3).text())
            self.tablle.setItem(i, 1, item2)
            self.tablle.item(i, 0).setFlags(item1.flags() & ~Qt.ItemIsEditable)
            self.tablle.item(i, 1).setFlags(item2.flags() & ~Qt.ItemIsEditable)

    def button_pressed(self):
        sender = self.sender()
        if sender and (sender.text() == "Сохранить"):
            self.parent.saving_system()
        self.close()

    def closeEvent(self, event):
        self.parent.setEnabled(True)


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