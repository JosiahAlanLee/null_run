from pathlib import Path
import zipfile,io,struct,zlib,wave,math
from PIL import Image
R=Path(__file__).resolve().parent;S=R/'src'
with zipfile.ZipFile(R/'candidate-v7/cistern-v7.pk3','w',zipfile.ZIP_DEFLATED) as z:
 for n in ['v5-player.zs','v5-encounters.zs','CVARINFO','MENUDEF','KEYCONF']:z.write(S/n,n)
 im=Image.open(R/'hollow-source.png').convert('RGBA')
 for name,box in [('C7BKA0',(190,285,217,349)),('C7RTA0',(213,502,253,553)),('C7LTA0',(243,276,288,324))]:
  piece=im.crop(box);b=io.BytesIO();piece.save(b,format='PNG');d=b.getvalue();grab=struct.pack('>ii',piece.width//2,piece.height);chunk=b'grAb'+grab;d=d[:33]+struct.pack('>I',8)+chunk+struct.pack('>I',zlib.crc32(chunk))+d[33:];z.writestr('sprites/'+name+'.png',d)
 for name,metal in [('settle',True),('clatter',False)]:
  b=io.BytesIO()
  with wave.open(b,'wb') as w:
   w.setparams((1,2,22050,0,'NONE','not compressed'));samples=[]
   for i in range(int(22050*(.55 if metal else .22))):
    t=i/22050;s=sum(math.sin(2*math.pi*f*t)*math.exp(-t*(10+j*8)) for j,f in enumerate([387,713,1231,2173] if metal else [216,581,1091]));samples.append(int(max(-1,min(1,s*.12))*32767))
   w.writeframes(struct.pack('<'+'h'*len(samples),*samples))
  z.writestr('sounds/c7'+name+'.wav',b.getvalue())
 z.writestr('SNDINFO','c7/settle sounds/c7settle.wav\nc7/clatter sounds/c7clatter.wav\n')
def unused():pass
