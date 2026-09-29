#!/usr/bin/env python3
"""Register and verify only this generated catalog location via the portal API."""
import base64,importlib.util,json,os,pathlib,subprocess,time,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('portal_identity',ROOT/'deploy/vendor/verification/portal_identity.py')
identity=importlib.util.module_from_spec(spec);spec.loader.exec_module(identity)
OC=os.environ.get('OC','oc')
def get(kind,name,ns):return json.loads(subprocess.check_output([OC,'get',kind,name,'-n',ns,'-o','json']))
def main():
    if '--stdin' in sys.argv:
        c=json.load(sys.stdin);url=c['portal_url'];issuer=c['issuer'];s={'data':c['personas']};workspace=c['workspace']
    else:
        pns=os.environ['PORTAL_NAMESPACE'];pname=os.environ['PORTAL_NAME'];ins=os.environ['IDENTITY_NAMESPACE'];iname=os.environ['IDENTITY_NAME'];realm=os.environ['IDENTITY_REALM']
        url='https://'+get('route',pname,pns)['spec']['host']
        issuer='https://'+get('route',iname,ins)['spec']['host']+'/realms/'+realm
        s=get('secret',iname+'-personas',ins)
        assert s['metadata'].get('labels',{}).get('demo-library.io/owner')=='identity-foundation','Foreign identity inputs'
        bb=get('secret',pname+'-bitbucket',pns)['data'];workspace=base64.b64decode(bb['workspace']).decode()
    session,headers=identity.login(url,issuer,'carol',base64.b64decode(s['data']['carol']).decode())
    target='https://bitbucket.org/'+workspace+'/wealthwise-demo-catalog/src/main/catalog-info.yaml'
    r=session.get(url+'/api/catalog/locations',headers=headers,timeout=30);r.raise_for_status()
    found=[x for x in r.json() if x.get('data',x).get('target')==target]
    if not found:
        r=session.post(url+'/api/catalog/locations',headers=headers,json={'type':'url','target':target},timeout=60)
        assert r.status_code==201,'Catalog registration failed with status '+str(r.status_code)
    expected=[('system','wealthwise'),('component','wealthwise'),('component','wealthwise-financial-advisor'),('component','wealthwise-investment-advisor'),('component','wealthwise-history'),('resource','wealthwise-postgresql'),('api','wealthwise-api')]
    verified=[]
    for kind,name in expected:
        for _ in range(20):
            r=session.get(url+'/api/catalog/entities/by-name/'+kind+'/default/'+name,headers=headers,timeout=30)
            if r.status_code==200:break
            time.sleep(3)
        assert r.status_code==200,'Entity pending: '+name
        e=r.json();assert not e.get('status',{}).get('items'), 'Catalog processing issue: '+name
        if kind=='api':
            definition=json.loads(e['spec']['definition'])
            assert '/api/history' in definition['paths'] and definition['components']['securitySchemes']['oidc']['scheme']=='bearer','Unexpected API contract'
        if name=='wealthwise' and kind=='component':assert 'wealthwise-api' in e['spec']['providesApis'] or 'api:default/wealthwise-api' in e['spec']['providesApis']
        verified.append(kind+':default/'+name)
    # Independently prove a developer can see the registered application and API.
    alice,ah=identity.login(url,issuer,'alice',base64.b64decode(s['data']['alice']).decode())
    for kind,name in [('component','wealthwise'),('api','wealthwise-api')]:
        r=alice.get(url+'/api/catalog/entities/by-name/'+kind+'/default/'+name,headers=ah,timeout=30)
        assert r.status_code==200,'Developer cannot view '+name
    out=ROOT/'.private/acceptance';out.mkdir(parents=True,exist_ok=True)
    (out/'catalog.json').write_text(json.dumps({'status':'VERIFIED','entities':verified,'alice_access':'VERIFIED','location':target,'portal':url+'/catalog/default/component/wealthwise'},indent=2))
    print('Catalog accepted:',len(verified),'entities; Alice can read application/API')
    print('Portal:',url+'/catalog/default/component/wealthwise')
if __name__=='__main__':
    try:main()
    except Exception as exc:
        print('Catalog acceptance failed:',str(exc) if isinstance(exc,AssertionError) else type(exc).__name__);raise SystemExit(1)
