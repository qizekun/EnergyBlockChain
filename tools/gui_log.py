
"""
GUI for PYPOWER
Message log tab user interface

"""

import os, sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
import numpy as np

class log_ui(QtGui.QVBoxLayout): 
    
    def setup(self, window):   
        """Setup for message log tab"""
        font = QtGui.QFont("Courier New",10)
        
        self.main_window = window        
        
        hbox = QtGui.QHBoxLayout()
        hbox.setAlignment(Qt.AlignLeft)
        
        self.textBox = QtGui.QTextEdit()
        self.textBox.setReadOnly(True)
        self.textBox.setFont(font)

        self.addLayout(hbox) 
        self.addWidget(self.textBox)
        
        # Clear log
        self.textBox.setContextMenuPolicy(Qt.CustomContextMenu)
        self.textBox.customContextMenuRequested.connect(self.textbox_menu)

    def textbox_menu(self, point):
        """ Custom context menu for text box """
        menu = self.textBox.createStandardContextMenu(point)
        
        # Include clear log action
        clearLog = QtGui.QAction('Clear message log', self)
        clearLog.setStatusTip('Clear message log')
        clearLog.triggered.connect(self.clear_fn)
        
        menu.addAction(clearLog)
        menu.exec_(self.textBox.viewport().mapToGlobal(point))
    
    def write(self, msg):
        """ Function to write messages into log """
        self.textBox.insertPlainText(str(msg))
    
    def clear_fn(self):
        """ Function to clear message log """
        self.textBox.clear()
        