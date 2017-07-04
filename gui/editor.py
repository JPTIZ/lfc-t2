import sys

from PyQt5.QtWidgets import (
        QAbstractItemView,
        QAction,
        QApplication,
        QFrame,
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMenu,
        QMessageBox,
        QPlainTextEdit,
        QPushButton,
        QTableWidget,
        QTableWidgetItem,
        QVBoxLayout,
        QWidget,
        qApp,
        )
from PyQt5.QtGui import (
        QKeySequence,
        )

from gui.parse_view import ParseTableViewer
from stub import (Grammar, first, follow, first_nt, grammar_from, accept,
                  as_proper)


class GLCEditor:
    def __init__(self):
        '''Initializes editor.'''
        self.grammar = Grammar()

        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.window.resize(800, 600)
        self.window.setWindowTitle('Context-Free Grammar Editor')

        self.central_widget = QWidget()
        self.window.setCentralWidget(self.central_widget)

        self.window.statusBar()
        self.window.statusBar().showMessage('Done.')

        def build_menu_bar():
            '''Builds menu bar items.'''
            menu_bar = self.window.menuBar()

            def build_file_menu():
                file_menu = menu_bar.addMenu('&File')
                new_cfg = file_menu.addAction('&New CFG')
                new_cfg.setShortcut('Ctrl+N')
                new_cfg.triggered.connect(self.new_cfg)

                file_menu.addSeparator()

                exit = file_menu.addAction('&Exit')
                exit.setShortcut('Alt+F4')
                exit.triggered.connect(qApp.quit)

            def build_transform_menu():
                transform_menu = menu_bar.addMenu('&Transform')
                make_proper = transform_menu.addAction('Make &Proper')
                make_proper.setShortcut('Ctrl+P')
                make_proper.triggered.connect(self.make_grammar_proper)

            def build_view_menu():
                view_menu = menu_bar.addMenu('&View')
                parse_table = view_menu.addAction('LL(1) &Parse Table')
                parse_table.setShortcut('Ctrl+L')
                parse_table.triggered.connect(self.show_parse_table)

            build_file_menu()
            build_transform_menu()
            build_view_menu()

        def build_contents():
            self.editor = QPlainTextEdit()
            self.editor.textChanged.connect(self.update_grammar)

            self.first_table = QTableWidget()
            self.first_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.follow_table = QTableWidget()
            self.follow_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.first_nt_table = QTableWidget()
            self.first_nt_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

            self.right_side = QVBoxLayout()

            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setFrameShadow(QFrame.Sunken)

            self.test_string_edit = QLineEdit()
            self.test_string_edit.returnPressed.connect(self.verify_test_string)
            self.verify_test_btn = QPushButton('Verify')
            self.verify_test_btn.clicked.connect(self.verify_test_string)

            self.right_side.addWidget(QLabel('Test string:'))
            self.right_side.addWidget(self.test_string_edit)
            self.right_side.addWidget(self.verify_test_btn)
            self.right_side.addWidget(separator)
            self.right_side.addWidget(QLabel('First'))
            self.right_side.addWidget(self.first_table)
            self.right_side.addWidget(QLabel('Follow'))
            self.right_side.addWidget(self.follow_table)
            self.right_side.addWidget(QLabel('First-NT'))
            self.right_side.addWidget(self.first_nt_table)

            contents = QHBoxLayout(self.central_widget)
            contents.addWidget(self.editor)
            contents.addLayout(self.right_side)

        build_menu_bar()
        build_contents()

    def new_cfg(self):
        '''Setups new Context-Free Grammar.'''
        if QMessageBox.question(self.window, 'Confirm new grammar', 'Discard unsaved changes and create new empty grammar?',
                QMessageBox.Yes, QMessageBox.No) == QMessageBox.Yes:
            self.editor.clear()
            self.test_string_edit.clear()
            self.first_table.clear()
            self.follow_table.clear()
            self.first_nt_table.clear()
            self.grammar = Grammar()
            print('(stub!) Creating CFG...')

    def make_grammar_proper(self):
        '''Transforms current grammar into a proper grammar.'''
        self.grammar = as_proper(self.grammar)

    def verify_test_string(self):
        '''Verifies if test input string belongs to language.'''
        print(f'(stub!) Verifying {self.test_string_edit.text()}...')
        if accept(self.grammar, self.test_string_edit.text()):
            result = 'Accept!'
        else:
            result = 'Reject!'
        QMessageBox.information(self.window, 'Test result', result, QMessageBox.Ok)

    def show_parse_table(self):
        '''Shows LL(1) parse table.'''
        print('(stub!) Showing LL(1) parse table...')
        ParseTableViewer(self.window, self.grammar).show()

    def update_grammar(self):
        '''Updates grammar with given input and then updates UI.
           If it fails to generate the grammar, nothing happens.'''
        try:
            self.grammar = grammar_from(self.editor.toPlainText())
            self.window.statusBar().showMessage('Done.')
        except:
            self.window.statusBar().showMessage('Failed to generate grammar. Check your syntax.')
            return
        self.update_tables()

    def update_tables(self):
        '''Updates first, follow and firstNT tables.'''
        print('(stub!) Updating tables...')
        self.update_first_table()
        self.update_follow_table()
        self.update_first_nt_table()

    def update_first_table(self):
        self.first_table.clear()
        non_terminals = ['S'] + sorted(self.grammar.non_terminals() - {'S'})
        firsts = first(self.grammar)

        self.first_table.setRowCount(len(non_terminals))
        self.first_table.setColumnCount(2)

        for row, symbol in enumerate(non_terminals):
            self.first_table.setItem(row, 0, QTableWidgetItem(symbol))
            self.first_table.setItem(row, 1, QTableWidgetItem(str(firsts[symbol])))

        self.first_table.resizeColumnsToContents()

    def update_follow_table(self):
        self.follow_table.clear()
        non_terminals = ['S'] + sorted(self.grammar.non_terminals() - {'S'})
        follows = follow(self.grammar)

        self.follow_table.setRowCount(len(non_terminals))
        self.follow_table.setColumnCount(2)

        for row, symbol in enumerate(non_terminals):
            self.follow_table.setItem(row, 0, QTableWidgetItem(symbol))
            self.follow_table.setItem(row, 1, QTableWidgetItem(str(follows[symbol])))

        self.follow_table.resizeColumnsToContents()

    def update_first_nt_table(self):
        self.first_nt_table.clear()
        non_terminals = ['S'] + sorted(self.grammar.non_terminals() - {'S'})
        first_nts = first_nt(self.grammar)

        self.first_nt_table.setRowCount(len(non_terminals))
        self.first_nt_table.setColumnCount(2)

        for row, symbol in enumerate(non_terminals):
            self.first_nt_table.setItem(row, 0, QTableWidgetItem(symbol))
            self.first_nt_table.setItem(row, 1, QTableWidgetItem(str(first_nts[symbol])))

        self.first_nt_table.resizeColumnsToContents()

    def run(self):
        '''Runs the editor.'''
        self.window.show()
        self.app.exec_()
