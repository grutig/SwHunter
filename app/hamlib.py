import ctypes
import platform
import os
import logging
from ctypes import c_int, c_char_p, c_double, c_void_p, POINTER, CFUNCTYPE, c_long
from enum import IntEnum
from gettext import gettext as _
from PyQt5 import QtCore

""" 
ShortwaveHunter
BCL radio software
HamLib Wrapper

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


class RigState(IntEnum):
    """Stati del rig"""
    RIG_OK = 0
    RIG_EINVAL = -1
    RIG_ECONF = -2
    RIG_ENOMEM = -3
    RIG_ENIMPL = -4
    RIG_ETIMEOUT = -5
    RIG_EIO = -6
    RIG_EINTERNAL = -7
    RIG_EPROTO = -8
    RIG_ERJCTED = -9
    RIG_ETRUNC = -10
    RIG_ENAVAIL = -11
    RIG_ENTARGET = -12
    RIG_BUSERROR = -13
    RIG_BUSBUSY = -14
    RIG_EARG = -15


class RigCaps(ctypes.Structure):
    _fields_ = [
        ("rig_model", c_int),  # Radio model ID
        ("model_name", c_char_p),  # Model name
        ("mfg_name", c_char_p),  # Manufacturer name
        ("version", c_char_p),  # Version
        ("copyright", c_char_p),  # Copyright
        ("status", c_int),  # Status (stable, beta, etc.)
        ("rig_type", c_int),  # Radio type
        ("ptt_type", c_int),  # PTT type
        ("dcd_type", c_int),  # DCD type
        ("port_type", c_int),  # Port type
        ("serial_rate_min", c_int),  # Minimum serial speed
        ("serial_rate_max", c_int),  # Maximum serial speed
        ("serial_data_bits", c_int),  # Serial data bits
        ("serial_stop_bits", c_int),  # Serial stop bits
        ("serial_parity", c_int),  # Serial parity
        ("serial_handshake", c_int),  # Serial handshake
        ("write_delay", c_int),  # Write delay
        ("post_write_delay", c_int),  # Post-write delay
        ("timeout", c_int),  # Timeout
        ("retry", c_int)  # Retry attempts
    ]


RIG_MODES = {
    "AM": 1,
    "CW": 2,
    "USB": 4,
    "LSB": 8,
    "RTTY": 16,
    "FM": 32
}

RIG_MODES_INV = {v: k for k, v in RIG_MODES.items()}


class HamlibError(Exception):
    def __init__(self, code, message=""):
        self.code = code
        self.message = message or f"Hamlib error code: {code}"
        logging.error(message)
        super().__init__(self.message)


class HamlibWrapper():
    """
    Cross platform hamlib wrapper
    """

    # Mappa i tipi di status
    status_map = {
        0: "Alpha",
        1: "Beta",
        2: "Stable",
        3: "Untested"
    }


    def __init__(self, rootapp):
        self.rootapp = rootapp
        self.lib = None
        self.rig = None
        self.rigid = None
        self.opnd = False
        self._load_library()
        self._setup_c_function()
        self._rig_list = {}
        self.flmode = True
        self.flsmeter = True


    def _load_library(self):
        """
        load hamlib lib
        """
        system = platform.system().lower()
        loader = ctypes.CDLL
        if system == 'windows':
            paths = ["c:\\windows", "c:\\windows\\system32", os.path.join(self.rootapp.rootdir, 'hamlib', 'bin')]
            names = ['hamlib-4.dll', 'hamlib.dll', 'libhamlib-4.dll', 'libhamlib.dll']
            loader = ctypes.WinDLL
        elif system == 'darwin':
            paths = ['/usr/lib/', '/usr/local/lib/', '/opt/homebrew/lib/']
            names = ['libhamlib.4.dylib', 'libhamlib.dylib']
        else:
            # linux
            paths = ['/usr/lib/', '/usr/local/lib/', '/usr/lib/aarch64-linux-gnu/']
            names = ['libhamlib.so.4', 'libhamlib.so']

        for path in paths:
            for name in names:
                try:
                    self.lib = loader(os.path.join(path, name))
                    self.rootapp.hllink = True
                    return
                except OSError:
                    continue
        self.rootapp.hllink = False
        self.rootapp.show_error("hamlib", _("hamlib not found!"), _("Radio functions are disabled"))

    def _setup_c_function(self):
        """
        setup c bindings
        """
        if not self.lib:
            return

        # rig_set_debug
        self.lib.rig_set_debug.argtypes = [c_int]

        # rig_init
        self.lib.rig_init.argtypes = [c_int]
        self.lib.rig_init.restype = c_void_p

        # rig_cleanup
        self.lib.rig_cleanup.argtypes = [c_void_p]
        self.lib.rig_cleanup.restype = c_int

        # rig_open
        self.lib.rig_open.argtypes = [c_void_p]
        self.lib.rig_open.restype = c_int

        # rig_close
        self.lib.rig_close.argtypes = [c_void_p]
        self.lib.rig_close.restype = c_int

        # rig_set_vfo
        self.lib.rig_set_vfo.argtypes = [c_void_p, c_int]
        self.lib.rig_set_vfo.restype = c_int

        # rig_set_freq
        self.lib.rig_set_freq.argtypes = [c_void_p, c_int, c_double]
        self.lib.rig_set_freq.restype = c_int

        # rig_get_freq
        self.lib.rig_get_freq.argtypes = [c_void_p, c_int, POINTER(c_double)]
        self.lib.rig_get_freq.restype = c_int

        # rig_set_conf
        self.lib.rig_set_conf.argtypes = [c_void_p, ctypes.c_int, c_char_p]
        self.lib.rig_set_conf.restype = ctypes.c_int

        # rig_load_all_backends() -> int
        self.lib.rig_load_all_backends.restype = ctypes.c_int
        self.lib.rig_load_all_backends.argtypes = []
        self.CALLBACK_TYPE = CFUNCTYPE(
            c_int,  # return type
            POINTER(ctypes.c_void_p),  # rig_caps *
            c_void_p  # data pointer
        )
        self.lib.rig_list_foreach.restype = ctypes.c_int
        self.lib.rig_list_foreach.argtypes = [
            self.CALLBACK_TYPE,
            c_void_p
        ]

        # rig_get_caps()
        self.lib.rig_get_caps.restype = ctypes.POINTER(RigCaps)
        self.lib.rig_get_caps.argtypes = [ctypes.c_int]

        # rig_set_debug debug verbosity
        self.lib.rig_set_debug.argtypes = [ctypes.c_int]
        self.lib.rig_set_debug.restype = None
        # set verbosity none
        RIG_VERB_NONE = 0
        self.lib.rig_set_debug(RIG_VERB_NONE)
        # self.lib.rig_set_debug(6)

        # rig_token_lookup
        self.lib.rig_token_lookup.argtypes = [c_void_p, ctypes.c_char_p]
        self.lib.rig_token_lookup.restype = ctypes.c_ulong

        # rig_set_vfo_opt
        self.lib.rig_set_vfo_opt.argtypes = [c_void_p, c_int]
        self.lib.rig_set_vfo_opt.restype = c_int

        # rig_get_conf
        self.lib.rig_get_conf.argtypes = [c_void_p, ctypes.c_ulong, ctypes.c_char_p]
        self.lib.rig_get_conf.restype = ctypes.c_int

        # get_mode
        self.lib.rig_get_mode.argtypes = [c_void_p, c_int, POINTER(c_long), POINTER(c_long)]
        self.lib.rig_get_mode.restype = c_int

        # get_mode
        self.lib.rig_set_mode.argtypes = [c_void_p, c_int, c_long, c_long]
        self.lib.rig_set_mode.restype = c_int

        # rig_set_cache_timeout_ms
        self.lib.rig_set_cache_timeout_ms.argtypes = [c_void_p, c_int, c_int, c_int]
        self.lib.rig_set_cache_timeout_ms.restype = c_int

        # get_level
        self.lib.rig_has_get_level.argtypes = [c_void_p, c_int, POINTER(ctypes.c_int)]
        self.lib.rig_has_get_level.restype = c_long
        self.lib.rig_get_level.argtypes = [c_void_p, c_int, c_int, POINTER(ctypes.c_int)]
        self.lib.rig_get_level.restype = c_int

        # rigerror
        self.lib.rigerror.argtypes = [ctypes.c_int]
        self.lib.rigerror.restype = ctypes.c_char_p

    def load_all_backends(self) -> int:
        """
        Carica all backend
        return loaded backend, error code if negative
        """
        try:
            result = self.lib.rig_load_all_backends()
            if result < 0:
                self.rootapp.hllink = False
                self.rootapp.show_error("hamlib", _("Can't supported radio list, error") + f" {result}")
            return result
        except Exception as e:
            self.rootapp.show_error("hamlib", _("Fatal error - ") + f" {e}", abort=10)
            return -1

    def get_radio_list(self):
        """
        Get supported radio list
        """
        self.load_all_backends()
        radio = []
        brand = []

        class RadioInfo(ctypes.Structure):
            _fields_ = [
                ("rig_model", ctypes.c_int),
                ("model_name", ctypes.c_char_p),
                ("mfg_name", ctypes.c_char_p),
                ("version", ctypes.c_char_p),
                ("copyright", ctypes.c_char_p),
                ("status", ctypes.c_int),
                ("rig_type", ctypes.c_int),
            ]

        # ---------------------------------------------- callback
        def callback(caps_ptr, data):
            try:
                if not caps_ptr:
                    return 1
                caps = ctypes.cast(caps_ptr, ctypes.POINTER(RadioInfo)).contents
                # extract fiels
                model_id = caps.rig_model
                model_name = caps.model_name.decode('utf-8') if caps.model_name else "Unknown"
                mfg_name = caps.mfg_name.decode('utf-8') if caps.mfg_name else "Unknown"
                version = caps.version.decode('utf-8') if caps.version else "Unknown"
                status = caps.status
                rig_type = caps.rig_type
                # radio dictionary
                radio_info = {
                    'id': model_id,
                    'model': model_name,
                    'manufacturer': mfg_name,
                    'version': version,
                    'status': self.status_map.get(status, f"Unknown({status})"),
                    'status_code': status,
                    'type_code': rig_type
                }
                radio.append(radio_info)
                if radio_info['manufacturer'] not in brand:
                    brand.append(radio_info['manufacturer'])
                # return 1 to continue
                return 1
            except Exception as e:
                logging.error(f"Error hamlib: {e}")
                return 1

        # ---------------------------------------------- callback

        try:
            # Esegue il callback per ogni radio
            callback_func = self.CALLBACK_TYPE(callback)
            result = self.lib.rig_list_foreach(callback_func, None)

            # Ordina per produttore e modello
            radio.sort(key=lambda x: (x['manufacturer'], x['model']))
            brand.sort()
            return brand, radio

        except Exception as e:
            logging.error(f"Error hamlib: {e}")

    def get_rig_caps(self, id):
        """
        get rig caps
        Args: id (int): hamlib ID
        dict: dictionary
        """
        caps_ptr = self.lib.rig_get_caps(id)
        if not caps_ptr:
            return None
        return caps_ptr.contents

    def decode_status(self, stc):
        try:
            return self.status_map[stc]
        except:
            return "???"

    def decode_type(self, rtc):
        """
        rig_type (int)
        Dictionary
        """
        # bitmaps 
        RIG_FLAG_TRANSCEIVER = 0x0001
        RIG_FLAG_SCANNER = 0x0002
        RIG_FLAG_MOBILE = 0x0004
        RIG_FLAG_HANDHELD = 0x0008
        RIG_FLAG_COMPUTER = 0x0010
        RIG_FLAG_TRUNKING = 0x0020
        RIG_FLAG_TUNER = 0x0040
        # descriptions 
        type_flags = {
            RIG_FLAG_TRANSCEIVER: "Transceiver",
            RIG_FLAG_SCANNER: "Scanner",
            RIG_FLAG_MOBILE: "Mobile",
            RIG_FLAG_HANDHELD: "Handheld",
            RIG_FLAG_COMPUTER: "Computer",
            RIG_FLAG_TRUNKING: "Trunking",
            RIG_FLAG_TUNER: "Tuner"
        }

        active_types = []
        active_flags = {}
        for flag, description in type_flags.items():
            if rtc & flag:
                active_types.append(description)
                active_flags[description.lower()] = True
            else:
                active_flags[description.lower()] = False

        # description
        if not active_types:
            description = "Unknown/Other"
        elif len(active_types) == 1:
            description = active_types[0]
        else:
            description = " + ".join(active_types)

        return {
            'active_types': active_types,
            'description': description,
            'flags': active_flags,
            'is_transceiver': bool(rtc & RIG_FLAG_TRANSCEIVER),
            'is_scanner': bool(rtc & RIG_FLAG_SCANNER),
            'is_mobile': bool(rtc & RIG_FLAG_MOBILE),
            'is_handheld': bool(rtc & RIG_FLAG_HANDHELD),
            'is_computer': bool(rtc & RIG_FLAG_COMPUTER),
            'is_trunking': bool(rtc & RIG_FLAG_TRUNKING),
            'is_tuner': bool(rtc & RIG_FLAG_TUNER)
        }

    def _get_error(self, result, func, parms):
        """
        get hamllib error
        """
        emsg = ""
        if result == RigState.RIG_OK:
            return 0, ''
        # decode error
        emsg = "Unknown error"
        try:
            if hasattr(self.lib, 'rigerror'):
                err = self.lib.rigerror(result)
                if err:
                    # extract last message from list
                    msgl = err.decode(errors='ignore').split("\n")
                    emsg = [s for s in msgl if s][-1]
        except:
            pass
        logging.error(f"hamlib error {emsg}, rigid {self.rigid}, func: {func} {parms}")
        return result, emsg

    def init_rig(self, model_id):
        """
        model_id (int): hamlib ID of rig
        Returns:  1 if success ok, negative for errors
        """
        if not self.lib:
            # Hamlib not loaded
            return -1
        self.rig = self.lib.rig_init(model_id)
        if not self.rig:
            # Rig init error
            logging.error(f"hamlib error, cant initialize rig id {model_id}")
            return -2
        self.rigid = model_id
        return 1

    def c_conv(self, msg):
        """
        return a mutable string buffer to c calla
        """
        return ctypes.create_string_buffer(msg.encode())

    def set_conf(self, param, value):
        """
        Set rig configuration value
        param (str): par name
        value (str): par value
        """
        if not self.lib:
            # Hamlib not loaded
            return -1

        token = self.lib.rig_token_lookup(self.rig, self.c_conv(param))
        result = self.lib.rig_set_conf(self.rig, token, self.c_conv(value))
        return self._get_error(result, 'setconf', f"p: {param}, v:{value}")

    def open(self):
        """
        Open rig
        """
        if not self.rig:
            return -1, "Select Rig first"
        result = self.lib.rig_open(self.rig)
        if result == RigState.RIG_OK:
            self.opnd = True
        return self._get_error(result, 'open', f"")

    def get_conf(self, key):
        """
        enumerate rig parameters
        """
        if not self.rig:
            return -1, "Select Rig first"
        if not self.opnd:
            return -2, "Open Rig first"
        buffer = ctypes.create_string_buffer(256)
        rc = self.lib.rig_get_conf(self.rig, key.encode(), buffer, ctypes.sizeof(buffer))
        if rc != 0:
            return None
        return buffer.value.decode()

    def set_vfo(self, vfo=RIG_VFO_A):
        """
        Set rig vfo
        vfo (int): VFO id
        """
        if not self.rig:
            return -1, "Select Rig first"
        if not self.opnd:
            return -2, "Open Rig first"

        result = self.lib.rig_set_vfo(self.rig, vfo)
        return self._get_error(result, 'setvfo', f"vfo: {vfo}")

    def get_frequency(self, vfo=RIG_VFO_A):
        """
        Get rig frequency
        vfo (int): VFO id
        Returns: float: Frequency (Hz)
        """
        if not self.rig:
            return -1, "Select Rig first", ""
        if not self.opnd:
            return -2, "Open Rig first", ""

        freq = c_double()
        result = self.lib.rig_get_freq(self.rig, vfo, ctypes.byref(freq))
        s, m = self._get_error(result, 'getfreq', f"vfo: {vfo}")
        return int(freq.value), s, m

    def set_frequency(self, frequency, vfo=RIG_VFO_A):
        """
        Set rig frequency
        vfo (int): VFO id
        frequency (float): Freq (Hz)
        """
        if not self.rig:
            return -1, "Select Rig first"
        if not self.opnd:
            return -2, "Open Rig first"

        result = self.lib.rig_set_freq(self.rig, vfo, c_double(frequency))
        return self._get_error(result, 'setfreq', f"vfo: {vfo}, freq: {frequency}")

    def get_mode(self, vfo=RIG_VFO_A):
        """
        Get rig mode
        vfo (int): VFO id
        """
        if not self.rig:
            return -1, "Select Rig first", "", "", ""
        if not self.opnd:
            return -2, "Open Rig first", "", "", ""

        mode = c_long(0)
        width = c_long(0)
        result = self.lib.rig_get_mode(self.rig, vfo, ctypes.byref(mode), ctypes.byref(width))
        mstr = "???"
        try:
            mstr = RIG_MODES_INV[mode.value]
        except:
            pass
        s, e = self._get_error(result, 'getmode', f"vfo: {vfo}")
        return mstr, mode.value, width.value, s, e

    def set_mode(self, mstr, vfo=RIG_VFO_A):
        """
        Set rig mode
        vfo (int): VFO id
        """
        if not self.rig:
            return -1, "Select Rig first"
        if not self.opnd:
            return -2, "Open Rig first"

        try:
            mode = RIG_MODES[mstr]
        except:
            return -1, "Invalid mode"
        for width in [0, 500, 2400, 6000, 10000]:
            result = self.lib.rig_set_mode(self.rig, vfo, mode, width)
            if result == 0:
                break
        return self._get_error(result, 'setmode', f"vfo: {vfo}, mode: {mstr}")

    def get_smeter(self, vfo=RIG_VFO_A):
        if not self.rig:
            return -1, "Select Rig first", ""
        if not self.opnd:
            return -2, "Open Rig first", ""

        RIG_LEVEL_STRENGTH = (1 << 30)  # 0x40000000

        value = ctypes.c_int(0)
        if self.lib.rig_has_get_level(self.rig, RIG_LEVEL_STRENGTH, ctypes.byref(value)) == RIG_LEVEL_STRENGTH:
            result = self.lib.rig_get_level(self.rig, vfo + 1, RIG_LEVEL_STRENGTH, ctypes.byref(value))
        s, e = self._get_error(result, 'getsmeter', f"vfo: {vfo}")
        return value.value, s, e

    def testcon(self, conf):
        """
        test radio communications
        """
        sts = self.init_rig(conf['id'])
        port = conf['port']
        if platform.system().lower() == "windows":
            port = "////.//" + conf['port']
        self.set_conf("rig_pathname", port)
        self.set_conf("serial_speed", conf['baudrate'])
        self.set_conf("data_bits", conf['databits'])
        self.set_conf("stop_bits", conf['stopbits'])
        self.set_conf("serial_parity", conf['parity'])
        self.set_conf("retry", "2")

        s, e = self.open()
        if s != 0:
            self.close()
            return False
        s, e = self.set_vfo(0)
        mstr, mode, width, s, e = self.get_mode(0)
        if s != 0:
            self.close()
            return False
        freq, s, e = self.get_frequency(0)
        if s != 0:
            self.close()
            return False
        sm, s, e = self.get_smeter(0)
        if s != 0:
            self.close()
            return False
        self.close()
        return True

    def openconf(self, conf, cacheto, vfo=RIG_VFO_A):
        """
        open radio communications
        conf: config dictionary
        cacheto: cache expiration timeout msec
        vfo: vfo to use
        """
        sts = self.init_rig(conf['id'])
        if sts <= 0:
            return sts
        if platform.system().lower() == "windows":
            port = "////.//" + conf['port']
        self.set_conf("rig_pathname", port)
        self.set_conf("serial_speed", conf['baudrate'])
        self.set_conf("data_bits", conf['databits'])
        self.set_conf("stop_bits", conf['stopbits'])
        self.set_conf("serial_parity", conf['parity'])
        self.set_conf("timeout", "1000")
        self.set_conf("retry", "2")

        self.flmode = True
        self.flsmeter = True

        self.lib.rig_set_vfo_opt(self.rig, 0)

        s, e = self.open()
        if s != 0:
            self.close()
            return -1.1

        s, e = self.set_vfo(vfo)
        if s != 0:
            self.close()
            return -1.2

        # set cache timeout equal to poll time
        HAMLIB_CACHE_FREQ = 2
        self.lib.rig_set_cache_timeout_ms(self.rig, HAMLIB_CACHE_FREQ, vfo, cacheto)
        return 0

    def poll(self, vfo=RIG_VFO_A):
        """
        read radio values
        """
        try:
            freq, s, e = self.get_frequency(vfo)
            if e: raise HamlibError(e, f"{e} reading freq")
            mstr = "---"
            if self.flmode:
                mstr, mode, width, s, e = self.get_mode(0)
                if e:
                    self.flmode = False
            smeter = -54
            if self.flsmeter:
                smeter, s, e = self.get_smeter(0)
                if e:
                    self.flsmeter = False
                    smeter = -54
            return 0, mstr, freq, smeter, ""
        except HamlibError as e:
            return e, None, None, None, str(e)
        except Exception as e:
            return -2, None, None, None, str(e)

    def cleanup(self):
        """
        Rig cleanup
        """
        if not self.opnd:
            return -2, "Open Rig first"
        if self.rig:
            result = self.lib.rig_cleanup(self.rig)
            if result == RigState.RIG_OK:
                self.rig = None
                self.opnd = False
                self.rigid = None
            return self._get_error(result, 'cleanup', f"")
        return -1, "No rig selected"

    def close(self):
        """
        Terminate rig communications
        """
        if not self.opnd:
            return -2, "Open Rig first"
        if self.rig:
            result = self.lib.rig_close(self.rig)
            if result == RigState.RIG_OK:
                self.rig = None
                self.opnd = False
                self.rigid = None
            return self._get_error(result, 'close', f"")
        return -1, "No rig selected"

# hamlib api docs -> https://hamlib.sourceforge.net/manuals/4.3/index.html
