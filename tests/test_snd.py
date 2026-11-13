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
        for id in ['gtr','gt3','f40','chal']:
            ctx=await b.new_context(viewport={'width':1280,'height':720});pg=await ctx.new_page()
            errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
            await pg.route('**/*',route)
            await pg.goto('file://'+HTML);await pg.wait_for_timeout(1000)
            await pg.click(f'.cars [data-car={id}]');await pg.wait_for_timeout(300)
            await pg.click('#go');await pg.wait_for_timeout(2500)
            r=await pg.evaluate("({car:CARID,snd:$('snd').textContent,dur:eng&&eng.buffer.duration,sr:eng&&eng.buffer.sampleRate,loop:eng&&eng.loop,gain:eg&&eg.gain.value,rate:eng&&eng.playbackRate.value,state:AC.state})")
            print(id,r,errs)
            await ctx.close()
        await b.close()
asyncio.run(main())
