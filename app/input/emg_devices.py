"""Serial discovery without opening unrelated COM ports."""
from serial.tools import list_ports

USB_BRIDGES = {(0x1A86, 0x7523), (0x1A86, 0x5523), (0x0403, 0x6001), (0x10C4, 0xEA60)}


def device_identity(port):
    if port.vid is None or port.pid is None:
        return ''
    return f'usb:{port.vid:04x}:{port.pid:04x}:' + (port.serial_number or '')


def discover_emg_devices():
    devices = []
    for port in list_ports.comports():
        description = port.description or port.device
        candidate = (port.vid, port.pid) in USB_BRIDGES or port.vid in (0x2341, 0x2A03)
        candidate = candidate or any(word in description.lower() for word in ('arduino', 'ch340', 'ch341', 'ft232'))
        devices.append(dict(port=port.device, description=description, identity=device_identity(port),
                            candidate=candidate, serial_number=port.serial_number,
                            vid=port.vid, pid=port.pid))
    return sorted(devices, key=lambda item: (not item['candidate'], item['port']))
