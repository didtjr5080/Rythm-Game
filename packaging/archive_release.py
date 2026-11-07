"""Zip the complete onedir bundle, preserving its top-level directory."""
import sys
import zipfile
from pathlib import Path
source, target = map(Path,sys.argv[1:3])
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for file in sorted(source.rglob('*')):
        if not file.is_file(): continue
        relative = file.relative_to(source)
        if '__pycache__' in relative.parts: continue
        if relative.parts[:3] == ('_internal','app','data') and file.name != '.gitkeep': continue
        archive.write(file,file.relative_to(source.parent))
print(f'{target.name}: {target.stat().st_size/1024/1024:.1f} MiB')
