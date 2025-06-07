import sys
import sqlite3
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QDialog, QTableWidget, QTableWidgetItem,
                             QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QHeaderView,
                             QMessageBox, QAbstractItemView)
from PyQt5.QtCore import Qt, pyqtSignal, QCoreApplication
from app.ui.impsum_ui import Ui_ImportSummaryDialog
import os


_translate = QCoreApplication.translate


class WaitDialog(QDialog):
    """
    Used to show wait windows
    """
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_translate("", "Please wait"))
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.setModal(True)
        layout = QVBoxLayout()
        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.resize(250, 100)
        if parent:
            parent_geometry = self.parent().frameGeometry()
            center_point = parent_geometry.center()
            fg = self.frameGeometry()
            fg.moveCenter(center_point)
            self.move(fg.topLeft())


class ImpsumWindow(QDialog):

    def __init__(self, imp, upd, err, parent=None):
        super().__init__(parent)
        
        self.imp = imp
        self.upd = upd
        self.err = err

        # Configura l'interfaccia
        self.ui = Ui_ImportSummaryDialog()
        self.ui.setupUi(self)
        self.ui.lblImported.setText(_translate("", "Imported: ") + f"{imp}")
        self.ui.lblUpdated.setText(_translate("", "Updated: ") + f"{upd}")
        self.ui.buttonBox.rejected.connect(self.reject)


        if err:
            self.ui.txtErrors.setPlainText("\n".join(err))
        else:
            self.ui.txtErrors.setPlainText(_translate("", "No errors."))

        if self.parent():
            parent_geometry = self.parent().frameGeometry()
            center_point = parent_geometry.center()
            fg = self.frameGeometry()
            fg.moveCenter(center_point)
            self.move(fg.topLeft())
