from PyQt5.QtWidgets import QWidget, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
from app.ui.frequencies_ui import Ui_FrequencyBandForm

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


class FrequencyWindow(QWidget):
    def __init__(self, rootapp, parent=None):
        super().__init__()
        self.db = rootapp.db
        self.rootapp = rootapp
        self.current_id = None
        self.current_search = None

        # Setup UI
        self.ui = Ui_FrequencyBandForm()
        self.ui.setupUi(self)

        # Configure search field options
        self.search_fields = {
            "Band Name": "band_name",
            "Frequency Range": "range",
            "Description": "description"
        }

        # Connect signals
        self.connect_signals()

        # Load initial data
        self.load_data()

        if parent:
            parent_geom = parent.frameGeometry()
            parent_pos = parent_geom.topLeft()
            parent_size = parent_geom.size()
            new_x = parent_pos.x()
            new_y = parent_pos.y() + parent_size.height()
            self.move(new_x, new_y)

    def connect_signals(self):
        self.ui.btn_new.clicked.connect(self.clear_form)
        self.ui.btn_save.clicked.connect(self.save_record)
        self.ui.btn_delete.clicked.connect(self.delete_record)
        self.ui.table_frequency_bands.itemSelectionChanged.connect(self.load_selected_record)

        # Search signals
        self.ui.btn_search.clicked.connect(self.search_records)
        self.ui.btn_reset_search.clicked.connect(self.reset_search)
        self.ui.txt_search_term.returnPressed.connect(self.search_records)

        # Connect frequency validation
        self.ui.spin_start_freq.valueChanged.connect(self.validate_frequencies)
        self.ui.spin_end_freq.valueChanged.connect(self.validate_frequencies)

    def validate_frequencies(self):
        if self.ui.spin_start_freq.value() > self.ui.spin_end_freq.value():
            self.ui.spin_end_freq.setValue(self.ui.spin_start_freq.value())

    def load_data(self, search_params=None):
        try:
            query = "SELECT id, band_name, freq_start, freq_end, description FROM frequency_bands"
            params = ()

            if search_params:
                field, term = search_params
                if field == "band_name":
                    query += " WHERE band_name LIKE ?"
                    params = (f"%{term}%",)
                elif field == "description":
                    query += " WHERE description LIKE ?"
                    params = (f"%{term}%",)
                elif field == "range":
                    try:
                        freq = float(term)
                        query += " WHERE ? BETWEEN freq_start AND freq_end"
                        params = (freq,)
                    except ValueError:
                        self.show_error("Please enter a valid frequency number")
                        return

            query += " ORDER BY freq_start"

            records = self.db.conn.execute(query, params).fetchall()

            self.ui.table_frequency_bands.setRowCount(0)

            for row_number, row_data in enumerate(records):
                self.ui.table_frequency_bands.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    if column_number in (2, 3):  # Frequency columns
                        item = QTableWidgetItem(f"{data:.3f}")
                    else:
                        item = QTableWidgetItem(str(data) if data is not None else "")
                    item.setData(Qt.UserRole, row_data[0])  # Store ID in user role
                    self.ui.table_frequency_bands.setItem(row_number, column_number, item)

        except Exception as e:
            self.show_error(f"Error loading frequency bands: {str(e)}")

    def load_selected_record(self):
        selected = self.ui.table_frequency_bands.selectedItems()
        if not selected:
            return

        try:
            band_id = selected[0].data(Qt.UserRole)
            record = self.db.conn.execute(
                "SELECT band_name, freq_start, freq_end, description FROM frequency_bands WHERE id=?",
                (band_id,)
            ).fetchone()

            if record:
                self.current_id = band_id
                self.ui.txt_band_name.setText(record[0])
                self.ui.spin_start_freq.setValue(record[1])
                self.ui.spin_end_freq.setValue(record[2])
                self.ui.txt_description.setPlainText(record[3] if record[3] else "")

        except Exception as e:
            self.show_error(f"Error loading frequency band: {str(e)}")

    def clear_form(self):
        self.current_id = None
        self.ui.txt_band_name.clear()
        self.ui.spin_start_freq.setValue(0)
        self.ui.spin_end_freq.setValue(0)
        self.ui.txt_description.setPlainText("")
        self.ui.table_frequency_bands.clearSelection()

    def validate_form(self):
        errors = []
        band_name = self.ui.txt_band_name.text().strip()
        start_freq = self.ui.spin_start_freq.value()
        end_freq = self.ui.spin_end_freq.value()

        if not band_name:
            errors.append("Band name is required")

        if start_freq <= 0:
            errors.append("Start frequency must be greater than 0")

        if end_freq <= start_freq:
            errors.append("End frequency must be greater than start frequency")

        # Check for duplicate band name
        if not self.current_id:  # Only check for new records
            existing = self.db.conn.execute(
                "SELECT id FROM frequency_bands WHERE band_name=?",
                (band_name,)
            ).fetchone()
            if existing:
                errors.append("A band with this name already exists")

        return errors

    def save_record(self):
        errors = self.validate_form()
        if errors:
            self.show_error("\n".join(errors))
            return

        try:
            data = (
                self.ui.txt_band_name.text().strip(),
                self.ui.spin_start_freq.value(),
                self.ui.spin_end_freq.value(),
                self.ui.txt_description.toPlainText().strip() or None,
            )

            if self.current_id:
                # Update existing record
                self.db.conn.execute(
                    """UPDATE frequency_bands 
                    SET band_name=?, freq_start=?, freq_end=?, description=? 
                    WHERE id=?""",
                    data + (self.current_id,)
                )
            else:
                # Insert new record
                self.db.conn.execute(
                    """INSERT INTO frequency_bands 
                    (band_name, freq_start, freq_end, description) 
                    VALUES (?, ?, ?, ?)""",
                    data
                )

            self.db.conn.commit()
            self.load_data(self.current_search)
            self.clear_form()
            QMessageBox.information(self, "Success", "Frequency band saved successfully")

        except Exception as e:
            self.show_error(f"Error saving frequency band: {str(e)}")

    def delete_record(self):
        if not self.current_id:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this frequency band?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.db.conn.execute("DELETE FROM frequency_bands WHERE id=?", (self.current_id,))
                self.db.conn.commit()
                self.load_data(self.current_search)
                self.clear_form()
                QMessageBox.information(self, "Success", "Frequency band deleted successfully")
            except Exception as e:
                self.show_error(f"Error deleting frequency band: {str(e)}")

    def search_records(self):
        search_term = self.ui.txt_search_term.text().strip()
        if not search_term:
            return

        selected_field = self.ui.cmb_search_field.currentText()
        db_field = self.search_fields.get(selected_field)

        self.current_search = (db_field, search_term)
        self.load_data(self.current_search)

    def reset_search(self):
        self.current_search = None
        self.ui.txt_search_term.clear()
        self.load_data()

    def show_error(self, message):
        self.rootapp.show_error("Area edit", message)