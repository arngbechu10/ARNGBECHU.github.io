import asyncio,sys
from playwright.async_api import async_playwright
THREE=open('npm/node_modules/three/build/three.min.js').read()
HTML=sys.argv[1];TAG=sys.argv[2];PTS=[int(x) for x in sys.argv[3].split(',')]
async def route(r):
    u=r.request.url
    if 'three.min.js' in u: await r.fulfill(body=THREE,content_type='application/javascript')
    elif u.startswith(('file:','data:')): await r.continue_()
    else: await r.abort()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        ctx=await b.new_context(viewport={'width':1280,'height':720});pg=await ctx.new_page();errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.route('**/*',route);await pg.goto('file://'+HTML);await pg.wait_for_timeout(1200)
        await pg.click('.maps [data-map=mountain]');await pg.wait_for_timeout(300)
        await pg.evaluate("document.getElementById('go').click()");await pg.wait_for_timeout(500)
        for k in PTS:
            await pg.evaluate("(k)=>{const i=k;c.x=TP[i][0];c.z=TP[i][1];c.h=TH[i];c.vx=c.vz=0;ci=i;prog=i;camY=TY[i]}",k)
            await pg.wait_for_timeout(1000)
            await pg.screenshot(path=f'{TAG}_{k}.png')
        print('errors',errs or 'none')
        await b.close()
asyncio.run(main())
