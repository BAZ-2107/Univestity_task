 # -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import numpy as np
import sympy as sp
from sympy import parse_expr, Function, symbols, sympify
import sys
from datetime import datetime
from scipy.integrate import solve_ivp
import json
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)

        super(PlotCanvas, self).__init__(self.figure)
        self.setParent(parent)

    def plot_t(self, indexes):
        self.axes.clear()
        self.axes.set_title("Зависимость " + ",".join(f"x{i + 1}(t)" for i in indexes) + "от t")
        self.axes.set_xlabel("Ось t")
        self.axes.set_ylabel("Ось xi(t)")
        for index in indexes:
            for i, arr in enumerate(self.parent().arr_of_arr):
                #print(arr)
                self.axes.plot(arr['t'], arr['y'][index], label=f'x{index + 1}(t), ' + self.parent().listWidget.item(i).text(), linewidth=2)
        #self.axes.grid(True)
        self.axes.legend()
        self.figure.tight_layout()
        self.draw()

    def plot_x(self, x, y):
        self.axes.clear()
        self.axes.set_title("Зависимость " + f"x{x + 1}(t)" + "от " + f"x{y + 1}(t)")
        self.axes.set_xlabel("Ось " + f"x{y + 1}(t)")
        self.axes.set_ylabel("Ось " + f"x{x + 1}(t)")
        for i, arr in enumerate(self.parent().arr_of_arr):
            self.axes.plot(arr['y'][y], arr['y'][x], label=self.parent().listWidget.item(i).text(), linewidth=2)

            self.axes.plot(arr['y'][y][0], arr['y'][x][0], 'ro', markersize=10)
            self.axes.text(arr['y'][y][0], arr['y'][x][0], ' S', fontsize=12, va='bottom', ha='left')
            self.axes.plot(arr['y'][y][-1], arr['y'][x][-1], 'go', markersize=10)
            self.axes.text(arr['y'][y][-1], arr['y'][x][-1], ' F', fontsize=12, va='bottom', ha='left')

        self.axes.set_aspect("equal")
        #self.axes.grid(True)
        self.axes.axhline(y=0, color='black', linewidth=0.8)
        self.axes.axvline(x=0, color='black', linewidth=0.8)
        self.axes.legend()
        self.figure.tight_layout()
        self.draw()    


class ShowGraphic(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__()
        uic.loadUi("ui/for_showGraphic.ui", self)
        self.parent = parent
        self.setupUI(*args, **kwargs)

    def setupUI(self, *args, **kwargs):
        self.arr_of_arr = list([arr for arr in args])
        for i in range(len(args)):
            self.listWidget.addItem(self.parent.name_of_gr + f"_{i + 1}")
        self.n = len(args[0]['y'])
        self.arrr_for_t, self.arrr_for_x_y, self.arrr_for_x_x = list([self.checkBox]), list([self.radioButton_3]), list([self.radioButton_4])
        for i in range(1, self.n):
            for_tt = QCheckBox(f"x{i + 1}")
            for_tt.toggled.connect(self.__draw)
            for_x_yy = QRadioButton(f"x{i + 1}")
            for_x_xx = QRadioButton(f"x{i + 1}")
            for_x_yy.toggled.connect(self.__draw)
            for_x_xx.toggled.connect(self.__draw)
            self.arrr_for_t.append(for_tt)
            self.arrr_for_x_x.append(for_x_xx)
            self.arrr_for_x_y.append(for_x_yy)
            self.for_t.layout().addWidget(for_tt)
            self.for_x_y.layout().addWidget(for_x_yy)
            self.for_x_x.layout().addWidget(for_x_xx)
        self.canvas = PlotCanvas(self)
        self.for_x.hide()
        self.layout().addWidget(self.canvas)
        #self.n_count = QSpinBox(self)
        #self.n_count.setRange(2, 1000)
        #self.n_count.setValue(100)
        #self.n_count.setSingleStep(100)
        #self.run = QPushButton("Запуск", self)
        self.save_img = QPushButton("Сохранить картинку", self)
        self.save_gr = QPushButton("Сохранить график", self)
        self.open_gr = QPushButton("Открыть график", self)

        #hboxlayout = QHBoxLayout()
        #hboxlayout.addWidget(QLabel("Число точек: ", self))
        #hboxlayout.addWidget(self.n_count)

        hboxlayout2 = QHBoxLayout()
        #hboxlayout2.addWidget(self.run)
        hboxlayout2.addWidget(self.save_img)
        hboxlayout2.addWidget(self.save_gr)
        hboxlayout2.addWidget(self.open_gr)

        #self.layout().addItem(hboxlayout)
        self.layout().addItem(hboxlayout2)
        #self.run.clicked.connect(self.__draw)
        self.save_img.clicked.connect(self.__save_fig)
        self.save_gr.clicked.connect(self.__save_gr)
        self.open_gr.clicked.connect(self.__load_graphic)
        self.parent.setDisabled(True)
        self.checkBox.toggled.connect(self.__draw)
        self.radioButton.toggled.connect(self.__draw)
        self.radioButton_2.toggled.connect(self.__draw)
        self.radioButton_3.toggled.connect(self.__draw)
        self.radioButton_4.toggled.connect(self.__draw)
        self.__draw()

    def __save_gr(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить", get_random_path(), "NPZ Files (*.npz)")
        if file_path:
            try:
                np.savez(file_path, **dict((str(i), np.vstack([arr['t'], arr['y']])) for i, arr in enumerate(self.arr_of_arr)))
                self.listWidget.clear()
                #st = file_path.split('/')[-1].split('.')[0]
                stt = file_path[file_path.rfind('/') + 1:]
                st = stt[:stt.rfind('.')]
                for i in range(len(self.arr_of_arr)):
                    self.listWidget.addItem(st + f"_{i + 1}")
                self.__draw()
                QMessageBox.information(self, "Сохранение графика", f"График сохранен как: {file_path}")
            except Exception as e:
                print(e)
                QMessageBox.information(self, "Сохранение графика", "Ошибка сохранения")

    def __load_graphic(self):
        answer, _ = QFileDialog.getOpenFileName(self, "Выбор файла", ".", "NPZ Files (*.npz)")
        if answer:
            data = np.load(answer)
            if len(data['0']) - 1 != len(self.arr_of_arr[0]['y']):
                QMessageBox.information(self, "Открытие графика", "Внимание! Размерности графиков не совпадают!")
            else:
                self.arr_of_arr += [{'t': data[str(i)][0], 'y': data[str(i)][1:]} for i in range(len(data))]
                stt = answer[answer.rfind('/') + 1:]
                st = stt[:stt.rfind('.')]
                for i in range(len(data)):
                    self.listWidget.addItem(st + f"_{i + 1}")                
                self.__draw()

    def __save_fig(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить график", get_random_path(),"Изображения (*.png *.jpg *.jpeg *.bmp *.svg *.pdf);;Все файлы (*)")
        if file_path:
            try:
                self.canvas.figure.savefig(file_path, dpi=300, bbox_inches='tight')
                QMessageBox.information(self, "Сохранение графика", f"График сохранен как: {file_path}")
            except Exception as e:
                QMessageBox.information(self, "Сохранение графика", "Ошибка сохранения")        

    def __draw(self):
        if self.for_x.isHidden():
            indexes = list()
            for i, elem in enumerate(self.arrr_for_t):
                if elem.isChecked():
                    indexes.append(i)
            self.canvas.plot_t(indexes)
        else:
            _arr = list([0, 0])
            for i, arr in enumerate([self.arrr_for_x_y, self.arrr_for_x_x]):
                for index, elem in enumerate(arr):
                    if elem.isChecked():
                        _arr[i] = index
                        break
            self.canvas.plot_x(*_arr)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Close):
            self.close()
        elif event.matches(QKeySequence.Open):
            self.__load_graphic()

    def closeEvent(self, event):
        self.parent.setEnabled(True)


class Window(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()
        uic.loadUi("ui/PRAK_main.ui", self)
        self.setupUI()

    def setupUI(self):
        self.arr = []
        self.show_author = None
        self.show_help = None
        self.show_save_system = None
        self.warning = None
        self.a, self.b, self.p0, self.name_of_gr = 0., 0., None, ""
        self.f = None
        self.R, self.R_x, self.R_y = None, None, None
        self.vars_a, self.vars_b = None, None
        self.for_graphic = None

        self.save_system_action.triggered.connect(self.__open_save_system)
        self.load_system_action.triggered.connect(self.__load_system)
        self.open_graphic_action.triggered.connect(self.__open_gr_window)

        self._header = self.table.horizontalHeader()
        self._header.sectionDoubleClicked.connect(self.__resize_columns)

        self._header3 = self.table2.horizontalHeader()
        self._header3.sectionDoubleClicked.connect(self.__resize_columns_2)

        self._header2 = self.table2.verticalHeader()
        self._header2.sectionDoubleClicked.connect(self.__run_graphic_window)

        self.about_action.triggered.connect(self.__open_author)
        self.help_action.triggered.connect(self.__open_help)
        self.add_string.clicked.connect(self.__add_line)
        self.del_string.clicked.connect(self.__del_line)
        self.run.clicked.connect(self.__solve_expression)
        self.next_step.clicked.connect(self.__run_cycle)
        self.break_run.clicked.connect(self.__for_run)
        #self.table.rowsRemoved.connect(self.__resize_table_2)
        self.__load_system(True)
        self.iteration_count = 0

    def __open_gr_window(self):
        answer, _ = QFileDialog.getOpenFileName(self, "Выбор файла", ".", "NPZ Files (*.npz)")
        if answer:
            data = np.load(answer)
            arr_of_arr = [{'t': data[str(i)][0], 'y': data[str(i)][1:]} for i in range(len(data))]        
            st = answer[answer.rfind('/') + 1:]
            self.name_of_gr = st[:st.rfind('.')]
            self.for_graphic = ShowGraphic(self, *arr_of_arr)
            self.for_graphic.show()

    def __run_graphic_window(self, index):
        if self.table2.rowCount() > 1:
            p = self.__get_pk(index)
            n = len(p)
            a, b = self.a, self.b
            variables = sp.symbols(" ".join(f"x{i + 1}" for i in range(n)))
            f = sp.lambdify(variables, self.f, "numpy")


            def my_func(t, x):
                return f(*x)


            acc = float(f"1e-{self.accuracy_6.value()}")
            solution = solve_ivp(my_func, (a, b), p, t_eval=np.linspace(a, b, 101), method=self.method_6.currentText(), rtol=acc, atol=acc)
            self.name_of_gr = "p" + str(index)
            self.for_graphic = ShowGraphic(self, {'t': solution.t, 'y': solution.y})
            self.for_graphic.show()

    def __resize_table_2(self):
        self.table2.setColumnCount(self.table.rowCount())

    def __get_pk(self, index):
        return np.array(list(float(self.table2.item(index, i).text()) for i in range(self.table2.columnCount())))

    def __add_line_2(self, arr=None):
        n = self.table2.rowCount()
        self.table2.insertRow(n)
        if arr is None:
            arr = np.zeros(self.table.rowCount())
        nnn = self.f_num_count.value()
        for i, el in enumerate(arr):
            self.table2.setItem(n, i, QTableWidgetItem(str(f"{el:.{nnn}f}")))
        self.table2.setVerticalHeaderItem(n, QTableWidgetItem(f"p{n}"))
        self.table2.resizeColumnsToContents()

    def __resize_columns(self):
        self.table.resizeColumnsToContents()

    def __resize_columns_2(self):
        self.table2.resizeColumnsToContents()

    def __open_author(self):
        self.show_author = Author()
        self.show_author.show()

    def __open_help(self):
        self.show_help = Help()
        self.show_help.show()

    def __solve_expression(self):
        try:
            n = self.table.rowCount()
            f_arr = list(self.table.item(i, 2).text() for i in range(n)) # получаем n правых частей уравнения dx/dt = f(x, t)
            self.f = get_f(f_arr)
        
            variables = sp.symbols(" ".join(f"x{i + 1}" for i in range(n))) # создаем n переменных
        
            exprs = list()
            initial = list(self.table.item(i, 4).text() for i in range(n)) # получаем n краевых условий
            self.a, self.b, R = get_a_b_R(initial) # получаем из краевых условий краевые точки и массив
            arr_forr_R = list()
            vars_a = sp.symbols(" ".join(f"x{i + 1}_a" for i in range(n)))
            vars_b = sp.symbols(" ".join(f"x{i + 1}_b" for i in range(n)))
            for st in R:
                lf, rg = st.split("=")
                arr_forr_R.append(sympify(lf) - sympify(rg))
            self.R = sp.lambdify([vars_a + vars_b], arr_forr_R)
            self.R_x = sp.lambdify([vars_a + vars_b], sp.Matrix(arr_forr_R).jacobian(vars_a))
            self.R_y = sp.lambdify([vars_a + vars_b], sp.Matrix(arr_forr_R).jacobian(vars_b))
        
            #self.p0 = np.random.randn(n)
            self.p0 = self.__get_pk(0)
            self.table2.setRowCount(1)
            self.iteration_count = 0
            self.__for_run(True)
            if self.stop_on_step.isChecked():
                self.__run_cycle()
            else:
                while not self.method_5.isEnabled():
                    self.__run_cycle()
                #print(self.get_x_X_a_b(self.p0))
        except Exception as message:
            #print(message)
            self.statusbar.showMessage(str(message))
            if not self.accuracy_5.isEnabled():
                self.__for_run()

    def __for_run(self, flag=False):
        self.accuracy_5.setDisabled(flag)
        self.accuracy_6.setDisabled(flag)
        self.method_5.setDisabled(flag)
        self.method_6.setDisabled(flag)
        self.add_string.setDisabled(flag)
        self.del_string.setDisabled(flag)
        self.stop_on_step.setDisabled(flag)
        self.run.setDisabled(flag)
        self.epsilon.setDisabled(flag)
        self.next_step.setEnabled(flag)
        self.break_run.setEnabled(flag)

    def __run_cycle(self):
        self.iteration_count += 1
        self.iteration.display(self.iteration_count)
        n = len(self.p0)
        res = self.get_x_X_a_b(self.p0)
        if len(res) != 2:
            raise Exception("Нет решения для x, X в крайней точке")
        #print(res)
        x_a, x_b = res[0][:n], res[1][:n]
        Phi_0 = self.R(np.concatenate([x_a, x_b]))
        def func_for_p(mu, p):
            res2 = self.get_x_X_a_b(p)
            if len(res2) != 2:
                raise Exception("Нет решения для x, X в крайней точке")
            x_a, x_b = res2[0][:n], res2[1][:n]
            X_a, X_b = res2[0][n:].reshape(n, n), res2[1][n:].reshape(n, n)
            Phi_pr = self.R_x(np.concatenate([x_a, x_b])) @ X_a + self.R_y(np.concatenate([x_a, x_b])) @ X_b
            v = np.linalg.solve(np.array(Phi_pr), -np.array(Phi_0))
            return v


        acc = float(f"1e-{self.accuracy_5.value()}")
        solll = solve_ivp(func_for_p, (0, 1), self.p0, t_eval=np.array([0., 1.]), method=self.method_5.currentText(), rtol=acc, atol=acc).y.T
        if len(solll) != 2:
            raise Exception("Нет решения для p на крайней точке")
        p1 = solll[-1]
        #print("p1: ", p1)
        self.__add_line_2(p1)
        if np.linalg.norm(self.p0 - p1) <= float(f"1e-{self.epsilon.value()}"):
            self.__for_run(False)
        else:
            self.p0 = p1.copy()


    def get_x_X_a_b(self, p):
        n = len(p)
        variables = sp.symbols(" ".join(f"x{i + 1}" for i in range(n)))
        f = sp.lambdify(variables, self.f, "numpy")
        A = sp.Matrix(self.f).jacobian(variables)
        f_x = sp.lambdify([variables], A)


        def my_func(t, y):
            x = y[:n]
            res_for_x = f(*x)
            X = y[n:].reshape(n, n)
            res_for_X = f_x(x) @ X
            return np.concatenate([res_for_x, res_for_X.flatten()])


        acc = float(f"1e-{self.accuracy_6.value()}")
        return solve_ivp(my_func, (self.a, self.b), np.concatenate([p, np.eye(n).flatten()]), t_eval=np.array([self.a, self.b]), method=self.method_6.currentText(), rtol=acc, atol=acc).y.T


    def __load_system(self, for_run=False):
        if for_run:
            answer = "user_files/default.json"
        else:
            answer, _ = QFileDialog.getOpenFileName(self, "Выбор файла", "user_files", "JSON Files (*.json)")
        if answer:
            try:
                self.table2.clearContents()
                self.table2.setRowCount(0)
                with open(answer, 'r', encoding="utf-8") as fille:
                    data = json.load(fille)
                n = len(data)
                #print(n)
                self.table.clearContents()
                self.table.setRowCount(0)
                #print(self.table.rowCount())
                for i in range(n - 8):
                    self.__add_line()
                    st_i = str(i)
                    self.table.setItem(i, 2, QTableWidgetItem(data[st_i][0]))
                    self.table.setItem(i, 4, QTableWidgetItem(data[st_i][1]))
                self.epsilon.setValue(int(data["p_acc"]))
                self.f_num_count.setValue(int(data["f_count"]))
                self.accuracy_5.setValue(int(data["acc_5"]))
                self.accuracy_6.setValue(int(data["acc_6"]))
                self.method_5.setCurrentText(data["method_5"])
                self.method_6.setCurrentText(data["method_6"])
                self.__add_line_2(list(map(float, data["p0"])))
                with open(data["comments"], 'r', encoding="utf-8") as fil:
                    self.comment.setText(fil.read())
                self.table.resizeColumnsToContents()
                self.statusbar.showMessage(f"Система из файла {answer} успешно загружена")
            except Exception as m:
                self.statusbar.showMessage(f"Не удалось обработать файл: {answer}")

    def __add_line(self):
        n = self.table.rowCount()
        self.table.insertRow(n)
        self.__resize_table_2()
        items = [QTableWidgetItem(f"dx{n + 1}/dt"), QTableWidgetItem("="), QTableWidgetItem(f"f{n + 1}(x)"),
                 QTableWidgetItem(f"R{n + 1}(x(a), x(b))=0"), QTableWidgetItem(f"R{n + 1}(x(a), x(b))=0")]
        for i, item in enumerate(items):
            self.table.setItem(n, i, item)
            if (i != 2) and (i != 4): # i = 0, 1, 3
                self.table.item(n, i).setFlags(self.table.item(n, i).flags() & ~Qt.ItemIsEditable)
            if i == 1: # i = 1
                self.table.item(n, i).setTextAlignment(Qt.AlignCenter)
        self.statusbar.showMessage(f"Добавлена {n + 1}-я строка")

    def __del_line(self):
        n = self.table.rowCount()
        if n > 0:
            self.table.removeRow(n - 1)
            self.statusbar.showMessage(f"Удалена {n}-я строка")
        self.__resize_table_2()

    def __open_save_system(self):
        n = self.table.rowCount()
        if n > 0:
            self.show_save_system = SaveSystem(self)
            self.show_save_system.show()

    def saving_system(self):
        n = self.table.rowCount()
        arr = dict((i, [self.table.item(i, j).text() for j in [2, 4]]) for i in range(n))
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить", f"user_files/{get_random_path()}.json", "JSON Files (*.json)")
        arr.update({"p0": list(map(str, self.__get_pk(0))), "p_acc": str(self.epsilon.value()), "f_count": str(self.f_num_count.value()), "acc_5": str(self.accuracy_5.value()), "acc_6": str(self.accuracy_6.value()), "method_5": self.method_5.currentText(), "method_6": self.method_6.currentText()})
        if path:
            st = f"txt/{path.replace('/', '!')}.txt"
            with open(path, "w", encoding="utf-8") as fille:
                with open(st, 'w', encoding="utf-8") as fil:
                    fil.write(self.comment.toPlainText())
                arr["comments"] = st
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
            for j in [2, 4]:
                item = QTableWidgetItem(table.item(i, j).text())
                self.tablle.setItem(i, (j // 2) - 1, item)
                self.tablle.item(i, (j // 2) - 1).setFlags(item.flags() & ~Qt.ItemIsEditable)

    def button_pressed(self):
        sender = self.sender()
        if sender and (sender.text() == "Сохранить"):
            self.parent.saving_system()
        self.close()

    def closeEvent(self, event):
        self.parent.setEnabled(True)


def get_a_b_R(arr):
    set_a_b = set()
    arr_for_R = list()
    for st in arr:
        br_l_i = 0
        f = False
        arr_for_R.append("")
        for i, sym in enumerate(st):
            if not f:
                arr_for_R[-1] += sym
            if (sym == '(') and (i != 0) and (st[i - 1].isdigit()):
                br_l_i = i
                f = True
            elif sym == ')' and f:
                num = float(st[br_l_i + 1:i])
                set_a_b.add(num)
                arr_for_R[-1] += str(num) + ")"
                f = False
    a, b = sorted(list(set_a_b))
    st_a, st_b = "(" + str(a) + ")", "(" + str(b) + ")"
    return a, b, list(elem.replace(st_a, "_a").replace(st_b, "_b") for elem in arr_for_R)


def get_f(arr):
    n = len(arr)
    symbols = sp.symbols(" ".join(f"x{i + 1}" for i in range(n)))
    return list(sympify(eq) for eq in arr)


def get_random_path():
    st = str(datetime.now())
    return st[:st.find('.')].replace(':', '.')    

# catch errors
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

if __name__ == "__main__":
    # show interface
    app = QApplication(sys.argv)
    #form = ShowGraphic(5, np.array([2., 0., -.5, .5]))
    form = Window()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())