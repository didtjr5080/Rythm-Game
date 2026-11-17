"""Same-directory replacement prevents partially written records."""
import os
import tempfile
from pathlib import Path

def atomic_text(path, text):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix=path.name+'.',suffix='.tmp',dir=path.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8',newline='') as handle: handle.write(text)
        os.replace(name,path)
    finally:
        if os.path.exists(name): os.unlink(name)
