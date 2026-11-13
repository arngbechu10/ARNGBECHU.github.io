import asyncio,sys,json
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
        ctx=await b.new_context(viewport={'width':844,'height':390},is_mobile=True,has_touch=True)
        pg=await ctx.new_page();errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.route('**/*',route)
        await pg.goto('file://'+HTML);await pg.wait_for_timeout(1200)
        await pg.click('#go');await pg.wait_for_timeout(600)
        R=await pg.evaluate('''()=>{
          const kmh=()=>Math.round(Math.hypot(c.vx,c.vz)*3.6);
          const sync=()=>{const n=TN[ci],s=(c.x-TP[ci][0])*n[0]+(c.z-TP[ci][1])*n[1];c.x-=n[0]*s;c.z-=n[1]*s;const sp=Math.hypot(c.vx,c.vz);c.h=TH[ci];c.vx=Math.cos(c.h)*sp;c.vz=Math.sin(c.h)*sp};
          const run=(n)=>{for(let i=0;i<n;i++){step(1/60);sync()}};
          const out={};
          reset();keys.gas=1;run(120);out.A_gasOnly_2s=kmh();run(180);out.A_gasOnly_5s=kmh();
          reset();keys.gas=1;fireNitro();out.B_fired=NIT.on;run(120);out.B_nitro_2s=kmh();out.B_on_2s=NIT.on;
          run(120);out.B_nitro_4s=kmh();run(30);out.B_on_after4s=NIT.on;out.B_ready_after_use=NIT.ready;
          fireNitro();out.B_refire_same_lap_started=NIT.on;
          run(120);out.B_after_6s=kmh();
          const i=N-3;c.x=TP[i][0];c.z=TP[i][1];c.h=TH[i];c.vx=Math.cos(TH[i])*25;c.vz=Math.sin(TH[i])*25;ci=i;prog=N-3;
          run(60);out.C_ready_after_lap=NIT.ready;fireNitro();out.C_fires_next_lap=NIT.on;
          reset();keys.gas=1;c.vx=Math.cos(c.h)*66;c.vz=Math.sin(c.h)*66;run(40);out.D_cruise=kmh();fireNitro();run(120);out.D_nitro_2s=kmh();run(120);out.D_nitro_4s=kmh();
          keys.gas=0;return out}''')
        print(json.dumps(R,ensure_ascii=False,indent=1))
        # 화면 효과 확인 (실시간 렌더링)
        await pg.evaluate("reset();keys.gas=1;fireNitro();")
        await pg.wait_for_timeout(1500)
        info=await pg.evaluate("({nitroK:+nitroK.toFixed(2),fov:+cam.fov.toFixed(1),nitClass:document.getElementById('nit').className,barW:document.getElementById('nbar').style.width,btn:document.querySelector('.pad button[data-k=nitro]').className})")
        print('burning visuals',info)
        await pg.screenshot(path='n1_burn.png')
        await pg.evaluate("keys.gas=0")
        await pg.wait_for_timeout(300)
        await pg.evaluate("reset()");await pg.wait_for_timeout(1200)
        await pg.screenshot(path='n2_ready.png')
        await pg.evaluate("reset();fireNitro();for(let i=0;i<260;i++)step(1/60)");await pg.wait_for_timeout(1500)
        info2=await pg.evaluate("({nitClass:document.getElementById('nit').className,barW:document.getElementById('nbar').style.width,btn:document.querySelector('.pad button[data-k=nitro]').className,fov:+cam.fov.toFixed(1)})")
        print('spent visuals',info2)
        await pg.screenshot(path='n3_spent.png')
        print('errors:',errs or 'none')
        await b.close()
asyncio.run(main())
