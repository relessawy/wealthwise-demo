"""Live OIDC and authorization acceptance. Credentials enter via stdin only.
Adapted from Demo-Library capabilities/lib/portal_login.py; provisioning is Ansible.
"""
import json,sys,time
from html.parser import HTMLParser
from urllib.parse import urlsplit
import requests
class Form(HTMLParser):
 def __init__(self):super().__init__();self.action=None
 def handle_starttag(self,tag,attrs):
  if tag=='form':self.action=dict(attrs).get('action')
def require(response,code=200):
 if response.status_code!=code:raise RuntimeError('Unexpected HTTP status '+str(response.status_code))
 return response

def login(url,issuer,name,password):
 s=requests.Session()
 def req(method,target,**kwargs):return s.request(method,target,timeout=(10,30),allow_redirects=False,**kwargs)
 r=req('GET',url+'/api/auth/oidc/start',params={'env':'production','origin':url,'scope':'openid profile email','flow':'popup'})
 target=r.headers.get('Location','')
 assert r.status_code in (302,303) and urlsplit(target)[:2]==urlsplit(issuer)[:2], 'Unexpected identity redirect'
 f=Form();f.feed(require(req('GET',target)).text)
 assert f.action and urlsplit(f.action)[:2]==urlsplit(issuer)[:2], 'Unexpected login destination'
 r=req('POST',f.action,data={'username':name,'password':password,'credentialId':''})
 target=r.headers.get('Location','')
 assert r.status_code in (302,303) and target.split('?',1)[0]==url+'/api/auth/oidc/handler/frame', 'Login rejected'
 require(req('GET',target))
 r=require(req('GET',url+'/api/auth/oidc/refresh',params={'env':'production'},headers={'X-Requested-With':'XMLHttpRequest','Origin':url}))
 token=r.json()['backstageIdentity']['token'];headers={'Authorization':'Bearer '+token}
 identity=require(req('GET',url+'/api/auth/v1/userinfo',headers=headers)).json();identity=identity.get('claims',identity)
 assert identity.get('userEntityRef',identity.get('sub'))=='user:default/'+name,'Wrong identity'
 return s,headers

def main():
 c=json.load(sys.stdin);url=c['url'];issuer=c['issuer'];out={}
 permissions=[{'id':'create','permission':{'type':'basic','name':'scaffolder.task.create','attributes':{'action':'create'}}},{'id':'delete','permission':{'type':'resource','name':'catalog.entity.delete','attributes':{'action':'delete'},'resourceType':'catalog-entity'},'resourceRef':'component:default/platform-readiness'}]
 for name,password in c['passwords'].items():
  s,h=login(url,issuer,name,password)
  entity=require(s.get(url+'/api/catalog/entities/by-name/user/default/'+name,headers=h,timeout=30)).json()
  assert c['groups'][name] in entity['spec']['memberOf'] or 'group:default/'+c['groups'][name] in entity['spec']['memberOf'], 'Unexpected group'
  response=require(s.post(url+'/api/permission/authorize',headers=h,json={'items':permissions},timeout=30)).json()
  decisions={x['id']:x['result'] for x in response['items']}
  assert decisions=={'create':'ALLOW','delete':'ALLOW' if name=='carol' else 'DENY'},'Permission mismatch'
  task=require(s.post(url+'/api/scaffolder/v2/tasks',headers=h,json={'templateRef':'template:default/portal-access-check','values':{}},timeout=30),201).json()['id']
  for attempt in range(30):
   status=require(s.get(url+'/api/scaffolder/v2/tasks/'+task,headers=h,timeout=30)).json()['status']
   if status in ('completed','failed','cancelled'):break
   time.sleep(2)
  assert status=='completed','Template execution did not complete'
  out[name]={'group':c['groups'][name],'permissions':decisions,'task_id':task,'task_status':status}
 assert requests.get(url+'/api/auth/guest/refresh',headers={'X-Requested-With':'XMLHttpRequest'},timeout=30).status_code in (400,401,403,404),'Guest enabled'
 print(json.dumps({'status':'VERIFIED','personas':out,'guest':'DENIED'}))
if __name__=='__main__':
 try:main()
 except Exception as exc:
  print('Portal identity acceptance failed: '+type(exc).__name__,file=sys.stderr);sys.exit(1)
