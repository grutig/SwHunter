from PyQt5.QtWidgets import QWidget, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
from app.ui.languages_ui import Ui_LanguageForm

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

class LanguageWindow(QWidget):
    def __init__(self, rootapp, parent=None):
        super().__init__()
        self.db = rootapp.db
        self.rootapp = rootapp
        self.current_id = None
        self.current_search = None

        # Setup UI
        self.ui = Ui_LanguageForm()
        self.ui.setupUi(self)

        # Configure search field options
        self.search_fields = {
            "Code": "code",
            "Language": "lang",
            "Area": "area",
            "All Fields": None
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
        self.ui.table_languages.itemSelectionChanged.connect(self.load_selected_record)

        # Search signals
        self.ui.btn_search.clicked.connect(self.search_records)
        self.ui.btn_reset_search.clicked.connect(self.reset_search)
        self.ui.txt_search_term.returnPressed.connect(self.search_records)

    def load_data(self, search_params=None):
        try:
            query = "SELECT id, code, lang, area, code2 FROM languages"
            params = ()

            if search_params:
                field, term = search_params
                if field:  # Specific field search
                    query += f" WHERE {field} LIKE ?"
                    params = (f"%{term}%",)
                else:  # Search all fields
                    query += " WHERE code LIKE ? OR lang LIKE ? OR area LIKE ? OR code2 LIKE ?"
                    params = (f"%{term}%", f"%{term}%", f"%{term}%", f"%{term}%")

            query += " ORDER BY code"

            records = self.db.conn.execute(query, params).fetchall()

            self.ui.table_languages.setRowCount(0)

            for row_number, row_data in enumerate(records):
                self.ui.table_languages.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data) if data is not None else "")
                    item.setData(Qt.UserRole, row_data[0])  # Store ID in user role
                    self.ui.table_languages.setItem(row_number, column_number, item)

        except Exception as e:
            self.show_error(f"Error loading languages: {str(e)}")

    def load_selected_record(self):
        selected = self.ui.table_languages.selectedItems()
        if not selected:
            return

        try:
            language_id = selected[0].data(Qt.UserRole)
            record = self.db.conn.execute(
                "SELECT code, lang, area, code2 FROM languages WHERE id=?",
                (language_id,)
            ).fetchone()

            if record:
                self.current_id = language_id
                self.ui.txt_code.setText(record[0])
                self.ui.txt_lang.setText(record[1])
                self.ui.txt_area.setText(record[2] if record[2] else "")
                self.ui.txt_code2.setText(record[3] if record[3] else "")

        except Exception as e:
            self.show_error(f"Error loading language: {str(e)}")

    def clear_form(self):
        self.current_id = None
        self.ui.txt_code.clear()
        self.ui.txt_lang.clear()
        self.ui.txt_area.clear()
        self.ui.txt_code2.clear()
        self.ui.table_languages.clearSelection()

    def validate_form(self):
        errors = []
        if not self.ui.txt_code.text().strip():
            errors.append("Code is required")
        if not self.ui.txt_lang.text().strip():
            errors.append("Language name is required")

        # Check for duplicate code
        if not self.current_id:  # Only check for new records
            existing = self.db.conn.execute(
                "SELECT id FROM languages WHERE code=?",
                (self.ui.txt_code.text().strip(),)
            ).fetchone()
            if existing:
                errors.append("A language with this code already exists")

        return errors

    def save_record(self):
        errors = self.validate_form()
        if errors:
            self.show_error("\n".join(errors))
            return

        try:
            data = (
                self.ui.txt_code.text().strip(),
                self.ui.txt_lang.text().strip(),
                self.ui.txt_area.text().strip() or None,
                self.ui.txt_code2.text().strip() or None,
            )

            if self.current_id:
                # Update existing record
                self.db.conn.execute(
                    "UPDATE languages SET code=?, lang=?, area=?, code2=? WHERE id=?",
                    data + (self.current_id,)
                )
            else:
                # Insert new record
                self.db.conn.execute(
                    "INSERT INTO languages (code, lang, area, code2) VALUES (?, ?, ?, ?)",
                    data
                )

            self.db.conn.commit()
            self.load_data(self.current_search)
            self.clear_form()
            QMessageBox.information(self, "Success", "Language saved successfully")

        except Exception as e:
            self.show_error(f"Error saving language: {str(e)}")

    def delete_record(self):
        if not self.current_id:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this language?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.db.conn.execute("DELETE FROM languages WHERE id=?", (self.current_id,))
                self.db.conn.commit()
                self.load_data(self.current_search)
                self.clear_form()
                QMessageBox.information(self, "Success", "Language deleted successfully")
            except Exception as e:
                self.show_error(f"Error deleting language: {str(e)}")

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