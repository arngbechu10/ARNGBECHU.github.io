import asyncio,sys
from playwright.async_api import async_playwright
THREE=open('npm/node_modules/three/build/three.min.js').read()
async def route(r):
    u=r.request.url
    if 'three.min.js' in u: await r.fulfill(body=THREE,content_type='application/javascript')
    elif u.startswith(('file:','data:')): await r.continue_()
    else: await r.abort()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required'])
        ctx=await b.new_context(viewport={'width':1280,'height':720});pg=await ctx.new_page();errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.route('**/*',route);await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(1000)
        await pg.evaluate("document.getElementById('go').click()");await pg.wait_for_timeout(2500)
        for hand in (0,1):
            r=await pg.evaluate("""(h)=>{keys.hand=h;c.vx=0;c.vz=-15;slip=12;for(let i=0;i<40;i++){slip=12;drive(.016)}return sg.gain.value}""",hand)
            print('hand',hand,'skid gain',round(r,3))
        # 일반 주행(핸드 안 누름) 중 코너링 시 소리 없는지: 실제 물리로 몇 초 주행
        r=await pg.evaluate("""()=>{keys.hand=0;keys.gas=1;skG=0;return 1}""")
        mx=0
        for i in range(30):
            await pg.evaluate("keys.left=(Math.floor(performance.now()/700)%2)?1:0;keys.right=1-keys.left")
            await pg.wait_for_timeout(120);mx=max(mx,await pg.evaluate("sg.gain.value"))
        print('max skid gain without hand while swerving',round(mx,3),'errors',errs or 'none')
        await b.close()
asyncio.run(main())
