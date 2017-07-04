import sys

from PyQt5.QtWidgets import (
        QAction,
        QApplication,
        QGridLayout,
        QLabel,
        QHBoxLayout,
        QVBoxLayout,
        QMainWindow,
        QMenu,
        QPlainTextEdit,
        QTableWidget,
        QWidget,
        qApp,
        )
from PyQt5.QtGui import QKeySequence


class GLCEditor:
    def __init__(self):
        '''Initializes editor.'''

        class Grammar:
            '''Stub grammar.'''
            def make_proper(self):
                print('(stub!) making grammar proper')
                return self
        self.grammar = Grammar()

        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.window.resize(800, 600)
        self.window.setWindowTitle('Context-Free Grammar Editor')

        self.central_widget = QWidget()
        self.window.setCentralWidget(self.central_widget)

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
                make_proper.triggered.connect(self.grammar.make_proper)

            build_file_menu()
            build_transform_menu()

        def build_contents():
            self.editor = QPlainTextEdit()
            self.first_table = QTableWidget()
            self.follow_table = QTableWidget()
            self.first_nt_table = QTableWidget()

            self.right_side = QVBoxLayout()
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
        print('(stub!) Creating CFG...')

    def run(self):
        '''Runs the editor.'''
        self.window.show()
        self.app.exec_()
