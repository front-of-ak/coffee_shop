import sqlite3
import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, \
    QTableWidgetItem, QDialog
from main_win import Ui_MainWindow as mW
from addEditCoffeeForm import Ui_Dialog as dF


class CoffeeShop(mW, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.titles = []
        self.coffee_dialog = None

        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.buttons.buttonClicked.connect(self.add_edit)
        self.load_database()

    def load_database(self):
        connection = sqlite3.connect('data/coffee.sqlite')
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

    def add_edit(self, btn):
        self.statusbar.showMessage('')

        rows = list(set([i.row() for i in self.table.selectedItems()]))
        ids = [self.table.item(i, 0).text() for i in rows]
        if btn.text() == 'Добавить':
            self.coffee_dialog = AddEditCoffee(self)
            self.coffee_dialog.show()
        elif btn.text() == 'Редактировать':
            if ids:
                self.coffee_dialog = AddEditCoffee(self, ids[0])
                self.coffee_dialog.show()
            else:
                self.statusbar.showMessage('Выберите редактируемый сорт')


class AddEditCoffee(dF, QDialog):
    def __init__(self, main_window, ids=None):
        super().__init__()
        self.setupUi(self)

        self.main_win = main_window

        if ids is not None:
            self.ids = ids
        else:
            self.ids = False

        connection = sqlite3.connect('data/coffee.sqlite')
        cursor = connection.cursor()

        self.roasts = cursor.execute("""SELECT * FROM roast_degree""").fetchall()
        for i in self.roasts:
            self.roast.addItem(i[1])
        self.is_powder.addItem('молотый')
        self.is_powder.addItem('в зёрнах')

        if self.ids:
            self.id = self.ids
            self.form_filler = cursor.execute("""SELECT coffee_information.sort_name, 
                                        roast_degree.degree_value, coffee_information.is_powder,
                                        coffee_information.taste, coffee_information.price, coffee_information.volume
                                        FROM
                                            coffee_information
                                        LEFT JOIN roast_degree
                                            ON roast_degree.id = coffee_information.roast
                                        WHERE coffee_information.id = ?""", (ids,)).fetchone()
            self.sort_name.setText(self.form_filler[0])
            self.roast.setCurrentText(self.form_filler[1])
            self.is_powder.setCurrentText(self.form_filler[2])
            self.taste.setPlainText(self.form_filler[3])
            self.price.setValue(int(self.form_filler[4]))
            self.volume.setValue(int(self.form_filler[5]))
            self.ok_btn.clicked.connect(self.ok_ret_edit)
        connection.close()

        if not ids:
            self.ok_btn.clicked.connect(self.ok_ret_add)

    def ok_ret_add(self):
        connection = sqlite3.connect('data/coffee.sqlite')
        cursor = connection.cursor()

        for i in self.roasts:
            if i[1] == self.roast.currentText():
                roast = i[0]

        if self.sort_name.text() and not self.sort_name.text().isdigit() and self.taste.toPlainText():
            cursor.execute("""INSERT INTO coffee_information(sort_name, roast, is_powder, taste, price, volume)
                              VALUES (?, ?, ?, ?, ?, ?)""", (self.sort_name.text(), roast,
                                                             self.is_powder.currentText(), self.taste.toPlainText(),
                                                             self.price.value(), self.volume.value()))
            connection.commit()
            connection.close()
            self.close()
        else:
            self.error_lbl.setText('Введите корректные данные')
        self.main_win.load_database()

    def ok_ret_edit(self):
        connection = sqlite3.connect('data/coffee.sqlite')
        cursor = connection.cursor()

        for i in self.roasts:
            if i[1] == self.roast.currentText():
                roast = i[0]

        if self.sort_name.text() and not self.sort_name.text().isdigit() and self.taste.toPlainText():
            cursor.execute("""UPDATE coffee_information
                              SET sort_name = ?,
                                   roast = ?,
                                   is_powder = ?,
                                   taste = ?,
                                   price = ?,
                                   volume = ?
                              WHERE id = ?""", (self.sort_name.text(), roast,
                                                self.is_powder.currentText(), self.taste.toPlainText(),
                                                self.price.value(), self.volume.value(), self.id))
            connection.commit()
            connection.close()
            self.close()
        else:
            self.error_lbl.setText('Введите корректные данные')
        self.main_win.load_database()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CoffeeShop()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
