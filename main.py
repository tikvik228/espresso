from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtWidgets import QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6 import uic
import sqlite3
import sys

connection = sqlite3.connect("coffee.db")
cursor = connection.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS coffee_table (
coffee_id INTEGER PRIMARY KEY AUTOINCREMENT,
sort_name TEXT,
roasting_degree INTEGER,
beans_or_ground TEXT,
taste TEXT,
price REAL,
volume REAL)
''')

connection.commit()
connection.close()


class CoffeeLibrary(QMainWindow):
    """Класс библиотеки"""
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.setWindowTitle("кофе")
        self.myTableWidget.setFont(QFont('Cascadia Code SemiBold', 10))
        self.comboBox.addItems(["Добавлению", "Цене", "Объему", "Степени прожарки", "Названию"])
        self.ground_check.setChecked(True)
        self.beans_check.setChecked(True)
        self.ground_check.stateChanged.connect(self.create_table)
        self.beans_check.stateChanged.connect(self.create_table)
        self.comboBox.activated.connect(self.create_table)
        self.myTableWidget.setStyleSheet("QTableWidget::item:selected{ background-color: white}")
        self.myTableWidget.horizontalHeader().setDefaultSectionSize(210)
        self.myTableWidget.verticalHeader().setDefaultSectionSize(280)
        self.myTableWidget.setHorizontalHeaderLabels(("","","",""))
        self.myTableWidget.setVerticalHeaderLabels(("","","",""))
        central_widget = QWidget()
        central_widget.setLayout(self.gridLayout)
        self.setCentralWidget(central_widget)
        self.setGeometry(100, 100, 875, 500)

        self.connection = sqlite3.connect("coffee.db")
        self.cursor = self.connection.cursor()
        self.create_table()

    def sort_data(self):
        """Отвечает за сортировку книг по заданным признакам, возвращает отсортированные
        id в метод create_table"""
        if self.comboBox.currentText() == "Добавлению":
            order, sorting = "coffee_id", "DESC"
        elif self.comboBox.currentText() == "Цене":
            order, sorting = "price", "ASC"
        elif self.comboBox.currentText() == "Объему":
            order, sorting = "volume", "DESC"
        elif self.comboBox.currentText() == "Степени прожарки":
            order, sorting = "roasting_degree", "ASC"
        elif self.comboBox.currentText() == "Названию":
            order, sorting = "sort_name", "ASC"

        if self.beans_check.isChecked() and self.ground_check.isChecked():
            self.cursor.execute(f'SELECT coffee_id FROM coffee_table ORDER BY {order} {sorting}')
        elif self.beans_check.isChecked() and not self.ground_check.isChecked():
            self.cursor.execute(f'SELECT coffee_id FROM coffee_table WHERE beans_or_ground = "зерновой" ORDER BY {order} {sorting}')
        elif not self.beans_check.isChecked() and self.ground_check.isChecked():
            self.cursor.execute(f'SELECT coffee_id FROM coffee_table WHERE beans_or_ground = "молотый" ORDER BY {order} {sorting}')
        result = list(map(lambda x: x[0], self.cursor.fetchall()))
        self.connection.commit()
        return result

    def create_table(self):
        """Пересоздает таблицу библиотеки"""
        self.myTableWidget.clear()
        self.results = self.sort_data()
        if not self.results:
            self.statusBar().showMessage("Кофе не найден")
            return None
        self.statusBar().clearMessage()
        if len(self.results) % 4 == 0:
            kolv_rows = len(self.results) // 4
        else:
            kolv_rows = len(self.results) // 4 + 1

        self.myTableWidget.setColumnCount(4)
        self.myTableWidget.setRowCount(kolv_rows)

        for num, i in enumerate(self.results):
            self.cursor.execute(f"SELECT sort_name, roasting_degree, taste, price, volume FROM coffee_table WHERE coffee_id = {i}")
            sort_name, roasting, taste, price, volume = self.cursor.fetchall()[0]  # краткая информация
            sort_name = "Cорт: " + sort_name
            if len(sort_name) > 25:
                sort_name = sort_name[:22] + "..."
            f_taste = taste.split()
            stroki = [""]
            count = 25
            for word in f_taste:
                if count - len(word) >= 0:
                    stroki[-1] += word + " "
                    count -= len(word) + 1
                else:
                    count = 25 - len(word) - 1
                    stroki.append(word + " ")
            formated_taste = "Вкус:\n" + "\n".join(stroki)
            if roasting == 0:
                formated_roasting = "Обжарка: легкая"
            elif roasting == 1:
                formated_roasting = "Обжарка: средняя"
            else:
                formated_roasting = "Обжарка: сильная"

            coffee_layout = QVBoxLayout()  # собираем информацию в лэйаут
            coffee_layout.addWidget(QLabel("\n\n".join([sort_name, formated_roasting, formated_taste,
                                                        "Цена: " + str(price), "Объем: " + str(volume) + " л"])))
            coffee_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cellWidget = QWidget()
            cellWidget.setLayout(coffee_layout)
            self.myTableWidget.setCellWidget(num // 4, num % 4, cellWidget)

        self.connection.commit()

    def closeEvent(self, event):
        self.connection.close()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = CoffeeLibrary()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())