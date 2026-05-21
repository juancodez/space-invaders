import base64

BASE  = "C:/Users/tn/Desktop/Game-Portfolio/Legacy Collection/Legacy Collection/Assets"
BOSS  = BASE + "/Warped/Characters/top-down-boss/PNG/spritesheets"

def b64(path):
    with open(path,'rb') as f: return base64.b64encode(f.read()).decode()

assets = {
    'player':   BASE+"/Warped/Characters/top-down-shooter-ship/spritesheets/yellow/ship-01.png",
    'enemy01':  BASE+"/Warped/Characters/top-down-shooter-enemies/spritesheets/enemy-01.png",
    'enemy02':  BASE+"/Warped/Characters/top-down-shooter-enemies/spritesheets/enemy-02.png",
    'enemy03':  BASE+"/Warped/Characters/top-down-shooter-enemies/spritesheets/enemy-03.png",
    'alien':    BASE+"/Warped/Characters/alien-flying-enemy/spritesheet.png",
    'expl':     BASE+"/Explosions and Magic/EnemyDeath/spritesheet.png",
    'bg1':      BASE+"/Warped/Environments/space_background_pack/Old Version/layers/parallax-space-backgound.png",
    'bg2':      BASE+"/Warped/Environments/space_background_pack/Old Version/layers/parallax-space-stars.png",
    'bg3':      BASE+"/Warped/Environments/space_background_pack/Old Version/layers/parallax-space-far-planets.png",
    'boss':     BOSS+"/boss.png",
    'rays':     BOSS+"/rays.png",
    'bolt':     BOSS+"/bolt.png",
    'canl':     BOSS+"/cannon-left.png",
    'canr':     BOSS+"/cannon-right.png",
    'bthr':     BOSS+"/boss-thrust.png",
}

b64s = {k: b64(v) for k,v in assets.items()}

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Space Invaders — Legacy Edition</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;display:flex;align-items:center;justify-content:center;height:100vh;overflow:hidden}
canvas{display:block;image-rendering:pixelated;image-rendering:crisp-edges}
</style>
</head>
<body><canvas id="c"></canvas>
<script>
// ── assets ───────────────────────────────────────────────────────────
const B64={
  player:'data:image/png;base64,__player__',enemy01:'data:image/png;base64,__enemy01__',
  enemy02:'data:image/png;base64,__enemy02__',enemy03:'data:image/png;base64,__enemy03__',
  alien:'data:image/png;base64,__alien__',expl:'data:image/png;base64,__expl__',
  bg1:'data:image/png;base64,__bg1__',bg2:'data:image/png;base64,__bg2__',
  bg3:'data:image/png;base64,__bg3__',boss:'data:image/png;base64,__boss__',
  rays:'data:image/png;base64,__rays__',bolt:'data:image/png;base64,__bolt__',
  canl:'data:image/png;base64,__canl__',canr:'data:image/png;base64,__canr__',
  bthr:'data:image/png;base64,__bthr__',
};

// ── canvas ──────────────────────────────────────────────────────────
const cv=document.getElementById('c'),cx=cv.getContext('2d');
const W=800,H=450;
cv.width=W;cv.height=H;
function resize(){const s=Math.min(innerWidth/W,innerHeight/H);cv.style.width=(W*s)+'px';cv.style.height=(H*s)+'px';}
addEventListener('resize',resize);resize();

// ── assets ──────────────────────────────────────────────────────────
const imgs={};let loaded=0,total=Object.keys(B64).length;
for(const[k,src] of Object.entries(B64)){const i=new Image();i.onload=()=>loaded++;i.src=src;imgs[k]=i;}

// ── input ────────────────────────────────────────────────────────────
const keys={},prev={};
addEventListener('keydown',e=>{keys[e.code]=true;if(['Space','ArrowUp','ArrowDown','KeyW','KeyS','KeyP'].includes(e.code))e.preventDefault();});
addEventListener('keyup',e=>keys[e.code]=false);
function jp(c){return keys[c]&&!prev[c];}

// ── constants ────────────────────────────────────────────────────────
const SZ=48,PDR=44,EDR=38;
const ACW=83,ACH=64,ADW=40,ADH=32;    // alien cell / draw dims
const BCW=192,BCH=144,BDW=144,BDH=108; // boss  cell / draw dims

// ── state ────────────────────────────────────────────────────────────
const ST={MENU:0,PLAY:1,PAUSE:2,CLEAR:3,BOSS:4,WIN:5,OVER:6};
let gs=ST.MENU;
let score=0,gt=0,shakeT=0,currentLevel=1;

// ── player ───────────────────────────────────────────────────────────
const P={x:80,y:H/2,spd:230,w:PDR,h:PDR,fr:0,ft:0,fRate:.10,lives:3,inv:false,invT:0,scd:0};

// ── bullets ──────────────────────────────────────────────────────────
let pb=[],eb=[];

// ── enemies ──────────────────────────────────────────────────────────
let enemies=[],eST=3.5,pST=2.5,dvST=2.0,dvN=0;
function mkE(o){return Object.assign({fr:0,ft:0,fRate:.12,ph:Math.random()*Math.PI*2,alive:true,required:true,pts:100,speed:62,vy:0,diving:false,hasShot:false,dw:EDR,dh:EDR,cw:SZ,ch:SZ,mf:5},o);}
function spawnL1(){enemies=[];eST=3.5;dvN=0;const gy=72,gx=68,top=(H-2*gy)/2;for(let r=0;r<3;r++)for(let c=0;c<5;c++)enemies.push(mkE({type:'march',key:'enemy01',x:890+c*gx,y:top+r*gy,bY:top+r*gy,pts:100,speed:62}));}
function spawnL2(){enemies=[];eST=2.5;dvST=2.0;dvN=0;const gy=72,gx=68,top=(H-2*gy)/2;for(let r=0;r<3;r++)for(let c=0;c<5;c++)enemies.push(mkE({type:'march',key:'enemy02',x:900+c*gx,y:top+r*gy,bY:top+r*gy,mf:4,pts:150,speed:80,fRate:.10}));}
function spawnDiver(){const side=dvN%2,y=side===0?55+Math.random()*90:H-55-Math.random()*90;enemies.push(mkE({type:'diver',key:'alien',x:W+20,y,bY:y,dw:ADW,dh:ADH,cw:ACW,ch:ACH,mf:8,pts:250,required:false,fRate:.09,speed:145}));}
function spawnL3(){enemies=[];eST=99;pST=2.5;dvN=0;const gx=65;for(let r=0;r<2;r++)for(let c=0;c<4;c++){enemies.push(mkE({type:'pincer',key:'enemy03',x:920+c*gx,y:65+r*55,bY:65+r*55,mf:4,pts:200,speed:82,fRate:.10,vy:28}));enemies.push(mkE({type:'pincer',key:'enemy03',x:920+c*gx,y:H-65-r*55,bY:H-65-r*55,mf:4,pts:200,speed:82,fRate:.10,vy:-28}));}}

// ── boss ─────────────────────────────────────────────────────────────
const boss={x:920,y:H/2,targetX:660,hp:300,maxHp:300,phase:0,
  fr:0,frT:0,thrFr:0,thrT:0,
  rayState:'idle',rayT:3.0,rayTimer:0,rayY:H/2,rayFr:0,
  canT:99,dying:false,deathT:0,deathN:0,entering:true,alive:false};
function spawnBoss(){pb=[];eb=[];explosions=[];Object.assign(boss,{x:920,y:H/2,targetX:660,hp:300,maxHp:300,phase:0,fr:0,frT:0,thrFr:0,thrT:0,rayState:'idle',rayT:3.5,rayTimer:0,rayY:H/2,rayFr:0,canT:99,dying:false,deathT:0,deathN:0,entering:true,alive:true});gs=ST.BOSS;}

// ── explosions ───────────────────────────────────────────────────────
let explosions=[];
function boom(x,y,sz=44){explosions.push({x,y,sz,fr:0,ft:0,fRate:.07});}

// ── background ───────────────────────────────────────────────────────
const BW=272,BH=160,BS=H/BH,BTW=BW*BS;
const bgl=[{k:'bg1',x:0,spd:28},{k:'bg2',x:0,spd:55},{k:'bg3',x:0,spd:92}];

// ── sprite helper ────────────────────────────────────────────────────
function sp(key,fr,ccx,ccy,dw,dh,rot,cw,ch){
  cw=cw||SZ;ch=ch||SZ;
  cx.save();cx.translate(ccx,ccy);cx.rotate(rot);
  cx.imageSmoothingEnabled=false;
  cx.drawImage(imgs[key],fr*cw,0,cw,ch,-dw/2,-dh/2,dw,dh);
  cx.restore();
}

// ── start / advance ──────────────────────────────────────────────────
function startGame(){score=0;gt=0;currentLevel=1;P.y=H/2;P.lives=3;P.inv=false;P.scd=0;pb=[];eb=[];explosions=[];spawnL1();gs=ST.PLAY;}
function advanceLevel(){pb=[];eb=[];explosions=[];currentLevel++;if(currentLevel===2)spawnL2(),gs=ST.PLAY;else if(currentLevel===3)spawnL3(),gs=ST.PLAY;else spawnBoss();}

// ── enemy AI ─────────────────────────────────────────────────────────
function updMarch(e,dt){e.x-=e.speed*dt;e.y=e.bY+Math.sin(gt*1.4+e.ph)*14;e.ft+=dt;if(e.ft>=e.fRate){e.ft=0;e.fr=(e.fr+1)%e.mf;}if(e.x<50&&gs===ST.PLAY)gs=ST.OVER;}
function updDiver(e,dt){e.x-=e.speed*dt;if(!e.diving&&e.x<440)e.diving=true;if(e.diving){const dy=P.y-e.y;e.vy+=Math.sign(dy)*380*dt;e.vy=Math.max(-190,Math.min(190,e.vy));}e.y+=e.vy*dt;e.ft+=dt;if(e.ft>=e.fRate){e.ft=0;e.fr=(e.fr+1)%e.mf;}if(!e.hasShot&&e.x<460&&e.x>100){eb.push({x:e.x-ADH/2,y:e.y,vx:-230,vy:0});e.hasShot=true;}if(e.x<-60||e.y<-60||e.y>H+60)e.alive=false;}
function updPincer(e,dt){e.x-=e.speed*dt;const diff=H/2-e.bY;e.bY+=Math.sign(diff)*Math.min(35*dt,Math.abs(diff));e.y=e.bY+Math.sin(gt*1.6+e.ph)*12;e.ft+=dt;if(e.ft>=e.fRate){e.ft=0;e.fr=(e.fr+1)%e.mf;}if(e.x<50&&gs===ST.PLAY)gs=ST.OVER;}
function hitR(e){return Math.max(e.dw,e.dh)/2+4;}

// ── levels 1-3 update ────────────────────────────────────────────────
function update(dt){
  for(const l of bgl){l.x-=l.spd*dt;if(l.x<=-BTW)l.x+=BTW;}
  if(gs!==ST.PLAY)return;
  gt+=dt;
  // player
  if(keys['ArrowUp']  ||keys['KeyW'])P.y-=P.spd*dt;
  if(keys['ArrowDown']||keys['KeyS'])P.y+=P.spd*dt;
  P.y=Math.max(P.h/2+2,Math.min(H-P.h/2-2,P.y));
  P.ft+=dt;if(P.ft>=P.fRate){P.ft=0;P.fr=(P.fr+1)%5;}
  P.scd-=dt;if(keys['Space']&&P.scd<=0){pb.push({x:P.x+P.w/2+4,y:P.y});P.scd=.22;}
  if(P.inv){P.invT-=dt;if(P.invT<=0)P.inv=false;}
  // level 2 diver spawn
  if(currentLevel===2&&dvN<5){dvST-=dt;if(dvST<=0){spawnDiver();dvN++;dvST=2.4+Math.random()*1.2;}}
  // enemy AI
  for(const e of enemies){if(!e.alive)continue;if(e.type==='march')updMarch(e,dt);else if(e.type==='diver')updDiver(e,dt);else if(e.type==='pincer')updPincer(e,dt);if(gs!==ST.PLAY)return;}
  // clear check
  if(!enemies.some(e=>e.required&&e.alive)){gs=ST.CLEAR;return;}
  // formation shoot
  eST-=dt;if(eST<=0){const sh=enemies.filter(e=>e.alive&&e.type==='march');if(sh.length){const s=sh[0|Math.random()*sh.length];eb.push({x:s.x-EDR/2-4,y:s.y,vx:-(180+currentLevel*20),vy:0});}eST=currentLevel===2?1.8+Math.random()*.8:3.0+Math.random()*1.5;}
  // pincer 3-spread
  if(currentLevel===3){const ag=enemies.filter(e=>e.alive&&e.type==='pincer'&&e.x<285);if(ag.length){pST-=dt;if(pST<=0){const s=ag[0|Math.random()*ag.length],ox=s.x-EDR/2;eb.push({x:ox,y:s.y,vx:-295,vy:0},{x:ox,y:s.y,vx:-245,vy:-145},{x:ox,y:s.y,vx:-245,vy:145});pST=1.5+Math.random()*.5;}}}
  // player bullets vs enemies
  for(let i=pb.length-1;i>=0;i--){const b=pb[i];b.x+=570*dt;if(b.x>W+20){pb.splice(i,1);continue;}for(const e of enemies){if(!e.alive)continue;if(Math.hypot(b.x-e.x,b.y-e.y)<hitR(e)){e.alive=false;boom(e.x,e.y);score+=e.pts;pb.splice(i,1);break;}}}
  // enemy bullets vs player
  for(let i=eb.length-1;i>=0;i--){const b=eb[i];b.x+=b.vx*dt;b.y+=b.vy*dt;if(b.x<-20||b.y<-20||b.y>H+20){eb.splice(i,1);continue;}if(!P.inv&&Math.hypot(b.x-P.x,b.y-P.y)<PDR/2+4){P.lives--;P.inv=true;P.invT=2.0;boom(P.x,P.y,52);eb.splice(i,1);if(!P.lives){gs=ST.OVER;return;}}}
  // explosions
  for(let i=explosions.length-1;i>=0;i--){const e=explosions[i];e.ft+=dt;if(e.ft>=e.fRate){e.ft=0;e.fr++;}if(e.fr>=8)explosions.splice(i,1);}
}

// ── boss AI ──────────────────────────────────────────────────────────
function updateBossAI(dt){
  if(!boss.alive)return;
  // animate body & thruster
  boss.frT+=dt;if(boss.frT>=.15){boss.frT=0;boss.fr=(boss.fr+1)%5;}
  boss.thrT+=dt;if(boss.thrT>=.10){boss.thrT=0;boss.thrFr=(boss.thrFr+1)%4;}
  // entry slide
  if(boss.entering){
    boss.x-=220*dt;boss.y=H/2;
    if(boss.x<=boss.targetX){boss.x=boss.targetX;boss.entering=false;boss.phase=1;boss.rayT=3.5;shakeT=.8;}
    return;
  }
  // death sequence
  if(boss.dying){
    boss.deathT-=dt;
    if(boss.deathT<=0){boss.deathN++;boom(boss.x+(Math.random()-.5)*70,boss.y+(Math.random()-.5)*60,55+Math.random()*30);boss.deathT=.28;if(boss.deathN>=7){score+=P.lives*1000;gs=ST.WIN;}}
    return;
  }
  // phase transitions
  const np=boss.hp>200?1:(boss.hp>100?2:3);
  if(np!==boss.phase){boss.phase=np;shakeT=.6;if(np===2)boss.canT=3.0;if(np===3){boss.rayT=Math.min(boss.rayT,2.2);boss.canT=Math.min(boss.canT,1.6);}}
  // oscillation
  const freq=boss.phase===3?1.6:.8;
  boss.y=H/2+Math.sin(gt*freq*Math.PI*2)*80;
  // ray state machine
  if(boss.rayState==='idle'){boss.rayT-=dt;if(boss.rayT<=0){boss.rayState='telegraph';boss.rayTimer=1.0;boss.rayY=boss.y;}}
  else if(boss.rayState==='telegraph'){boss.rayTimer-=dt;if(boss.rayTimer<=0){boss.rayState='fire';boss.rayTimer=.44;boss.rayFr=0;}}
  else if(boss.rayState==='fire'){
    boss.rayTimer-=dt;
    boss.rayFr=Math.min(10,0|((0.44-boss.rayTimer)/.04));
    if(!P.inv&&Math.abs(P.y-boss.rayY)<24){P.lives--;P.inv=true;P.invT=2.0;boom(P.x,P.y,52);shakeT=.3;if(!P.lives){gs=ST.OVER;return;}}
    if(boss.rayTimer<=0){boss.rayState='idle';boss.rayT=boss.phase===1?3.5:(boss.phase===2?5.5:2.2);}
  }
  // cannon (phase 2+)
  if(boss.phase>=2){
    boss.canT-=dt;
    if(boss.canT<=0){
      const bx=boss.x-52;
      eb.push({x:bx,y:boss.y,vx:-285,vy:0,isBolt:true});
      eb.push({x:bx,y:boss.y,vx:-240,vy:-145,isBolt:true});
      eb.push({x:bx,y:boss.y,vx:-240,vy:145,isBolt:true});
      if(boss.phase===3){eb.push({x:bx,y:boss.y,vx:-190,vy:-210,isBolt:true});eb.push({x:bx,y:boss.y,vx:-190,vy:210,isBolt:true});}
      boss.canT=boss.phase===3?1.5:2.2;
    }
  }
}

// ── boss fight update ─────────────────────────────────────────────────
function updateBoss(dt){
  for(const l of bgl){l.x-=l.spd*dt;if(l.x<=-BTW)l.x+=BTW;}
  if(gs!==ST.BOSS)return;
  gt+=dt;shakeT=Math.max(0,shakeT-dt);
  // player
  if(keys['ArrowUp']  ||keys['KeyW'])P.y-=P.spd*dt;
  if(keys['ArrowDown']||keys['KeyS'])P.y+=P.spd*dt;
  P.y=Math.max(P.h/2+2,Math.min(H-P.h/2-2,P.y));
  P.ft+=dt;if(P.ft>=P.fRate){P.ft=0;P.fr=(P.fr+1)%5;}
  P.scd-=dt;if(keys['Space']&&P.scd<=0){pb.push({x:P.x+P.w/2+4,y:P.y});P.scd=.22;}
  if(P.inv){P.invT-=dt;if(P.invT<=0)P.inv=false;}
  // boss AI
  updateBossAI(dt);if(gs!==ST.BOSS)return;
  // player bullets vs boss
  for(let i=pb.length-1;i>=0;i--){
    const b=pb[i];b.x+=570*dt;
    if(b.x>W+20){pb.splice(i,1);continue;}
    if(!boss.dying&&!boss.entering&&Math.abs(b.x-boss.x)<56&&Math.abs(b.y-boss.y)<72){
      pb.splice(i,1);boss.hp=Math.max(0,boss.hp-10);
      if(boss.hp===0&&!boss.dying){boss.dying=true;boss.deathT=.25;boss.deathN=0;boom(boss.x,boss.y,80);shakeT=1.0;}
    }
  }
  // boss bullets vs player
  for(let i=eb.length-1;i>=0;i--){const b=eb[i];b.x+=b.vx*dt;b.y+=b.vy*dt;if(b.x<-20||b.y<-20||b.y>H+20){eb.splice(i,1);continue;}if(!P.inv&&Math.hypot(b.x-P.x,b.y-P.y)<PDR/2+6){P.lives--;P.inv=true;P.invT=2.0;boom(P.x,P.y,52);shakeT=.3;eb.splice(i,1);if(!P.lives){gs=ST.OVER;return;}}}
  // explosions
  for(let i=explosions.length-1;i>=0;i--){const e=explosions[i];e.ft+=dt;if(e.ft>=e.fRate){e.ft=0;e.fr++;}if(e.fr>=8)explosions.splice(i,1);}
}

// ── draw helpers ─────────────────────────────────────────────────────
function drawBG(){cx.imageSmoothingEnabled=false;for(const l of bgl){let x=l.x;while(x>0)x-=BTW;while(x<W){cx.drawImage(imgs[l.k],0,0,BW,BH,x,0,BTW,H);x+=BTW;}}}

function drawBullets(){
  for(const b of pb){cx.shadowColor='#00ffee';cx.shadowBlur=10;cx.fillStyle='#00ffee';cx.fillRect(b.x-11,b.y-2,20,4);cx.fillStyle='#fff';cx.fillRect(b.x-8,b.y-1,13,2);cx.shadowBlur=0;}
  for(const b of eb){
    if(b.isBolt){
      const ang=Math.atan2(b.vy,b.vx);
      cx.save();cx.translate(b.x,b.y);cx.rotate(ang);cx.imageSmoothingEnabled=false;
      cx.shadowColor='#ffcc00';cx.shadowBlur=8;
      cx.drawImage(imgs.bolt,0,0,16,8,-14,-6,26,11);
      cx.shadowBlur=0;cx.restore();
    }else{
      const lv3col=currentLevel===3;
      cx.shadowColor=lv3col?'#ff8800':'#ff3333';cx.shadowBlur=8;
      cx.fillStyle=lv3col?'#ff8800':'#ff3333';
      if(b.vy===0){cx.fillRect(b.x-9,b.y-2,16,4);cx.fillStyle=lv3col?'#ffc880':'#ffbbbb';cx.fillRect(b.x-6,b.y-1,10,2);}
      else{cx.beginPath();cx.arc(b.x,b.y,4,0,Math.PI*2);cx.fill();}
      cx.shadowBlur=0;
    }
  }
}

function drawExplosions(){for(const e of explosions){cx.save();cx.imageSmoothingEnabled=false;cx.drawImage(imgs.expl,e.fr*SZ,0,SZ,SZ,e.x-e.sz/2,e.y-e.sz/2,e.sz,e.sz);cx.restore();}}

function drawPlayer(){if(!(P.inv&&Math.floor(P.invT*8)%2===0))sp('player',P.fr,P.x,P.y,PDR,PDR,Math.PI/2);}

function drawHUD(){
  cx.imageSmoothingEnabled=true;cx.textBaseline='top';cx.font='bold 14px monospace';
  cx.textAlign='left';cx.fillStyle='#ff6688';
  let h='';for(let i=0;i<P.lives;i++)h+='♥ ';cx.fillText(h+(P.inv?'  !!':''),10,8);
  cx.textAlign='center';cx.fillStyle='#ffe066';cx.fillText('SCORE  '+String(score).padStart(6,'0'),W/2,8);
  cx.textAlign='right';cx.fillStyle='#88aaff';cx.fillText('LEVEL  '+currentLevel,W-10,8);
}

function drawEnemies(){for(const e of enemies){if(!e.alive)continue;if(e.type==='diver')sp(e.key,e.fr,e.x,e.y,e.dw,e.dh,-Math.PI/2,e.cw,e.ch);else sp(e.key,e.fr,e.x,e.y,e.dw,e.dh,-Math.PI/2);}}

// ── boss scene ───────────────────────────────────────────────────────
function drawRayEffect(){
  if(boss.rayState==='idle'||boss.entering)return;
  const by=boss.rayY,bx=boss.x-52;
  if(boss.rayState==='telegraph'){
    if(Math.floor(Date.now()/110)%2){
      cx.save();cx.setLineDash([8,6]);cx.strokeStyle='rgba(255,100,40,.55)';cx.lineWidth=2;
      cx.beginPath();cx.moveTo(0,by);cx.lineTo(bx,by);cx.stroke();
      cx.setLineDash([]);cx.restore();
    }
    // triangle warning at mouth
    cx.fillStyle='rgba(255,80,30,.35)';
    cx.beginPath();cx.moveTo(bx,by);cx.lineTo(bx+18,by-9);cx.lineTo(bx+18,by+9);cx.fill();
  }
  if(boss.rayState==='fire'){
    const fade=Math.min(1,boss.rayTimer/.18);
    cx.save();
    cx.shadowColor='#ff6600';cx.shadowBlur=24;
    cx.strokeStyle='rgba(255,120,30,'+((.75*fade).toFixed(2))+')';cx.lineWidth=22;
    cx.beginPath();cx.moveTo(0,by);cx.lineTo(bx,by);cx.stroke();
    cx.strokeStyle='rgba(255,220,100,'+(fade.toFixed(2))+')';cx.lineWidth=7;
    cx.beginPath();cx.moveTo(0,by);cx.lineTo(bx,by);cx.stroke();
    cx.strokeStyle='rgba(255,255,230,'+((fade*.9).toFixed(2))+')';cx.lineWidth=2;
    cx.beginPath();cx.moveTo(0,by);cx.lineTo(bx,by);cx.stroke();
    cx.shadowBlur=0;cx.restore();
    // muzzle spray from rays sheet (11 frames, cell 64×224)
    if(boss.rayFr<11)sp('rays',boss.rayFr,bx-8,by,56,140,Math.PI/2,64,224);
  }
}

function drawHPBar(){
  const tw=280,th=10,tx=W/2-140,ty=22;
  const pct=Math.max(0,boss.hp/boss.maxHp);
  const col=boss.hp>200?'#44ff88':(boss.hp>100?'#ffee44':'#ff4444');
  cx.fillStyle='#111';cx.fillRect(tx-2,ty-2,tw+4,th+4);
  cx.fillStyle='#2a2a2a';cx.fillRect(tx,ty,tw,th);
  if(boss.hp<=100){cx.shadowColor=col;cx.shadowBlur=10;}
  cx.fillStyle=col;cx.fillRect(tx,ty,tw*pct,th);
  cx.shadowBlur=0;
  cx.fillStyle='rgba(0,0,0,.45)';
  for(let i=1;i<10;i++)cx.fillRect(tx+tw*i/10-.5,ty,1,th);
  cx.strokeStyle='#555';cx.lineWidth=1;cx.strokeRect(tx,ty,tw,th);
  cx.textAlign='center';cx.textBaseline='top';cx.font='bold 11px monospace';cx.fillStyle='#888';
  cx.fillText('THE  OVERLORD',W/2,ty+th+3);
}

function drawBossSprite(){
  if(!boss.alive)return;
  const bx=boss.x,by=boss.y;
  // thruster (to the right of boss, pointing right)
  sp('bthr',boss.thrFr,bx+66,by,52,40,Math.PI/2,64,48);
  // boss body — 5 frames at 192×144, draw at 144×108, rotated -90° (faces left)
  if(boss.dying&&Math.floor(boss.deathT*20)%2===0){
    cx.save();cx.globalAlpha=.5;sp('boss',boss.fr,bx,by,BDW,BDH,-Math.PI/2,BCW,BCH);cx.globalAlpha=1;cx.restore();
  }else{
    sp('boss',boss.fr,bx,by,BDW,BDH,-Math.PI/2,BCW,BCH);
  }
  // cannons (phase 2+, not during entry/dying)
  if(!boss.entering&&!boss.dying&&boss.phase>=2){
    sp('canl',0,bx-12,by-66,28,28,-Math.PI/2);
    sp('canr',0,bx-12,by+66,28,28, Math.PI/2);
  }
  // entry warning pulse
  if(boss.entering&&Math.floor(Date.now()/280)%2){
    cx.textAlign='center';cx.textBaseline='middle';cx.shadowColor='#ff2222';cx.shadowBlur=22;
    cx.font='bold 38px monospace';cx.fillStyle='#ff3333';
    cx.fillText('⚠  WARNING  ⚠',W/2,H/2);
    cx.shadowBlur=0;
  }
  // HP bar
  if(!boss.entering)drawHPBar();
}

// ── screen overlays ──────────────────────────────────────────────────
function overlay(title,col,sub){
  cx.fillStyle='rgba(0,0,0,.65)';cx.fillRect(0,0,W,H);
  cx.textAlign='center';cx.textBaseline='middle';
  cx.shadowColor=col;cx.shadowBlur=22;cx.font='bold 44px monospace';cx.fillStyle=col;cx.fillText(title,W/2,H/2-44);
  cx.shadowBlur=0;cx.font='18px monospace';cx.fillStyle='#ffe066';cx.fillText('SCORE  '+String(score).padStart(6,'0'),W/2,H/2+6);
  cx.font='14px monospace';cx.fillStyle='#aaa';cx.fillText(sub,W/2,H/2+46);
}

function drawMenu(){
  cx.fillStyle='rgba(0,0,0,.55)';cx.fillRect(0,0,W,H);
  cx.textAlign='center';cx.textBaseline='middle';
  cx.shadowColor='#ffe066';cx.shadowBlur=20;cx.font='bold 48px monospace';cx.fillStyle='#ffe066';cx.fillText('SPACE INVADERS',W/2,H/2-72);
  cx.shadowBlur=0;cx.font='20px monospace';cx.fillStyle='#cccccc';cx.fillText('LEGACY  EDITION',W/2,H/2-24);
  cx.font='15px monospace';cx.fillStyle='#88ffcc';
  if(Math.floor(Date.now()/500)%2)cx.fillText('PRESS  SPACE  TO  START',W/2,H/2+30);
  cx.font='12px monospace';cx.fillStyle='#556677';cx.fillText('↑↓ / W S — MOVE          SPACE — SHOOT          P — PAUSE',W/2,H/2+74);
  cx.font='11px monospace';cx.fillStyle='#445566';cx.fillText('3 LEVELS  ·  ALIEN DIVERS  ·  PINCER ASSAULT  ·  BOSS BATTLE',W/2,H/2+100);
}

function drawWin(){
  cx.fillStyle='rgba(0,0,10,.92)';cx.fillRect(0,0,W,H);
  // sparkle rain
  const t=Date.now();
  for(let i=0;i<35;i++){
    const x=((i*79+t*.03*(1+i%4))%W+W)%W;
    const y=((i*113+t*.05*(1+(i+1)%3))%H+H)%H;
    cx.globalAlpha=.4+.6*Math.abs(Math.sin(t/400+i));
    cx.fillStyle=i%3===0?'#ffe066':(i%3===1?'#ff88cc':'#88ffcc');
    cx.fillRect(x,y,2,4);
  }
  cx.globalAlpha=1;
  cx.textAlign='center';cx.textBaseline='middle';
  cx.shadowColor='#ffee44';cx.shadowBlur=30;cx.font='bold 56px monospace';cx.fillStyle='#ffee44';cx.fillText('YOU  WIN!',W/2,H/2-90);
  cx.shadowBlur=0;
  cx.font='16px monospace';cx.fillStyle='#88ffcc';cx.fillText('The Overlord has been defeated.',W/2,H/2-42);
  const lb=P.lives*1000,cs=score-lb;
  cx.font='14px monospace';
  cx.fillStyle='#aaa';cx.fillText('Combat Score   '+String(Math.max(0,cs)).padStart(7,'0'),W/2,H/2+4);
  cx.fillStyle='#88ffcc';cx.fillText('Lives Bonus  + '+String(lb).padStart(7,'0'),W/2,H/2+28);
  cx.strokeStyle='#444';cx.lineWidth=1;cx.beginPath();cx.moveTo(W/2-130,H/2+46);cx.lineTo(W/2+130,H/2+46);cx.stroke();
  cx.fillStyle='#ffe066';cx.fillText('TOTAL          '+String(score).padStart(7,'0'),W/2,H/2+60);
  cx.font='13px monospace';cx.fillStyle='#aaa';
  if(Math.floor(Date.now()/600)%2)cx.fillText('PRESS  SPACE  TO  PLAY  AGAIN',W/2,H/2+108);
}

function levelClearLabel(){return currentLevel===3?'LEVEL  3  CLEAR!':'LEVEL  '+currentLevel+'  CLEAR!';}
function levelClearSub(){return currentLevel===3?'PRESS  SPACE  —  BOSS  INCOMING':'PRESS  SPACE  —  LEVEL  '+(currentLevel+1)+'  INCOMING';}

// ── main loop ─────────────────────────────────────────────────────────
let lastTs=0;
function loop(ts){
  const dt=Math.min((ts-lastTs)/1000,.05);lastTs=ts;
  cx.fillStyle='#000010';cx.fillRect(0,0,W,H);
  if(loaded<total){cx.textAlign='center';cx.textBaseline='middle';cx.font='18px monospace';cx.fillStyle='#fff';cx.fillText('Loading  '+loaded+' / '+total+'...',W/2,H/2);Object.assign(prev,keys);requestAnimationFrame(loop);return;}
  // update
  if(gs===ST.BOSS)updateBoss(dt);else update(dt);
  // draw BG
  drawBG();
  // shake offset
  if(shakeT>0){const s=shakeT*9;cx.save();cx.translate((Math.random()-.5)*s,(Math.random()-.5)*s);}
  // draw by state
  if(gs===ST.MENU){drawMenu();if(jp('Space'))startGame();}
  else if(gs===ST.PLAY){drawEnemies();drawPlayer();drawBullets();drawExplosions();drawHUD();if(jp('KeyP'))gs=ST.PAUSE;}
  else if(gs===ST.PAUSE){drawEnemies();drawPlayer();drawBullets();drawExplosions();drawHUD();overlay('PAUSED','#ffffff','PRESS  P  TO  RESUME');if(jp('KeyP'))gs=ST.PLAY;}
  else if(gs===ST.CLEAR){drawEnemies();drawExplosions();drawHUD();overlay(levelClearLabel(),'#88ffcc',levelClearSub());if(jp('Space'))advanceLevel();}
  else if(gs===ST.BOSS){
    drawRayEffect();
    drawPlayer();drawBullets();drawExplosions();
    drawBossSprite();
    drawHUD();
    if(!boss.entering&&!boss.dying&&jp('KeyP'))gs=ST.PAUSE;
  }
  else if(gs===ST.WIN){drawWin();if(jp('Space'))startGame();}
  else if(gs===ST.OVER){overlay('GAME  OVER','#ff4444','PRESS  SPACE  TO  RETRY');if(jp('Space'))startGame();}
  if(shakeT>0)cx.restore();
  Object.assign(prev,keys);
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);
</script></body></html>"""

for k, v in b64s.items():
    TEMPLATE = TEMPLATE.replace(f'__{k}__', v)

out = "C:/Users/tn/Desktop/Game-Portfolio/space-invaders.html"
with open(out,'w',encoding='utf-8') as f:
    f.write(TEMPLATE)
print(f"Done - {len(TEMPLATE)//1024} KB -> {out}")
