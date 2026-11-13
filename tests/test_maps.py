import asyncio,sys,json
from playwright.async_api import async_playwright
THREE=open('npm/node_modules/three/build/three.min.js').read()
HTML=sys.argv[1]
async def route(r):
    u=r.request.url
    if 'three.min.js' in u: await r.fulfill(body=THREE,content_type='application/javascript')
    elif u.startswith(('file:','data:')): await r.continue_()
    else: await r.abort()
AUTO='''([id,lim])=>{
  setMap(id);started=true;reset();
  const out={id,len:Math.round(TLEN),laps:0,maxSide:0,wallFrames:0,maxKmh:0,hits:0,t:0,offFrames:0};
  const wrap=thump;let prevH=0;
  for(let f=0;f<60*400;f++){
    const j=(ci+22)%N,des=Math.atan2(TP[j][1]-c.z,TP[j][0]-c.x);let e=des-c.h;e=Math.atan2(Math.sin(e),Math.cos(e));
    keys.left=e<-.04?1:0;keys.right=e>.04?1:0;
    const sp=Math.hypot(c.vx,c.vz);keys.gas=sp<lim?1:0;keys.brake=sp>lim*1.25?1:0;
    const before=hitK;step(1/60);if(hitK>before+.001)out.hits++;
    out.maxSide=Math.max(out.maxSide,Math.abs(side));if(WALL&&Math.abs(side)>WALL+.01)out.wallFrames++;
    if(Math.abs(side)>HALF+1.2)out.offFrames++;
    out.maxKmh=Math.max(out.maxKmh,Math.round(sp*3.6));
    out.t=f/60;
    if($('last').textContent!=='-'){out.lap1=$('last').textContent;break}
  }
  keys.left=keys.right=keys.gas=keys.brake=0;return out}'''
STRAIGHT='''(id)=>{
  setMap(id);started=true;reset();
  keys.gas=1;let maxS=0,minTY=1e9,maxTY=-1e9,hits=0,minKmh=1e9;
  for(let f=0;f<60*25;f++){const b=hitK;step(1/60);if(hitK>b+.001)hits++;maxS=Math.max(maxS,Math.abs(side));}
  keys.gas=0;return {id,maxSide:+maxS.toFixed(2),wall:WALL,hits,kmh:Math.round(Math.hypot(c.vx,c.vz)*3.6)}}'''
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        ctx=await b.new_context(viewport={'width':844,'height':390},is_mobile=True,has_touch=True)
        pg=await ctx.new_page();errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.on('console',lambda m:errs.append('console:'+m.text) if m.type=='error' else None)
        await pg.route('**/*',route)
        await pg.goto('file://'+HTML);await pg.wait_for_timeout(1500)
        await pg.screenshot(path='m0_home_phoneL.png')
        for id,lim in [('seoul',34),('mountain',26),('xmas',36)]:
            r=await pg.evaluate(AUTO,[id,lim]);print(json.dumps(r,ensure_ascii=False))
        for id in ['mountain','xmas','seoul']:
            r=await pg.evaluate(STRAIGHT,id);print('straight',json.dumps(r))
        print('errors:',errs or 'none')
        await b.close()
asyncio.run(main())
