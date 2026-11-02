from pathlib import Path
import subprocess,numpy as np,json,sys
O=Path(__file__).resolve().parent;result={}
for name in sys.argv[1:]:
 p=O/name
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-vf','scale=160:100','-pix_fmt','gray','-f','rawvideo','-'])
 a=np.frombuffer(raw,dtype=np.uint8).reshape(-1,100,160).astype(np.float32)/255
 means=a.mean(axis=(1,2));delta=np.abs(np.diff(means));large=np.flatnonzero(delta>.1)
 result[name]={'frames':len(a),'fps':20,'max_mean_luminance_step':float(delta.max()),'over_10_percent_steps':[{'time':float((i+1)/20),'delta':float(delta[i])} for i in large], 'method':'Adjacent decoded frames, whole-frame mean gray luminance. Screen transitions and camera motion are retained and reported; not a photosensitivity certification.'}
(O/'V5-VIDEO-SAFETY.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
