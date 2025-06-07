import sqlite3
from typing import Optional, Tuple, List
from PyQt5.QtCore import QObject, pyqtSignal
import os
from datetime import datetime, timedelta

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

class RadioDatabase:
    def __init__(self, obj: object, db_path="."):
        self.conn = sqlite3.connect(os.path.join(db_path, "swhunter.db"))
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        # check if db is populated
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        if not tables:
            obj.settings.clear()
            self.init_db(db_path)
        self.bands = None

    def init_db(self, db_path):
        """
        Execute database creation script
        """
        with open(os.path.join(db_path, "dbcreate.sql"), "r") as f:
            buf = f.read()
            self.conn.executescript(buf)
        with open(os.path.join(db_path, "datainit.sql"), "r") as f:
            buf = f.read()
            self.conn.executescript(buf)


    def parse_time_range(self, time_str: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Time range parsing (es: '0000-2400')
        """
        if not time_str or time_str.strip() == "":
            return None, None

        if '-' in time_str:
            start, end = time_str.split('-', 1)
            return start.strip(), end.strip()

        return time_str.strip(), None

    def get_or_create_country_id(self, country_code: str) -> Optional[int]:
        """
        Get country id
        """
        if not country_code:
            return None

        cursor = self.conn.execute("SELECT id FROM countries WHERE ccode = ?", (country_code,))
        result = cursor.fetchone()

        if result:
            return result[0]

        # If not exists, create it
        cursor = self.conn.execute("INSERT INTO countries (ccode, cname) VALUES (?, ?)",
                          (country_code, f"Country {country_code}"))
        return cursor.lastrowid

    def get_or_create_language_id(self, lang_code: str) -> Optional[int]:
        """
        Get language id
        """
        if not lang_code:
            return None

        cursor = self.conn.execute("SELECT id FROM languages WHERE code = ?", (lang_code,))
        result = cursor.fetchone()

        if result:
            return result[0]

        # If not exists, create it
        cursor = self.conn.execute("INSERT INTO languages (code, lang) VALUES (?, ?)",
                          (lang_code, f"Language {lang_code}"))
        return cursor.lastrowid

    def get_or_create_area_id(self, area_code: str) -> Optional[int]:
        """
        get area id
        """
        if not area_code:
            return None

        cursor = self.conn.execute("SELECT id FROM area WHERE acode = ?", (area_code,))
        result = cursor.fetchone()

        if result:
            return result[0]

        # If not exists, create it
        cursor = self.conn.execute("INSERT INTO area (acode, aname) VALUES (?, ?)",
                          (area_code, f"Area {area_code}"))
        return cursor.lastrowid

    def load_bands(self):
        """
        Load bandplan
        """
        cursor = self.conn.execute("SELECT band_name, freq_start, freq_end FROM frequency_bands")
        self.bands = [
            {'band_name': row[0], 'freq_start': row[1], 'freq_end': row[2]}
            for row in cursor.fetchall()
        ]

    def get_band(self, frequency):
        """
        return band by frequency
        """
        if not self.bands:
            self.load_bands()

        for band in self.bands:
            if band['freq_start'] <= frequency <= band['freq_end']:
                return band['band_name']
        return "---"

    def get_middle(self, band):
        """
        return band center
        """
        if not self.bands:
            self.load_bands()
        for item in self.bands:
            if item['band_name'] == band:
                return (int(item['freq_start']) + int(item['freq_end'])) / 2 * 1000
        return 10000000


    def import_eibi_csv(self, csv_file_path: str, update: bool = True):
        """
        Imports eibi csv
        """
        imported_count = 0
        updated_count = 0
        error_list = []

        if not update:
            self.conn.execute ("delete from broadcasts where fleibi != 0;")
            self.conn.commit()

        with open(csv_file_path, 'r') as file:
            # first line contains headers
            next(file)

            for line_num, line in enumerate(file, 2):
                try:
                    # strip line
                    line = line.strip()
                    if not line:
                        continue
                    fields = line.split(';')
                    if len(fields) < 11:
                        error_list.append(f"Row {line_num}: not enough data ({len(fields)})")
                        continue

                    # Process fields
                    frequency = float(fields[0]) if fields[0] else None
                    start_time, end_time = self.parse_time_range(fields[1])
                    days_operation = fields[2] if fields[2] else None
                    country_code = fields[3] if fields[3] else None
                    station_name = fields[4] if fields[4] else "Unknown"
                    language_code = fields[5] if fields[5] else None
                    target_area_code = fields[6] if fields[6] else None
                    transmitter_site = fields[7] if fields[7] else None
                    persistence_code = int(fields[8]) if fields[8].isdigit() else None
                    start_date = fields[9] if fields[9] else None
                    end_date = fields[10] if len(fields) > 10 and fields[10] else None

                    # remarks 
                    remarks = None
                    if len(fields) > 11:
                        remarks = ';'.join(fields[11:])
                    elif end_date and '[' in end_date:
                        # remarks in end date
                        remarks = end_date
                        end_date = None

                    if not frequency:
                        error_list.append(f"Row {line_num}: missing frequency")
                        continue

                    # get ids of related fields
                    country_id = self.get_or_create_country_id(country_code)
                    language_id = self.get_or_create_language_id(language_code)
                    area_id = self.get_or_create_area_id(target_area_code)

                    # check if already exists
                    existing_cursor = self.conn.execute("""
                        SELECT id FROM broadcasts 
                        WHERE frequency_khz = ? AND station_name = ? AND start_time = ?
                    """, (frequency, station_name, start_time))

                    existing = existing_cursor.fetchone()

                    if existing and update:
                        # Update row
                        self.conn.execute("""
                            UPDATE broadcasts SET
                                end_time = ?, days_operation = ?, country_id = ?,
                                language_id = ?, target_area_id = ?, transmitter_site = ?,
                                persistence_code = ?, start_date = ?, end_date = ?, remarks = ?,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE id = ?
                        """, (end_time, days_operation, country_id, language_id, area_id,
                              transmitter_site, persistence_code, start_date, end_date, remarks,
                              existing[0]))
                        updated_count += 1

                    elif not existing:
                        # Insert new row
                        self.conn.execute("""
                            INSERT INTO broadcasts (
                                frequency_khz, start_time, end_time, days_operation, country_id,
                                station_name, language_id, target_area_id, transmitter_site,
                                persistence_code, start_date, end_date, remarks, fleibi
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                        """, (frequency, start_time, end_time, days_operation, country_id,
                              station_name, language_id, area_id, transmitter_site,
                              persistence_code, start_date, end_date, remarks))
                        imported_count += 1

                    # Commit every 1000 lines
                    if (imported_count + updated_count) % 1000 == 0:
                        self.conn.commit()

                except Exception as e:
                    error_list.append(f"Row {line_num}: error {e}")
                    continue

        self.conn.commit()
        return (imported_count, updated_count, error_list)


################## Lookup on frequency based on current time/day of week

    def _get_curtime(self):
        """
        get current time
        """
        now = datetime.now()
        current_time = now.strftime("%H%M")
        current_day = now.strftime("%a").lower()  # mon, tue, wed, etc.

        # 10 minutes allowance
        time_margin = timedelta(minutes=10)
        start_time = (now - time_margin).strftime("%H%M")
        end_time = (now + time_margin).strftime("%H%M")

        return current_time, current_day, start_time, end_time

    def _time2min(self, time_str):
        """
        convert hh:mm to minutes from 00:00
        """
        if len(time_str) == 4:
            hours = int(time_str[:2])
            minutes = int(time_str[2:])
            return hours * 60 + minutes
        return 0

    def _check_dow(self, days_operation, current_day):
        """
        Check if dow is ok
        """
        if not days_operation or days_operation.strip() == "":
            return True  # Vuoto significa tutti i giorni

        days_operation = days_operation.lower().strip()

        # handles ranges as "mon-fri"
        if "-" in days_operation and len(days_operation.split("-")) == 2:
            start_day, end_day = days_operation.split("-")
            days_week = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

            try:
                start_idx = days_week.index(start_day.strip())
                end_idx = days_week.index(end_day.strip())
                current_idx = days_week.index(current_day)

                if start_idx <= end_idx:
                    return start_idx <= current_idx <= end_idx
                else:  # Attraversa la settimana (es. fri-mon)
                    return current_idx >= start_idx or current_idx <= end_idx
            except ValueError:
                pass

        # handles distinct days as "mon,thu,sat"
        days_list = [day.strip() for day in days_operation.split(",")]
        return current_day in days_list

    def _check_time(self, start_time, end_time, current_start, current_end):
        """
        check time
        """
        if not start_time or not end_time:
            return True  # Se non ci sono orari, assume sempre attiva

        try:
            # Converte in minuti per facilitare il confronto

            broadcast_start = self._time2min(start_time)
            broadcast_end = self._time2min(end_time)
            window_start = self._time2min(current_start)
            window_end = self._time2min(current_end)

            if broadcast_end < broadcast_start:
                # handles skeds that crosses midnight
                return (window_start >= broadcast_start or window_end <= broadcast_end or
                        window_start <= broadcast_end or window_end >= broadcast_start)
            else:
                return not (window_end < broadcast_start or window_start > broadcast_end)

        except (ValueError, IndexError):
            return True

    def lookup(self, freq=10000.0):
        """
        Do database lookup based on frequency
        """
        try:
            cursor = self.conn.cursor()
            current_time, current_day, start_window, end_window = self._get_curtime()
            freq_min = float(freq) - 5.0
            freq_max = float(freq) + 5.0

            query = """
            SELECT 
                b.id,
                b.frequency_khz,
                b.start_time,
                b.end_time,
                b.days_operation,
                b.station_name,
                c.cname as country_name,
                l.lang as language_name,
                b.persistence_code,
                b.transmitter_site,
                b.remarks
            FROM broadcasts b
            LEFT JOIN countries c ON b.country_id = c.id
            LEFT JOIN languages l ON b.language_id = l.id
            WHERE b.frequency_khz >= ? AND b.frequency_khz <= ?
                AND b.persistence_code != 8
            ORDER BY b.frequency_khz, b.start_time
            """

            cursor.execute(query, (freq_min, freq_max))
            rows = cursor.fetchall()
            results = []
            # Filter data
            for row in rows:
                row_dict = dict(row)
                # check days of week
                if self._check_dow(row_dict['days_operation'], current_day):
                    # check time
                    if self._check_time(row_dict['start_time'], row_dict['end_time'], start_window, end_window):
                        results.append(row_dict)

            return results, 0, ""

        except sqlite3.Error as e:
            return [], -1, f"Database error loading data: {str(e)}"
        except Exception as e:
            return [], -2, f"Error in lookup data: {str(e)}"

########### Free field search

    def search_skeds(self, filters):
        """
        Free fields search
        """
        query = """
            SELECT DISTINCT
                b.frequency_khz, b.start_time, b.end_time, b.days_operation,
                c.cname as country, b.station_name, l.lang as language,
                a.aname as target_area, b.transmitter_site, b.persistence_code,
                b.start_date, b.end_date, b.remarks,
                fb.band_name
            FROM broadcasts b
            LEFT JOIN countries c ON b.country_id = c.id
            LEFT JOIN languages l ON b.language_id = l.id
            LEFT JOIN area a ON b.target_area_id = a.id
            LEFT JOIN frequency_bands fb ON b.frequency_khz >= fb.freq_start 
                AND b.frequency_khz < fb.freq_end
            WHERE 1=1
        """

        params = []

        # Filtri possibili
        if 'freq_min' in filters:
            query += " AND b.frequency_khz >= ?"
            params.append(filters['freq_min'])

        if 'freq_max' in filters:
            query += " AND b.frequency_khz <= ?"
            params.append(filters['freq_max'])

        if 'station' in filters:
            query += " AND b.station_name LIKE ?"
            params.append(f"%{filters['station']}%")

        if 'country' in filters:
            query += " AND c.ccode = ?"
            params.append(filters['country'])

        if 'language' in filters:
            query += " AND l.code = ?"
            params.append(filters['language'])

        if 'target_area' in filters:
            query += " AND a.acode = ?"
            params.append(filters['target_area'])

        if 'band' in filters:
            query += " AND fb.band_name = ?"
            params.append(filters['band'])

        if 'time' in filters:
            # Ricerca per ora specifica (formato HHMM)
            query += " AND (b.start_time <= ? AND b.end_time >= ?)"
            params.extend([filters['time'], filters['time']])

        query += " ORDER BY b.frequency_khz, b.start_time"

        if 'limit' in filters:
            query += f" LIMIT {filters['limit']}"

        cursor = self.conn.execute(query, params)
        columns = [description[0] for description in cursor.description]

        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results

    def get_statistics(self) -> dict:
        """
        Return database usage
        """
        stats = {}

        # Conteggi generali
        cursor = self.conn.execute("SELECT COUNT(*) FROM broadcasts")
        stats['total_broadcasts'] = cursor.fetchone()[0]

        cursor = self.conn.execute("SELECT COUNT(DISTINCT station_name) FROM broadcasts")
        stats['unique_stations'] = cursor.fetchone()[0]

        cursor = self.conn.execute("SELECT COUNT(*) FROM countries")
        stats['countries'] = cursor.fetchone()[0]

        cursor = self.conn.execute("SELECT COUNT(*) FROM languages")
        stats['languages'] = cursor.fetchone()[0]

        # Top 10 stations
        cursor = self.conn.execute("""
            SELECT station_name, COUNT(*) as freq_count
            FROM broadcasts
            GROUP BY station_name
            ORDER BY freq_count DESC
            LIMIT 10
        """)
        stats['top_stations'] = cursor.fetchall()

        # Band distribution
        cursor = self.conn.execute("""
            SELECT fb.band_name, COUNT(*) as count
            FROM broadcasts b
            LEFT JOIN frequency_bands fb ON b.frequency_khz >= fb.freq_start 
                AND b.frequency_khz < fb.freq_end
            GROUP BY fb.band_name
            ORDER BY count DESC
        """)
        stats['band_distribution'] = cursor.fetchall()

        return stats

    def get_countries(self):
        cursor = self.conn.execute("SELECT ccode, cname FROM countries")
        return cursor.fetchall()

    def get_langs(self):
        cursor = self.conn.execute("SELECT code, lang FROM languages")
        return cursor.fetchall()

    def get_areas(self):
        cursor = self.conn.execute("SELECT acode, aname FROM area")
        return cursor.fetchall()

    def get_bands(self):
        cursor = self.conn.execute("SELECT id, band_name FROM frequency_bands")
        return cursor.fetchall()

    def close(self):
        """
        Close connection
        """
        self.conn.close()



if __name__ == "__main__":
    db = RadioDatabase(None, "data")
    print(db.lookup(10000))