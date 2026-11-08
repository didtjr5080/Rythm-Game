"""Compile/upload classic Nano firmware using Arduino CLI; no IDE edits needed."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.input.emg_devices import discover_emg_devices


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', help='Explicit Nano COM port, e.g. COM4')
    parser.add_argument('--cli', help='Path to arduino-cli.exe')
    parser.add_argument('--compile-only', action='store_true')
    parser.add_argument('--old-bootloader', action='store_true')
    args = parser.parse_args()
    cli = args.cli or shutil.which('arduino-cli')
    if not cli:
        locations = [Path(os.environ.get('LOCALAPPDATA', ''))/'Programs/Arduino IDE/resources/app/lib/backend/resources/arduino-cli.exe',
                     Path('C:/Program Files/Arduino IDE/resources/app/lib/backend/resources/arduino-cli.exe')]
        cli = next((str(p) for p in locations if p.is_file()), None)
    if not cli:
        parser.error('Install Arduino CLI / Arduino IDE and the arduino:avr core first.')
    port = args.port
    if not args.compile_only and not port:
        candidates = [d for d in discover_emg_devices() if d['candidate']]
        if len(candidates) != 1:
            parser.error('Expected one Nano-compatible USB serial device. Check power/data cable, or pass --port COMx.')
        port = candidates[0]['port']
    processors = ['atmega328old'] if args.old_bootloader else ['atmega328', 'atmega328old']
    for processor in processors:
        fqbn = f'arduino:avr:nano:cpu={processor}'
        output = ROOT/'build'/'firmware'/processor
        subprocess.run([cli, 'compile', '--fqbn', fqbn, '--build-path', str(output), str(ROOT/'firmware/nano_emg')], check=True)
        if args.compile_only:
            continue
        result = subprocess.run([cli, 'upload', '--fqbn', fqbn, '--port', port,
                                 '--input-dir', str(output), '--verify'])
        if result.returncode == 0:
            print(f'Uploaded and verified: {port} / {processor}. Firmware serial baud: 115200.')
            return 0
    if args.compile_only:
        print('Compiled both Nano bootloader configurations. No board was flashed.')
        return 0
    print('Upload failed. Close the app/Serial Monitor and check the board, USB cable and bootloader.', file=sys.stderr)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
