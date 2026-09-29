#!/usr/bin/env python3
"""Launch versioned Ansible catalog publication with stdin-only credentials."""
import base64,json,os,pathlib,subprocess,tarfile,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
OC=os.environ.get('OC','oc');NS=os.environ.get('WEALTHWISE_NAMESPACE','wealthwise-demo')
def get(kind,name,ns):return json.loads(subprocess.check_output([OC,'get',kind,name,'-n',ns,'-o','json']))
def main():
    pns=os.environ['PORTAL_NAMESPACE'];pname=os.environ['PORTAL_NAME']
    s=get('secret',pname+'-bitbucket',pns)
    assert s['metadata'].get('labels',{}).get('demo-library.io/owner')=='developer-hub-foundation','Unrecognized integration ownership'
    d={k:base64.b64decode(v).decode() for k,v in s['data'].items()}
    values={'workspace':d['workspace'],'email':d['email'],'api_token':d['api-token'],
        'seed_repository':d['template-url'].split('/')[4],
        'application_url':'https://'+get('route','wealthwise',NS)['spec']['host']}
    remote='/work/catalog-onboarding'
    subprocess.run([OC,'exec','-n',NS,'wealthwise-tools','-c','runner','--','mkdir','-p',remote],check=True)
    with tempfile.TemporaryDirectory() as t:
        path=pathlib.Path(t)/'catalog.tar'
        with tarfile.open(path,'w') as tar:
            for name in ('deploy/catalog.yml','catalog/catalog.yaml.j2'):tar.add(ROOT/name,arcname=name)
        with path.open('rb') as f:subprocess.run([OC,'exec','-i','-n',NS,'wealthwise-tools','-c','runner','--','tar','xf','-','-C',remote],stdin=f,check=True)
    command='umask 077; f=$(mktemp /work/catalog.XXXXXX); trap \'rm -f "$f"\' EXIT HUP INT TERM; cat > "$f"; ansible-playbook "$1/deploy/catalog.yml" -e @"$f"'
    subprocess.run([OC,'exec','-i','-n',NS,'wealthwise-tools','-c','runner','--','sh','-c',command,'sh',remote],input=json.dumps(values).encode(),check=True)
    print('Catalog URL: https://bitbucket.org/'+d['workspace']+'/wealthwise-demo-catalog/src/main/catalog-info.yaml')
if __name__=='__main__':main()
