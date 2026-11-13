from PIL import Image
from rembg import remove, new_session
import numpy as np
A='/mnt/user-data/attachments/f9ae0b19-9e15-514d-b64c-42a1ff34b6c5/'
sess=new_session('isnet-general-use')
def cut(src,out,box=None,w=900,pad=6):
    im=Image.open(src).convert('RGB')
    if box: im=im.crop(box)
    r=remove(im,session=sess,alpha_matting=False)
    a=np.array(r)[:,:,3]
    ys,xs=np.where(a>20)
    x0,x1,y0,y1=max(xs.min()-pad,0),min(xs.max()+pad,r.width),max(ys.min()-pad,0),min(ys.max()+pad,r.height)
    r=r.crop((x0,y0,x1,y1));print(out,r.size)
    r=r.resize((w,int(r.height*w/r.width)),Image.LANCZOS)
    r.save(out+'.png');r.save(out+'.webp',quality=86,method=6)
cut(A+'f3cd3b81-image.jpg','hero_gt3')
cut(A+'a049b932-image.jpg','hero_chal')
cut(A+'425c1abe-image.jpg','hero_f40')
