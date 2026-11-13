from PIL import Image, ImageDraw, ImageFilter
import numpy as np, json
A='/mnt/user-data/attachments/f9ae0b19-9e15-514d-b64c-42a1ff34b6c5/'
CW,CH=1800,600; PCX=972; DASH_C=340; HDR=44
CARS={
 'gt3':dict(src=A+'b65f688c-image.png',panel=(15,489,1082,1003),dash=588,
   dpoly=[(150,598),(200,594),(260,588),(330,584),(420,582),(480,578),(500,576),(540,574),(547,560),(565,552),(583,558),(588,574),(640,580),(700,586),(800,593),(880,598),(905,602)],
   wheel=(187,578,483,850),wsrc=(1152,553,1507,907),fill=(24,25,29)),
 'chal':dict(src=A+'9b8225f9-image.png',panel=(20,505,1105,1003),dash=660,
   dpoly=[(152,655),(220,652),(300,650),(400,652),(470,650),(560,655),(700,662),(820,665),(900,662),(944,655)],
   wheel=(187,646,458,903),wsrc=(1161,576,1526,947),fill=(22,22,25)),
 'f40':dict(src=A+'f7d4182d-image.png',panel=(15,350,930,668),dash=412,
   dpoly=[(112,424),(150,414),(220,408),(300,404),(400,408),(500,410),(600,411),(700,411),(790,410)],
   wheel=(168,400,400,622),wsrc=(1098,350,1396,655),fill=(20,19,21)),

 'mcl':dict(src='/tmp/claude-0/-home-claude/f9ae0b19-9e15-514d-b64c-42a1ff34b6c5/scratchpad/mc/src.png',panel=(22,488,1072,1000),dash=550,
   dpoly=[(150,562),(215,558),(280,553),(350,550),(430,547),(520,545),(620,547),(720,550),(820,552),(880,556),(910,563)],
   wheel=(172,553,490,885),wsrc=(1139,532,1518,904),fill=(26,26,28)),
}
# 창문 기둥 안쪽 선: (패널 맨 위 x, 대시 x) 
PIL_L={'gt3':(105,150),'chal':(115,152),'f40':(106,112),'mcl':(116,150)}
PIL_R={'gt3':(945,905),'chal':(1010,944),'f40':(822,790),'mcl':(978,915)}
out={}
for k,c in CARS.items():
    im=Image.open(c['src']).convert('RGB')
    x0,y0,x1,y1=c['panel'];s=1350/(x1-x0);pcx=(x0+x1)/2
    T=lambda x,y:(PCX+(x-pcx)*s,DASH_C+(y-c['dash'])*s)
    # 1) 패널 붙이기
    pw,ph=round((x1-x0)*s),round((y1-y0)*s)
    pan=im.crop((x0,y0,x1,y1)).resize((pw,ph),Image.LANCZOS)
    px,py=round(T(x0,y0)[0]),round(T(x0,y0)[1])
    base=np.zeros((CH,CW,3),np.float32);base[:]=c['fill']
    P=np.array(pan,np.float32)
    # 위/아래 잘림
    def paste(arr,img,ox,oy,mask=None):
        h,w=img.shape[:2]
        ys0,xs0=max(oy,0),max(ox,0);ys1,xs1=min(oy+h,CH),min(ox+w,CW)
        sub=img[ys0-oy:ys1-oy,xs0-ox:xs1-ox]
        if mask is None: arr[ys0:ys1,xs0:xs1]=sub
        else:
            m=mask[ys0-oy:ys1-oy,xs0-ox:xs1-ox,None];arr[ys0:ys1,xs0:xs1]=arr[ys0:ys1,xs0:xs1]*(1-m)+sub*m
    # 좌우 번짐 (문 쪽)
    for y in range(max(py,0),min(py+ph,CH)):
        row=P[y-py]
        l=row[:8].mean(axis=0)*.75;r=row[-8:].mean(axis=0)*.75
        if px>0: base[y,:px]=l
        if px+pw<CW: base[y,px+pw:]=r
    # 패널 가장자리 부드럽게
    m=np.ones((ph,pw),np.float32);f=26
    for i in range(f):
        v=(i+1)/f;m[i,:]=np.minimum(m[i,:],v)
    paste(base,P,px,py,m)
    # 2) 창문 영역 폴리곤 (캔버스 좌표)
    pts=[T(*p) for p in c['dpoly']]
    def line_x(a,b,y):  # 패널 맨 위(y0)와 대시선 두 점으로 기둥 안쪽 직선 → 임의 y에서 x
        (xa,ya),(xb,yb)=a,b;return xa+(xb-xa)*(y-ya)/(yb-ya)
    TL=T(PIL_L[k][0],y0);BL=T(PIL_L[k][1],c['dpoly'][0][1])
    TR=T(PIL_R[k][0],y0);BR=T(PIL_R[k][1],c['dpoly'][-1][1])
    # 기둥 선은 대시 아래 끝점을 폴리곤 첫/끝점에 맞춘다
    lx=lambda y:line_x(BL,TL,y);rx=lambda y:line_x(BR,TR,y)
    poly=[(lx(HDR),HDR)]+[(lx(pts[0][1]),pts[0][1])]+pts+[(rx(pts[-1][1]),pts[-1][1]),(rx(HDR),HDR)]
    mask=Image.new('L',(CW,CH),0);ImageDraw.Draw(mask).polygon(poly,fill=255)
    mask=mask.filter(ImageFilter.GaussianBlur(1.3))
    # 3) 천장 라이닝 그라디언트 + 룸미러
    rgb=Image.fromarray(np.clip(base,0,255).astype(np.uint8))
    d=ImageDraw.Draw(rgb)
    for y in range(0,HDR+6):
        t=y/(HDR+6);col=tuple(int(a*(.55+.45*t)) for a in c['fill'])
        d.line([(0,y),(CW,y)],fill=col)
    # 룸미러
    mx,my=PCX,HDR+4
    d.line([(mx,HDR-4),(mx,my+6)],fill=(30,31,35),width=7)
    d.rounded_rectangle([mx-62,my+2,mx+62,my+34],radius=10,fill=(18,19,22),outline=(58,60,66),width=2)
    d.rounded_rectangle([mx-56,my+7,mx+56,my+29],radius=7,fill=(52,58,66))
    alpha=Image.new('L',(CW,CH),255)
    a=np.array(mask,np.float32)
    # 룸미러는 불투명으로 유지
    mm=Image.new('L',(CW,CH),0);ImageDraw.Draw(mm).rounded_rectangle([mx-62,my+2,mx+62,my+34],radius=10,fill=255)
    a=np.maximum(0,a)  # 창문=255 → 투명
    A_=255-a;A_=np.maximum(A_,np.array(mm,np.float32))
    rgba=np.dstack([np.array(rgb),A_]).astype(np.uint8)
    Image.fromarray(rgba,'RGBA').save(f'cabin_{k}.webp',quality=90,method=6)
    prev=Image.new('RGB',(CW,CH),(110,150,200));prev.paste(Image.fromarray(rgba,'RGBA'),(0,0),Image.fromarray(rgba,'RGBA'))
    prev.resize((900,300)).save(f'cabin_{k}_prev.png')
    # 휠 설정
    wx0,wy0,wx1,wy1=c['wheel'];cx,cy=T((wx0+wx1)/2,(wy0+wy1)/2);ww=(wx1-wx0)*s*1.06
    out[k]=dict(wx=round(cx/CW*100,2),wy=round(cy/CH*100,2),ww=round(ww/CW*100,2))
    # 휠 이미지 저장 (가로 400px로)
    w=Image.open(f'wheel_{k}.png');w=w.resize((360,round(360*w.height/w.width)),Image.LANCZOS);w.save(f'wheelS_{k}.webp',quality=88,method=6)
print(json.dumps(out))
json.dump(out,open('wheelcfg.json','w'))
