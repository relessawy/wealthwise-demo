#!/usr/bin/env python3
"""Exercise the public API without printing or persisting credentials."""
import os,json,subprocess,base64,urllib.request,urllib.error,urllib.parse,uuid,pathlib,time,http.cookiejar
root=pathlib.Path(__file__).resolve().parents[1];ns=os.environ.get("WEALTHWISE_NAMESPACE","wealthwise-demo");oc=os.environ.get("OC","oc")
def get(kind,name):return json.loads(subprocess.check_output([oc,"--request-timeout=30s","get",kind,name,"-n",ns,"-o","json"]))
url="https://"+get("route","wealthwise")["spec"]["host"]
s=get("secret","wealthwise-access")["data"];user=base64.b64decode(s["username"]).decode();password=base64.b64decode(s["password"]).decode();auth="Basic "+base64.b64encode((user+":"+password).encode()).decode()
checks=[]
def call(path,data=None,credentials=auth):
 headers={"Content-Type":"application/json"}
 if credentials:headers["Authorization"]=credentials
 req=urllib.request.Request(url+path,data=json.dumps(data).encode() if data is not None else None,headers=headers)
 try:
  with urllib.request.urlopen(req,timeout=25) as r:return r.status,json.loads(r.read())
 except urllib.error.HTTPError as e:return e.code,None

def check(name,truth):
 if not truth:raise SystemExit("FAIL: "+name)
 checks.append(name);print("PASS:",name)
check("anonymous history rejected",call("/api/history",credentials=None)[0]==401)
check("incorrect credential rejected",call("/api/history",credentials="Basic Zm9vOmJhcg==")[0]==401)
id=str(uuid.uuid4());body={"message":"How can I plan my household budget?","requestId":id}
status,response=call("/api/financial/chat",body);check("financial response explicitly scripted",status==200 and response.get("mode")=="demonstration" and "not live AI" in response["message"])
check("retry succeeds",call("/api/financial/chat",body)[0]==200)
check("conflicting retry rejected",call("/api/financial/chat",{"message":"different question","requestId":id})[0]==409)
status,h=call("/api/history");check("one persisted row after retry",status==200 and sum(x["requestId"]==id for x in h["message"])==1)
for risk in ("Conservative","Balanced","Aggressive"):
 status,response=call("/api/investment/chat",{"message":risk,"requestId":str(uuid.uuid4())});check("investment "+risk,status==200 and "Demonstration" in response["message"])
check("invalid investment rejected",call("/api/investment/chat",{"message":"INVALID","requestId":str(uuid.uuid4())})[0]==400)
check("empty financial question rejected",call("/api/financial/chat",{"message":"","requestId":str(uuid.uuid4())})[0]==400)
check("invalid history page rejected",call("/api/history?limit=1000")[0]==400)
check("missing request identity rejected",call("/api/financial/chat",{"message":"budget"})[0]==400)
# Spoofed incoming headers are ignored: frontend derives identity from authenticated account.
req=urllib.request.Request(url+"/api/history",headers={"Authorization":auth,"X-Demo-User":"another-user"})
with urllib.request.urlopen(req,timeout=25) as resp:data=json.load(resp)
check("client cannot override history identity",any(x["requestId"]==id for x in data["message"]))
jar=http.cookiejar.CookieJar()
form_client=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
form=urllib.parse.urlencode({"j_username":user,"j_password":password}).encode()
with form_client.open(urllib.request.Request(url+"/j_security_check",data=form),timeout=25) as response:
 check("form sign-in succeeds",response.status==200)
with form_client.open(url+"/api/history",timeout=25) as response:
 check("form session authorizes API",response.status==200)
cookie=next((c for c in jar if c.name=="quarkus-credential"),None)
check("form cookie protections",cookie is not None and cookie.secure and "httponly" in {k.lower() for k in cookie._rest} and cookie._rest.get("SameSite","").lower()=="strict")
with urllib.request.urlopen(url+"/q/openapi?format=json",timeout=25) as response: spec=json.load(response)
check("OpenAPI documents protected application endpoints","/api/financial/chat" in spec["paths"] and "/api/history" in spec["paths"] and spec["components"]["securitySchemes"]["demo"]["scheme"]=="basic")
out=root/".private"/"acceptance";out.mkdir(parents=True,exist_ok=True);os.chmod(root/".private",0o700)
(out/"latest.json").write_text(json.dumps({"status":"VERIFIED","checked_at":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"checks":checks,"persistence_request_id":id,"namespace":ns},indent=2))
print("Acceptance evidence:",out/"latest.json")
