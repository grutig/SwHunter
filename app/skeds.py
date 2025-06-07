from PyQt5.QtWidgets import (QWidget, QMessageBox, QTableWidgetItem)
from PyQt5.QtCore import Qt, QTime
from app.ui.skeds_ui import Ui_SkedForm

class SkedsWindow(QWidget):
    def __init__(self, rootapp, parent=None):
        super().__init__()
        self.db = rootapp.db
        self.rootapp = rootapp
        self.current_id = None
        self.current_search = None

        # Setup UI
        self.ui = Ui_SkedForm()
        self.ui.setupUi(self)

        # Configure search field options
        self.search_fields = {
            "Frequency": "frequency_khz",
            "Station Name": "station_name",
            "Country": "country",
            "Language": "language",
            "Target Area": "target_area"
        }

        # Initialize comboboxes
        self.init_comboboxes()

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


    def init_comboboxes(self):
        """Initialize comboboxes with data from database"""
        try:
            # Countries
            countries = self.db.conn.execute(
                "SELECT id, cname FROM countries ORDER BY cname"
            ).fetchall()
            self.ui.cmb_country.clear()
            for country_id, cname in countries:
                self.ui.cmb_country.addItem(cname, country_id)

            # Languages
            languages = self.db.conn.execute(
                "SELECT id, lang FROM languages ORDER BY lang"
            ).fetchall()
            self.ui.cmb_language.clear()
            for lang_id, lang in languages:
                self.ui.cmb_language.addItem(lang, lang_id)

            # Areas
            areas = self.db.conn.execute(
                "SELECT id, aname FROM area ORDER BY aname"
            ).fetchall()
            self.ui.cmb_target_area.clear()
            self.ui.cmb_target_area.addItem("", None)  # Empty option
            for area_id, aname in areas:
                self.ui.cmb_target_area.addItem(aname, area_id)

            # Transmitter sites
            transmitters = self.db.conn.execute(
                "SELECT DISTINCT site_code FROM transmitters ORDER BY site_code"
            ).fetchall()
            self.ui.cmb_transmitter_site.clear()
            self.ui.cmb_transmitter_site.addItem("", "")  # Empty option
            for (site_code,) in transmitters:
                self.ui.cmb_transmitter_site.addItem(site_code, site_code)

        except Exception as e:
            self.show_error(f"Error initializing comboboxes: {str(e)}")

    def connect_signals(self):
        """Connect UI signals to slots"""
        self.ui.btn_new.clicked.connect(self.clear_form)
        self.ui.btn_save.clicked.connect(self.save_record)
        self.ui.btn_delete.clicked.connect(self.delete_record)
        self.ui.table_Skeds.itemSelectionChanged.connect(self.load_selected_record)

        # Search signals
        self.ui.btn_search.clicked.connect(self.search_records)
        self.ui.btn_reset_search.clicked.connect(self.reset_search)
        self.ui.txt_search_term.returnPressed.connect(self.search_records)

    def load_data(self, search_params=None):
        """Load data into the table view"""
        try:
            query = """SELECT b.id, b.frequency_khz, 
                      b.start_time, b.end_time, b.station_name,
                      c.cname, l.lang
                      FROM broadcasts b
                      LEFT JOIN countries c ON b.country_id = c.id
                      LEFT JOIN languages l ON b.language_id = l.id
                   """
            params = ()

            if search_params:
                field, term = search_params
                if field == "frequency_khz":
                    try:
                        freq = float(term)
                        query += " WHERE b.frequency_khz = ?"
                        params = (freq,)
                    except ValueError:
                        self.show_error("Please enter a valid frequency number")
                        return
                elif field == "station_name":
                    query += " WHERE b.station_name LIKE ?"
                    params = (f"%{term}%",)
                elif field == "country":
                    query += " WHERE c.cname LIKE ?"
                    params = (f"%{term}%",)
                elif field == "language":
                    query += " WHERE l.lang LIKE ?"
                    params = (f"%{term}%",)
                elif field == "target_area":
                    query += " WHERE a.aname LIKE ?"
                    params = (f"%{term}%",)

            query += " ORDER BY b.frequency_khz, b.start_time"

            records = self.db.conn.execute(query, params).fetchall()

            self.ui.table_Skeds.setRowCount(0)

            for row_number, row_data in enumerate(records):
                self.ui.table_Skeds.insertRow(row_number)

                # ID
                item = QTableWidgetItem(str(row_data[0]))
                item.setData(Qt.UserRole, row_data[0])
                self.ui.table_Skeds.setItem(row_number, 0, item)

                # Frequency
                self.ui.table_Skeds.setItem(
                    row_number, 1, QTableWidgetItem(f"{row_data[1]:.3f}"))

                # Time range
                time_str = f"{row_data[2]} - {row_data[3]}" if row_data[2] and row_data[3] else ""
                self.ui.table_Skeds.setItem(
                    row_number, 2, QTableWidgetItem(time_str))

                # Station name
                self.ui.table_Skeds.setItem(
                    row_number, 3, QTableWidgetItem(row_data[4]))

                # Country
                self.ui.table_Skeds.setItem(
                    row_number, 4, QTableWidgetItem(row_data[5] if row_data[5] else ""))

                # Language
                self.ui.table_Skeds.setItem(
                    row_number, 5, QTableWidgetItem(row_data[6] if row_data[6] else ""))

        except Exception as e:
            self.show_error(f"Error loading Skeds: {str(e)}")

    def load_selected_record(self):
        """Load selected record from table into form"""
        selected = self.ui.table_Skeds.selectedItems()
        if not selected:
            return

        try:
            broadcast_id = selected[0].data(Qt.UserRole)
            record = self.db.conn.execute(
                """SELECT frequency_khz, start_time, end_time, days_operation,
                   country_id, station_name, language_id, target_area_id,
                   transmitter_site, persistence_code, start_date, end_date, remarks
                   FROM broadcasts WHERE id=?""",
                (broadcast_id,)
            ).fetchone()

            if record:
                self.current_id = broadcast_id

                # Basic fields
                self.ui.spin_frequency.setValue(record[0])
                self.ui.txt_days_operation.setText(record[3] if record[3] else "")
                self.ui.txt_station_name.setText(record[5])
                self.ui.spin_persistence.setValue(record[9] if record[9] else 1)
                self.ui.txt_start_date.setText(record[10] if record[10] else "")
                self.ui.txt_end_date.setText(record[11] if record[11] else "")
                self.ui.txt_remarks.setPlainText(record[12] if record[12] else "")

                # Time fields
                if record[1]:  # start_time
                    time = QTime.fromString(record[1], "HHMM")
                    self.ui.time_start.setTime(time)
                if record[2]:  # end_time
                    time = QTime.fromString(record[2], "HHMM")
                    self.ui.time_end.setTime(time)

                # Combobox fields
                self.set_combobox_value(self.ui.cmb_country, record[4])
                self.set_combobox_value(self.ui.cmb_language, record[6])
                self.set_combobox_value(self.ui.cmb_target_area, record[7])
                self.set_combobox_value(self.ui.cmb_transmitter_site, record[8])

        except Exception as e:
            self.show_error(f"Error loading broadcast: {str(e)}")

    def set_combobox_value(self, combobox, value):
        """Set combobox value by data"""
        if value is None:
            combobox.setCurrentIndex(0)
            return

        for i in range(combobox.count()):
            if combobox.itemData(i) == value:
                combobox.setCurrentIndex(i)
                return
        combobox.setCurrentIndex(0)

    def clear_form(self):
        """Clear the form and reset selection"""
        self.current_id = None

        # Clear basic fields
        self.ui.spin_frequency.setValue(0)
        self.ui.time_start.setTime(QTime(0, 0))
        self.ui.time_end.setTime(QTime(0, 0))
        self.ui.txt_days_operation.clear()
        self.ui.txt_station_name.clear()
        self.ui.spin_persistence.setValue(1)
        self.ui.txt_start_date.clear()
        self.ui.txt_end_date.clear()
        self.ui.txt_remarks.setPlainText("")

        # Reset comboboxes
        self.ui.cmb_country.setCurrentIndex(0)
        self.ui.cmb_language.setCurrentIndex(0)
        self.ui.cmb_target_area.setCurrentIndex(0)
        self.ui.cmb_transmitter_site.setCurrentIndex(0)

        self.ui.table_Skeds.clearSelection()

    def validate_form(self):
        """Validate form data before saving"""
        errors = []

        # Required fields
        if self.ui.spin_frequency.value() <= 0:
            errors.append("Frequency must be greater than 0")

        if not self.ui.txt_station_name.text().strip():
            errors.append("Station name is required")

        if self.ui.cmb_country.currentData() is None:
            errors.append("Country is required")

        # Time validation
        start_time = self.ui.time_start.time().toString("HHMM")
        end_time = self.ui.time_end.time().toString("HHMM")

        if start_time != "0000" and end_time != "0000":
            if start_time >= end_time:
                errors.append("End time must be after start time")

        # Date validation
        start_date = self.ui.txt_start_date.text().strip()
        end_date = self.ui.txt_end_date.text().strip()

        if start_date or end_date:
            if len(start_date) != 4 or not start_date.isdigit():
                errors.append("Start date must be in MMDD format")
            if len(end_date) != 4 or not end_date.isdigit():
                errors.append("End date must be in MMDD format")
            if start_date and end_date and start_date > end_date:
                errors.append("End date must be after start date")

        return errors

    def save_record(self):
        """Save the current record (insert or update)"""
        errors = self.validate_form()
        if errors:
            self.show_error("\n".join(errors))
            return

        try:
            # Prepare data
            start_time = self.ui.time_start.time().toString("HHMM")
            end_time = self.ui.time_end.time().toString("HHMM")

            data = (
                self.ui.spin_frequency.value(),
                start_time if start_time != "0000" else None,
                end_time if end_time != "0000" else None,
                self.ui.txt_days_operation.text().strip() or None,
                self.ui.cmb_country.currentData(),
                self.ui.txt_station_name.text().strip(),
                self.ui.cmb_language.currentData(),
                self.ui.cmb_target_area.currentData(),
                self.ui.cmb_transmitter_site.currentData(),
                self.ui.spin_persistence.value(),
                self.ui.txt_start_date.text().strip() or None,
                self.ui.txt_end_date.text().strip() or None,
                self.ui.txt_remarks.toPlainText().strip() or None,
            )

            if self.current_id:
                # Update existing record
                self.db.conn.execute(
                    """UPDATE Skeds 
                    SET frequency_khz=?, start_time=?, end_time=?, days_operation=?,
                        country_id=?, station_name=?, language_id=?, target_area_id=?,
                        transmitter_site=?, persistence_code=?, start_date=?, end_date=?, remarks=?
                    WHERE id=?""",
                    data + (self.current_id,)
                )
            else:
                # Insert new record
                self.db.conn.execute(
                    """INSERT INTO Skeds 
                    (frequency_khz, start_time, end_time, days_operation,
                     country_id, station_name, language_id, target_area_id,
                     transmitter_site, persistence_code, start_date, end_date, remarks)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    data
                )

            self.db.conn.commit()
            self.load_data(self.current_search)
            self.clear_form()
            QMessageBox.information(self, "Success", "Broadcast saved successfully")

            # Refresh comboboxes in case new options were added
            self.init_comboboxes()

        except Exception as e:
            self.show_error(f"Error saving broadcast: {str(e)}")

    def delete_record(self):
        """Delete the currently selected record"""
        if not self.current_id:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this broadcast?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.db.conn.execute("DELETE FROM broadcasts WHERE id=?", (self.current_id,))
                self.db.conn.commit()
                self.load_data(self.current_search)
                self.clear_form()
                QMessageBox.information(self, "Success", "Broadcast deleted successfully")
            except Exception as e:
                self.show_error(f"Error deleting broadcast: {str(e)}")

    def search_records(self):
        """Search records based on the current criteria"""
        search_term = self.ui.txt_search_term.text().strip()
        if not search_term:
            return

        selected_field = self.ui.cmb_search_field.currentText()
        db_field = self.search_fields.get(selected_field)

        self.current_search = (db_field, search_term)
        self.load_data(self.current_search)

    def reset_search(self):
        """Reset the search and show all records"""
        self.current_search = None
        self.ui.txt_search_term.clear()
        self.load_data()

    def show_error(self, message):
        self.rootapp.show_error("Area edit", message)