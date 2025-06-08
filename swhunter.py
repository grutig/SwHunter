import sys
from logging.handlers import RotatingFileHandler
from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog, QVBoxLayout, QLabel
from PyQt5.QtCore import QSettings, QTranslator, Qt
from app.db import RadioDatabase
import locale
from babel.support import Translations
import argparse
import os
import logging
from gettext import gettext as _

from app.radio import RadioWindow
from app.hamlib import HamlibWrapper


""" 
ShortwaveHunter
BCL radio software
rel 0.4.01

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

rootdir = os.path.dirname(os.path.abspath(__file__))
if hasattr(sys, '_MEIPASS'):
    # pyinstaller
    rootdir = sys._MEIPASS

def setup_logging():
    """
    Logging setup
    """
    logfile = os.path.join(rootdir, "data", "swhunt.log")
    # set rotation
    handler = RotatingFileHandler(logfile, "a", 1024 * 1024, 2)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    handler.setLevel(logging.INFO)
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    handler.setLevel(logging.ERROR)



class BabelTranslator(QTranslator):
    """
    Set babel as app translator
    """
    def __init__(self, translations):
        super().__init__()
        self.translations = translations

    def translate(self, context, source_text, disambiguation=None, n=-1):
        return self.translations.gettext(source_text)


class SWHunter():
    db = None       # database class
    hamlib = None   # hamlib wrapper class
    rootdir = None  # application absolute path
    hllink = False   # hamlink working

    def __init__(self, lang):
        self.app = QApplication(sys.argv)
        self.settings = QSettings("I8ZSE", "SwHunter")

        self.app.setApplicationName("ShortWaveHunter")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("I8ZSE")
        self.app.setOrganizationDomain("www.i8zse.it")

        # set translator
        translations = Translations.load('locale', lang, domain='messages')
        translator = BabelTranslator(translations)
        self.app.installTranslator(translator)

        self.app.setStyle('Fusion')
        self.main_window = RadioWindow(self)

    def run(self):
        logging.info("Start app")
        self.main_window.show()
        sys.exit(self.app.exec_())

    def show_error(self, error_type, message, details="", **kwargs):
        """
        Error dialog
        """
        logging.critical(f"Error {error_type}: {message} | {details}  ")
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(_("Error")+f" - {error_type}")
        msg_box.setText(message)
        if details:
            msg_box.setDetailedText(details)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
        abort = kwargs.get('abort', 0)
        if abort != 0:
            sys.exit(abort)


#####
# Main Entry Point
###########

if __name__ == "__main__":
    setup_logging()
    parser = argparse.ArgumentParser(description='Shortwave Hunter')
    parser.add_argument('-l', '--lang', type=str, help='Country lang code [it, en, de, fr, es]')
    args = parser.parse_args()
    if args.lang is None:
        args.lang = locale.setlocale(locale.LC_CTYPE).split(".")[0]
        if ("_") in args.lang:
            lang, country = args.lang.split("_")
            if lang.lower() != lang:
                # windows
                args.lang = {
                    'Italian': 'it',
                    'English': 'en',
                    'French': 'fr',
                    'German': 'de',
                    'Spanish': 'es'}[lang]
    try:
        hunter = SWHunter(args.lang)
        hunter.rootdir = rootdir
        hunter.db = RadioDatabase(hunter, os.path.join(rootdir, "data"))
        hunter.hamlib = HamlibWrapper(hunter)
        if hunter.hamlib is None:
            hunter.show_error("hamlib", _("hamlib not responding"), details="", abort=10)
        # a = hunter.settings.fileName()
        hunter.run()
    except Exception as e:
        logging.critical(f"Error {str(e)} starting app")
        import traceback
        traceback.print_exc()
        sys.exit(1)
