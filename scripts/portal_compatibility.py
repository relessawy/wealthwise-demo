#!/usr/bin/env python3
"""One-time compatibility for an existing owned 1.10.4 portal; uses platform SA."""
import json,os,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
OC=os.environ.get('OC','oc');NS=os.environ['PLATFORM_RUNNER_NAMESPACE'];IMAGE=os.environ['RUNNER_IMAGE'];POD='wealthwise-catalog-compat'
def oc(*a,data=None):return subprocess.check_output([OC,*a],input=data)
def main():
    assert '@sha256:' in IMAGE,'Use an immutable qualified runner image'
    previous=json.loads(oc('get','pod',POD,'-n',NS,'--ignore-not-found','-o','json') or b'{}')
    assert not previous or previous['metadata'].get('labels',{}).get('demo-library.io/owner')=='wealthwise-demo','Foreign compatibility pod'
    if previous and previous.get('status',{}).get('phase') in ('Failed','Succeeded'):
        oc('delete','pod',POD,'-n',NS,'--wait=true');previous={}
    if not previous:
        pod={'apiVersion':'v1','kind':'Pod','metadata':{'name':POD,'namespace':NS,'labels':{'demo-library.io/owner':'wealthwise-demo'}},'spec':{'serviceAccountName':'automation-runner','restartPolicy':'Never','securityContext':{'runAsNonRoot':True,'seccompProfile':{'type':'RuntimeDefault'}},'containers':[{'name':'runner','image':IMAGE,'command':['sleep','1800'],'env':[{'name':'HOME','value':'/tmp'},{'name':'KUBECONFIG','value':'/tmp/not-a-kubeconfig'},{'name':'ANSIBLE_LOCAL_TEMP','value':'/tmp/ansible-local'},{'name':'ANSIBLE_REMOTE_TEMP','value':'/tmp/ansible-remote'}],'resources':{'requests':{'cpu':'100m','memory':'128Mi'},'limits':{'cpu':'1','memory':'512Mi'}},'securityContext':{'allowPrivilegeEscalation':False,'capabilities':{'drop':['ALL']}}}]}}
        oc('create','-f','-',data=json.dumps(pod).encode())
    oc('wait','-n',NS,'pod/'+POD,'--for=condition=Ready','--timeout=180s')
    base=[OC,'exec','-n',NS,POD,'--']
    subprocess.run(base+['mkdir','-p','/tmp/portal-catalog'],check=True)
    for src,dest in [('enable-resources.yml','playbook.yml'),('chart.tgz','chart.tgz')]:
        oc('exec','-i','-n',NS,POD,'--','sh','-c','cat > "$1"','sh','/tmp/portal-catalog/'+dest,data=(ROOT/'deploy/portal-compatibility'/src).read_bytes())
    subprocess.run(base+['env','ANSIBLE_LOCAL_TEMP=/tmp/ansible-local','ANSIBLE_REMOTE_TEMP=/tmp/ansible-remote','ansible-playbook','/tmp/portal-catalog/playbook.yml','-e',json.dumps({'portal_namespace':os.environ['PORTAL_NAMESPACE'],'portal_name':os.environ['PORTAL_NAME']})],check=True)
    oc('delete','pod',POD,'-n',NS,'--wait=true')
if __name__=='__main__':main()
