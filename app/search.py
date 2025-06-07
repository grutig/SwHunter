import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QPushButton
from PyQt5.QtCore import Qt, QTime
from app.ui.search_ui import Ui_SearchWindow

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

_translate = QtCore.QCoreApplication.translate

class SearchWindow(QWidget):
    def __init__(self, rootapp, parent=None):
        super().__init__()
        self.db = rootapp.db
        self.rootapp = rootapp
        self.current_id = None
        self.setup_ui()
        self.load_combos()
        self.connect_signals()
        if parent:
            parent_geom = parent.frameGeometry()
            parent_pos = parent_geom.topLeft()
            parent_size = parent_geom.size()
            new_x = parent_pos.x()
            new_y = parent_pos.y() + parent_size.height()
            self.move(new_x, new_y)

    def setup_ui(self):
        self.ui = Ui_SearchWindow()
        self.ui.setupUi(self)


    def connect_signals(self):
        self.ui.btnClear.clicked.connect(self.reset_form)
        self.ui.btnSearch.clicked.connect(self.search)

    def load_combos(self):
        """
        Load combo box from database
        """
        if not self.db:
            return

        try:
            countries = self.db.get_countries()
            self.ui.countryComboBox.clear()
            self.ui.countryComboBox.addItem("All", "")
            for country in countries:
                self.ui.countryComboBox.addItem(f"{country[0]} ({country[1]})", country[1])

            languages = self.db.get_langs()
            self.ui.languageComboBox.clear()
            self.ui.languageComboBox.addItem("All", "")
            for language in languages:
                self.ui.languageComboBox.addItem(f"{language[1]} ({language[0]})", language[0])

            # Populate areas
            areas = self.db.get_areas()
            self.ui.targetAreaComboBox.clear()
            self.ui.targetAreaComboBox.addItem("All", "")
            for area in areas:
                self.ui.targetAreaComboBox.addItem(f"{area[1]} ({area[0]})", area[0])

            # Populate bands
            bands = self.db.get_bands() 
            self.ui.bandComboBox.clear()
            self.ui.bandComboBox.addItem("All", "")
            for band in bands:
                self.ui.bandComboBox.addItem(band[1], band[1])

        except Exception as e:
            self.show_error(str(e))

    def reset_form(self):
        # Reset frequency
        self.ui.freqMinSpinBox.setValue(50)
        self.ui.freqMaxSpinBox.setValue(30000)

        # Reset time
        self.ui.useTimeCheckBox.setChecked(False)
        self.ui.timeEdit.setTime(QTime.currentTime())
        self.ui.timeEdit.setEnabled(False)

        # Reset text fields
        self.ui.daysLineEdit.clear()
        self.ui.stationLineEdit.clear()
        self.ui.startDateLineEdit.clear()
        self.ui.endDateLineEdit.clear()

        # Reset combo boxes
        self.ui.countryComboBox.setCurrentIndex(0)
        self.ui.languageComboBox.setCurrentIndex(0)
        self.ui.targetAreaComboBox.setCurrentIndex(0)
        self.ui.bandComboBox.setCurrentIndex(0)

        # Reset limit
        self.ui.limitSpinBox.setValue(100)

    def search(self):
        errors  = self.validate_form()
        if errors:
            QMessageBox.warning(self, _translate("", "Validation Error"), "\n".join(errors))
        filters = self.get_filters()
        self._load_table(self.db.search_skeds(filters))


    def get_filters(self):
        params = {}

        # Frequency range
        if self.ui.freqMinSpinBox.value() > 0:
            params['freq_min'] = self.ui.freqMinSpinBox.value()
        if self.ui.freqMaxSpinBox.value() > 0:
            params['freq_max'] = self.ui.freqMaxSpinBox.value()

        # Time filter
        if self.ui.useTimeCheckBox.isChecked():
            time_str = self.ui.timeEdit.time().toString("HHmm")
            params['time'] = time_str

        # Days operation
        days_text = self.ui.daysLineEdit.text().strip()
        if days_text:
            params['days'] = days_text

        # Station name
        station_text = self.ui.stationLineEdit.text().strip()
        if station_text:
            params['station'] = station_text

        # Country
        country_data = self.ui.countryComboBox.currentData()
        if country_data:
            params['country'] = country_data

        # Language
        language_data = self.ui.languageComboBox.currentData()
        if language_data:
            params['language'] = language_data

        # Target area
        area_data = self.ui.targetAreaComboBox.currentData()
        if area_data:
            params['target_area'] = area_data

        # Band
        band_data = self.ui.bandComboBox.currentData()
        if band_data:
            params['band'] = band_data

        # Start date
        start_date = self.ui.startDateLineEdit.text().strip()
        if start_date and len(start_date) == 4:
            params['start_date'] = start_date

        # End date
        end_date = self.ui.endDateLineEdit.text().strip()
        if end_date and len(end_date) == 4:
            params['end_date'] = end_date

        # Limit
        if self.ui.limitSpinBox.value() > 0:
            params['limit'] = self.ui.limitSpinBox.value()

        return params

    def validate_form(self):
        errors = []

        # Validate frequency range
        freq_min = self.ui.freqMinSpinBox.value()
        freq_max = self.ui.freqMaxSpinBox.value()
        if freq_min > 0 and freq_max > 0 and freq_min >= freq_max:
            errors.append(_translate("", "Minimum frequency must be less than maximum frequency"))

        # Validate date format
        start_date = self.ui.startDateLineEdit.text().strip()
        if start_date and (len(start_date) != 4 or not start_date.isdigit()):
            errors.append(_translate("", "Start date must be in MMDD format (4 digits)"))

        end_date = self.ui.endDateLineEdit.text().strip()
        if end_date and (len(end_date) != 4 or not end_date.isdigit()):
            errors.append(_translate("", "End date must be in MMDD format (4 digits)"))

        # Validate date range
        if start_date and end_date and len(start_date) == 4 and len(end_date) == 4:
            try:
                start_month = int(start_date[:2])
                start_day = int(start_date[2:])
                end_month = int(end_date[:2])
                end_day = int(end_date[2:])

                if not (1 <= start_month <= 12) or not (1 <= start_day <= 31):
                    errors.append(_translate("", "Invalid start date"))
                if not (1 <= end_month <= 12) or not (1 <= end_day <= 31):
                    errors.append(_translate("", "Invalid end date"))
            except ValueError:
                errors.append(_translate("", "Invalid date format"))

        return errors

    def _load_table(self, rows):
        """
        Load sked table
        """

        self.ui.tblSked.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            # Tune in button
            btnTune = QPushButton(_translate("", "Tune"))
            btnTune.clicked.connect(lambda checked, data=row: self._tune_in(data))
            self.ui.tblSked.setCellWidget(row_idx, 6, btnTune)

            # Freq
            freq_item = QTableWidgetItem(f"{row['frequency_khz']:.1f}")
            freq_item.setData(Qt.UserRole, row)
            self.ui.tblSked.setItem(row_idx, 0, freq_item)

            # Station
            station_item = QTableWidgetItem(row['station_name'] or "")
            self.ui.tblSked.setItem(row_idx, 1, station_item)

            # Country
            country_item = QTableWidgetItem(row['country'] or "")
            self.ui.tblSked.setItem(row_idx, 2, country_item)

            # Language
            language_item = QTableWidgetItem(row['language'] or "")
            self.ui.tblSked.setItem(row_idx, 3, language_item)

            # Sked
            start_time = row['start_time'] or ""
            end_time = row['end_time'] or ""
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
            days_item = QTableWidgetItem(row['days_operation'] or _translate("", "All"))
            self.ui.tblSked.setItem(row_idx, 5, days_item)


    def _tune_in(self, data):
        if data['frequency_khz'] and data['frequency_khz'] > 0:
            if self.rootapp.hamlib.rig:
                self.rootapp.hamlib.set_frequency(data['frequency_khz'] * 1000)

    def show_error(self, message):
        self.rootapp.show_error("Area edit", message)
