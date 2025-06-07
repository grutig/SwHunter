from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from app.ui.radio_ui import Ui_MainWindow
from PyQt5.QtGui import QPixmap, QPainter, QPen, QFont, QFontDatabase, QMoveEvent, QCloseEvent, QIntValidator
from PyQt5.QtWidgets import QAction, QActionGroup, QFileDialog, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, \
    QMessageBox
import math
import json

from app.config import ConfigWindow
from app.lookup import LookupWindow
from app.search import SearchWindow
from app.impsum import ImpsumWindow, WaitDialog
# edit forms
from app.areas import AreaWindow
from app.countries import CountryWindow
from app.frequencies import FrequencyWindow
from app.languages import LanguageWindow
from app.skeds import SkedsWindow
from app.transmitters import TransmitterWindow


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

RIG_VFO_CURR = 0
RIG_VFO_A = 1
RIG_VFO_B = 2

class RadioWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    rootapp = None
    active = None

    def __init__(self, rootapp):
        super().__init__()
        self.rootapp = rootapp
        self.setupUi(self)

        # modes
        self.btnAM.clicked.connect(self.mode_clicked)
        self.btnUSB.clicked.connect(self.mode_clicked)
        self.btnLSB.clicked.connect(self.mode_clicked)
        self.btnCW.clicked.connect(self.mode_clicked)

        # freq
        self.lw = None
        self.lbFreq.clicked.connect(self.freq_clicked)

        # bands
        for btn in self.findChildren(QtWidgets.QPushButton):
            txt = btn.objectName()
            if txt[0:3] == "btn" and txt[3:].isdigit():
                btn.clicked.connect(self.band_clicked)


        self.loadfont()
        self.clear()
        self.smeter_needle(0)
        self.loadsettings()
        self.loadmenu()
        self.loadradio()
        self.setup_ui_connections()

        # clock update timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()

        # rig update timer
        self.timer1 = QtCore.QTimer(self)
        self.timer1.timeout.connect(self.update_radio)
        self.timer1.stop()

        #
        self.mode = 0
        self.freq = 0
        self.smeter = 0

        # window handles
        self.lw = None
        self.sw = None
        self.eaw = None
        self.ecw = None
        self.efw = None
        self.elw = None
        self.esw = None
        self.etw = None
        self.lkw = None


        # set initial position
        screen = self.rootapp.app.primaryScreen().availableGeometry()
        if not screen.contains(self.geom[0], self.geom[1]):
            self.geom = (100, 100)
            self.savesettings()
        self.move(self.geom[0], self.geom[1])


    def loadsettings(self):
        jconf = self.rootapp.settings.value("configs")
        if jconf:
            self.configs = json.loads(jconf)
        else:
            self.configs = {}
        jconf = self.rootapp.settings.value("geom")
        if jconf:
            self.geom = json.loads(jconf)
        else:
            self.geom = (100, 100)
        self.active = self.rootapp.settings.value("active")
        return

    def savesettings(self):
        self.rootapp.settings.setValue("configs", json.dumps(self.configs))
        self.rootapp.settings.setValue("geom", json.dumps([self.x(), self.y()]))
        self.rootapp.settings.setValue("active", self.active)
        return

    def setup_ui_connections(self):
        """
        Setup internal connections
        """


    def loadfont(self):
        """
        load font from resources
        """
        fontid = QFontDatabase.addApplicationFont(":/font/lcd2000.ttf")
        if fontid == -1:
            return
        else:
            ffamily = QFontDatabase.applicationFontFamilies(fontid)[0]
            font = QFont(ffamily, 19)
            self.lbRig.setFont(font)
            self.lbMode.setFont(font)
            self.lbBand.setFont(QFont(ffamily, 16))
            self.lbFreq.setFont(QFont(ffamily, 47))
            self.lbClock.setFont(QFont(ffamily, 30))


    def loadmenu(self):
        """
        menu setup
        """
        self.menu_edit.clear()
        action = QAction(_translate("", "Areas"), self)
        action.triggered.connect(self.edit_areas)
        self.menu_edit.addAction(action)
        action = QAction(_translate("", "Bands"), self)
        action.triggered.connect(self.edit_frequencies)
        self.menu_edit.addAction(action)
        action = QAction(_translate("", "Countries"), self)
        action.triggered.connect(self.edit_coutries)
        self.menu_edit.addAction(action)
        action = QAction(_translate("", "Languages"), self)
        action.triggered.connect(self.edit_languages)
        self.menu_edit.addAction(action)
        action = QAction(_translate("", "Skeds"), self)
        action.triggered.connect(self.edit_skeds)
        self.menu_edit.addAction(action)
        action = QAction(_translate("", "Transmitters"), self)
        action.triggered.connect(self.edit_transmitters)
        self.menu_edit.addAction(action)
        action = QAction(_translate("", "Lookup"), self)
        action.triggered.connect(self.info_lookup)
        self.menu_info.addAction(action)
        action = QAction(_translate("", "Search"), self)
        action.triggered.connect(self.info_search)
        self.menu_info.addAction(action)



    def loadradio(self):
        """
        Load configured radios
        """
        desc = _translate("", "Edit")
        ###
        ### file
        ###
        self.menu_file.clear()
        action = QAction(_translate("", "Eibi import"), self)
        action.triggered.connect(self.eibi_import)
        self.menu_file.addAction(action)
        self.menu_file.addSeparator()
        for i, (key, value) in enumerate(sorted(self.configs.items())):
            action = QAction(f"{desc} {key}", self)
            action.triggered.connect(lambda checked, k=key: self.editconfig(k))
            self.menu_file.addAction(action)
        self.menu_file.addSeparator()
        # new config
        new_action = QAction(_translate("", "New config"), self)
        new_action.triggered.connect(lambda checked, k=None: self.editconfig(k))
        self.menu_file.addAction(new_action)
        ###
        ### config
        ###
        self.menu_config.clear()
        self.conf_group = QActionGroup(self)
        self.conf_group.setExclusive(True)
        action = QAction(_translate("", "No radio"), self)
        action.setCheckable(True)
        action.setChecked(True)
        self.menu_config.addAction(action)
        self.conf_group.addAction(action)
        for i, (key, value) in enumerate(sorted(self.configs.items())):
            action = QAction(f"{key}", self)
            #action.triggered.connect(lambda checked, k=key: self.setconfig(k))
            action.setCheckable(True)
            self.menu_config.addAction(action)
            self.conf_group.addAction(action)
        self.conf_group.triggered.connect(self.selectconf)


    def selectconf(self):
        """
        activate selected config
        """
        sender = self.sender()
        selected_action = self.conf_group.checkedAction()
        index = self.conf_group.actions().index(selected_action)
        if index == 0:
            # hamlib disabled
            conf = None
        else:
            shortname = selected_action.text()
            conf = self.configs[shortname]
        if self.rootapp.hamlib and self.rootapp.hamlib.rig:
            self.rootapp.hamlib.cleanup()
        if conf is None:
            self.timer1.stop()
            self.lbRig.setText("---")
        else:
            rsp = self.rootapp.hamlib.openconf(conf, 100, RIG_VFO_A)
            if rsp != 0:
                self.conf_group.actions()[0].setChecked(True)
                self.rootapp.show_error("HamLib", _translate("","Error opening rig"), details=f"error {rsp}")
            else:
                self.lbRig.setText(shortname)
                self.timer1.start(100)
            # self.update_radio()


    def editconfig(self, key=None):
        """
        edit an existing configuration
        """
        cw = ConfigWindow(self.rootapp.hamlib)
        cw.configs = self.configs
        if key is None:
            cw.load_default_values()
        else:
            cw.load_default_values(self.configs[key])
        result = cw.exec_()
        #
        if result == cw.Accepted:
            self.savesettings()
        del cw
        self.loadradio()


    def setconfig(self, key):
        """
        set active configuration
        """
        sender = self.sender()
        if sender.isChecked():
            if self.rootapp.hamlib.rig:
                # close rig
                self.rootapp.hamlib.cleanup()
            # do action



    def clear(self):
        """
        Clear rx fields
        """
        self.lbRig.setText("---")
        self.lbFreq.setText("---")
        self.lbBand.setText("---")
        self.lbMode.setText("---")

    #
    # handlers
    #

    # class RigWorker(QtCore.QThread):
    #     def __init__(self, rig_wrapper):
    #         super().__init__()
    #         self.rig = rig_wrapper
    #
    #     def run(self):
    #         result, error = self.rig.set_mode("AM")
    #         print(f"QThread result: {result}, {error}")

    def mode_clicked(self):
        button = self.sender()
        rig = self.rootapp.hamlib.rig
        if self.rootapp.hamlib and rig is not None:
            self.rootapp.hamlib.set_mode(button.text(), RIG_VFO_A)

    def band_clicked(self):
        band = self.sender().objectName()[3:]+"m"
        freq = self.rootapp.db.get_middle(band)
        self.rootapp.hamlib.set_frequency(freq, RIG_VFO_A)


    def freq_clicked(self):
        """
        call show_lockup with rig frequency
        """
        if self.freq == 0:
            return
        self.show_lookup(int(self.freq/1000))

    def show_lookup(self, freq):
        """
        show lookup window centerd on freq
        """
        self.lw = LookupWindow(self.rootapp.db, freq, self)
        self.lw.show()


    def update_clock(self):
        current_time = QtCore.QDateTime.currentDateTimeUtc().time()
        self.lbClock.setText(current_time.toString("HH:mm:ss"))


    def update_radio(self):
        # read radio values and show on form
        sts, mode, freq, smeter, err = self.rootapp.hamlib.poll(RIG_VFO_A)
        if sts:
            self.rootapp.show_error("HamLib", _translate("", "Error polling rig"), details=f"error {err}")
            return
        print(smeter)
        self.smeter = (self.smeter + self.smetercal(smeter)) / 2
        self.smeter_needle(self.smeter)
        if freq != self.freq:
           self.lbFreq.setText(f"{freq / 1000:,.1f}")
           self.freq = freq
           self.lbBand.setText(self.rootapp.db.get_band(freq/1000))
            # lookup(freq/1000) # eibi lookup
        if mode != self.mode:
           self.mode = mode
           self.lbMode.setText(mode)

    def smetercal(self, dbm):
        if dbm < 0:
            return max(dbm * 66 / 54 + 66, 0)
        else:
            return min(dbm * 100 / 106 + 66, 100)

    def smeter_needle(self, val=0.0):
        """
        Draw s-meter needle overlay
        """
        width = 140
        height = 120
        rot = 135
        l = 90
        x = 73
        y = 20
        dy = 60

        if val < 0: val = 0
        if val > 100: val = 100

        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)  # Sfondo trasparente

        angle_deg = rot - (val / 100.0) * 90.0
        angle_rad = math.radians(angle_deg)

        l1 = (dy - y) / math.sin(angle_rad)
        x1 = int(x + l1 * math.cos(angle_rad))

        x2 = int(x + l * math.cos(angle_rad))
        y2 = int(y + l * math.sin(angle_rad))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(Qt.red, 1)
        painter.setPen(pen)
        painter.drawLine(x1, height - dy, x2, height - y2)
        painter.end()

        self.lbSmeter.setPixmap(pixmap)

    def eibi_import(self):
        """
        Import eibi data
        """
        filename, _ = QFileDialog.getOpenFileName(
            self,
            _translate("", "Select Eibi file"),
            "",
            _translate("", "Eibi file (*.csv);;All files (*)")
        )
        if not filename:
            return
        dlg = WaitDialog(_translate("","Importing..."), self)
        dlg.show()
        QtWidgets.QApplication.processEvents()
        imp, upd, err = self.rootapp.db.import_eibi_csv(filename, False)
        dlg.hide()
        del dlg
        iw = ImpsumWindow(imp, upd, err, self)
        iw.exec_()


    def edit_areas(self):
        self.eaw = AreaWindow(self.rootapp, self)
        self.eaw.show()

    def edit_coutries(self):
        self.ecw = CountryWindow(self.rootapp, self)
        self.ecw.show()

    def edit_frequencies(self):
        self.efw = FrequencyWindow(self.rootapp, self)
        self.efw.show()

    def edit_languages(self):
        self.elw = LanguageWindow(self.rootapp, self)
        self.elw.show()

    def edit_skeds(self):
        self.esw = SkedsWindow(self.rootapp, self)
        self.esw.show()

    def edit_transmitters(self):
        self.etw = TransmitterWindow(self.rootapp, self)
        self.etw.show()

    def info_search(self):
        self.sw = SearchWindow(self.rootapp, self)
        self.sw.show()

    def info_lookup(self):
        self.lkw = Lookup(self.show_lookup, self)
        self.lkw.show()

    def closeEvent(self, event: QCloseEvent):
        if self.lw:
            del self.lw
        if self.eaw:
            del self.eaw
        if self.ecw:
            del self.ecw
        if self.efw:
            del self.efw
        if self.elw:
            del self.elw
        if self.esw:
            del self.esw
        if self.etw:
            del self.etw
        if self.lkw:
            del self.lkw
        self.savesettings()


class Lookup(QWidget):
    def __init__(self, show_lookup, parent=None):
        super().__init__()
        self.show_lookup = show_lookup
        self.setWindowTitle(_translate("","Lookup"))
        self.label = QLabel(_translate("","Frequency (kHz):"))
        self.input = QLineEdit()
        self.input.setValidator(QIntValidator())
        self.button = QPushButton(_translate("","Search"))
        self.button.clicked.connect(self.enter_freq)
        self.input.returnPressed.connect(self.enter_freq)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input)
        layout.addWidget(self.button)
        self.setLayout(layout)
        if self.parent:
            parent_geom = parent.frameGeometry()
            parent_pos = parent_geom.topLeft()
            parent_size = parent_geom.size()
            new_x = parent_pos.x()
            new_y = parent_pos.y() + parent_size.height()
            self.move(new_x, new_y)

    def enter_freq(self):
        freq = self.input.text()
        if freq:
            self.show_lookup(freq)
            self.input.clear()
        else:
            QMessageBox.warning(self, _translate("", "Invalid frequency"))