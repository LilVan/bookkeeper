from PySide6.QtWidgets import QVBoxLayout, QLabel,  QWidget, QGridLayout, QComboBox, QLineEdit, QPushButton, QMessageBox
from PySide6 import QtCore, QtWidgets
from bookkeeper.view.categories_view import CategoryDialog
from datetime import datetime


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data
        self.header_names = list(data[0].__dataclass_fields__.keys())

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header_names[section]
        return super().headerData(section, orientation, role)

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            fields = list(self._data[index.row()].__dataclass_fields__.keys())
            return self._data[index.row()].__getattribute__(fields[index.column()])

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0].__dataclass_fields__)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.item_model = None
        self.setWindowTitle("Программа для ведения бюджета")

        self.layout = QVBoxLayout()

        self.layout.addWidget(QLabel('Последние расходы'))

        self.expenses_grid = QtWidgets.QTableView()
        self.expenses_grid.clicked.connect(self.get_clicked)
        self.layout.addWidget(self.expenses_grid)

        self.layout.addWidget(QLabel('Бюджет'))

        self.expenses_table = QtWidgets.QTableWidget(2, 3)
        self.expenses_table.setColumnCount(2)
        self.expenses_table.setRowCount(3)
        self.expenses_table.setHorizontalHeaderLabels(
            "Сумма Бюджет".split())
        self.expenses_table.setVerticalHeaderLabels(
            "День Месяц Год".split())

        hheader = self.expenses_table.horizontalHeader()
        vheader = self.expenses_table.verticalHeader()
        for i in range(3):
            hheader.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
            vheader.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
        self.start_data = [['0', '0'], ['0', '0'], ['0', '0']]
        self.add_data(self.start_data)

        self.expenses_table.keyReleaseEvent = self.table_key_release_event

        self.layout.addWidget(self.expenses_table)

        self.bottom_controls = QGridLayout()

        self.bottom_controls.addWidget(QLabel('Сумма'), 0, 0)

        self.amount_line_edit = QLineEdit()

        self.bottom_controls.addWidget(self.amount_line_edit, 0, 1)  # TODO: добавить валидатор
        self.bottom_controls.addWidget(QLabel('Категория'), 1, 0)

        self.category_dropdown = QComboBox()

        self.bottom_controls.addWidget(self.category_dropdown, 1, 1)

        self.category_edit_button = QPushButton('Редактировать')
        self.bottom_controls.addWidget(self.category_edit_button, 1, 2)
        self.category_edit_button.clicked.connect(self.show_cats_dialog)

        self.expense_add_button = QPushButton('Добавить')
        self.bottom_controls.addWidget(self.expense_add_button, 2, 1)

        self.expense_delete_button = QPushButton('Удалить')
        self.bottom_controls.addWidget(self.expense_delete_button, 2, 2)  # TODO: improve buttons layout

        self.bottom_widget = QWidget()
        self.bottom_widget.setLayout(self.bottom_controls)

        self.layout.addWidget(self.bottom_widget)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)

        self.setCentralWidget(self.widget)

    def get_clicked(self):
        selected = self.__get_selected_row_indices()
        day_total = 0
        month_total = 0
        year_total = 0

        for i in range(self.item_model.rowCount(0)):
            if datetime.fromisoformat(str(self.item_model._data[selected[0]].expense_date)).year == \
                    datetime.fromisoformat(str(self.item_model._data[i].expense_date)).year:
                year_total += self.item_model._data[i].amount

                if datetime.fromisoformat(str(self.item_model._data[selected[0]].expense_date)).month == \
                        datetime.fromisoformat(str(self.item_model._data[i].expense_date)).month:
                    month_total += self.item_model._data[i].amount

                    if datetime.fromisoformat(str(self.item_model._data[selected[0]].expense_date)).day == \
                            datetime.fromisoformat(str(self.item_model._data[i].expense_date)).day:
                        day_total += self.item_model._data[i].amount

        data = [[str(day_total)]] + [[str(month_total)]] + [[str(year_total)]]
        self.add_data(data)

    def set_expense_table(self, data):
        if data:
            self.item_model = TableModel(data)
            self.expenses_grid.setModel(self.item_model)
            self.expenses_grid.resizeColumnsToContents()
            grid_width = sum([self.expenses_grid.columnWidth(x) for x in range(0, self.item_model.columnCount(0) + 1)])
            self.setFixedSize(grid_width + 80, 600)

    def set_category_dropdown(self, data):
        for c in data:
            self.category_dropdown.addItem(c.name, c.pk)  # TODO несколько одинаковых категорий

    def on_expense_add_button_clicked(self, slot):
        self.expense_add_button.clicked.connect(slot)

    def on_expense_delete_button_clicked(self, slot):
        self.expense_delete_button.clicked.connect(slot)

    def get_amount(self) -> float:
        return float(self.amount_line_edit.text())  # TODO: обработка исключений

    def __get_selected_row_indices(self) -> list[int]:
        return list(set([qmi.row() for qmi in self.expenses_grid.selectionModel().selection().indexes()]))

    def get_selected_expenses(self) -> list[int] | None:
        idx = self.__get_selected_row_indices()
        if not idx:
            return None
        return [self.item_model._data[i].pk for i in idx]

    def get_selected_cat(self) -> int:
        return self.category_dropdown.itemData(self.category_dropdown.currentIndex())

    def on_category_edit_button_clicked(self, slot):
        self.category_edit_button.clicked.connect(slot)

    def show_cats_dialog(self, data):
        if data:
            cat_dlg = CategoryDialog(data)
            cat_dlg.setWindowTitle('Редактирование категорий')
            cat_dlg.setGeometry(300, 100, 600, 300)
            cat_dlg.exec_()

    def add_data(self, data):
        for i, row in enumerate(data):
            for j, x in enumerate(row):
                self.expenses_table.setItem(
                    i, j,
                    QtWidgets.QTableWidgetItem(x.capitalize())
                )

    def table_key_release_event(self, event):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Превышение бюджета")
        msg_box.setStandardButtons(QMessageBox.Ok)
        if float(self.expenses_table.item(0, 0).text()) > float(self.expenses_table.item(0, 1).text()):
            msg_box.setText("Внимание! Превышен бюджет за день!")
            msg_box.exec()
        elif float(self.expenses_table.item(1, 0).text()) > float(self.expenses_table.item(1, 1).text()):
            msg_box.setText("Внимание! Превышен бюджет за месяц!")
            msg_box.exec()
        elif float(self.expenses_table.item(2, 0).text()) > float(self.expenses_table.item(2, 1).text()):
            msg_box.setText("Внимание! Превышен бюджет за год!")
            msg_box.exec()
