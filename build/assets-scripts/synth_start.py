import numpy as np,wave
from scipy.signal import butter,lfilter
SR=32000;L=2.4;N=int(SR*L);t=np.arange(N)/SR
rng=np.random.default_rng(7)
def lp(x,f,o=2):b,a=butter(o,f/(SR/2));return lfilter(b,a,x)
def bp(x,f1,f2):b,a=butter(2,[f1/(SR/2),f2/(SR/2)],'band');return lfilter(b,a,x)
def synth(cyl,idle,peak,crank_hz,bright,seed):
    rng=np.random.default_rng(seed)
    # rpm 곡선: 0~0.9s 스타터(약 220rpm) -> 0.9s 점화 -> 플레어(peak) -> 아이들로 안착
    rpm=np.where(t<.9,230+60*np.sin(2*np.pi*3*t),0.)
    k=(t-.9)
    fl=np.clip(k/.25,0,1)
    rpm=np.where(t>=.9,230+(peak-230)*np.sin(fl*np.pi/2)**.7,rpm)
    dec=np.clip((t-1.25)/.9,0,1)
    rpm=np.where(t>=1.25,peak+(idle-peak)*(1-(1-dec)**2.2),rpm)
    out=np.zeros(N)
    # 스타터 모터: 톱니 톤 + 압축 펄스
    st=(t<1.0)*np.minimum(1,t/.08)*np.minimum(1,(1.0-t)/.06)
    ph=np.cumsum(crank_hz*(1+.15*np.sin(2*np.pi*5*t)))/SR
    motor=(2*(ph%1)-1)*.5+np.sin(2*np.pi*ph*2)*.3
    comp=.55+.45*np.maximum(0,np.sin(2*np.pi*cyl/2*np.cumsum(rpm)/60/SR*SR/SR*0+2*np.pi*np.cumsum(cyl/2*rpm/60)/SR))
    out+=bp(motor,150,2800)*st*comp*.55
    out+=bp(rng.standard_normal(N),900,3500)*st*.05
    # 점화 폭발음: 연소 펄스열(각 펄스 = 저음 감쇠 사인 + 대역 잡음)
    fire=np.cumsum(cyl/2*rpm/60)/SR
    idx=np.where(np.diff(np.floor(fire))>0)[0]
    idx=idx[t[idx]>=.88]
    pulse=np.zeros(N)
    for i in idx:
        r=rpm[i];f0=48+r/60*.9+rng.uniform(-6,6);amp=(.6+.4*rng.random())*(0.55+.45*min(1,r/peak))
        ln=int(SR*.045);tt=np.arange(ln)/SR
        w=np.sin(2*np.pi*f0*tt)*np.exp(-tt*55)+ .35*np.sin(2*np.pi*f0*2.1*tt)*np.exp(-tt*80)
        w+=bright*bp(rng.standard_normal(ln),300,2200)*np.exp(-tt*120)
        j=min(ln,N-i);pulse[i:i+j]+=amp*w[:j]
    out+=pulse*.9
    # 첫 점화 직전 '턱' 걸리는 느낌: 0.85~0.95 짧은 정적 대신 크랭크 감속
    out=lp(out,6000)
    env=np.minimum(1,t/.03)*np.minimum(1,(L-t)/.45)
    out*=env
    return out
def save(p,x,db=-21):
    x=x*10**((db-20*np.log10(np.sqrt(np.mean(x**2))+1e-9))/20);x=np.tanh(x*1.0)*.95
    w=wave.open(p,'wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR)
    w.writeframes((x*32767).astype('<i2').tobytes());w.close()
# 차량별 성격: 실린더, 아이들rpm, 플레어rpm, 스타터음 높이, 거친 정도
save('rb/lau_gt3.wav',synth(6,950,3300,125,.8,1))   # 수평대향 6기통: 맑고 날카로움
save('rb/lau_f40.wav',synth(8,1100,3000,110,1.0,2)) # 트윈터보 V8: 거칠고 크게
save('rb/lau_chal.wav',synth(8,700,2300,95,.6,3))   # 미국 V8: 낮고 묵직하게 덜컥
save('rb/lau_mcl.wav',synth(8,1000,3600,115,1.1,4))  # 720S 트윈터보 플랫플레인 V8: 높고 날카롭게
