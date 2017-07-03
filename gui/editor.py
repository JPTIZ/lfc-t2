import sys

from PyQt5.QtWidgets import (qApp, QApplication, QMainWindow, QWidget,
        QGridLayout, QMenu, QAction)
from PyQt5.QtGui import QKeySequence


class GLCEditor:
    def __init__(self):
        '''Initializes editor.'''
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.window.resize(800, 600)
        self.window.setWindowTitle('Context-Free Grammar Editor')

        self.central_widget = QWidget()
        self.window.setCentralWidget(self.central_widget)

        grid = QGridLayout(self.central_widget)
        grid.setSpacing(10)

        def build_menu_bar():
            '''Builds menu bar items.'''
            menu_bar = self.window.menuBar()
            file_menu = menu_bar.addMenu('&File')
            new_cfg = file_menu.addAction('&New CFG')
            new_cfg.setShortcut('Ctrl+N')
            new_cfg.triggered.connect(self.new_cfg)

            file_menu.addSeparator()

            exit = file_menu.addAction('&Exit')
            exit.setShortcut('Alt+F4')
            exit.triggered.connect(qApp.quit)

        build_menu_bar()

    def new_cfg(self):
        '''Setups new Context-Free Grammar.'''
        print('(stub!) Creating CFG...')

    def run(self):
        '''Runs the editor.'''
        self.window.show()
        self.app.exec_()
