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
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        errs=[]
        for tag,vw,vh,mob in [('pc',1280,720,False),('phoneL',844,390,True),('phoneP',390,844,True)]:
            ctx=await b.new_context(viewport={'width':vw,'height':vh},is_mobile=mob,has_touch=mob)
            pg=await ctx.new_page()
            pg.on('pageerror',lambda e:errs.append(str(e)))
            await pg.route('**/*',route)
            await pg.goto('file://'+HTML);await pg.wait_for_timeout(1300)
            await pg.screenshot(path=f'c1_home_{tag}.png')
            if tag=='pc':
                await pg.click('.cars [data-car=tesla]',force=True);await pg.wait_for_timeout(500)
                await pg.screenshot(path='c2_tesla_toast.png')
                print('after tesla checked:',await pg.evaluate("document.querySelector('.cars [aria-checked=true]').dataset.car"),'toast:',await pg.evaluate("document.getElementById('toast').textContent"))
                for id in ['gt3','chal','f40']:
                    await pg.click(f'.cars [data-car={id}]');await pg.wait_for_timeout(1100)
                    await pg.screenshot(path=f'c3_home_{id}.png')
                    await pg.click('#go');await pg.wait_for_timeout(500)
                    await pg.evaluate("(k)=>{c.x=TP[0][0];c.z=TP[0][1];c.vx=c.vz=0}",0)
                    await pg.wait_for_timeout(900)
                    await pg.screenshot(path=f'c4_game_{id}.png')
                    await pg.evaluate("document.getElementById('start').style.display='grid';started=false")
            await ctx.close()
        print('errors',errs or 'none')
        await b.close()
asyncio.run(main())
