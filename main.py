import sqlite3
import sys

from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem


class CoffeeShop(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)

        self.titles = []

        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.load_database()

    def load_database(self):
        connection = sqlite3.connect('coffee.sqlite')
        cursor = connection.cursor()
        result = cursor.execute("""SELECT coffee_information.id, coffee_information.sort_name, 
                                    roast_degree.degree_value, coffee_information.is_powder,
                                    coffee_information.taste, coffee_information.price, coffee_information.volume
                                    FROM
                                        coffee_information
                                    LEFT JOIN roast_degree
                                        ON roast_degree.id = coffee_information.roast;""").fetchall()
        connection.close()
        self.table.setRowCount(len(result))
        if result:
            self.titles = ['ID', 'название сорта', 'степень обжарки', 'молотый/в зернах',
                           'описание вкуса', 'цена', 'объем упаковки (в граммах)']
            self.table.setColumnCount(len(result[0]))
            self.table.setHorizontalHeaderLabels(self.titles)
            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    item = QTableWidgetItem(str(val))
                    self.table.setItem(i, j, item)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CoffeeShop()
    ex.show()
    sys.exit(app.exec_())
