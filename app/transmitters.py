from PyQt5.QtWidgets import QWidget, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
from app.ui.transmitters_ui import Ui_TransmitterForm

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

class TransmitterWindow(QWidget):
    def __init__(self, rootapp, parent=None):
        super().__init__()
        self.db = rootapp.db
        self.rootapp = rootapp
        self.current_id = None
        self.setup_ui()
        self.connect_signals()
        self.load_data()

        if parent:
            parent_geom = parent.frameGeometry()
            parent_pos = parent_geom.topLeft()
            parent_size = parent_geom.size()
            new_x = parent_pos.x()
            new_y = parent_pos.y() + parent_size.height()
            self.move(new_x, new_y)


    def setup_ui(self):
        self.ui = Ui_TransmitterForm()
        self.ui.setupUi(self)

        self.search_fields = {
            "Country Code": "country_code",
            "Site Code": "site_code",
            "Name": "name",
            "All Fields": None
        }

    def connect_signals(self):
        self.ui.btn_new.clicked.connect(self.clear_form)
        self.ui.btn_save.clicked.connect(self.save_record)
        self.ui.btn_delete.clicked.connect(self.delete_record)
        self.ui.table_transmitters.itemSelectionChanged.connect(self.load_selected_record)

        # Search signals
        self.ui.btn_search.clicked.connect(self.search_records)
        self.ui.btn_reset_search.clicked.connect(self.reset_search)
        self.ui.txt_search_term.returnPressed.connect(self.search_records)

    def load_data(self, search_params=None):
        try:
            query = """
                SELECT id, country_code, site_code, name, latitude, longitude 
                FROM transmitters
            """
            params = ()

            if search_params:
                field, term = search_params
                if field:  # Specific field search
                    query += f" WHERE {field} LIKE ?"
                    params = (f"%{term}%",)
                else:  # Search all fields
                    query += " WHERE country_code LIKE ? OR site_code LIKE ? OR name LIKE ?"
                    params = (f"%{term}%", f"%{term}%", f"%{term}%")

            query += " ORDER BY country_code, site_code"

            records = self.db.conn.execute(query, params).fetchall()

            self.ui.table_transmitters.setRowCount(0)

            for row_number, row_data in enumerate(records):
                self.ui.table_transmitters.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    item.setData(Qt.UserRole, row_data[0])  # Store ID in user role
                    self.ui.table_transmitters.setItem(row_number, column_number, item)

        except Exception as e:
            self.show_error(str(e))

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

    def load_selected_record(self):
        selected = self.ui.table_transmitters.selectedItems()
        if not selected:
            return

        try:
            transmitter_id = selected[0].data(Qt.UserRole)
            record = self.db.conn.execute("""
                SELECT country_code, site_code, name, latitude, longitude 
                FROM transmitters WHERE id=?
            """, (transmitter_id,)).fetchone()

            if record:
                self.current_id = transmitter_id
                self.ui.txt_country_code.setText(record[0])
                self.ui.txt_site_code.setText(record[1])
                self.ui.txt_name.setText(record[2])
                self.ui.txt_latitude.setText(str(record[3]))
                self.ui.txt_longitude.setText(str(record[4]))

        except Exception as e:
            self.show_error(str(e))

    def clear_form(self):
        self.current_id = None
        self.ui.txt_country_code.clear()
        self.ui.txt_site_code.clear()
        self.ui.txt_name.clear()
        self.ui.txt_latitude.clear()
        self.ui.txt_longitude.clear()
        self.ui.table_transmitters.clearSelection()

    def validate_form(self):
        errors = []
        if not self.ui.txt_country_code.text().strip():
            errors.append(self.tr("Country code is required"))
        if not self.ui.txt_site_code.text().strip():
            errors.append(self.tr("Site code is required"))
        if not self.ui.txt_name.text().strip():
            errors.append(self.tr("Name is required"))

        try:
            if self.ui.txt_latitude.text():
                float(self.ui.txt_latitude.text())
            if self.ui.txt_longitude.text():
                float(self.ui.txt_longitude.text())
        except ValueError:
            errors.append(self.tr("Latitude and longitude must be numeric"))

        return errors

    def save_record(self):
        errors = self.validate_form()
        if errors:
            self.show_error("\n".join(errors))
            return

        try:
            data = (
                self.ui.txt_country_code.text().strip(),
                self.ui.txt_site_code.text().strip(),
                self.ui.txt_name.text().strip(),
                float(self.ui.txt_latitude.text()) if self.ui.txt_latitude.text() else None,
                float(self.ui.txt_longitude.text()) if self.ui.txt_longitude.text() else None,
            )

            if self.current_id:
                # Update existing record
                self.db.conn.execute("""
                    UPDATE transmitters 
                    SET country_code=?, site_code=?, name=?, latitude=?, longitude=?
                    WHERE id=?
                """, data + (self.current_id,))
            else:
                # Insert new record
                self.db.conn.execute("""
                    INSERT INTO transmitters 
                    (country_code, site_code, name, latitude, longitude)
                    VALUES (?, ?, ?, ?, ?)
                """, data)

            self.db.conn.commit()
            self.load_data()
            self.clear_form()
            QMessageBox.information(self, self.tr("Success"), self.tr("Record saved successfully"))

        except Exception as e:
            self.show_error(str(e))

    def delete_record(self):
        if not self.current_id:
            return

        reply = QMessageBox.question(
            self, self.tr("Confirm Delete"),
            self.tr("Are you sure you want to delete this transmitter?"),
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.db.conn.execute("DELETE FROM transmitters WHERE id=?", (self.current_id,))
                self.db.conn.commit()
                self.load_data()
                self.clear_form()
                QMessageBox.information(self, self.tr("Success"), self.tr("Record deleted successfully"))
            except Exception as e:
                self.show_error(str(e))

    def show_error(self, message):
        self.rootapp.show_error("Area edit", message)