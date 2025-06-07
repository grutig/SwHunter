import sys
import sqlite3
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QDialog, QTableWidget, QTableWidgetItem,
                             QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QHeaderView,
                             QMessageBox, QAbstractItemView)
from PyQt5.QtCore import Qt, pyqtSignal, QCoreApplication
from PyQt5.QtGui import QFont
from app.ui.lookup_ui import Ui_LookupWindow
import os

""" 
ShortwaveHunter
BCL radio software

Copyright (c) 2025 I8ZSE, Giorgio L. Rutigliano
(www.i8zse.it, www.i8zse.eu, www.giorgiorutigliano.it)

radio communications are handled by https://github.com/Hamlib/Hamlib (LGPL)

This is free software released under LGPL License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


_translate = QCoreApplication.translate

class LookupWindow(QDialog):
    # Signal emesso quando viene cliccato il pulsante log
    log_requested = pyqtSignal(dict)  # Emette i dati della trasmissione

    def __init__(self, db, freq, parent=None):
        super().__init__(parent)
        
        self.freq = float(freq)
        self.db = db
        self.transmission_data = []

        # Configura l'interfaccia
        self.ui = Ui_LookupWindow()
        self.ui.setupUi(self)

        # # Connetti i segnali
        self._connect_signals()
        self.lookup(self.freq)

        if parent:
            parent_geom = parent.frameGeometry()
            parent_pos = parent_geom.topLeft()
            parent_size = parent_geom.size()
            new_x = parent_pos.x()
            new_y = parent_pos.y() + parent_size.height()
            self.move(new_x, new_y)

    def _connect_signals(self):
        if hasattr(self, 'refreshButton'):
            self.refreshButton.clicked.connect(self._load_transmissions)


    def _load_table(self, rows):
        """
        Load sked table
        """

        count = len(rows)
        text = _translate("", "Frequency: {0} kHz (±5 kHz) - Found {1} transmissions").format(f"{self.freq:.1f}", count)
        if hasattr(self.ui, 'infoLabel'):
            self.ui.infoLabel.setText(text)

        self.ui.tblSked.setRowCount(len(rows))
        for row_idx, transmission in enumerate(rows):
            # Log button
            log_button = QPushButton(_translate("FrequencyDialog", "Log"))
            log_button.clicked.connect(lambda checked, data=transmission: self._on_log_clicked(data))
            self.ui.tblSked.setCellWidget(row_idx, 6, log_button)

            # Freq
            freq_item = QTableWidgetItem(f"{transmission['frequency_khz']:.1f}")
            freq_item.setData(Qt.UserRole, transmission)
            self.ui.tblSked.setItem(row_idx, 0, freq_item)

            # Station
            station_item = QTableWidgetItem(transmission['station_name'] or "")
            self.ui.tblSked.setItem(row_idx, 1, station_item)

            # Country
            country_item = QTableWidgetItem(transmission['country_name'] or "")
            self.ui.tblSked.setItem(row_idx, 2, country_item)

            # Language
            language_item = QTableWidgetItem(transmission['language_name'] or "")
            self.ui.tblSked.setItem(row_idx, 3, language_item)

            # Sked
            start_time = transmission['start_time'] or ""
            end_time = transmission['end_time'] or ""
            time_text = ""
            if start_time and end_time:
                # HH:MM-HH:MM
                if len(start_time) == 4 and len(end_time) == 4:
                    time_text = f"{start_time[:2]}:{start_time[2:]}-{end_time[:2]}:{end_time[2:]}"
                else:
                    time_text = f"{start_time}-{end_time}"
            time_item = QTableWidgetItem(time_text)
            self.ui.tblSked.setItem(row_idx, 4, time_item)

            # Days
            days_item = QTableWidgetItem(transmission['days_operation'] or _translate("FrequencyDialog", "All"))
            self.ui.tblSked.setItem(row_idx, 5, days_item)


    def lookup(self, freq):
        results, e, emsg = self.db.lookup(freq)
        if e != 0:
            self.rootapp.show_error("Lookup", emsg)
        self._load_table(results)

    def _on_log_clicked(self, row):
        """Gestisce il click sul pulsante Log"""
        a = 0



