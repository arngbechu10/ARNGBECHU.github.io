from PIL import Image, ImageDraw
import numpy as np, sys
A='/mnt/user-data/attachments/f9ae0b19-9e15-514d-b64c-42a1ff34b6c5/'
SRC={
 'mountain':[(A+'f7676597-image.jpg',.60),(A+'d0a1cd0b-image.png',.58),(A+'f714ac1f-image.png',.62)],
 'xmas':[(A+'5598cc83-image.png',.60),(A+'dec02445-image.png',.60),(A+'ce49c768-image.png',.62)],
}
W,H=3468,520; CH=330; OV=260
GRADE={"mountain":1.0}
HAZE={'mountain':(174,196,216)}
def build(name,bottom):
    tiles=[]
    n=3; tw=(W+n*OV)//n
    canvas=np.zeros((H,W,3),np.float32)
    wsum=np.zeros((H,W,1),np.float32)
    raw=[]
    for k,(p,fr) in enumerate(SRC[name]):
        im=Image.open(p).convert('RGB'); w,h=im.size
        im=im.crop((0,0,w,int(h*fr))).resize((tw,CH),Image.LANCZOS)
        raw.append(np.asarray(im,np.float32))
    mu=np.mean([r.mean((0,1)) for r in raw],0); sd=np.mean([r.std((0,1)) for r in raw],0)
    STR=GRADE.get(name,0)
    for k,(p,fr) in enumerate(SRC[name]):
        a=raw[k]
        if STR:
            m,s_=a.mean((0,1)),a.std((0,1)); g=(a-m)/np.maximum(s_,1)*sd+mu
            a=a*(1-STR)+g*STR
        x0=k*(tw-OV)
        wt=np.ones((CH,tw,1),np.float32)
        ramp=np.linspace(0,1,OV)[None,:,None]
        wt[:,:OV]*=ramp; wt[:,-OV:]*=(1-ramp)
        for xx in range(tw):
            X=(x0+xx)%W
            canvas[:CH,X]+=a[:,xx]*wt[:,xx]; wsum[:CH,X]+=wt[:,xx]
    # first tile start (k=0) has ramp at left: wraps with last tile's tail -> seamless
    out=canvas/np.maximum(wsum,1e-4)
    if name in HAZE:
        hz=np.array(HAZE[name],np.float32)
        for y in range(CH-90,CH):
            t=((y-(CH-90))/90)**1.5*.6; out[y]=out[y]*(1-t)+hz*t
    # below crop: darkened mirror reflection fading to the ground color
    R=H-CH
    mir=out[CH-R:CH][::-1].copy()
    for y in range(R):
        t=min(1,(y/R)**.8*1.0)
        a=.55*(1-t)
        out[CH+y]=mir[y]*a+np.array(bottom,np.float32)*(1-a)
    Image.fromarray(np.clip(out,0,255).astype(np.uint8)).save(f'sky_{name}.webp',quality=78,method=6)
    Image.fromarray(np.clip(out,0,255).astype(np.uint8)).resize((1400,210)).save(f'sky_{name}_prev.png')
build('mountain',(120,145,170))
build('xmas',(20,30,60))
