import ctypes
from ctypes import Structure, Union, POINTER, c_int, c_uint, c_char, c_char_p, c_double, c_float, c_long, c_ulong, \
    c_short, c_ushort, c_ubyte, c_void_p, c_size_t
from enum import IntEnum

""" 
ShortwaveHunter
BCL radio software
rig.h compatible classes and functions

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

# Hamlib constants
HAMLIB_MAXDBLSTSIZ = 8
HAMLIB_CHANLSTSIZ = 16
HAMLIB_FRQRANGESIZ = 30
HAMLIB_TSLSTSIZ = 60
HAMLIB_FLTLSTSIZ = 42
HAMLIB_MAX_SPECTRUM_SCOPES = 10
HAMLIB_MAX_SPECTRUM_MODES = 10
HAMLIB_MAX_SPECTRUM_SPANS = 20
HAMLIB_MAX_SPECTRUM_AVG_MODES = 10
HAMLIB_MAX_AGC_LEVELS = 8
RIG_SETTING_MAX = 64

# Basic type definitions for hamlib compatibility
hamlib_port_t = c_int
freq_t = c_double
shortfreq_t = c_float
pbwidth_t = c_long
dcd_t = c_int
ptt_t = c_int
rptr_shift_t = c_int
rptr_offs_t = c_long
split_t = c_int
vfo_t = c_int
ant_t = c_int
powerstat_t = c_int
reset_t = c_int
parm_t = c_int
setting_t = c_ulong
value_t = c_int
chan_t = c_uint
bank_t = c_int
rig_model_t = c_int
tone_t = c_uint
rmode_t = c_int
ann_t = c_int
vfo_op_t = c_int
scan_t = c_int
hamlib_token_t = c_long
rig_ptr_t = c_void_p


RIG_VFO_CURR = 0
RIG_VFO_A = 1
RIG_VFO_B = 2


RIG_MODES = {
    "AM": 1,
    "CW": 2,
    "USB": 4,
    "LSB": 8,
    "RTTY": 16,
    "FM": 32
}

RIG_MODES_INV = {v: k for k, v in RIG_MODES.items()}


# Enumerations
class RigState(IntEnum):
    """
    Rig States
    """
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


class RigStatusE(c_int):
    RIG_STATUS_ALPHA = 0
    RIG_STATUS_BETA = 1
    RIG_STATUS_STABLE = 2
    RIG_STATUS_DEPRECATED = 3


class PttTypeT(c_int):
    RIG_PTT_NONE = 0
    RIG_PTT_RIG = 1
    RIG_PTT_SERIAL_DTR = 2
    RIG_PTT_SERIAL_RTS = 3
    RIG_PTT_PARALLEL = 4
    RIG_PTT_CM108 = 5
    RIG_PTT_GPIO = 6
    RIG_PTT_GPION = 7


class DcdTypeT(c_int):
    RIG_DCD_NONE = 0
    RIG_DCD_RIG = 1
    RIG_DCD_SERIAL_DSR = 2
    RIG_DCD_SERIAL_CTS = 3
    RIG_DCD_SERIAL_CAR = 4
    RIG_DCD_PARALLEL = 5
    RIG_DCD_CM108 = 6
    RIG_DCD_GPIO = 7
    RIG_DCD_GPION = 8


class RigPortT(c_int):
    RIG_PORT_NONE = 0
    RIG_PORT_SERIAL = 1
    RIG_PORT_NETWORK = 2
    RIG_PORT_DEVICE = 3
    RIG_PORT_PACKET = 4
    RIG_PORT_DTMF = 5
    RIG_PORT_ULTRA = 6
    RIG_PORT_RPC = 7
    RIG_PORT_PARALLEL = 8
    RIG_PORT_CM108 = 9
    RIG_PORT_GPIO = 10
    RIG_PORT_GPION = 11
    RIG_PORT_USB = 12


class SerialParityE(c_int):
    RIG_PARITY_NONE = 0
    RIG_PARITY_ODD = 1
    RIG_PARITY_EVEN = 2
    RIG_PARITY_MARK = 3
    RIG_PARITY_SPACE = 4


class SerialHandshakeE(c_int):
    RIG_HANDSHAKE_NONE = 0
    RIG_HANDSHAKE_XONXOFF = 1
    RIG_HANDSHAKE_HARDWARE = 2


class AgcLevelE(c_int):
    RIG_AGC_OFF = 0
    RIG_AGC_SLOW = 1
    RIG_AGC_MEDIUM = 2
    RIG_AGC_FAST = 3
    RIG_AGC_USER = 4
    RIG_AGC_SUPERFAST = 5
    RIG_AGC_AUTO = 6


class RigSpectrumModeE(c_int):
    RIG_SPECTRUM_MODE_NONE = 0
    RIG_SPECTRUM_MODE_CENTER = 1
    RIG_SPECTRUM_MODE_FIXED = 2
    RIG_SPECTRUM_MODE_CENTER_SCROLL = 3
    RIG_SPECTRUM_MODE_FIXED_SCROLL = 4


# Forward declarations for complex structures
class RIG(Structure):
    pass


class Channel(Structure):
    pass


# Callback types
chan_cb_t = ctypes.CFUNCTYPE(c_int, POINTER(Channel), rig_ptr_t)
confval_cb_t = ctypes.CFUNCTYPE(c_int, rig_ptr_t, hamlib_token_t, c_char_p)


# Gran_t structure for granularity
class GranT(Structure):
    _fields_ = [
        ("min", c_double),  # Minimum value
        ("max", c_double),  # Maximum value
        ("step", c_double),  # Step/increment
    ]


# confparams structure for configuration parameters
class ConfParams(Structure):
    _fields_ = [
        ("token", hamlib_token_t),  # Identification token
        ("name", c_char_p),  # Parameter name
        ("label", c_char_p),  # Label
        ("tooltip", c_char_p),  # Tooltip
        ("dflt", c_char_p),  # Default value
        ("type", c_int),  # Parameter type
        ("u", c_void_p),  # Union for value (simplified)
    ]


# freq_range_t structure for frequency ranges
class FreqRangeT(Structure):
    _fields_ = [
        ("startf", freq_t),  # Start frequency
        ("endf", freq_t),  # End frequency
        ("modes", rmode_t),  # Supported modes
        ("low_power", c_int),  # Minimum power (mW)
        ("high_power", c_int),  # Maximum power (mW)
        ("vfo", vfo_t),  # VFO
        ("ant", ant_t),  # Antenna
        ("label", c_char_p),  # Descriptive label
    ]


# tuning_step_list structure
class TuningStepList(Structure):
    _fields_ = [
        ("modes", rmode_t),  # Valid modes
        ("ts", shortfreq_t),  # Tuning step
    ]


# filter_list structure
class FilterList(Structure):
    _fields_ = [
        ("modes", rmode_t),  # Supported modes
        ("width", pbwidth_t),  # Filter width
    ]


# cal_table_t structure for S-meter calibration
class CalTableT(Structure):
    _fields_ = [
        ("size", c_int),  # Number of points
        ("table", POINTER(c_int * 2)),  # Array of pairs [raw_value, cal_value]
    ]


# cal_table_float_t structure for float calibration
class CalTableFloatT(Structure):
    _fields_ = [
        ("size", c_int),  # Number of points
        ("table", POINTER(c_float * 2)),  # Array of pairs [raw_value, cal_value]
    ]


# rig_spectrum_scope structure
class RigSpectrumScope(Structure):
    _fields_ = [
        ("id", c_int),  # Scope ID
        ("name", c_char_p),  # Scope name
    ]


# rig_spectrum_avg_mode structure
class RigSpectrumAvgMode(Structure):
    _fields_ = [
        ("id", c_int),  # Mode ID
        ("name", c_char_p),  # Mode name
    ]


# value_t union for parameter/level values (simplified)
class ValueT(Union):
    _fields_ = [
        ("i", c_int),
        ("f", c_float),
        ("s", c_char_p),
    ]


# Function pointer types for callbacks
RigInitFunc = ctypes.CFUNCTYPE(c_int, POINTER(RIG))
RigCleanupFunc = ctypes.CFUNCTYPE(c_int, POINTER(RIG))
RigOpenFunc = ctypes.CFUNCTYPE(c_int, POINTER(RIG))
RigCloseFunc = ctypes.CFUNCTYPE(c_int, POINTER(RIG))

SetFreqFunc = ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, freq_t)
GetFreqFunc = ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, POINTER(freq_t))
SetModeFunc = ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, rmode_t, pbwidth_t)
GetModeFunc = ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, POINTER(rmode_t), POINTER(pbwidth_t))
SetVfoFunc = ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t)
GetVfoFunc = ctypes.CFUNCTYPE(c_int, POINTER(RIG), POINTER(vfo_t))
SetPttFunc = ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, ptt_t)
GetPttFunc = ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, POINTER(ptt_t))
GetDcdFunc = ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, POINTER(dcd_t))

# Other important functions (add as needed)
SetLevelFunc = ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, setting_t, ValueT)
GetLevelFunc = ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, setting_t, POINTER(ValueT))
SetFuncFunc = ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, setting_t, c_int)
GetFuncFunc = ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, setting_t, POINTER(c_int))

GetInfoFunc = ctypes.CFUNCTYPE(c_char_p, POINTER(RIG))
ResetFunc = ctypes.CFUNCTYPE(c_int, POINTER(RIG), reset_t)
PowerStatFunc = ctypes.CFUNCTYPE(c_int, POINTER(RIG), powerstat_t)
GetPowerStatFunc = ctypes.CFUNCTYPE(c_int, POINTER(RIG), POINTER(powerstat_t))


class rig_caps(Structure):
    _fields_ = [
        ("rig_model", rig_model_t),
        ("model_name", c_char_p),
        ("mfg_name", c_char_p),
        ("version", c_char_p),
        ("copyright", c_char_p),
        ("status", rig_status_e),

        ("rig_type", c_int),
        ("ptt_type", ptt_type_t),
        ("dcd_type", dcd_type_t),
        ("port_type", rig_port_t),

        ("serial_rate_min", c_int),
        ("serial_rate_max", c_int),
        ("serial_data_bits", c_int),
        ("serial_stop_bits", c_int),
        ("serial_parity", serial_parity_e),
        ("serial_handshake", serial_handshake_e),

        ("write_delay", c_int),
        ("post_write_delay", c_int),
        ("timeout", c_int),
        ("retry", c_int),

        ("has_get_func", setting_t),
        ("has_set_func", setting_t),
        ("has_get_level", setting_t),
        ("has_set_level", setting_t),
        ("has_get_parm", setting_t),
        ("has_set_parm", setting_t),

        ("level_gran", gran_t * 0),  # RIG_SETTING_MAX would be actual size
        ("parm_gran", gran_t * 0),  # RIG_SETTING_MAX would be actual size

        ("extparms", POINTER(confparams)),
        ("extlevels", POINTER(confparams)),
        ("extfuncs", POINTER(confparams)),
        ("ext_tokens", POINTER(c_int)),

        ("ctcss_list", POINTER(tone_t)),
        ("dcs_list", POINTER(tone_t)),

        ("preamp", c_int * 0),  # HAMLIB_MAXDBLSTSIZ would be actual size
        ("attenuator", c_int * 0),  # HAMLIB_MAXDBLSTSIZ would be actual size
        ("max_rit", shortfreq_t),
        ("max_xit", shortfreq_t),
        ("max_ifshift", shortfreq_t),

        ("agc_level_count", c_int),
        ("agc_levels", agc_level_e * 0),  # HAMLIB_MAX_AGC_LEVELS would be actual size

        ("announces", ann_t),

        ("vfo_ops", vfo_op_t),
        ("scan_ops", scan_t),
        ("targetable_vfo", c_int),
        ("transceive", c_int),

        ("bank_qty", c_int),
        ("chan_desc_sz", c_int),

        ("chan_list", chan_t * 0),  # HAMLIB_CHANLSTSIZ would be actual size

        ("rx_range_list1", freq_range_t * 0),  # HAMLIB_FRQRANGESIZ would be actual size
        ("tx_range_list1", freq_range_t * 0),
        ("rx_range_list2", freq_range_t * 0),
        ("tx_range_list2", freq_range_t * 0),
        ("rx_range_list3", freq_range_t * 0),
        ("tx_range_list3", freq_range_t * 0),
        ("rx_range_list4", freq_range_t * 0),
        ("tx_range_list4", freq_range_t * 0),
        ("rx_range_list5", freq_range_t * 0),
        ("tx_range_list5", freq_range_t * 0),

        ("tuning_steps", tuning_step_list * 0),  # HAMLIB_TSLSTSIZ would be actual size
        ("filters", filter_list * 0),  # HAMLIB_FLTLSTSIZ would be actual size

        ("str_cal", cal_table_t),
        ("swr_cal", cal_table_float_t),
        ("alc_cal", cal_table_float_t),
        ("rfpower_meter_cal", cal_table_float_t),
        ("comp_meter_cal", cal_table_float_t),
        ("vd_meter_cal", cal_table_float_t),
        ("id_meter_cal", cal_table_float_t),

        ("spectrum_scopes", rig_spectrum_scope * 0),  # HAMLIB_MAX_SPECTRUM_SCOPES would be actual size
        ("spectrum_modes", rig_spectrum_mode_e * 0),  # HAMLIB_MAX_SPECTRUM_MODES would be actual size
        ("spectrum_spans", freq_t * 0),  # HAMLIB_MAX_SPECTRUM_SPANS would be actual size
        ("spectrum_avg_modes", rig_spectrum_avg_mode * 0),  # HAMLIB_MAX_SPECTRUM_AVG_MODES would be actual size
        ("spectrum_attenuator", c_int * 0),  # HAMLIB_MAXDBLSTSIZ would be actual size

        ("cfgparams", POINTER(confparams)),
        ("priv", c_void_p),

        # Function pointers
        ("rig_init", CFUNCTYPE(c_int, POINTER(RIG))),
        ("rig_cleanup", CFUNCTYPE(c_int, POINTER(RIG))),
        ("rig_open", CFUNCTYPE(c_int, POINTER(RIG))),
        ("rig_close", CFUNCTYPE(c_int, POINTER(RIG))),

        ("set_freq", CFUNCTYPE(c_int, POINTER(RIG), vfo_t, freq_t)),
        ("get_freq", CFUNCTYPE(c_int, POINTER(RIG), vfo_t, POINTER(freq_t))),

        # ... (all other function pointers would follow the same pattern)
        # For brevity, I'm omitting the rest of the 100+ function pointers
        # but they would all be defined similarly to the ones above

        ("clone_combo_set", c_char_p),
        ("clone_combo_get", c_char_p),
        ("macro_name", c_char_p),

        ("async_data_supported", c_int),
        ("read_frame_direct", CFUNCTYPE(c_int, POINTER(RIG), ctypes.c_size_t, POINTER(ctypes.c_ubyte))),
        ("is_async_frame", CFUNCTYPE(c_int, POINTER(RIG), ctypes.c_size_t, POINTER(ctypes.c_ubyte))),
        ("process_async_frame", CFUNCTYPE(c_int, POINTER(RIG), ctypes.c_size_t, POINTER(ctypes.c_ubyte))),

        ("hamlib_check_rig_caps", c_char_p),
        ("get_conf2", CFUNCTYPE(c_int, POINTER(RIG), hamlib_token_t, c_char_p, c_int)),
        ("password", CFUNCTYPE(c_int, POINTER(RIG), c_char_p)),
        ("set_lock_mode", CFUNCTYPE(c_int, POINTER(RIG), c_int)),
        ("get_lock_mode", CFUNCTYPE(c_int, POINTER(RIG), POINTER(c_int))),

        ("timeout_retry", ctypes.c_short),
        ("morse_qsize", ctypes.c_short),
    ]
# Main rig_caps structure
class RigCaps(Structure):
    _fields_ = [
        # Basic model information
        ("rig_model", rig_model_t),  # Rig model
        ("model_name", c_char_p),  # Model name
        ("mfg_name", c_char_p),  # Manufacturer
        ("version", c_char_p),  # Driver version
        ("copyright", c_char_p),  # Copyright info
        ("status", RigStatusE),  # Driver status
        ("rig_type", c_int),  # Rig type
        ("ptt_type", PttTypeT),  # PTT port type
        ("dcd_type", DcdTypeT),  # DCD port type
        ("port_type", RigPortT),  # Communication port type

        # Serial parameters
        ("serial_rate_min", c_int),  # Minimum serial speed
        ("serial_rate_max", c_int),  # Maximum serial speed
        ("serial_data_bits", c_int),  # Data bits
        ("serial_stop_bits", c_int),  # Stop bits
        ("serial_parity", SerialParityE),  # Parity
        ("serial_handshake", SerialHandshakeE),  # Handshake
        ("write_delay", c_int),  # Delay between bytes (mS)
        ("post_write_delay", c_int),  # Delay between commands (mS)
        ("timeout", c_int),  # Timeout (mS)
        ("retry", c_int),  # Maximum retry count

        # Supported capabilities
        ("has_get_func", setting_t),  # Get functions list
        ("has_set_func", setting_t),  # Set functions list
        ("has_get_level", setting_t),  # Get levels list
        ("has_set_level", setting_t),  # Set levels list
        ("has_get_parm", setting_t),  # Get parameters list
        ("has_set_parm", setting_t),  # Set parameters list

        # Granularity
        ("level_gran", GranT * RIG_SETTING_MAX),  # Level granularity
        ("parm_gran", GranT * RIG_SETTING_MAX),  # Parameter granularity

        # Extended parameters
        ("extparms", POINTER(ConfParams)),  # Extended parameters list
        ("extlevels", POINTER(ConfParams)),  # Extended levels list
        ("extfuncs", POINTER(ConfParams)),  # Extended functions list
        ("ext_tokens", POINTER(c_int)),  # Extended tokens list

        # CTCSS and DCS tones
        ("ctcss_list", POINTER(tone_t)),  # CTCSS tones list
        ("dcs_list", POINTER(tone_t)),  # DCS codes list

        # Preamps and attenuators
        ("preamp", c_int * HAMLIB_MAXDBLSTSIZ),  # Preamp list (dB)
        ("attenuator", c_int * HAMLIB_MAXDBLSTSIZ),  # Attenuators list (dB)

        # RIT/XIT/IF-SHIFT
        ("max_rit", shortfreq_t),  # Maximum RIT
        ("max_xit", shortfreq_t),  # Maximum XIT
        ("max_ifshift", shortfreq_t),  # Maximum IF-SHIFT

        # AGC
        ("agc_level_count", c_int),  # Number of AGC levels
        ("agc_levels", AgcLevelE * HAMLIB_MAX_AGC_LEVELS),  # Supported AGC levels

        # VFO operations and scan
        ("announces", ann_t),  # Supported announcements
        ("vfo_ops", vfo_op_t),  # VFO operations
        ("scan_ops", scan_t),  # Scan operations
        ("targetable_vfo", c_int),  # Addressable VFOs
        ("transceive", c_int),  # Transceive mode (deprecated)

        # Memory
        ("bank_qty", c_int),  # Number of banks
        ("chan_desc_sz", c_int),  # Maximum channel name length
        ("chan_list", chan_t * HAMLIB_CHANLSTSIZ),  # Channel list

        # Frequency ranges (5 lists for different regions)
        ("rx_range_list1", FreqRangeT * HAMLIB_FRQRANGESIZ),  # RX range list 1
        ("tx_range_list1", FreqRangeT * HAMLIB_FRQRANGESIZ),  # TX range list 1
        ("rx_range_list2", FreqRangeT * HAMLIB_FRQRANGESIZ),  # RX range list 2
        ("tx_range_list2", FreqRangeT * HAMLIB_FRQRANGESIZ),  # TX range list 2
        ("rx_range_list3", FreqRangeT * HAMLIB_FRQRANGESIZ),  # RX range list 3
        ("tx_range_list3", FreqRangeT * HAMLIB_FRQRANGESIZ),  # TX range list 3
        ("rx_range_list4", FreqRangeT * HAMLIB_FRQRANGESIZ),  # RX range list 4
        ("tx_range_list4", FreqRangeT * HAMLIB_FRQRANGESIZ),  # TX range list 4
        ("rx_range_list5", FreqRangeT * HAMLIB_FRQRANGESIZ),  # RX range list 5
        ("tx_range_list5", FreqRangeT * HAMLIB_FRQRANGESIZ),  # TX range list 5

        # Tuning steps and filters
        ("tuning_steps", TuningStepList * HAMLIB_TSLSTSIZ),  # Tuning steps
        ("filters", FilterList * HAMLIB_FLTLSTSIZ),  # Filters table

        # Calibrations
        ("str_cal", CalTableT),  # S-meter calibration
        ("swr_cal", CalTableFloatT),  # SWR calibration
        ("alc_cal", CalTableFloatT),  # ALC calibration
        ("rfpower_meter_cal", CalTableFloatT),  # RF power calibration
        ("comp_meter_cal", CalTableFloatT),  # COMP calibration
        ("vd_meter_cal", CalTableFloatT),  # Voltmeter calibration
        ("id_meter_cal", CalTableFloatT),  # Ammeter calibration

        # Spectrum scope
        ("spectrum_scopes", RigSpectrumScope * HAMLIB_MAX_SPECTRUM_SCOPES),
        ("spectrum_modes", RigSpectrumModeE * HAMLIB_MAX_SPECTRUM_MODES),
        ("spectrum_spans", freq_t * HAMLIB_MAX_SPECTRUM_SPANS),
        ("spectrum_avg_modes", RigSpectrumAvgMode * HAMLIB_MAX_SPECTRUM_AVG_MODES),
        ("spectrum_attenuator", c_int * HAMLIB_MAXDBLSTSIZ),

        # Configuration parameters
        ("cfgparams", POINTER(ConfParams)),  # Configuration parameters
        ("priv", rig_ptr_t),  # Private data

        # === API FUNCTIONS ===
        # Basic functions
        ("rig_init", RigInitFunc),  # Initialization
        ("rig_cleanup", RigCleanupFunc),  # Cleanup
        ("rig_open", RigOpenFunc),  # Open
        ("rig_close", RigCloseFunc),  # Close

        # Frequency and mode control functions
        ("set_freq", SetFreqFunc),  # Set frequency
        ("get_freq", GetFreqFunc),  # Read frequency
        ("set_mode", SetModeFunc),  # Set mode
        ("get_mode", GetModeFunc),  # Read mode
        ("set_vfo", SetVfoFunc),  # Set VFO
        ("get_vfo", GetVfoFunc),  # Read VFO
        ("set_ptt", SetPttFunc),  # Set PTT
        ("get_ptt", GetPttFunc),  # Read PTT
        ("get_dcd", GetDcdFunc),  # Read DCD

        # Repeater functions
        ("set_rptr_shift", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, rptr_shift_t)),
        ("get_rptr_shift", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, POINTER(rptr_shift_t))),
        ("set_rptr_offs", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, shortfreq_t)),
        ("get_rptr_offs", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, POINTER(shortfreq_t))),

        # Split functions
        ("set_split_freq", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, freq_t)),
        ("get_split_freq", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, POINTER(freq_t))),
        ("set_split_mode", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, rmode_t, pbwidth_t)),
        ("get_split_mode", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, POINTER(rmode_t), POINTER(pbwidth_t))),
        ("set_split_freq_mode", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, freq_t, rmode_t, pbwidth_t)),
        ("get_split_freq_mode",
         ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, POINTER(freq_t), POINTER(rmode_t), POINTER(pbwidth_t))),
        ("set_split_vfo", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, split_t, vfo_t)),
        ("get_split_vfo", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, POINTER(split_t), POINTER(vfo_t))),

        # RIT/XIT functions
        ("set_rit", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, shortfreq_t)),
        ("get_rit", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, POINTER(shortfreq_t))),
        ("set_xit", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, shortfreq_t)),
        ("get_xit", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, POINTER(shortfreq_t))),

        # Tuning step functions
        ("set_ts", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, shortfreq_t)),
        ("get_ts", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, POINTER(shortfreq_t))),

        # Tone functions
        ("set_dcs_code", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, tone_t)),
        ("get_dcs_code", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, POINTER(tone_t))),
        ("set_tone", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, tone_t)),
        ("get_tone", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, POINTER(tone_t))),
        ("set_ctcss_tone", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, tone_t)),
        ("get_ctcss_tone", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, POINTER(tone_t))),
        ("set_dcs_sql", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, tone_t)),
        ("get_dcs_sql", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, POINTER(tone_t))),
        ("set_tone_sql", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, tone_t)),
        ("get_tone_sql", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, POINTER(tone_t))),
        ("set_ctcss_sql", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, tone_t)),
        ("get_ctcss_sql", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, POINTER(tone_t))),

        # Power functions
        ("power2mW", ctypes.CFUNCTYPE(c_int, POINTER(RIG), POINTER(c_uint), c_float, freq_t, rmode_t)),
        ("mW2power", ctypes.CFUNCTYPE(c_int, POINTER(RIG), POINTER(c_float), c_uint, freq_t, rmode_t)),
        ("set_powerstat", PowerStatFunc),  # Set power
        ("get_powerstat", GetPowerStatFunc),  # Read power

        # System functions
        ("reset", ResetFunc),  # Reset

        # Antenna functions
        ("set_ant", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, ant_t, ValueT)),
        ("get_ant", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, ant_t, POINTER(ValueT), POINTER(ant_t), POINTER(ant_t),
                                     POINTER(ant_t))),

        # Level and function functions
        ("set_level", SetLevelFunc),  # Set level
        ("get_level", GetLevelFunc),  # Read level
        ("set_func", SetFuncFunc),  # Set function
        ("get_func", GetFuncFunc),  # Read function
        ("set_parm", ctypes.CFUNCTYPE(c_int, POINTER(RIG), setting_t, ValueT)),
        ("get_parm", ctypes.CFUNCTYPE(c_int, POINTER(RIG), setting_t, POINTER(ValueT))),

        # Extended functions
        ("set_ext_level", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, hamlib_token_t, ValueT)),
        ("get_ext_level", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, hamlib_token_t, POINTER(ValueT))),
        ("set_ext_func", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, hamlib_token_t, c_int)),
        ("get_ext_func", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, hamlib_token_t, POINTER(c_int))),
        ("set_ext_parm", ctypes.CFUNCTYPE(c_int, POINTER(RIG), hamlib_token_t, ValueT)),
        ("get_ext_parm", ctypes.CFUNCTYPE(c_int, POINTER(RIG), hamlib_token_t, POINTER(ValueT))),

        # Configuration functions
        ("set_conf", ctypes.CFUNCTYPE(c_int, POINTER(RIG), hamlib_token_t, c_char_p)),
        ("get_conf", ctypes.CFUNCTYPE(c_int, POINTER(RIG), hamlib_token_t, c_char_p)),

        # DTMF and Morse functions
        ("send_dtmf", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, c_char_p)),
        ("recv_dtmf", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, c_char_p, POINTER(c_int))),
        ("send_morse", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, c_char_p)),
        ("stop_morse", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t)),
        ("wait_morse", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t)),

        # Voice memory functions
        ("send_voice_mem", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, c_int)),
        ("stop_voice_mem", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t)),

        # Memory functions
        ("set_bank", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, c_int)),
        ("set_mem", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, c_int)),
        ("get_mem", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, POINTER(c_int))),

        # VFO operations and scan functions
        ("vfo_op", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, vfo_op_t)),
        ("scan", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, scan_t, c_int)),

        # Transceive functions
        ("set_trn", ctypes.CFUNCTYPE(c_int, POINTER(RIG), c_int)),
        ("get_trn", ctypes.CFUNCTYPE(c_int, POINTER(RIG), POINTER(c_int))),
        ("decode_event", ctypes.CFUNCTYPE(c_int, POINTER(RIG))),

        # Channel functions
        ("set_channel", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, POINTER(Channel))),
        ("get_channel", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, POINTER(Channel), c_int)),

        # Info functions
        ("get_info", GetInfoFunc),  # Rig info

        # Callback functions
        ("set_chan_all_cb", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, chan_cb_t, rig_ptr_t)),
        ("get_chan_all_cb", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, chan_cb_t, rig_ptr_t)),
        ("set_mem_all_cb", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, chan_cb_t, confval_cb_t, rig_ptr_t)),
        ("get_mem_all_cb", ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, chan_cb_t, confval_cb_t, rig_ptr_t)),

        # Special functions
        ("set_vfo_opt", ctypes.CFUNCTYPE(c_int, POINTER(RIG), c_int)),
        ("rig_get_vfo_info",
         ctypes.CFUNCTYPE(c_int, POINTER(RIG), vfo_t, POINTER(freq_t), POINTER(rmode_t), POINTER(pbwidth_t),
                          POINTER(split_t))),

        # Clock functions
        ("set_clock", ctypes.CFUNCTYPE(c_int, POINTER(RIG), c_int, c_int, c_int, c_int, c_int, c_int, c_double, c_int)),
        ("get_clock",
         ctypes.CFUNCTYPE(c_int, POINTER(RIG), POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_int),
                          POINTER(c_int), POINTER(c_int), POINTER(c_double), POINTER(c_int)))
        ,

        # Final properties (in correct order of original C structure)
        ("clone_combo_set", c_char_p),  # Clone set combo
        ("clone_combo_get", c_char_p),  # Clone get combo
        ("macro_name", c_char_p),  # Macro name
        ("async_data_supported", c_int),  # Async data support

        # Frame processing functions
        ("read_frame_direct", ctypes.CFUNCTYPE(c_int, POINTER(RIG), c_size_t, POINTER(c_ubyte))),
        ("is_async_frame", ctypes.CFUNCTYPE(c_int, POINTER(RIG), c_size_t, POINTER(c_ubyte))),
        ("process_async_frame", ctypes.CFUNCTYPE(c_int, POINTER(RIG), c_size_t, POINTER(c_ubyte))),

        # Hamlib integrity check
        ("hamlib_check_rig_caps", c_char_p),  # Integrity check

        # Additional functions
        ("get_conf2", ctypes.CFUNCTYPE(c_int, POINTER(RIG), hamlib_token_t, c_char_p, c_int)),
        ("password", ctypes.CFUNCTYPE(c_int, POINTER(RIG), c_char_p)),
        ("set_lock_mode", ctypes.CFUNCTYPE(c_int, POINTER(RIG), c_int)),
        ("get_lock_mode", ctypes.CFUNCTYPE(c_int, POINTER(RIG), POINTER(c_int))),

        # Final properties
        ("timeout_retry", c_short),  # Timeout retry
        ("morse_qsize", c_short),  # Morse queue size
    ]




# Python wrapper class to facilitate usage
class HamlibRigCaps:
    """
    Python wrapper for hamlib's rig_caps structure
    """

    def __init__(self, rig_caps_ptr=None):
        """
        Initialize the wrapper

        Args:
            rig_caps_ptr: Pointer to the C rig_caps structure, or None to create empty
        """
        if rig_caps_ptr:
            self.caps = rig_caps_ptr.contents
        else:
            self.caps = RigCaps()

    def get_frequency_ranges(self, list_num=1, tx=False):
        """
        Get frequency ranges

        Args:
            list_num: List number (1-5)
            tx: True for TX, False for RX

        Returns:
            List of tuples (start_freq, end_freq, modes, low_power, high_power)
        """
        if list_num < 1 or list_num > 5:
            raise ValueError("list_num must be between 1 and 5")

        attr_name = f"{'tx' if tx else 'rx'}_range_list{list_num}"
        range_list = getattr(self.caps, attr_name)

        ranges = []
        for i in range(HAMLIB_FRQRANGESIZ):
            freq_range = range_list[i]
            if freq_range.startf == 0 and freq_range.endf == 0:
                break
            ranges.append({
                'start_freq': freq_range.startf,
                'end_freq': freq_range.endf,
                'modes': freq_range.modes,
                'low_power': freq_range.low_power,
                'high_power': freq_range.high_power,
                'vfo': freq_range.vfo,
                'antenna': freq_range.ant,
                'label': freq_range.label.decode('utf-8') if freq_range.label else None
            })

        return ranges

    def get_tuning_steps(self):
        """
        Get supported tuning steps

        Returns:
            List of tuples (modes, step)
        """
        steps = []
        for i in range(HAMLIB_TSLSTSIZ):
            step = self.caps.tuning_steps[i]
            if step.modes == 0 and step.ts == 0:
                break
            steps.append({
                'modes': step.modes,
                'step': step.ts
            })

        return steps

    def get_filters(self):
        """
        Get supported filters

        Returns:
            List of tuples (modes, width)
        """
        filters = []
        for i in range(HAMLIB_FLTLSTSIZ):
            filt = self.caps.filters[i]
            if filt.modes == 0 and filt.width == 0:
                break
            filters.append({
                'modes': filt.modes,
                'width': filt.width
            })

        return filters

    def has_capability(self, cap_type, capability):
        """
        Check if a capability is supported

        Args:
            cap_type: Capability type ('get_func', 'set_func', 'get_level', 'set_level', etc.)
            capability: Bit mask of capability to check

        Returns:
            True if supported, False otherwise
        """
        caps_field = getattr(self.caps, f"has_{cap_type}", 0)
        return bool(caps_field & capability)

    def mode_to_string(self, mode_mask):
        """
        """
        modes = []
        if mode_mask & 0x01: modes.append("LSB")
        if mode_mask & 0x02: modes.append("USB")
        if mode_mask & 0x04: modes.append("CW")
        if mode_mask & 0x08: modes.append("FM")
        if mode_mask & 0x10: modes.append("AM")
        if mode_mask & 0x20: modes.append("DIG")
        return "|".join(modes) if modes else "NONE"


    def enumerate_filters(self, rig_caps):
        """
        """
        filters = []

        for i in range(HAMLIB_FLTLSTSIZ):
            filt = rig_caps.filters[i]

            # Stop when we hit an empty entry (modes=0 and width=0)
            if filt.modes == 0 and filt.width == 0:
                break

            # Convert modes to human-readable string (simplified example)
            mode_str = self.mode_to_string(filt.modes) if hasattr(self.mode_to_string, '__call__') else str(filt.modes)

            filters.append({
                'index': i,
                'modes': filt.modes,
                'modes_str': mode_str,
                'width': filt.width,
                'width_hz': filt.width  # Assuming width is already in Hz
            })

