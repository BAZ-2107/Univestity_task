import sys
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene
from PyQt5.QtCore import QByteArray
from PyQt5.QtGui import QPixmap
from io import BytesIO

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Matplotlib в QGraphicsView")

        # Создаем график в matplotlib
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
        ax.set_title("Пример графика")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        
        # Сохраняем график в байтовый буфер
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        
        # Создаем QPixmap из буфера
        pixmap = QPixmap()
        pixmap.loadFromData(buf.getvalue())
        
        # Создаем сцену и добавляем pixmap
        scene = QGraphicsScene()
        scene.addPixmap(pixmap)
        
        # Настраиваем QGraphicsView
        view = QGraphicsView(scene)
        
        self.setCentralWidget(view)
        self.resize(800, 600)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())