#!/usr/bin/env python3
"""Run HTTP checks in the automation pod; local Python uses only its standard library."""
import base64,json,os,pathlib,subprocess,sys,tarfile,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1];OC=os.environ.get('OC','oc');NS=os.environ.get('WEALTHWISE_NAMESPACE','wealthwise-demo')
def read(kind,name,ns):return json.loads(subprocess.check_output([OC,'get',kind,name,'-n',ns,'-o','json']))
def main():
    mode=sys.argv[1] if len(sys.argv)>1 else 'app'
    assert mode in ('app','catalog')
    ins=os.environ['IDENTITY_NAMESPACE'];iname=os.environ['IDENTITY_NAME'];realm=os.environ['IDENTITY_REALM']
    users=read('secret',iname+'-personas',ins)
    assert users['metadata'].get('labels',{}).get('demo-library.io/owner')=='identity-foundation','Foreign identity inputs'
    c={'issuer':'https://'+read('route',iname,ins)['spec']['host']+'/realms/'+realm,
       'personas':{k:users['data'][k] for k in (('alice','bob') if mode=='app' else ('alice','carol'))},
       'url':'https://'+read('route','wealthwise',NS)['spec']['host']}
    if mode=='catalog':
        c['catalog_repository']=os.environ.get('WEALTHWISE_CATALOG_REPOSITORY','wealthwise-demo-catalog')
        pns=os.environ['PORTAL_NAMESPACE'];pname=os.environ['PORTAL_NAME']
        c['portal_url']='https://'+read('route',pname,pns)['spec']['host']
        c['workspace']=base64.b64decode(read('secret',pname+'-bitbucket',pns)['data']['workspace']).decode()
    remote='/work/wealthwise-verification'
    prefix=[OC,'exec','-n',NS,'wealthwise-tools','-c','runner','--']
    subprocess.run(prefix+['mkdir','-p',remote],check=True)
    with tempfile.TemporaryDirectory() as tmp:
        archive=pathlib.Path(tmp)/'checks.tar'
        with tarfile.open(archive,'w') as tar:
            for name in ('scripts/acceptance.py','scripts/register_catalog.py','deploy/vendor/verification/portal_identity.py'):tar.add(ROOT/name,arcname=name)
        with archive.open('rb') as f:subprocess.run([OC,'exec','-i','-n',NS,'wealthwise-tools','-c','runner','--','tar','xf','-','-C',remote],stdin=f,check=True)
    script='acceptance.py' if mode=='app' else 'register_catalog.py'
    subprocess.run([OC,'exec','-i','-n',NS,'wealthwise-tools','-c','runner','--','env','WEALTHWISE_NAMESPACE='+NS,'python3',remote+'/scripts/'+script,'--stdin'],input=json.dumps(c).encode(),check=True)
    filename='oidc.json' if mode=='app' else 'catalog.json'
    raw=subprocess.check_output(prefix+['cat',remote+'/.private/acceptance/'+filename])
    target=ROOT/'.private/acceptance';target.mkdir(parents=True,exist_ok=True);os.chmod(ROOT/'.private',0o700)
    (target/filename).write_bytes(raw)
    print('Evidence:',target/filename)
if __name__=='__main__':main()
