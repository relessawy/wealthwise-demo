#!/usr/bin/env python3
"""Thin OpenShift transport/build launcher; deployment logic lives in Ansible/Helm."""
import json, os, pathlib, subprocess, tarfile, tempfile, time, sys
from transport import source_paths
from identity import configure
ROOT=pathlib.Path(__file__).resolve().parents[1]
OC=os.environ.get("OC","oc"); NS=os.environ.get("WEALTHWISE_NAMESPACE","wealthwise-demo")
OWNER="wealthwise-demo"; POD="wealthwise-tools"
import re
if not re.fullmatch(r"[a-z][a-z0-9-]{1,50}",NS): raise SystemExit("Invalid namespace")
RUNNER=os.environ.get("RUNNER_IMAGE","")
if "@sha256:" not in RUNNER: raise SystemExit("Set RUNNER_IMAGE to the qualified Demo-Library runner image digest")
MAVEN="docker.io/library/maven@sha256:6fdc855a6ed81d288ca7ca37ac6ff5e9308b612485c0801d70b25a858c83d237"
MODULES=["ww-frontend","financial-advisor","investment-advisor","advisor-history"]
def oc(*args, data=None, capture=True):
 p=subprocess.run([OC,"--request-timeout=120s",*args],input=data,stdout=subprocess.PIPE if capture else None,check=True)
 return p.stdout or b""
def apply(obj): oc("apply","-f","-",data=json.dumps(obj).encode())
def ex(*args,container="runner",capture=False):return oc("exec","-n",NS,POD,"-c",container,"--",*args,capture=capture)
existing=oc("get","namespace",NS,"--ignore-not-found","-o","json").strip()
if existing and json.loads(existing)["metadata"].get("labels",{}).get("demo-library.io/owner")!=OWNER: raise SystemExit("Refusing unrelated namespace")
apply({"apiVersion":"v1","kind":"Namespace","metadata":{"name":NS,"labels":{"demo-library.io/owner":OWNER}}})
for kind,name in [("ServiceAccount",POD)]:apply({"apiVersion":"v1","kind":kind,"metadata":{"name":name,"namespace":NS}})
apply({"apiVersion":"rbac.authorization.k8s.io/v1","kind":"RoleBinding","metadata":{"name":POD,"namespace":NS},"roleRef":{"apiGroup":"rbac.authorization.k8s.io","kind":"ClusterRole","name":"admin"},"subjects":[{"kind":"ServiceAccount","name":POD,"namespace":NS}]})
# An internal registry image requires explicit pull access for this one service account.
if RUNNER.startswith("image-registry.openshift-image-registry.svc:"):
 source=RUNNER.split("/")[1]
 apply({"apiVersion":"rbac.authorization.k8s.io/v1","kind":"RoleBinding","metadata":{"name":"wealthwise-tools-pull-"+NS,"namespace":source},"roleRef":{"apiGroup":"rbac.authorization.k8s.io","kind":"ClusterRole","name":"system:image-puller"},"subjects":[{"kind":"ServiceAccount","name":POD,"namespace":NS}]})
apply({"apiVersion":"v1","kind":"PersistentVolumeClaim","metadata":{"name":"wealthwise-tools","namespace":NS},"spec":{"accessModes":["ReadWriteOnce"],"resources":{"requests":{"storage":"3Gi"}}}})
pod=json.loads(oc("get","pod",POD,"-n",NS,"--ignore-not-found","-o","json") or b"{}")
if pod and (pod.get("status",{}).get("phase") in ("Failed","Succeeded") or pod["spec"]["containers"][0]["image"]!=RUNNER):
 oc("delete","pod",POD,"-n",NS,"--wait=true");pod={}
if not pod:
 containers=[]
 for name,image in [("runner",RUNNER),("maven",MAVEN)]:
  containers.append({"name":name,"image":image,"command":["sleep","infinity"],"workingDir":"/work","env":[{"name":"HOME","value":"/work/home"},{"name":"KUBECONFIG","value":"/work/unused-kubeconfig"},{"name":"MAVEN_OPTS","value":"-Duser.home=/work/home"}],"resources":{"requests":{"cpu":"100m","memory":"256Mi"},"limits":{"cpu":"2","memory":"2Gi"}},"securityContext":{"allowPrivilegeEscalation":False,"capabilities":{"drop":["ALL"]}},"volumeMounts":[{"name":"work","mountPath":"/work"}]})
 apply({"apiVersion":"v1","kind":"Pod","metadata":{"name":POD,"namespace":NS,"labels":{"demo-library.io/owner":OWNER}},"spec":{"serviceAccountName":POD,"securityContext":{"runAsNonRoot":True,"seccompProfile":{"type":"RuntimeDefault"}},"containers":containers,"volumes":[{"name":"work","persistentVolumeClaim":{"claimName":"wealthwise-tools"}}]}})
oc("wait","pod/"+POD,"-n",NS,"--for=condition=Ready","--timeout=300s",capture=False)
run=time.strftime("%Y%m%dT%H%M%SZ",time.gmtime()); remote="/work/runs/"+run
ex("mkdir","-p",remote,"/work/home")
local_build=os.environ.get("WEALTHWISE_USE_LOCAL_BUILD")=="1"
with tempfile.TemporaryDirectory() as tmp:
 archive=pathlib.Path(tmp)/"source.tar.gz"
 with tarfile.open(archive,"w:gz") as tar:
  for f in source_paths(ROOT,include_build=local_build):
   tar.add(f,arcname=str(f.relative_to(ROOT)))
 with archive.open("rb") as stream:subprocess.run([OC,"exec","-i","-n",NS,POD,"-c","runner","--","tar","xzf","-","-C",remote],stdin=stream,check=True)
configure(OC,NS,remote)
if not local_build:
 ex("mvn","-B","-ntp","-f",remote+"/pom.xml","-Dmaven.repo.local=/work/m2","verify",container="maven")
images={}
selected=set(os.environ.get("WEALTHWISE_BUILD_MODULES", ",".join(MODULES)).split(","))
if not selected or not selected.issubset(MODULES): raise SystemExit("Invalid WEALTHWISE_BUILD_MODULES")
for module in MODULES:
 if module not in selected:
  ref=oc("get","imagestreamtag",module+":baseline","-n",NS,"-o","jsonpath={.image.dockerImageReference}").decode()
  if "@sha256:" not in ref:raise SystemExit("No qualified image to reuse for "+module+"; run without WEALTHWISE_BUILD_MODULES")
  images[module]=ref
  continue
 apply({"apiVersion":"image.openshift.io/v1","kind":"ImageStream","metadata":{"name":module,"namespace":NS}})
 dockerfile=(ROOT/"Containerfile").read_text()
 apply({"apiVersion":"build.openshift.io/v1","kind":"BuildConfig","metadata":{"name":module,"namespace":NS},"spec":{"runPolicy":"Serial","source":{"type":"Binary","binary":{},"dockerfile":dockerfile},"strategy":{"type":"Docker","dockerStrategy":{}},"output":{"to":{"kind":"ImageStreamTag","name":module+":baseline"}},"resources":{"requests":{"cpu":"100m","memory":"256Mi"},"limits":{"cpu":"1","memory":"1Gi"}}}})
 ex("sh","-c",'cd "$1" && oc start-build "$2" -n "$3" --from-dir=target --wait --follow',"sh",remote+"/"+module,module,NS)
 ref=oc("get","imagestreamtag",module+":baseline","-n",NS,"-o","jsonpath={.image.dockerImageReference}").decode()
 if "@sha256:" not in ref:raise SystemExit("Image digest missing")
 images[module]=ref
sc=os.environ.get("STORAGE_CLASS")
if not sc:
 classes=json.loads(oc("get","storageclass","-o","json"))["items"]
 defaults=[c["metadata"]["name"] for c in classes if c["metadata"].get("annotations",{}).get("storageclass.kubernetes.io/is-default-class")=="true"]
 if len(defaults)!=1:raise SystemExit("Set STORAGE_CLASS explicitly")
 sc=defaults[0]
values={"namespace_precreated":True,"workload_namespace":NS,"storage_class":sc,"images":images}
payload=json.dumps(values).encode()
oc("exec","-i","-n",NS,POD,"-c","runner","--","sh","-c",'cat > "$1"',"sh",remote+"/deploy/run-values.json",data=payload)
ex("sh","-c",'cd "$1/deploy" && ansible-playbook provision.yml -e @run-values.json',"sh",remote)
route=oc("get","route","wealthwise","-n",NS,"-o","jsonpath={.spec.host}").decode()
evidence=ROOT/".private"/"runs"/run;evidence.mkdir(parents=True,exist_ok=True);os.chmod(ROOT/".private",0o700)
(evidence/"deployment.json").write_text(json.dumps({"namespace":NS,"url":"https://"+route,"images":images,"run":run},indent=2))
print("Application: https://"+route);print("Application identity: Keycloak via wealthwise-oidc in namespace "+NS);print("Evidence:",evidence)
