from PyQt5.QtWidgets import (
        QAbstractScrollArea,
        QAbstractItemView,
        QDialog,
        QMessageBox,
        QPushButton,
        QTableWidget,
        QTableWidgetItem,
        QVBoxLayout,
        )

import string
from stub import build_parse_table


class ParseTableViewer(QDialog):
    def __init__(self, parent, grammar):
        super(QDialog, self).__init__(parent)
        self.setModal(True)
        self.setWindowTitle('LL(1) Parsing Table')
        self.resize(640, 480)

        layout = QVBoxLayout(self)

        self.table = QTableWidget()

        def build_table():
            parse = build_parse_table(grammar)

            states = [grammar.initial_symbol] + sorted(grammar.nonterminals - {grammar.initial_symbol})

            symbols = sorted(grammar.terminals) + ['$']

            self.table.setRowCount(len(states))
            self.table.setColumnCount(len(symbols) + 1)

            self.table.setHorizontalHeaderLabels(['NT'] + symbols)
            self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

            for row, state in enumerate(states):
                self.table.setItem(row, 0, QTableWidgetItem(state))

            for (state, symbol) in parse:
                self.table.setItem(states.index(state),
                                   symbols.index(symbol) + 1,
                                   QTableWidgetItem(f'{parse[(state, symbol)]}'))

        build_table()
        layout.addWidget(self.table)


class ParseResultDialog(QDialog):
    def __init__(self, parent=None, text='No message'):
        super(ParseResultDialog, self).__init__(parent)

        self.msg_box = QMessageBox()
        self.msg_box.setWindowTitle('Test result')
        self.msg_box.setText(text)
        self.msg_box.addButton(QPushButton('&Ok'), QMessageBox.AcceptRole)
        self.msg_box.addButton(QPushButton('&Steps'), QMessageBox.NoRole)

    def show(self):
        return self.msg_box.exec_()

class ParseStepViewer(QDialog):
    def __init__(self, parent, steps):
        super(ParseStepViewer, self).__init__(parent)
        self.setModal(True)
        self.setWindowTitle('Parse steps view.')
        self.resize(640, 480)

        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setRowCount(len(steps))
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.table.setHorizontalHeaderLabels(['Stack', 'Input'])

        for row, (right, left) in enumerate(steps):
            self.table.setItem(row, 0, QTableWidgetItem(''.join(left)))
            self.table.setItem(row, 1, QTableWidgetItem(''.join(right) + '$'))

        self.table.resizeColumnsToContents()

        ok_btn = QPushButton('&Close')
        ok_btn.clicked.connect(self.close)

        layout.addWidget(self.table)
        layout.addWidget(ok_btn)
