from PyQt5.QtWidgets import (
        QDialog,
        QTableWidget,
        QTableWidgetItem,
        QVBoxLayout,
        QAbstractItemView
        )

import string
from stub import build_parse_table


class ParseTableViewer(QDialog):
    def __init__(self, parent, grammar):
        super(QDialog, self).__init__(parent)
        self.setModal(True)
        self.setWindowTitle('LL(1) Parse Table')
        self.resize(640, 480)

        layout = QVBoxLayout(self)

        self.table = QTableWidget()

        def build_table():
            parse = build_parse_table(grammar)
            alphabet = string.ascii_lowercase + '$' + string.ascii_uppercase

            #sorted(parse, key=lambda key: (key[0], alphabet.index(key[1])))

            states = sorted({i[0] for i in parse})
            symbols = sorted({i[1] for i in parse}, key=lambda key: alphabet.index(key))

            self.table.setRowCount(len(states))
            self.table.setColumnCount(len(symbols))

            self.table.setHorizontalHeaderLabels(symbols)
            self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

            for (state, symbol) in parse:
                self.table.setItem(states.index(state), symbols.index(symbol), QTableWidgetItem(str(parse[(state, symbol)])))

        build_table()
        layout.addWidget(self.table)
