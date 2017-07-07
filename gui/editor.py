import sys
import traceback
import os

from PyQt5.QtWidgets import (
        QAbstractItemView,
        QAction,
        QApplication,
        QFileDialog,
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
        QShortcut,
        QTableWidget,
        QTableWidgetItem,
        QVBoxLayout,
        QWidget,
        qApp,
        )
from PyQt5.QtGui import (
        QKeySequence,
        )

from gui.viewers import ParseTableViewer, ParseResultDialog, ParseStepViewer
from cfg import CFG
from stub import (first, follow, first_nt, accept,
                  as_proper)


def sorted_set_str(set_):
    return str(sorted(set_)).replace('[', '{').replace(']', '}')


class GLCEditor:
    def __init__(self):
        '''Initializes editor.'''
        self.grammar = None
        self.filename = None

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

                load_cfg = file_menu.addAction('&Load CFG')
                load_cfg.setShortcut('Ctrl+O')
                load_cfg.triggered.connect(self.load_cfg)

                save_cfg = file_menu.addAction('&Save CFG')
                save_cfg.setShortcut('Ctrl+S')
                save_cfg.triggered.connect(self.save_cfg)

                save_cfg_as = file_menu.addAction('Save CFG &As...')
                save_cfg_as.setShortcut('Ctrl+Shift+S')
                save_cfg_as.triggered.connect(self.save_cfg_as)

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
                self.parse_table_item = view_menu.addAction('LL(1) &Parse Table')
                self.parse_table_item.setShortcut('Ctrl+L')
                self.parse_table_item.triggered.connect(self.show_parse_table)

            build_file_menu()
            build_transform_menu()
            build_view_menu()

        def build_contents():
            self.editor = QPlainTextEdit()
            self.editor.setTabChangesFocus(True)
            self.editor.textChanged.connect(self.enable_run_grammar)

            self.run_grammar_btn = QPushButton('Run grammar')
            self.run_grammar_btn.clicked.connect(self.update_grammar)
            self.run_grammar_btn.setEnabled(False)

            run_btn_shortcut = QShortcut(QKeySequence('Ctrl+Return'), self.window)
            run_btn_shortcut.activated.connect(self.update_grammar)

            left_side = QVBoxLayout()
            left_side.addWidget(self.editor)
            left_side.addWidget(self.run_grammar_btn)

            self.first_table = QTableWidget()
            self.first_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.follow_table = QTableWidget()
            self.follow_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.first_nt_table = QTableWidget()
            self.first_nt_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

            right_side = QVBoxLayout()

            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setFrameShadow(QFrame.Sunken)

            self.test_string_edit = QLineEdit()
            self.test_string_edit.returnPressed.connect(self.verify_test_string)
            self.verify_test_btn = QPushButton('Verify')
            self.verify_test_btn.clicked.connect(self.verify_test_string)

            right_side.addWidget(QLabel('Test string:'))
            right_side.addWidget(self.test_string_edit)
            right_side.addWidget(self.verify_test_btn)
            right_side.addWidget(separator)
            right_side.addWidget(QLabel('First'))
            right_side.addWidget(self.first_table)
            right_side.addWidget(QLabel('Follow'))
            right_side.addWidget(self.follow_table)
            right_side.addWidget(QLabel('First-NT'))
            right_side.addWidget(self.first_nt_table)

            contents = QHBoxLayout(self.central_widget)
            contents.addLayout(left_side)
            contents.addLayout(right_side)

        build_menu_bar()
        build_contents()
        self.update_grammar()

    def new_cfg(self):
        '''Setups new Context-Free Grammar.'''
        if QMessageBox.question(self.window,
                                'Confirm new grammar',
                                'Discard unsaved changes and create new empty grammar?',
                QMessageBox.Yes, QMessageBox.No) == QMessageBox.Yes:
            self.editor.clear()
            self.test_string_edit.clear()
            self.first_table.clear()
            self.follow_table.clear()
            self.first_nt_table.clear()
            self.grammar = None
            self.update_grammar()

    def load_cfg(self):
        '''Shows file select dialog and loads GFC.'''
        dialog = QFileDialog(self.window)
        filename, _ = dialog.getOpenFileName(self.window, 'Open CFG', filter='CFG files (*.cfg)')
        if not filename:
            return
        self.filename = filename
        self.window.setWindowTitle(f'{self.filename} - Context-Free Grammar Editor')
        with open(filename) as f:
            self.editor.setPlainText(f.read())

    def save_cfg(self):
        '''Saves GFC. If no filename exists, shows save dialog.'''
        if self.filename == None:
            self.save_cfg_as()
            return
        with open(self.filename, 'w') as f:
            f.write(self.editor.toPlainText())
            f.close()

    def save_cfg_as(self):
        '''Shows file select dialog and saves GFC.'''
        dialog = QFileDialog(self.window)
        filename, _ = dialog.getSaveFileName(self.window,
                                             'Open CFG',
                                             filter='CFG files (*.cfg)')
        if not filename:
            return
        self.filename = os.path.splitext(filename)[0] + '.cfg'
        self.window.setWindowTitle(f'{self.filename} - Context-Free Grammar Editor')
        with open(self.filename, 'w') as f:
            f.write(self.editor.toPlainText())
            f.close()

    def make_grammar_proper(self):
        '''Transforms current grammar into a proper grammar.'''
        self.grammar = as_proper(self.grammar)

    def verify_test_string(self):
        '''Verifies if test input string belongs to language.'''
        if self.grammar is None:
            result = 'Grammar input not valid.'
        steps = []
        try:
            for step in self.grammar.parse(self.test_string_edit.text()):
                steps.append(step)
            result = 'Accept'
        except ValueError as e:
            result = 'Reject'

        if ParseResultDialog(self.window, result).show() == 1:
            ParseStepViewer(self.window, steps).show()

    def show_parse_table(self):
        '''Shows LL(1) parse table.'''
        if not self.grammar.is_ll1():
            QMessageBox.information(self.window,
                                    'Error showing parse table',
                                    'Grammar is not LL(1).',
                                    QMessageBox.Ok)
            return
        ParseTableViewer(self.window, self.grammar).show()

    def enable_run_grammar(self):
        '''Enables run grammar button.'''
        self.run_grammar_btn.setEnabled(True)

    def update_grammar(self):
        '''Updates grammar with given input and then updates UI.
           If it fails to generate the grammar, nothing happens.'''
        try:
            self.grammar = CFG.load(self.editor.toPlainText().splitlines())
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            self.window.statusBar().showMessage('Failed to generate grammar. Check your syntax.')
            self.parse_table_item.setEnabled(False)
            return

        self.window.statusBar().showMessage('Done.')
        self.parse_table_item.setEnabled(True)
        self.run_grammar_btn.setEnabled(False)
        try:
            self.update_tables()
        except RecursionError as e:
            self.window.statusBar().showMessage('Failed to generate grammar tables: Recursion depth overflow.')
            self.parse_table_item.setEnabled(False)
            return

    def update_tables(self):
        '''Updates first, follow and firstNT tables.'''
        self.update_first_table()
        self.update_follow_table()
        self.update_first_nt_table()

    def update_first_table(self):
        '''Updates table containing the `first(NT)` of each non-terminal NT.'''
        self.first_table.clear()
        s = self.grammar.initial_symbol
        non_terminals = [s] + sorted(self.grammar.nonterminals - {s})
        firsts = first(self.grammar)

        self.first_table.setRowCount(len(non_terminals))
        self.first_table.setColumnCount(2)

        for row, symbol in enumerate(non_terminals):
            item = sorted_set_str(firsts[symbol])
            self.first_table.setItem(row, 0, QTableWidgetItem(symbol))
            self.first_table.setItem(row, 1, QTableWidgetItem(item))

        self.first_table.resizeColumnsToContents()

    def update_follow_table(self):
        '''Updates table containing the `follow(NT)` of each non-terminal
           NT.'''
        self.follow_table.clear()
        s = self.grammar.initial_symbol
        non_terminals = [s] + sorted(self.grammar.nonterminals - {s})
        follows = follow(self.grammar)

        self.follow_table.setRowCount(len(non_terminals))
        self.follow_table.setColumnCount(2)

        for row, symbol in enumerate(non_terminals):
            item = sorted_set_str(follows[symbol])
            self.follow_table.setItem(row, 0, QTableWidgetItem(symbol))
            self.follow_table.setItem(row, 1, QTableWidgetItem(item))

        self.follow_table.resizeColumnsToContents()

    def update_first_nt_table(self):
        '''Updates table containing the `firstNT(NT)` of each non-terminal
           NT.'''
        self.first_nt_table.clear()
        s = self.grammar.initial_symbol
        non_terminals = [s] + sorted(self.grammar.nonterminals - {s})
        first_nts = first_nt(self.grammar)

        self.first_nt_table.setRowCount(len(non_terminals))
        self.first_nt_table.setColumnCount(2)

        for row, symbol in enumerate(non_terminals):
            item = sorted_set_str(first_nts[symbol])
            self.first_nt_table.setItem(row, 0, QTableWidgetItem(symbol))
            self.first_nt_table.setItem(row, 1, QTableWidgetItem(item))

        self.first_nt_table.resizeColumnsToContents()

    def run(self):
        '''Runs the editor.'''
        self.window.show()
        self.app.exec_()
