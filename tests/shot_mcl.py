import asyncio,sys
from playwright.async_api import async_playwright
THREE=open('npm/node_modules/three/build/three.min.js').read()
HTML=sys.argv[1]
async def route(r):
    u=r.request.url
    if 'three.min.js' in u: await r.fulfill(body=THREE,content_type='application/javascript')
    elif u.startswith(('file:','data:')): await r.continue_()
    else: await r.abort()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required'])
        errs=[]
        for tag,vw,vh,mob in [('pc',1280,720,False),('phoneL',844,390,True),('phoneP',390,844,True)]:
            ctx=await b.new_context(viewport={'width':vw,'height':vh},is_mobile=mob,has_touch=mob)
            pg=await ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
            await pg.route('**/*',route)
            await pg.goto('file://'+HTML);await pg.wait_for_timeout(1200)
            await pg.click('.cars [data-car=mcl]');await pg.wait_for_timeout(1100)
            await pg.screenshot(path=f'm1_home_{tag}.png')
            await pg.evaluate("document.getElementById('go').click()");await pg.wait_for_timeout(2600)
            await pg.screenshot(path=f'm2_game_{tag}.png')
            if tag=='pc': print(await pg.evaluate("({car:CARID,snd:$('snd').textContent,dur:eng&&eng.buffer.duration,state:AC.state})"))
            await ctx.close()
        print('errors',errs or 'none')
        await b.close()
asyncio.run(main())
