import asyncio,sys
from playwright.async_api import async_playwright
THREE=open('npm/node_modules/three/build/three.min.js').read()
HTML=sys.argv[1]
async def route(r):
    u=r.request.url
    if 'three.min.js' in u: await r.fulfill(body=THREE,content_type='application/javascript')
    elif 'supabase.co' in u: await r.fulfill(status=400,body='{}',content_type='application/json')
    elif u.startswith(('file:','data:')): await r.continue_()
    else: await r.abort()
SETUP="""()=>{MODE='hard';document.body.dataset.mode='hard';$('modes').classList.remove('on');hardBegin();hardIdx=3;setMap('ship');updateHH();$('start').style.display='none';started=true;reset();}"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required'])
        ctx=await b.new_context(viewport={'width':1280,'height':720});pg=await ctx.new_page();errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.route('**/*',route);await pg.goto('file://'+HTML);await pg.wait_for_timeout(1200)
        await pg.evaluate(SETUP);await pg.wait_for_timeout(1200)
        print('JMP',await pg.evaluate("JSON.stringify(JMP)"),'LAPEND',await pg.evaluate("LAPEND"),'OBS',await pg.evaluate("OBS.length"),'TY0',await pg.evaluate("TY[0]"))
        await pg.screenshot(path='s1_start.png')
        # 장애물 앞 화면
        await pg.evaluate("()=>{c.x=40;c.z=0;c.vx=c.vz=0;}");await pg.wait_for_timeout(900);await pg.screenshot(path='s2_obstacles.png')
        # 장애물 정면 충돌 → 충돌 횟수 증가?
        h0=await pg.evaluate("hits")
        await pg.evaluate("()=>{const o=OBS[0];c.x=o.x-6;c.z=o.z;c.vx=18;c.vz=0;}");await pg.wait_for_timeout(700)
        print('obstacle hit: hits',h0,'->',await pg.evaluate("hits"),'car x',round(await pg.evaluate("c.x"),1),'obs x',await pg.evaluate("OBS[0].x"))
        # 점프 안내 + 램프
        await pg.evaluate("()=>{hits=0;updateHH();c.x=300;c.z=0;c.h=0;c.vx=26;c.vz=0;ci=Math.round(300/(SH.L/(N-1)));prog=ci}");await pg.wait_for_timeout(400)
        await pg.screenshot(path='s3_approach.png');print('jh on',await pg.evaluate("$('jh').className"),await pg.evaluate("$('jhV').textContent"))
        # 성공 점프: 충분한 속도
        for sp,tag in [(30,'fast'),(17,'slow')]:
            await pg.evaluate("()=>{DEAD=false;HOLD=false;['boom','fail'].forEach(i=>$(i).classList.remove('on','water'));reset();}")
            await pg.evaluate(f"()=>{{const i=Math.round(345/(SH.L/(N-1)));c.x=345;c.z=0;c.h=0;c.vx={sp};c.vz=0;ci=i;prog=i;lapStart=performance.now()-50000;keys.gas=1}}")
            mx=0;air_seen=False;shot=False
            for k in range(400):
                await pg.wait_for_timeout(150)
                st=await pg.evaluate("({air:AIR,cy:cy,x:c.x,dead:DEAD,hold:HOLD,idx:hardIdx,fail:$('fail').classList.contains('on')})")
                if st['air']:air_seen=True
                if st['air'] and st['x']>375 and tag=='fast' and not shot:await pg.screenshot(path='s4_air.png');shot=True
                if st['dead'] or st['hold'] or st['fail']:break
            await pg.evaluate("keys.gas=0")
            await pg.wait_for_timeout(3500)
            st=await pg.evaluate("({air:AIR,cy:+cy.toFixed(2),x:+c.x.toFixed(1),dead:DEAD,hold:HOLD,fail:$('fail').classList.contains('on'),ft:$('failT').textContent,fs:$('failSub').textContent,need:JMP.needKmh})")
            print(tag,sp*3.6,'km/h ->',st,'airSeen',air_seen)
            await pg.screenshot(path=f's5_{tag}.png')
        print('errors',errs or 'none')
        await b.close()
asyncio.run(main())
