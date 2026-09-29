"""Transfer temporary identity inputs; provisioning remains in Ansible.
Administrative credentials are stdin-only and removed from the runner after execution.
"""
import base64, json, os, subprocess

def configure(oc, namespace, remote):
    identity_ns=os.environ.get('IDENTITY_NAMESPACE','')
    identity_name=os.environ.get('IDENTITY_NAME','')
    realm=os.environ.get('IDENTITY_REALM','')
    if not all((identity_ns,identity_name,realm)):
        raise SystemExit('Set IDENTITY_NAMESPACE, IDENTITY_NAME and IDENTITY_REALM for the existing identity service')
    def read(kind,name,ns):
        return json.loads(subprocess.check_output([oc,'get',kind,name,'-n',ns,'-o','json']))
    secret=read('secret',identity_name+'-bootstrap',identity_ns)
    if secret['metadata'].get('labels',{}).get('demo-library.io/owner')!='identity-foundation':
        raise SystemExit('Refusing unrelated identity bootstrap credential')
    host=read('route',identity_name,identity_ns)['spec']['host']
    domain=json.loads(subprocess.check_output([oc,'get','ingress.config.openshift.io','cluster','-o','json']))['spec']['domain']
    values={'workload_namespace':namespace,'identity_url':'https://'+host,'identity_realm':realm,
            'application_url':'https://wealthwise-'+namespace+'.'+domain,'client_id':'wealthwise-'+namespace,
            'bootstrap_client_id':base64.b64decode(secret['data']['client-id']).decode(),
            'bootstrap_client_secret':base64.b64decode(secret['data']['client-secret']).decode()}
    script='umask 077; f=$(mktemp /work/identity.XXXXXX); trap \'rm -f "$f"\' EXIT HUP INT TERM; cat > "$f"; cd "$1/deploy"; ansible-playbook identity.yml -e @"$f"'
    subprocess.run([oc,'exec','-i','-n',namespace,'wealthwise-tools','-c','runner','--','sh','-c',script,'sh',remote],input=json.dumps(values).encode(),check=True)
