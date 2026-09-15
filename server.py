import os, json, sqlite3, secrets, hashlib, time, asyncio, io, re, random, threading, unicodedata
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles
from PIL import Image
import qrcode
from seed import CATEGORIES, questions, FINAL
ROOT=Path(__file__).parent
(ROOT/'data').mkdir(exist_ok=True)
DB=sqlite3.connect(ROOT/'data/game.sqlite',check_same_thread=False)
DB.execute('PRAGMA journal_mode=WAL')
DB.execute('CREATE TABLE IF NOT EXISTS rooms(code TEXT PRIMARY KEY,owner TEXT,data TEXT)')
DB.execute('CREATE TABLE IF NOT EXISTS history(id TEXT PRIMARY KEY,owner TEXT,data TEXT)');DB.commit()
LOCK=threading.RLock()
RATE={}
app=FastAPI(docs_url=None,redoc_url=None)
app.mount('/assets',StaticFiles(directory=ROOT/'static/assets'),name='assets')
def fail(message,status=400): raise HTTPException(status,message)
def digest(t): return hashlib.sha256(t.encode()).hexdigest()
def now():return time.time()
def session_cookie(response,request,name,token):
 secure=request.url.scheme=='https' or request.headers.get('x-forwarded-proto')=='https'
 response.set_cookie(name,token,httponly=True,samesite='none' if secure else 'lax',max_age=31536000,secure=secure)
 # CHIPS allows authenticated hosting inside a cross-site live-preview iframe.
 if secure:
  response.raw_headers=[(k,v+b'; Partitioned' if k.lower()==b'set-cookie' else v) for k,v in response.raw_headers]

def load(code):
 row=DB.execute('SELECT owner,data FROM rooms WHERE code=?',(code.upper(),)).fetchone()
 if not row:fail('Room not found. Check the room code.',404)
 r=json.loads(row[1]);r.setdefault('finalQuestion',FINAL);r.setdefault('roundHistory',[])
 if r.get('current'):r['current'].setdefault('duration',r['settings']['timer'])
 return row[0],r
def save(r,owner):
 r['revision']=r.get('revision',0)+1
 DB.execute('INSERT OR REPLACE INTO rooms VALUES(?,?,?)',(r['code'],owner,json.dumps(r)));DB.commit()
def owner(request):return digest(request.cookies.get('arch_host',''))
def host(request,code):
 o,r=load(code)
 if not request.cookies.get('arch_host') or owner(request)!=o:fail('Host access required.',403)
 return o,r
def player(request,r):return next((p for p in r['players'] if p['token']==digest(request.cookies.get('arch_player',''))),None)
def board(r):
 ids=[]
 lo,hi={'easy':(1,2),'normal':(1,5),'hard':(3,5),'expert':(4,5)}.get(r['settings']['difficulty'],(1,5))
 for cat in r['selected']:
  for difficulty in range(lo,hi+1):
   pool=[q for q in r['bank'] if q['category']==cat and q['difficulty']==difficulty and q['id'] not in ids]
   if pool:ids.append(random.choice(pool)['id'])
 r['board']=ids

def new_room(o,copy=None):
 code='ARCH-'+secrets.token_hex(3).upper()
 r=dict(code=code,name='Architecture Day 2026',department='Department of Architecture',university='',eventDate='2026-09-15',sponsors='',logo='',background='',accent='#d56143',phase='lobby',teams=[dict(id=str(i),name=n,color=c,score=0,logo='',powers=[]) for i,(n,c) in enumerate(zip(['The Designers','The Builders','The Visionaries','The Architects'],['#d56143','#4c807c','#a48bba','#c4a45b']))],players=[],selected=[c[0] for c in CATEGORIES[:6]],categories=[dict(id=c[0],name=c[1],description=c[2],image='/assets/'+c[3]+'.jpg',number=c[4]) for c in CATEGORIES],bank=questions(),used=[],current=None,finalQuestion=FINAL,roundHistory=[],activeTeam='0',settings=dict(timer=30,steal=50,doubleChance=10,difficulty='normal',powers=True,sound=True,penalty=False),revision=0,wagers={},finalResults={},startedAt=None,log=[])
 if copy:
  for k in ['name','department','university','eventDate','sponsors','logo','background','accent','categories','bank','selected','settings','teams','finalQuestion']:r[k]=json.loads(json.dumps(copy[k]))
  for t in r['teams']:t.update(score=0,powers=[])
 board(r);save(r,o);return r

def view(r,is_host=False,p=None):
 keys=['code','name','department','university','eventDate','sponsors','logo','background','accent','phase','teams','selected','categories','used','activeTeam','settings','revision','startedAt']
 v={k:r[k] for k in keys};v['serverNow']=now();v['participants']=len(r['players']);v['board']=[{k:q[k] for k in ['id','category','points','difficulty']} for q in r['bank'] if q['id'] in r['board']]
 v['leaderboard']=[{k:x[k] for k in ['id','name','team','score','streak']} for x in sorted(r['players'],key=lambda p:-p['score'])]
 v['wagersReady']=list(r['wagers']);v['finalResults']=r['finalResults'] if r['phase']=='results' or is_host else {}
 if p:v['me']={k:p[k] for k in ['id','name','team','score','streak']};v['me']['captain']=next((x['id'] for x in r['players'] if x['team']==p['team']),None)==p['id']
 c=r['current']
 if c:
  v['current']={k:c[k] for k in ['id','question','category','points','type','options','image','deadline','paused','remaining','revealed','multiplier','steal','awarded','hidden','hintShown','hintText','mode','duration']}
  v['current']['submissions']=len(c['answers']);v['current']['submitted']=bool(p and p['id'] in c['answers'])
  if c['revealed'] or is_host:
   for k in ['correctAnswer','explanation','source']:v['current'][k]=c.get(k,'')
  if c['revealed']:
   counts={option:0 for option in c['options']}
   for a in c['answers'].values():
    if a['answer'] in counts:counts[a['answer']]+=1
   v['current']['distribution']=counts
  if is_host:v['current']['answers']=c['answers']
 else:v['current']=None
 if is_host:v['finalQuestion']=r.get('finalQuestion',FINAL);v['bank']=r['bank'];v['log']=r['log'][-30:];v['wagers']=r['wagers']
 return v

@app.exception_handler(ValueError)
async def invalid_value(request,exc):return JSONResponse({'detail':'Invalid value. Check numbers and required fields.'},400)
@app.middleware('http')
async def guard(request,call_next):
 if int(request.headers.get('content-length','0') or 0)>7*1024*1024:return JSONResponse({'detail':'Request is too large.'},413)
 if request.method=='POST' or request.url.path=='/api/bootstrap':
  path=request.url.path
  identity=request.cookies.get('arch_player') or request.cookies.get('arch_host') or request.client.host
  limit=600 if path.endswith('/join') else 12 if path=='/api/recovery' else 120
  key=(identity,path);times=[t for t in RATE.get(key,[]) if now()-t<60]
  if len(times)>=limit:return JSONResponse({'detail':'Too many requests. Please wait a minute.'},429)
  if len(RATE)>10000:RATE.clear()
  RATE[key]=times+[now()]
 if request.method not in ['GET','HEAD','OPTIONS']:
  origin=request.headers.get('origin')
  if origin:
   from urllib.parse import urlparse
   allowed={request.headers.get('host',''),request.headers.get('x-forwarded-host','')}
   if urlparse(origin).netloc not in allowed:return JSONResponse({'detail':'Cross-origin request denied.'},403)
 response=await call_next(request)
 response.headers['X-Content-Type-Options']='nosniff'
 if request.url.path.startswith('/api'):response.headers['Cache-Control']='no-store'
 return response

@app.get('/api/bootstrap')
def bootstrap(request:Request):
 token=request.cookies.get('arch_host') or secrets.token_urlsafe(32);o=digest(token)
 rows=DB.execute('SELECT data FROM rooms WHERE owner=?',(o,)).fetchall()
 r=json.loads(rows[-1][0]) if rows else new_room(o)
 res=JSONResponse({'room':r['code'],'state':view(r,True)})
 session_cookie(res,request,'arch_host',token)
 return res
@app.get('/api/rooms')
def rooms(request:Request):
 return [dict(code=r['code'],name=r['name'],phase=r['phase']) for (d,) in DB.execute('SELECT data FROM rooms WHERE owner=?',(owner(request),)).fetchall() for r in [json.loads(d)]]
@app.post('/api/rooms')
async def create(request:Request):
 if not request.cookies.get('arch_host'):fail('Initialize a host session first.',403)
 d=await request.json();copy=None
 if d.get('copy'):_,copy=host(request,d['copy'])
 r=new_room(owner(request),copy)
 if d.get('name'):r['name']=str(d['name'])[:100];save(r,owner(request))
 return {'room':r['code']}
@app.get('/api/room/{code}')
def state(code:str,request:Request):
 o,r=load(code);return view(r,o==owner(request),player(request,r))
@app.get('/api/room/{code}/events')
async def events(code:str,request:Request):
 load(code)
 async def stream():
  rev=-1;heartbeat=0
  while not await request.is_disconnected():
   o,r=load(code)
   if r['revision']!=rev:
    rev=r['revision'];yield 'data: '+json.dumps(view(r,o==owner(request) and request.query_params.get('public')!='1',player(request,r)))+'\n\n'
   elif heartbeat%20==0:yield ': heartbeat\n\n'
   heartbeat+=1;await asyncio.sleep(.4)
 return StreamingResponse(stream(),media_type='text/event-stream',headers={'X-Accel-Buffering':'no','Cache-Control':'no-cache'})
@app.get('/api/room/{code}/public')
def public(code:str,request:Request):
 _,r=load(code);return view(r,False,player(request,r))
@app.get('/api/room/{code}/qr')
def qr(code:str,request:Request):
 load(code)
 base=str(request.base_url).rstrip('/')
 # Reverse proxy supplies the browser-visible host and protocol.
 if request.headers.get('x-forwarded-host'):base=request.headers.get('x-forwarded-proto','https')+'://'+request.headers['x-forwarded-host']
 image=qrcode.make(base+'/join?room='+code);b=io.BytesIO();image.save(b,format='PNG');return Response(b.getvalue(),media_type='image/png')
@app.post('/api/room/{code}/join')
async def join(code:str,request:Request):
 d=await request.json()
 with LOCK:
  o,r=load(code);p=player(request,r)
  if p:return {'ok':True}
  if len(r['players'])>=500:fail('This room has reached its 500-participant capacity.')
  if r['phase']=='results':fail('This event has ended.')
  name=str(d.get('name','')).strip()[:35];team=str(d.get('team',''))
  if not name:fail('Enter a nickname.')
  if team not in [t['id'] for t in r['teams']]:fail('Choose a team.')
  if any(p['name'].casefold()==name.casefold() for p in r['players']):fail('That nickname is already in use.')
  token=secrets.token_urlsafe(32);r['players'].append(dict(id=secrets.token_hex(8),token=digest(token),name=name,team=team,score=0,streak=0));save(r,o)
  res=JSONResponse({'ok':True});session_cookie(res,request,'arch_player',token);return res

def normalize(s):return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
def correct(q,a):
 if q['type']=='estimate':
  try:return abs(float(a)-float(q['correctAnswer']))<=float(q.get('tolerance',0))
  except:return False
 return normalize(a) in [normalize(x) for x in q['correctAnswer'].split('|')]
@app.post('/api/room/{code}/answer')
async def answer(code:str,request:Request):
 d=await request.json()
 with LOCK:
  o,r=load(code);p=player(request,r);c=r['current']
  if not p:fail('Join this room first.',403)
  if not c or r['phase']!='question' or c['revealed'] or c['paused'] or now()>c['deadline']:fail('Answers are closed.')
  if c['mode'] in ['draw','design','final']:fail('This challenge is judged by the host.')
  if p['id'] in c['answers']:fail('Your answer is already locked.')
  a=str(d.get('answer','')).strip()[:600]
  if not a:fail('Enter an answer.')
  if c['options'] and a not in c['options']:fail('Choose one of the options.')
  c['answers'][p['id']]={'answer':a,'correct':None};save(r,o);return {'ok':True}
@app.post('/api/room/{code}/wager')
async def wager(code:str,request:Request):
 d=await request.json()
 with LOCK:
  o,r=load(code);p=player(request,r);ishost=o==owner(request)
  if r['phase']!='wagers':fail('Wagers are closed.')
  if not ishost and not p:fail('Join first.',403)
  tid=str(d.get('team')) if ishost else p['team']
  if not ishost and next(x['id'] for x in r['players'] if x['team']==tid)!=p['id']:fail('Only the first player in each team can lock its wager.',403)
  t=next((t for t in r['teams'] if t['id']==tid),None)
  if not t:fail('Team not found.')
  if tid in r['wagers']:fail('This wager is already locked.')
  amount=int(d.get('amount',0))
  if not 0<=amount<=max(0,t['score']):fail('Wager must be between zero and your team score.')
  r['wagers'][tid]=amount;save(r,o);return {'ok':True}

def open_question(r,q,mode='standard'):
 duration=q.get('timeLimit',30) if mode!='standard' or q.get('customTimer') else r['settings']['timer']
 c=json.loads(json.dumps(q));c.update(deadline=now()+duration,duration=duration,paused=False,remaining=0,revealed=False,multiplier=2 if mode=='standard' and random.random()*100<r['settings']['doubleChance'] else 1,steal=False,awarded=[],answers={},hidden=[],hintShown=False,hintText='',mode=mode)
 r['current']=c;r['phase']='question'
 if mode=='standard':r['used'].append(q['id'])
def reveal(r):
 c=r['current']
 if not c:fail('No question is open.')
 if c['revealed']:return
 c['revealed']=True;c['deadline']=now()
 for p in r['players']:
  a=c['answers'].get(p['id'])
  if a:
   ok=correct(c,a['answer']);a['correct']=ok;p['streak']=p['streak']+1 if ok else 0
   if ok:p['score']+=100
 r.setdefault('roundHistory',[]).append(dict(id=c['id'],question=c['question'],answer=c['correctAnswer'],responses=json.loads(json.dumps(c['answers'])),mode=c['mode'],time=now()))

def log(r,text):r['log'].append({'time':now(),'text':text})
@app.post('/api/room/{code}/action')
async def action(code:str,request:Request):
 d=await request.json();act=d.get('action')
 with LOCK:
  o,r=host(request,code);c=r['current'];t=next((x for x in r['teams'] if x['id']==str(d.get('team',r['activeTeam']))),None)
  if act=='start':
   if r['phase'] not in ['lobby','board']:fail('Return to the board before starting.')
   r['phase']='board';r['startedAt']=r['startedAt'] or now()
  elif act=='select':
   if r['phase'] not in ['board','lobby']:fail('Finish the current question first.')
   if d.get('id') in r['used'] or d.get('id') not in r['board']:fail('This question is unavailable.')
   q=next(q for q in r['bank'] if q['id']==d['id']);open_question(r,q);r['startedAt']=r['startedAt'] or now()
  elif act=='active':
   if not t:fail('Team not found.')
   r['activeTeam']=t['id']
  elif act=='pause':
   if not c or c['revealed']:fail('No running timer.')
   if c['paused']:
    c['deadline']=now()+c['remaining'];c['paused']=False
    if c['mode']=='rapid':r['rapidEnd']=c['deadline']
   else:c['remaining']=max(0,c['deadline']-now());c['paused']=True
  elif act=='reveal':reveal(r)
  elif act=='double':
   if not c or c['revealed'] or c['awarded']:fail('Double points must be set before scoring or reveal.')
   c['multiplier']=2 if c['multiplier']==1 else 1
  elif act=='steal':
   if not c or c['revealed'] or c['awarded']:fail('Steal must be offered before reveal or an award.')
   c['steal']=True;c['deadline']=now()+r['settings']['timer'];c['paused']=False
   r['activeTeam']=r['teams'][(next(i for i,t in enumerate(r['teams']) if t['id']==r['activeTeam'])+1)%len(r['teams'])]['id']
  elif act in ['correct','wrong']:
   if not c or not t:fail('Select a question and team.')
   if c['mode']=='final':fail('Use final judging for wagers.')
   if c['awarded']:fail('This question has already been scored. Use a manual adjustment if needed.')
   value=round(c['points']*c['multiplier']*(r['settings']['steal']/100 if c['steal'] else 1))
   if act=='correct':t['score']+=value;c['awarded'].append(t['id']);reveal(r);log(r,f'{t["name"]} +{value}')
   elif c['mode']=='rapid':
    reveal(r);log(r,f'{t["name"]}: rapid answer incorrect (+0)')
   else:
    if r['settings']['penalty']:t['score']-=value
    c['steal']=True;c['deadline']=now()+r['settings']['timer'];c['paused']=False
    r['activeTeam']=r['teams'][(r['teams'].index(t)+1)%len(r['teams'])]['id'];log(r,f'{t["name"]}: incorrect; steal available')
  elif act=='adjust':
   if not t:fail('Team not found.')
   value=int(d.get('amount',0))
   if abs(value)>100000:fail('Adjustment is too large.')
   t['score']+=value;log(r,f'Manual adjustment: {t["name"]} {value:+}')
  elif act=='power':
   power=d.get('power')
   if not r['settings']['powers'] or not c or c['revealed'] or c['paused'] or not t:fail('Power-up unavailable.')
   if power not in ['blueprint','support','analysis','consult']:fail('Unknown power-up.')
   if power in t['powers']:fail('This team has already used this power-up.')
   if power=='blueprint':
    if len(c['options'])<4:fail('Blueprint requires at least four answer options.')
    c['hidden']=random.sample([x for x in c['options'] if x!=c['correctAnswer']],2)
   elif power in ['support','consult']:c['deadline']=max(now(),c['deadline'])+(10 if power=='support' else 15)
   else:c['hintShown']=True;c['hintText']=c.get('hint') or 'Consider the category and the defining characteristics.'
   if c['mode']=='rapid':r['rapidEnd']=c['deadline']
   t['powers'].append(power)
  elif act=='board':
   r['phase']='board';r['current']=None
  elif act=='random':
   if r['phase'] not in ['board','lobby']:fail('Return to the board first.')
   board(r)
  elif act in ['draw','design','rapid']:
   if r['phase'] not in ['board','lobby']:fail('Return to the board first.')
   if act=='rapid':
    q=next((q for q in r['bank'] if q['category']=='speed' and q['id'] not in r['used']),None)
    if not q:fail('All rapid questions have been used. Add more in the library.')
    q=dict(q,timeLimit=60,points=100);open_question(r,q,'rapid');r['used'].append(q['id']);r['rapidEnd']=now()+60
   else:
    q=dict(id=act,question='Sketch a courtyard house with a wind tower. Label the airflow.' if act=='draw' else 'Design a shelter for the UAE desert. Present your concept in two minutes.',category='drawing',points=500,type='drawing',options=[],image='/assets/plan.svg' if act=='draw' else '',correctAnswer='Host judged: spatial clarity and communication.' if act=='draw' else 'Host judged: creativity, function, sustainability, aesthetics, presentation (0–100 each).',explanation='Use manual score adjustments to award each team.',timeLimit=60 if act=='draw' else 120)
    open_question(r,q,act)
  elif act=='rapidNext':
   if not c or c['mode']!='rapid':fail('Start a rapid round first.')
   if now()>=r.get('rapidEnd',0):fail('Rapid round is over. Return to the board.')
   q=next((q for q in r['bank'] if q['category']=='speed' and q['id'] not in r['used']),None)
   if not q:fail('Rapid question bank exhausted. Return to the board.')
   open_question(r,dict(q,points=100),'rapid');r['current']['deadline']=r['rapidEnd'];r['used'].append(q['id'])
  elif act=='final':r['phase']='wagers';r['current']=None;r['wagers']={};r['finalResults']={}
  elif act=='finalStart':
   if r['phase']!='wagers' or len(r['wagers'])!=len(r['teams']):fail('Lock a wager for every team first.')
   open_question(r,r.get('finalQuestion',FINAL),'final')
  elif act=='finalJudge':
   if not c or c['mode']!='final' or not c['revealed'] or not t:fail('Reveal the final answer before judging.')
   if t['id'] in r['finalResults']:fail('This team has already been judged.')
   value=r['wagers'][t['id']]*(1 if d.get('correct') else -1);t['score']+=value;r['finalResults'][t['id']]=value;log(r,f'Final: {t["name"]} {value:+}')
  elif act=='end':
   if r['phase']=='results':fail('This game is already saved.')
   if c and c['mode']=='final' and len(r['finalResults'])!=len(r['teams']):fail('Judge every final wager before ending.')
   r['phase']='results';r['current']=None
   result=dict(id=secrets.token_hex(8),name=r['name'],date=now(),teams=r['teams'],participants=len(r['players']),leaderboard=view(r)['leaderboard'],questions=len(r['used']),rounds=r.get('roundHistory',[]),log=r['log'],code=r['code'])
   DB.execute('INSERT INTO history VALUES(?,?,?)',(result['id'],o,json.dumps(result)))
  elif act=='reset':
   for team in r['teams']:team.update(score=0,powers=[])
   r.update(players=[],used=[],phase='lobby',current=None,wagers={},finalResults={},startedAt=None,log=[],roundHistory=[]);board(r)
  else:fail('Unknown action.')
  save(r,o);return view(r,True)

@app.post('/api/room/{code}/settings')
async def settings(code:str,request:Request):
 d=await request.json()
 with LOCK:
  o,r=host(request,code)
  if r['phase'] not in ['lobby','board']:fail('Return to the board before editing settings.')
  for k in ['name','department','university','eventDate','sponsors','logo','background','accent']:
   if k in d:r[k]=str(d[k])[:500]
  if 'settings' in d:
   s=d['settings']
   for k in ['timer','steal','doubleChance']:
    if k in s:r['settings'][k]=max(0 if k!='timer' else 10,min(120 if k=='timer' else 100,int(s[k])))
   for k in ['powers','sound','penalty']:
    if k in s:r['settings'][k]=bool(s[k])
   if s.get('difficulty') in ['easy','normal','hard','expert']:r['settings']['difficulty']=s['difficulty']
  if 'selected' in d:
   selected=list(dict.fromkeys(d['selected']))
   if not 1<=len(selected)<=6 or any(c not in [x['id'] for x in r['categories']] for c in selected):fail('Choose between one and six categories.')
   r['selected']=selected
  board(r);save(r,o);return view(r,True)
@app.post('/api/room/{code}/teams')
async def teams(code:str,request:Request):
 d=await request.json()
 with LOCK:
  o,r=host(request,code)
  if r['phase'] not in ['lobby','board']:fail('Return to the board first.')
  tid=str(d.get('id',''));t=next((t for t in r['teams'] if t['id']==tid),None)
  if d.get('delete'):
   if len(r['teams'])<=1:fail('Keep at least one team.')
   if any(p['team']==tid for p in r['players']):fail('Cannot delete a team with participants.')
   r['teams']=[x for x in r['teams'] if x['id']!=tid];r['activeTeam']=r['teams'][0]['id']
  else:
   name=str(d.get('name','')).strip()[:40]
   if not name:fail('Team name is required.')
   if not t:
    if len(r['teams'])>=8:fail('Maximum eight teams.')
    t=dict(id=secrets.token_hex(4),score=0,powers=[],logo='');r['teams'].append(t)
   t.update(name=name,color=d.get('color','#d56143') if re.fullmatch('#[0-9A-Fa-f]{6}',d.get('color','')) else '#d56143',logo=str(d.get('logo',''))[:200])
  save(r,o);return view(r,True)
@app.post('/api/room/{code}/category')
async def category(code:str,request:Request):
 d=await request.json();o,r=host(request,code)
 name=str(d.get('name','')).strip()[:60]
 if not name:fail('Category name required.')
 c=next((c for c in r['categories'] if c['id']==d.get('id')),None)
 if not c:c=dict(id=secrets.token_hex(4),number=str(len(r['categories'])+1),image='/assets/world.jpg',description='Your event. Your questions.');r['categories'].append(c)
 c['name']=name;save(r,o);return view(r,True)
@app.post('/api/room/{code}/question')
async def question(code:str,request:Request):
 d=await request.json()
 with LOCK:
  o,r=host(request,code)
  if r['current']:fail('Close the current question before editing the library.')
  if d.get('delete'):
   r['bank']=[q for q in r['bank'] if q['id']!=d['id']]
  else:
   q=d.get('question',{})
   if not isinstance(q,dict):fail('Question must be an object.')
   for field in ['question','correctAnswer','explanation','source','hint','image']:
    if field in q and (not isinstance(q[field],str) or len(q[field])>5000):fail('Question text fields must be strings under 5000 characters.')
   if not isinstance(q.get('options',[]),list) or len(q.get('options',[]))>8 or any(not isinstance(x,str) or len(x)>500 for x in q.get('options',[])):fail('Provide at most eight text options.')
   if q.get('image') and not re.fullmatch(r'/assets/[A-Za-z0-9._-]+',q['image']):fail('Use an uploaded image.')
   if not q.get('question') or not q.get('correctAnswer'):fail('Question and answer are required.')
   if q.get('category') not in [c['id'] for c in r['categories']]:fail('Choose a valid category.')
   q['difficulty']=max(1,min(5,int(q.get('difficulty',1))));q['points']=max(0,min(10000,int(q.get('points',100))));q['timeLimit']=max(10,min(300,int(q.get('timeLimit',30))))
   if q.get('type') in ['choice','truefalse'] and (len(q.get('options',[]))<2 or q['correctAnswer'] not in q['options']):fail('Choice questions need at least two options, including the exact correct answer.')
   q['id']=q.get('id') or secrets.token_hex(8)
   for k in ['explanation','image','source','hint']:q.setdefault(k,'')
   q.setdefault('options',[]);q.setdefault('tolerance',0);q['customTimer']=True
   if not q.get('type'):q['type']='open'
   if q['id']=='final-1':r['finalQuestion']=q
   else:r['bank']=[x for x in r['bank'] if x['id']!=q['id']]+[q]
  board(r);save(r,o);return view(r,True)
@app.post('/api/room/{code}/upload')
async def upload(code:str,request:Request,file:UploadFile=File(...)):
 host(request,code);b=await file.read(6*1024*1024)
 if len(b)>5*1024*1024:fail('Maximum image size is 5 MB.')
 try:
  image=Image.open(io.BytesIO(b))
  if image.width*image.height>20000000:fail('Image resolution exceeds 20 megapixels.')
  image.thumbnail((2000,2000));image=image.convert('RGB')
 except:fail('Upload a valid PNG, JPEG, or WebP image.')
 name='upload-'+secrets.token_hex(12)+'.jpg';image.save(ROOT/'static/assets'/name,quality=88);return {'url':'/assets/'+name}
@app.get('/api/history')
def history(request:Request):return [json.loads(d) for (d,) in DB.execute('SELECT data FROM history WHERE owner=? ORDER BY rowid DESC',(owner(request),)).fetchall()]
@app.get('/api/room/{code}/export')
def export(code:str,request:Request):
 _,r=host(request,code);return JSONResponse(r['bank'],headers={'Content-Disposition':'attachment; filename="architecture-questions.json"'})
@app.get('/api/recovery')
def recovery(request:Request):
 if not request.cookies.get('arch_host'):fail('No host session.',403)
 return {'key':request.cookies['arch_host']}
@app.post('/api/recovery')
async def recover(request:Request):
 d=await request.json();token=str(d.get('key',''))
 if not DB.execute('SELECT 1 FROM rooms WHERE owner=?',(digest(token),)).fetchone():fail('Invalid recovery key.',403)
 res=JSONResponse({'ok':True});session_cookie(res,request,'arch_host',token);return res
@app.get('/health')
def health():
 DB.execute('SELECT 1').fetchone()
 return {'status':'ok'}

@app.get('/app.js')
def js():return FileResponse(ROOT/'static/app.js')
@app.get('/style.css')
def css():return FileResponse(ROOT/'static/style.css')
@app.get('/{path:path}')
def index(path:str):return FileResponse(ROOT/'static/index.html')
