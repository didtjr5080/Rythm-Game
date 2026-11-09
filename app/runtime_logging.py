"""Keep Python and native fault traces available in windowed Windows builds."""
import faulthandler
import sys
import time
import traceback
from pathlib import Path

_stream = None


def install_runtime_logging():
    global _stream
    if _stream is not None: return
    try:
        directory = Path(__file__).resolve().parent/'data'/'logs'
        directory.mkdir(parents=True, exist_ok=True)
        _stream = (directory/f'runtime-{time.strftime("%Y%m%d")}.log').open('a', encoding='utf-8', buffering=1)
        _stream.write('\nApplication starting: '+time.strftime('%Y-%m-%d %H:%M:%S')+'\n')
        faulthandler.enable(file=_stream, all_threads=True)
    except (OSError, RuntimeError):
        return
    original = sys.excepthook
    def record_exception(kind, value, tb):
        traceback.print_exception(kind, value, tb, file=_stream)
        _stream.flush()
        original(kind, value, tb)
    sys.excepthook = record_exception
