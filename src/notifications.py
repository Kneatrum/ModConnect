"""
This module contains methods for showing notifications
to the user using pop up windows.
"""

from PyQt5.QtWidgets import QMessageBox

class Notification:
      
    def set_warning_message(self, title, message):
        self.messageBox = QMessageBox()
        self.messageBox.setIcon(QMessageBox.Warning)
        self.messageBox.setWindowTitle(title)
        self.messageBox.setText(message)
        self.messageBox.setStandardButtons(QMessageBox.Ok)
        self.messageBox.exec_()