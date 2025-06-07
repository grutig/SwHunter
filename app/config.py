import serial.tools.list_ports
from PyQt5.QtCore import QEvent
from PyQt5.QtGui import QFocusEvent
from PyQt5.QtWidgets import QMessageBox, QDialog, QLineEdit, QFormLayout, QComboBox
from app.ui.config_ui import Ui_ConfigWindow
from PyQt5 import QtCore, QtWidgets

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

class ConfigWindow(QDialog):
    """
    Radio configuration dialog
    """
    hamlib = None
    radio = []
    brand = {}
    configs = {}
    flEdit = False

    def __init__(self, hamlib, current=None):
        super().__init__()
        self.hamlib = hamlib
        self.brand, self.radio = hamlib.get_radio_list()
        # Load dialog data
        self.ui = Ui_ConfigWindow()
        self.ui.setupUi(self)

        # Set interface dropdown
        self.setup_ui_connections()
        # setup fields
        self.validate(None, None)
        # set log focus handling
        for child in self.findChildren((QLineEdit, QComboBox)):
            if child.objectName():  # Solo se ha un nome
                child.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Event filter globale"""
        if event.type() == QEvent.FocusOut:
            control_name = obj.objectName()
            if control_name:
                self.validate(obj, control_name)

        return super().eventFilter(obj, event)

    def loaddata(self):
        return {
            'shortname': self.ui.lineEdit_shortname.text(),
            'mfg': self.ui.comboBox_manufacturer.currentData(),
            'radio': self.ui.comboBox_model.currentText(),
            'id': self.ui.comboBox_model.currentData(),
            'port': self.ui.comboBox_port.currentData(),
            'baudrate': self.ui.comboBox_baudrate.currentText(),
            'databits': self.ui.comboBox_databits.currentText(),
            'stopbits': self.ui.comboBox_stopbits.currentText(),
            'parity': self.ui.comboBox_parity.currentText(),
        }

    def validate(self, obj, event):
        conf = self.loaddata()
        bckok = "rgba(115, 255, 115, 0.5)"
        bckerr = "rgba(255, 115 , 115, 0.5)"
        flerr = False
        bck = bckok
        if self.flEdit:
            bck = "rgba(200, 200, 200)"
        else:
            if conf['shortname'] in self.configs.keys() or conf['shortname'] == "":
                flerr = True
                bck = bckerr
        self.ui.lineEdit_shortname.setStyleSheet("QLineEdit { background-color: " + bck + "; }")
        bckok = "rgba(115, 255, 115)"
        bckerr = "rgba(255, 115 , 115)"
        if conf['mfg'] == None or conf['radio'] == None or conf['id'] < 1:
            flerr = True
        bck = bckerr if flerr else bckok
        self.ui.pushButton_test.setEnabled(not flerr)
        self.ui.pushButton_save.setEnabled(not flerr)
        self.ui.pushButton_save.setStyleSheet(
                   "QPushButton { background-color: " + bck + "; color: white; font-weight: bold; padding: 8px; }")


    def setup_ui_connections(self):
        """
        Setup internal connections
        """
        # combobox
        self.ui.comboBox_manufacturer.currentTextChanged[str].connect(self.on_manufacturer_changed)
        self.ui.comboBox_model.currentTextChanged[str].connect(self.on_model_changed)

        # buttons
        self.ui.pushButton_refresh_ports.clicked.connect(self.update_ports)
        self.ui.pushButton_save.clicked.connect(self.saveconfig)
        self.ui.pushButton_delete.clicked.connect(self.deleteconfig)
        self.ui.pushButton_test.clicked.connect(self.testconfig)

        # Splitter
        # self.ui.splitter_main.setStretchFactor(0, 2)
        # self.ui.splitter_main.setStretchFactor(1, 1)

    def load_default_values(self, conf=None):
        """
        set baud rates
        """
        # fill radio backends
        for item in self.brand:
            self.ui.comboBox_manufacturer.addItem(item, userData=item)
        # fill serial ports
        self.update_ports()

        # Baud rates
        self.ui.comboBox_baudrate.clear()
        standard_bauds = ["1200", "2400", "4800", "9600", "19200", "38400", "57600", "115200"]
        self.ui.comboBox_baudrate.addItems(standard_bauds)

        # Data bits
        self.ui.comboBox_databits.addItems(["5", "6", "7", "8"])

        # Stop bits
        self.ui.comboBox_stopbits.addItems(["1", "1.5", "2"])

        # Parità con codici
        parity_options = [
            ("None", "N"),
            ("Odd", "O"),
            ("Even", "E"),
            ("Mark", "M"),
            ("Space", "S")
        ]
        for display, code in parity_options:
            self.ui.comboBox_parity.addItem(display, code)

        if conf is None:
            self.flEdit = False
            self.ui.lineEdit_shortname.setText("")
            self.ui.comboBox_manufacturer.addItem(_translate("", "-- Radio Brands --"))
            self.ui.comboBox_model.addItem(_translate("", "-- No models --"))
            self.ui.comboBox_baudrate.setCurrentText("9600")
            self.ui.comboBox_databits.setCurrentText("8")
            self.ui.comboBox_stopbits.setCurrentText("1")
            self.ui.comboBox_parity.setCurrentText("No")
            self.ui.lineEdit_shortname.setEnabled(True)
            self.ui.pushButton_delete.setEnabled(False)
        else:
            self.flEdit = True
            self.ui.lineEdit_shortname.setText(conf['shortname'])
            self.ui.comboBox_manufacturer.setCurrentText(conf['mfg'])
            models = [(model['id'], model['model'])
                      for model in self.radio
                      if model['manufacturer'] == conf['mfg']]
            for model in models:
                self.ui.comboBox_model.addItem(model[1], userData=model[0])
            self.ui.comboBox_model.setCurrentText(conf['radio'])

            idx = self.ui.comboBox_port.findData(conf['port'])
            self.ui.comboBox_port.setCurrentIndex(idx)
            self.ui.label_model_id_value.setText(str(conf['id']))
            self.ui.comboBox_baudrate.setCurrentText(conf['baudrate'])
            self.ui.comboBox_databits.setCurrentText(conf['databits'])
            self.ui.comboBox_stopbits.setCurrentText(conf['stopbits'])
            self.ui.comboBox_parity.setCurrentText(conf['parity'])
            self.ui.lineEdit_shortname.setEnabled(False)
            self.ui.pushButton_delete.setEnabled(True)

    def on_manufacturer_changed(self, data):
        """
        Event handler for brand change
        """
        self.ui.comboBox_model.clear()
        self.ui.label_model_id_value.setText("--")
        # get current value
        models = [(model['id'], model['model'])
                  for model in self.radio
                  if model['manufacturer'] == data]
        for model in models:
            self.ui.comboBox_model.addItem(model[1], userData=model[0])
        if not models:
            self.load_default_values()
        self.validate(None, None)

    def update_ports(self):
        self.ui.comboBox_port.clear()
        ports = serial.tools.list_ports.comports()
        if not ports:
            self.ui.comboBox_port.addItem(_translate("", "No ports"))
        else:
            ports = sorted(ports, key=lambda port: port.device)
            for port in ports:
                description = f"{port.device}"
                if port.description and port.description != "n/a":
                    description += f" - {port.description}"
                self.ui.comboBox_port.addItem(description, port.device)

    def on_model_changed(self, txt):
        """
        Model change handler
        """
        idx = self.ui.comboBox_model.currentIndex()
        if idx < 0:
            return
        hid = self.ui.comboBox_model.itemData(idx)  # hamlib id
        if hid is None:
            return
        caps = self.hamlib.get_rig_caps(hid)
        # populate window
        self.ui.label_model_id_value.setText(str(hid))
        info = _translate("", "Model: ") + f"{caps.model_name.decode()}\n"
        info += _translate("", "Brand: ") + f"{caps.mfg_name.decode()}\n"
        info += _translate("", "ID: ") + f"{hid}\n"
        info += _translate("", "Status: ") + f"{self.hamlib.decode_status(caps.status)}\n"
        info += _translate("", "Version: ") + f"{caps.version.decode()}\n"
        self.ui.textEdit_info.setPlainText(info)
        # serial ports
        self.update_ports()
        idx = self.ui.comboBox_baudrate.findText(str(caps.serial_rate_max))
        if idx >= 0:
            self.ui.comboBox_baudrate.setCurrentIndex(idx)
        idx = self.ui.comboBox_databits.findText(str(caps.serial_data_bits))
        if idx >= 0:
            self.ui.comboBox_databits.setCurrentIndex(idx)
        idx = self.ui.comboBox_stopbits.findText(str(caps.serial_stop_bits))
        if idx >= 0:
            self.ui.comboBox_stopbits.setCurrentIndex(idx)
        self.ui.comboBox_parity.setCurrentIndex(caps.serial_parity)
        self.validate(None, None)

    def saveconfig(self):
        """
        Validate and save configuration
        """
        conf = self.loaddata()
        self.configs[conf['shortname']] = conf
        QMessageBox.information(self, "Info", _translate("", "Configuration saved"))
        self.accept()


    def deleteconfig(self):
        reply = QMessageBox.question(
            self, _translate("", "Confirm Delete"),
            _translate("","Are you sure you want to delete this configuration?"),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            conf = self.loaddata()
            del self.configs[conf['shortname']]
            QMessageBox.information(self, "Info", _translate("", "Configuration deleted"))
            self.accept()

    def testconfig(self):
        conf = self.loaddata()
        resp = self.hamlib.testcon(conf)
        if resp:
            QMessageBox.information(self, _translate("","Test"), _translate("", "Configuration working"))
        else:
            QMessageBox.warning(self, _translate("","Test"), _translate("", "Configuration not working"))


