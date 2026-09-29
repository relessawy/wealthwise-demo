#!/usr/bin/env python3
"""Live OIDC protocol and application acceptance; never logs passwords or tokens.
Uses the normal authorization-code login flow with PKCE, not password grants.
"""
import base64, json, os, pathlib, subprocess, time, uuid, sys
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit
import requests
ROOT=pathlib.Path(__file__).resolve().parents[1]
OC=os.environ.get('OC','oc'); NS=os.environ.get('WEALTHWISE_NAMESPACE','wealthwise-demo')
class Form(HTMLParser):
    def __init__(self): super().__init__(); self.action=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='form' and a.get('id')=='kc-form-login': self.action=a.get('action')
def get(kind,name,namespace):
    return json.loads(subprocess.check_output([OC,'get',kind,name,'-n',namespace,'-o','json']))
def login(url,issuer,username,password):
    s=requests.Session()
    r=s.get(url+'/api/session',timeout=30,allow_redirects=False)
    target=r.headers.get('Location','')
    assert r.status_code==302 and urlsplit(target)[:2]==urlsplit(issuer)[:2], 'Unexpected OIDC challenge'
    assert 'code_challenge=' in target and 'code_challenge_method=S256' in target, 'PKCE missing'
    r=s.get(target,timeout=30,allow_redirects=False)
    form=Form();form.feed(r.text)
    assert r.status_code==200 and form.action and urlsplit(form.action)[:2]==urlsplit(issuer)[:2], 'Unexpected credential destination'
    r=s.post(form.action,data={'username':username,'password':password,'credentialId':''},timeout=30,allow_redirects=False)
    target=r.headers.get('Location','')
    assert r.status_code in (302,303) and target.split('?',1)[0]==url+'/oidc/callback', 'Identity login rejected'
    for _ in range(5):
        assert urlsplit(target)[:2]==urlsplit(url)[:2], 'Unexpected callback destination'
        r=s.get(target,timeout=30,allow_redirects=False)
        if r.status_code==200: break
        assert r.status_code in (302,303), 'Callback failed'
        target=urljoin(url,r.headers['Location'])
    assert r.status_code==200,'Code flow not completed'
    return s

def main():
    checks=[]
    def check(name,ok):
        if not ok: raise RuntimeError(name)
        checks.append(name);print('PASS:',name)
    if '--stdin' in sys.argv:
        config=json.load(sys.stdin);url=config['url'];issuer=config['issuer'];personas=config['personas']
    else:
        url='https://'+get('route','wealthwise',NS)['spec']['host']
        oidc=get('secret','wealthwise-oidc',NS)['data'];issuer=base64.b64decode(oidc['issuer']).decode()
        identity_ns=os.environ.get('IDENTITY_NAMESPACE',''); identity_name=os.environ.get('IDENTITY_NAME','')
        if not identity_ns or not identity_name: raise RuntimeError('Set IDENTITY_NAMESPACE and IDENTITY_NAME for persona acceptance')
        personas=get('secret',identity_name+'-personas',identity_ns)['data']
    anon=requests.get(url+'/api/history',headers={'X-Requested-With':'XMLHttpRequest'},timeout=30,allow_redirects=False)
    check('anonymous API denied',anon.status_code in (401,499))
    forged=requests.get(url+'/api/history',headers={'Authorization':'Bearer invalid'},timeout=30,allow_redirects=False)
    check('forged bearer denied',forged.status_code==401)
    alice=login(url,issuer,'alice',base64.b64decode(personas['alice']).decode())
    bob=login(url,issuer,'bob',base64.b64decode(personas['bob']).decode())
    check('Alice authorization code with PKCE',alice.get(url+'/api/me',timeout=30).json()['username']=='alice')
    check('Bob authorization code with PKCE',bob.get(url+'/api/me',timeout=30).json()['username']=='bob')
    check('distinct verified subjects',alice.get(url+'/api/me',timeout=30).json()['identity']!=bob.get(url+'/api/me',timeout=30).json()['identity'])
    def post(s,path,body):return s.post(url+path,json=body,headers={'X-Requested-With':'XMLHttpRequest'},timeout=30,allow_redirects=False)
    rid=str(uuid.uuid4());body={'message':'How can I plan my household budget?','requestId':rid}
    r=post(alice,'/api/financial/chat',body)
    check('scripted financial answer',r.status_code==200 and r.json()['mode']=='demonstration')
    check('idempotent retry',post(alice,'/api/financial/chat',body).status_code==200)
    check('conflicting retry denied',post(alice,'/api/financial/chat',{'message':'different','requestId':rid}).status_code==409)
    a=alice.get(url+'/api/history',timeout=30).json()['message']
    b=bob.get(url+'/api/history',timeout=30).json()['message']
    check('one Alice history row',sum(x['requestId']==rid for x in a)==1)
    check('Bob cannot read Alice history',all(x['requestId']!=rid for x in b))
    check('same request ID permitted for another user',post(bob,'/api/financial/chat',{'message':'Bob budget','requestId':rid}).status_code==200)
    b=bob.get(url+'/api/history',headers={'X-Demo-User':alice.get(url+'/api/me',timeout=30).json()['identity']},timeout=30).json()['message']
    check('spoofed owner ignored',any(x['requestId']==rid and x['question']=='Bob budget' for x in b) and all(x['question']!='How can I plan my household budget?' for x in b if x['requestId']==rid))
    for risk in ('Conservative','Balanced','Aggressive'):
        r=post(alice,'/api/investment/chat',{'message':risk,'requestId':str(uuid.uuid4())})
        check('investment '+risk,r.status_code==200 and 'Demonstration' in r.json()['message'])
    check('invalid investment denied',post(alice,'/api/investment/chat',{'message':'INVALID','requestId':str(uuid.uuid4())}).status_code==400)
    check('empty question denied',post(alice,'/api/financial/chat',{'message':'','requestId':str(uuid.uuid4())}).status_code==400)
    check('invalid pagination denied',alice.get(url+'/api/history?limit=1000',timeout=30).status_code==400)
    cookie=next((c for c in alice.cookies if c.name.startswith('q_session')),None)
    check('secure HttpOnly session cookie',cookie is not None and cookie.secure and 'httponly' in {k.lower() for k in cookie._rest})
    spec=requests.get(url+'/q/openapi?format=json',timeout=30).json()
    check('OpenAPI documents bearer authentication',spec['components']['securitySchemes']['oidc']['scheme']=='bearer')
    r=alice.get(url+'/logout',timeout=30,allow_redirects=False)
    target=r.headers.get('Location','')
    check('logout delegates to correct identity provider',r.status_code==302 and urlsplit(target)[:2]==urlsplit(issuer)[:2] and '/logout' in urlsplit(target).path)
    r=alice.get(target,timeout=30,allow_redirects=False)
    check('provider ends session',r.status_code in (200,302,303))
    r=alice.get(url+'/api/history',headers={'X-Requested-With':'XMLHttpRequest'},timeout=30,allow_redirects=False)
    check('logged out session cannot read history',r.status_code in (401,499))
    out=ROOT/'.private/acceptance';out.mkdir(parents=True,exist_ok=True)
    (out/'oidc.json').write_text(json.dumps({'status':'VERIFIED','checked_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'checks':checks,'namespace':NS,'persistence_request_id':rid},indent=2))
    print('OIDC acceptance evidence:',out/'oidc.json')
if __name__=='__main__':
    try: main()
    except Exception as exc:
        # Avoid printing response bodies, cookies or URLs containing authorization codes.
        print('OIDC acceptance failed:',str(exc) if isinstance(exc,(AssertionError,RuntimeError)) else type(exc).__name__)
        raise SystemExit(1)
