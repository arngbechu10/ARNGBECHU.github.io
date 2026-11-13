from PIL import Image
from rembg import remove, new_session
import numpy as np, json
A='/mnt/user-data/attachments/f9ae0b19-9e15-514d-b64c-42a1ff34b6c5/'
sess=new_session('isnet-general-use')
out={}
for k,p,box in [('gt3',A+'b65f688c-image.png',(1110,510,1510,950)),('chal',A+'9b8225f9-image.png',(1130,520,1536,960)),('f40',A+'f7d4182d-image.png',(1070,330,1440,680))]:
    im=Image.open(p).convert('RGB').crop(box)
    r=remove(im,session=sess)
    a=np.array(r)[:,:,3]
    ys,xs=np.where(a>40)
    x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
    r=r.crop((x0,y0,x1,y1));r.save(f'wheel_{k}.png')
    out[k]=(r.width,r.height);print(k,r.size,'abs bbox',box[0]+x0,box[1]+y0,box[0]+x1,box[1]+y1)
