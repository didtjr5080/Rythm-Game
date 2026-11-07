"""Encode the supplied PNG as a multi-resolution Windows icon, without cropping."""
from pathlib import Path
from PIL import Image

root=Path(__file__).resolve().parents[1]
source=Image.open(root/'app/assets/app.png').convert('RGBA')
side=max(source.size)
canvas=Image.new('RGBA',(side,side),(0,0,0,0))
canvas.paste(source,((side-source.width)//2,(side-source.height)//2))
canvas.save(root/'app/assets/app.ico',format='ICO',sizes=[(s,s) for s in (16,20,24,32,40,48,64,96,128,256)])
print('Created app/assets/app.ico')
