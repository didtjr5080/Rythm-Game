"""ctypes binding of the manufacturer's gForce C# C ABI, pinned in vendor/oymotion.

Callback order/pack and function signatures follow gforce/core/libgforce.cs.
The C callback supplies the data type separately; EMG payload has NO 0x08 prefix.
"""
import ctypes as C
import sys
from pathlib import Path
from serial.tools.list_ports import comports


def sdk_path():
    return (Path(sys._MEIPASS)/'oymotion' if getattr(sys, 'frozen', False)
            else Path(__file__).resolve().parents[1]/'vendor'/'oymotion')


class OYMotionSDK:
    def __init__(self, events):
        if sys.platform != 'win32' or C.sizeof(C.c_void_p) != 8:
            raise RuntimeError('OYMotion USB SDK requires 64-bit Windows.')
        self.dll = C.WinDLL(str(sdk_path()/'gforcecsharp64.dll'))
        callback = C.WINFUNCTYPE
        empty = callback(None)
        state = callback(None, C.c_int)
        device = callback(None, C.c_void_p)
        disconnected = callback(None, C.c_void_p, C.c_int)
        orientation = callback(None, C.c_void_p, C.c_float, C.c_float, C.c_float, C.c_float)
        uint_event = callback(None, C.c_void_p, C.c_uint32)
        extended = callback(None, C.c_void_p, C.c_int, C.c_int, C.c_void_p)
        self.result_type = callback(None, C.c_void_p, C.c_uint32)
        class Listener(C.Structure):
            _pack_ = 1
            _fields_ = list(zip(('scan', 'state', 'found', 'discard', 'connected', 'disconnected',
                                'orientation', 'gesture', 'status', 'data'),
                               (empty, state, device, device, device, disconnected,
                                orientation, uint_event, uint_event, extended)))
        self.listener = Listener(
            empty(events.on_scan_finished), state(lambda value: None),
            device(events.on_found), device(lambda handle: None), device(events.on_connected),
            disconnected(events.on_disconnected), orientation(lambda *args: None),
            uint_event(lambda *args: None), uint_event(lambda *args: None), extended(events.on_data))
        assert C.sizeof(self.listener) == 10*C.sizeof(C.c_void_p)
        self._bind('hub_instance', [C.c_char_p])
        self._bind('hub_init', [C.c_uint32])
        self._bind('hub_deinit', [])
        self._bind('hub_set_workmode', [C.c_int], None)
        self._bind('hub_run', [C.c_uint32])
        self._bind('hub_start_scan', [])
        self._bind('hub_stop_scan', [])
        self._bind('hub_register_listener', [C.POINTER(Listener)])
        self._bind('hub_unregister_listener', [C.POINTER(Listener)])
        self._bind('device_connect', [C.c_void_p])
        self._bind('device_disconnect', [C.c_void_p])
        self._bind('device_enable_data_notification', [C.c_void_p, C.c_uint32])
        self._bind('device_set_emg_config', [C.c_void_p]+[C.c_uint32]*4+[self.result_type])
        self._bind('device_set_data_switch', [C.c_void_p, C.c_uint32, self.result_type])
        self._bind('device_get_name', [C.c_void_p, C.c_void_p, C.c_uint32])
        self._bind('device_get_address', [C.c_void_p, C.c_void_p, C.c_uint32])
        self.initialized = self.registered = False

    def _bind(self, name, args, result=C.c_uint32):
        function = getattr(self.dll, name)
        function.argtypes, function.restype = args, result

    @staticmethod
    def check(result, operation):
        if result != 0:
            raise RuntimeError(f'OYMotion {operation} failed: code {result}')

    def open(self, port):
        available = {p.device.upper() for p in comports()}
        if not available or (port and f'COM{port}' not in available):
            target = f'COM{port}' if port else 'COM port'
            raise RuntimeError(f'OYMotion {target} not detected. Reconnect USB dongle, refresh devices and select its current COM port.')
        self.check(self.dll.hub_instance(b'EMG Motion Rhythm'), 'hub instance')
        self.check(self.dll.hub_register_listener(C.byref(self.listener)), 'register listener')
        self.registered = True
        self.check(self.dll.hub_init(port), 'USB dongle init (check dongle/COM port; close other armband apps)')
        self.initialized = True
        self.dll.hub_set_workmode(1)  # Polling: callbacks run on the reader worker.
        self.check(self.dll.hub_start_scan(), 'scan')

    def text(self, handle, kind='name'):
        buffer = C.create_string_buffer(128)
        self.check(getattr(self.dll, 'device_get_'+kind)(handle, buffer, len(buffer)), kind)
        return buffer.value.decode('utf-8', errors='replace')

    def close(self):
        if self.initialized:
            self.dll.hub_stop_scan()
        if self.registered:
            self.dll.hub_unregister_listener(C.byref(self.listener))
        if self.initialized:
            self.dll.hub_deinit()
