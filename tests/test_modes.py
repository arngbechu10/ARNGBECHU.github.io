import asyncio,sys,json
from playwright.async_api import async_playwright
THREE=open('npm/node_modules/three/build/three.min.js').read()
HTML=sys.argv[1]
posts=[]
async def route(r):
    u=r.request.url
    if 'three.min.js' in u: await r.fulfill(body=THREE,content_type='application/javascript')
    elif 'supabase.co' in u:
        # 가짜 Supabase: map/mode 열이 없는 표처럼 동작 (400)
        req=r.request
        if req.method=='POST':
            b=req.post_data or '';posts.append(b)
            if 'mode' in b: await r.fulfill(status=400,body='{"code":"PGRST204"}',content_type='application/json')
            else: await r.fulfill(status=201,body='')
        else:
            if 'mode=eq' in u or 'map=eq' in u: await r.fulfill(status=400,body='{"code":"42703"}',content_type='application/json')
            else: await r.fulfill(status=200,body='[{"name":"민준","lap_ms":65432}]',content_type='application/json')
    elif u.startswith(('file:','data:')): await r.continue_()
    else: await r.abort()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required'])
        for tag,vw,vh,mob in [('pc',1280,720,False),('phoneL',844,390,True),('phoneP',390,844,True)]:
            ctx=await b.new_context(viewport={'width':vw,'height':vh},is_mobile=mob,has_touch=mob);pg=await ctx.new_page()
            errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
            await pg.route('**/*',route);await pg.goto('file://'+HTML);await pg.wait_for_timeout(1300)
            await pg.screenshot(path=f't1_modes_{tag}.png')
            print(tag,'start visible:',await pg.evaluate("getComputedStyle($('start')).display"),'modes:',await pg.evaluate("getComputedStyle($('modes')).display"))
            if tag=='pc':
                await pg.click('.mc[data-mode=duel]',force=True);await pg.wait_for_timeout(400)
                print('duel toast:',await pg.evaluate("$('toast').textContent"),'| still modes:',await pg.evaluate("$('modes').classList.contains('on')"))
                await pg.click('.mc[data-mode=hard]');await pg.wait_for_timeout(300)
                await pg.screenshot(path='t2_name.png')
                await pg.click('#mStep2 button[type=submit]');await pg.wait_for_timeout(200)
                print('empty name hint:',await pg.evaluate("$('mnHint').textContent"))
                await pg.fill('#mnName','테스트');await pg.press('#mnName','Enter');await pg.wait_for_timeout(2500)
                print('hard home: start',await pg.evaluate("getComputedStyle($('start')).display"),'maps hidden',await pg.evaluate("getComputedStyle(document.querySelector('#start .maps')).display"),'MAP',await pg.evaluate("MAPID"),'name',await pg.evaluate("localStorage.getItem('drift-name')"))
                await pg.screenshot(path='t3_home_hard.png')
                # 플레이 → 하드
                await pg.evaluate("$('go').click()");await pg.wait_for_timeout(1500)
                await pg.screenshot(path='t4_hard_play.png')
                # 벽 충돌 5번 시뮬레이션
                for i in range(5):
                    await pg.evaluate("""()=>{const n=TN[ci];c.vx=n[0]*16;c.vz=n[1]*16;c.x+=n[0]*(WALL-side+1);c.z+=n[1]*(WALL-side+1);}""")
                    await pg.wait_for_timeout(1000)
                    print('  hit',i+1,'hits=',await pg.evaluate("hits"),'dead',await pg.evaluate("DEAD"))
                await pg.wait_for_timeout(2600)
                await pg.screenshot(path='t5_fail.png')
                print('fail panel:',await pg.evaluate("$('failT').textContent+' | '+$('failSub').textContent+' | '+$('failNet').textContent"))
                # 1 스테이지 클리어 후 실패 -> 기록 전송 확인
                await pg.click('#failRetry');await pg.wait_for_timeout(800)
                print('retry: hits',await pg.evaluate("hits"),'dead',await pg.evaluate("DEAD"),'map',await pg.evaluate("MAPID"))
                await pg.evaluate("()=>{lapStart=performance.now()-61000;prog=N-1;c.x=TP[N-1][0];c.z=TP[N-1][1];ci=N-1}")
                await pg.evaluate("keys.gas=1");await pg.wait_for_timeout(1200);await pg.evaluate("keys.gas=0")
                await pg.screenshot(path='t6_stage_clear.png')
                print('after lap: stageTimes',await pg.evaluate("stageTimes.length"),'HOLD',await pg.evaluate("HOLD"))
                await pg.wait_for_timeout(3200)
                print('stage now',await pg.evaluate("hardIdx"),'map',await pg.evaluate("MAPID"),'HOLD',await pg.evaluate("HOLD"))
                for i in range(5):
                    await pg.evaluate("""()=>{const n=TN[ci];c.vx=n[0]*16;c.vz=n[1]*16;c.x+=n[0]*(WALL-side+1);c.z+=n[1]*(WALL-side+1);}""")
                    await pg.wait_for_timeout(1000)
                await pg.wait_for_timeout(2800)
                print('fail net:',await pg.evaluate("$('failNet').textContent"),'| posts:',posts)
                print('fail fields:',await pg.evaluate("[$('fStage').textContent,$('fClear').textContent,$('fTime').textContent,$('fHits').textContent].join(' / ')"))
                await pg.click('#failMenu');await pg.wait_for_timeout(500)
                print('back to modes:',await pg.evaluate("$('modes').classList.contains('on')"),'AC',await pg.evaluate("AC===null"))
                # 개인 랩타임
                await pg.click('.mc[data-mode=lap]');await pg.fill('#mnName','테스트');await pg.press('#mnName','Enter');await pg.wait_for_timeout(2500)
                print('lap home: maps display',await pg.evaluate("getComputedStyle(document.querySelector('#start .maps')).display"),'MAP',await pg.evaluate("MAPID"))
                await pg.screenshot(path='t7_home_lap.png')
                await pg.evaluate("$('lbBtn').click()");await pg.wait_for_timeout(500)
                await pg.screenshot(path='t8_home_board.png')
                await pg.evaluate("$('lbBtn').click()")
                await pg.evaluate("$('go').click()");await pg.wait_for_timeout(1200)
                await pg.evaluate("()=>{lapStart=performance.now()-71000;prog=N-1;c.x=TP[N-1][0];c.z=TP[N-1][1];ci=N-1}")
                await pg.evaluate("keys.gas=1");await pg.wait_for_timeout(1500);await pg.evaluate("keys.gas=0")
                print('lap msg:',await pg.evaluate("$('msg').textContent"),'| posts:',len(posts),'last:',posts[-1][:80])
                await pg.screenshot(path='t9_lap_record.png')
            print(tag,'errors',errs or 'none')
            await ctx.close()
        await b.close()
asyncio.run(main())
