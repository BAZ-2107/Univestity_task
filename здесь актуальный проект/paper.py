import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# 1. Создаем класс для холста, на котором будем рисовать
class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        # Создаем фигуру и оси
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)
        
        # Инициализируем холст
        super(PlotCanvas, self).__init__(self.figure)
        self.setParent(parent)
        
        # Вызываем функцию построения графика
        self.plot()

    def plot(self):
        # 2. Готовим данные
        x = np.linspace(-10, 10, 1000)  # 1000 точек от -10 до 10
        y = np.sin(x)  # Здесь можно задать любую функцию, например, x**2, np.cos(x) и т.д.
        
        # 3. Рисуем график
        self.axes.clear()  # Очищаем оси, чтобы избежать наложений
        self.axes.plot(x, y, 'b-', linewidth=2)  # 'b-' означает синюю сплошную линию
        self.axes.set_title("График функции y = sin(x)")
        self.axes.set_xlabel("Ось X")
        self.axes.set_ylabel("Ось Y")
        self.axes.grid(True)  # Включаем сетку
        self.figure.tight_layout()  # Оптимизируем расположение элементов
        self.draw()  # Перерисовываем холст

# 4. Главное окно PyQt5
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("График функции")
        self.setGeometry(100, 100, 800, 600)
        
        # Создаем виджет-холст и устанавливаем его центральным виджетом
        canvas = PlotCanvas(self)
        self.setCentralWidget(canvas)

# Запуск приложения
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())