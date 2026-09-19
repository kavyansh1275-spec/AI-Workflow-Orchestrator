from __future__ import annotations
import base64, json, os, re, subprocess, sys, time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import httpx

@dataclass
class Step:
    name: str
    status: str = "pending"
    detail: str = ""
    duration: float = 0.0

@dataclass
class RunReport:
    run_id: str
    request: str
    project_dir: str
    steps: list[Step] = field(default_factory=list)
    tests: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    deployment: dict[str, Any] = field(default_factory=dict)
    live_url: str | None = None
    def json(self):
        return json.dumps({"run_id":self.run_id,"request":self.request,"project_dir":self.project_dir,
            "steps":[s.__dict__ for s in self.steps],"tests":self.tests,"errors":self.errors,
            "deployment":self.deployment,"live_url":self.live_url},indent=2)

class GitHubWorkspace:
    def __init__(self, token=None):
        self.token=token or os.getenv("GITHUB_TOKEN")
        self.base="https://api.github.com"
    def headers(self):
        h={"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2026-03-10"}
        if self.token: h["Authorization"]="Bearer "+self.token
        return h
    def list_files(self,repo,path="",branch="main"):
        r=httpx.get(f"{self.base}/repos/{repo}/contents/{path.lstrip('/')}",headers=self.headers(),params={"ref":branch},timeout=30)
        r.raise_for_status(); d=r.json(); return d if isinstance(d,list) else [d]
    def read_file(self,repo,path,branch="main"):
        r=httpx.get(f"{self.base}/repos/{repo}/contents/{path.lstrip('/')}",headers=self.headers(),params={"ref":branch},timeout=30)
        r.raise_for_status(); return base64.b64decode(r.json()["content"]).decode()
    def sync_to_local(self,repo,destination,branch="main"):
        destination.mkdir(parents=True,exist_ok=True); self._tree(repo,"",destination,branch); return destination
    def _tree(self,repo,remote,local,branch):
        for x in self.list_files(repo,remote,branch):
            t=local/x["name"]
            if x["type"]=="dir":
                t.mkdir(parents=True,exist_ok=True); self._tree(repo,x["path"],t,branch)
            elif x["type"]=="file" and x.get("size",0)<=1000000:
                try: t.write_text(self.read_file(repo,x["path"],branch),encoding="utf-8")
                except Exception: pass

class AIProvider:
    def __init__(self):
        self.key=os.getenv("GEMINI_API_KEY"); self.model=os.getenv("GEMINI_MODEL","gemini-2.5-flash")
        self.client=None
        if self.key:
            try:
                from google import genai
                self.client=genai.Client(api_key=self.key)
            except Exception: pass
    def ask(self,prompt):
        if not self.client: return ""
        r=self.client.models.generate_content(model=self.model,contents=prompt)
        return getattr(r,"text","") or ""

class WebDeveloper:
    def __init__(self,root="generated_web_projects"):
        self.root=Path(root).resolve(); self.root.mkdir(parents=True,exist_ok=True)
        self.ai=AIProvider(); self.github=GitHubWorkspace()
    def run(self,request,project_name=None,github_repo=None,github_branch="main",deploy=False,max_repairs=3):
        project=self.root/self.slug(project_name or self.infer_name(request))
        report=RunReport(time.strftime("%Y%m%d-%H%M%S"),request,str(project))
        self.stage(report,"plan",lambda:self.plan(request)); project.mkdir(parents=True,exist_ok=True)
        if github_repo: self.stage(report,"github_sync",lambda:self.github.sync_to_local(github_repo,project,github_branch))
        self.stage(report,"generate",lambda:self.generate(request,project))
        self.stage(report,"validate",lambda:self.validate_files(project))
        for attempt in range(max_repairs+1):
            result=self.run_tests(project); report.tests.append({"attempt":attempt+1,**result})
            if result["passed"]: break
            if attempt>=max_repairs:
                report.errors.append(result.get("output","Tests failed")); break
            changed=self.repair(request,project,result.get("output",""))
            report.steps.append(Step("repair_"+str(attempt+1),"passed" if changed else "failed",result.get("output","")[-1200:]))
        self.stage(report,"browser_qa",lambda:self.browser_qa(project))
        if deploy:
            dep=self.stage(report,"deploy",lambda:self.deploy(project))
            if isinstance(dep,dict): report.deployment=dep; report.live_url=dep.get("url")
        return report
    def stage(self,report,name,fn):
        t=time.perf_counter()
        try:
            v=fn(); report.steps.append(Step(name,"passed",self.short(v),time.perf_counter()-t)); return v
        except Exception as e:
            report.steps.append(Step(name,"failed",str(e),time.perf_counter()-t)); report.errors.append(name+": "+str(e)); return None
    def short(self,v):
        if v is None:return ""
        return v[-1500:] if isinstance(v,str) else json.dumps(v,default=str)[-1500:]
    def plan(self,request):
        return {"request":request,"pipeline":["requirements","code","tests","repair","browser_qa","deploy"]}
    def generate(self,request,project):
        if not list(project.rglob("*")):
            (project/"index.html").write_text(self.starter_html(request),encoding="utf-8")
            (project/"style.css").write_text(self.starter_css(),encoding="utf-8")
            (project/"app.js").write_text(self.starter_js(),encoding="utf-8")
            (project/"README.md").write_text("# "+self.infer_name(request)+"\nGenerated by AI Web Developer.\n",encoding="utf-8")
        if self.ai.client:
            prompt=("Return ONLY JSON array of {path,content} edits. Act as a senior autonomous web developer. "
                    "Improve the existing project for this request without secrets:\n",¨­ÅÕÍÐ¤(¥ÑÌõÍ±¹ÁÉÍ}©Í½¸¡Í±¹¤¹Í¬¡ÁÉ½µÁÐ¤¤(½Èà¥¸¥ÑÌ¥¥Í¥¹ÍÑ¹¡¥ÑÌ±±¥ÍÐ¤±Ímtè(¥¥Í¥¹ÍÑ¹¡à±¥Ð¤¹¥Í¥¹ÍÑ¹¡à¹Ð ÁÑ ¤±ÍÑÈ¤¹¥Í¥¹ÍÑ¹¡à¹Ð ½¹Ñ¹Ð¤±ÍÑÈ¤è(ÑÉÐô¡ÁÉ½©Ð½álÁÑ t¤¹ÉÍ½±Ù ¤(¥ÁÉ½©Ð¹ÉÍ½±Ù ¤¥¸ÑÉÐ¹ÁÉ¹ÑÌè(ÑÉÐ¹ÁÉ¹Ð¹µ­¥È¡ÁÉ¹ÑÌõQÉÕ±á¥ÍÑ}½¬õQÉÕ¤ìÑÉÐ¹ÝÉ¥Ñ}ÑáÐ¡ál½¹Ñ¹Ðt±¹½¥¹ôÕÑ´à¤(ÉÑÕÉ¸ì¥±Ìé±¸¡mÀ½ÈÀ¥¸ÁÉ½©Ð¹É±½ ¨¤¥À¹¥Í}¥± ¥t¥ô(Ù±¥Ñ}¥±Ì¡Í±±ÁÉ½©Ð¤è(¥±ÌõmÀ½ÈÀ¥¸ÁÉ½©Ð¹É±½ ¨¤¥À¹¥Í}¥± ¤¹¹¥Ð¹½Ð¥¸À¹ÁÉÑÍt(¥¹½Ð¥±ÌèÉ¥ÍIÕ¹Ñ¥µÉÉ½È 9¼ÁÉ½©Ð¥±ÌÝÉ¹ÉÑ¤(½ÈÀ¥¸¥±Ìè(¥À¹ÍÕ¥àôô¹Áäè(ÍÕÁÉ½ÍÌ¹ÉÕ¸¡mÍåÌ¹áÕÑ±°µ´°Áå}½µÁ¥±±ÍÑÈ¡À¥t±¡¬õQÉÕ±ÁÑÕÉ}½ÕÑÁÕÐõQÉÕ±ÑáÐõQÉÕ¤(ÉÑÕÉ¸ì¥±}½Õ¹Ðé±¸¡¥±Ì¥ô(ÉÕ¹}ÑÍÑÌ¡Í±±ÁÉ½©Ð¤è(µÌõmt(¥¡ÁÉ½©Ð¼ÑÍÑÌ¤¹á¥ÍÑÌ ¤èµÌ¹ÁÁ¹¡mÍåÌ¹áÕÑ±°µ´°ÁåÑÍÐ°µÄt¤(¥¡ÁÉ½©Ð¼Á­¹©Í½¸¤¹á¥ÍÑÌ ¤èµÌ¹ÁÁ¹¡l¹Á´°ÑÍÐ°´´°´µÉÕ¹%¹	¹t¤(¥¹½ÐµÌéÉÑÕÉ¸ìÁÍÍéQÉÕ°½ÕÑÁÕÐè9¼ÑÍÐ½µµ¹ÑÑìÍÑÉÕÑÕÉ°Ù±¥Ñ¥½¸ÁÍÍ¸ô(½ÕÐõmt(½Èµ¥¸µÌè(ÑÉäè(ÀõÍÕÁÉ½ÍÌ¹ÉÕ¸¡µ±ÝõÁÉ½©Ð±ÁÑÕÉ}½ÕÑÁÕÐõQÉÕ±ÑáÐõQÉÕ±Ñ¥µ½ÕÐôÄàÀ¤ì½ÕÐ¹ÁÁ¹ ¡À¹ÍÑ½ÕÐ­À¹ÍÑÉÈ¥l´ØÀÀÀét(¥À¹ÉÑÕÉ¹½éÉÑÕÉ¸ìÁÍÍé±Í°½ÕÑÁÕÐèq¸¹©½¥¸¡½ÕÐ¥ô(áÁÐáÁÑ¥½¸ÌéÉÑÕÉ¸ìÁÍÍé±Í°½ÕÑÁÕÐéÍÑÈ¡¥ô(ÉÑÕÉ¸ìÁÍÍéQÉÕ°½ÕÑÁÕÐèq¸¹©½¥¸¡½ÕÐ¥ô(ÉÁ¥È¡Í±±ÉÅÕÍÐ±ÁÉ½©Ð±ÉÉ½È¤è(¥¹½ÐÍ±¹¤¹±¥¹ÐéÉÑÕÉ¸±Í(¥ÑÌõÍ±¹ÁÉÍ}©Í½¸¡Í±¹¤¹Í¬ IÑÕÉ¸=91d)M=8ÉÉä½íÁÑ ±½¹Ñ¹Ñô¸¥àÑ¡¥ÌÁÉ½©Ð¸IÅÕÍÐéq¸­ÉÅÕÍÐ¬q¹ÉÉ½Èéq¸­ÉÉ½È¤¤(¡¹õ±Í(½Èà¥¸¥ÑÌ¥¥Í¥¹ÍÑ¹¡¥ÑÌ±±¥ÍÐ¤±Ímtè(¥¥Í¥¹ÍÑ¹¡à±¥Ð¤¹¥Í¥¹ÍÑ¹¡à¹Ð ÁÑ ¤±ÍÑÈ¤¹¥Í¥¹ÍÑ¹¡à¹Ð ½¹Ñ¹Ð¤±ÍÑÈ¤è(ÑÉÐô¡ÁÉ½©Ð½álÁÑ t¤¹ÉÍ½±Ù ¤(¥ÁÉ½©Ð¹ÉÍ½±Ù ¤¥¸ÑÉÐ¹ÁÉ¹ÑÌè(ÑÉÐ¹ÁÉ¹Ð¹µ­¥È¡ÁÉ¹ÑÌõQÉÕ±á¥ÍÑ}½¬õQÉÕ¤ìÑÉÐ¹ÝÉ¥Ñ}ÑáÐ¡ál½¹Ñ¹Ðt±¹½¥¹ôÕÑ´à¤ì¡¹õQÉÕ(ÉÑÕÉ¸¡¹(É½ÝÍÉ}Å¡Í±±ÁÉ½©Ð¤è(¥¹½Ð¡ÁÉ½©Ð¼¥¹à¹¡Ñµ°¤¹á¥ÍÑÌ ¤éÉÑÕÉ¸ìÍÑÑÕÌèÍ­¥ÁÁ°ÉÍ½¸è9¼¥¹à¹¡Ñµ°ô(ÑÉäèÉ½´Á±åÝÉ¥¡Ð¹Íå¹}Á¤¥µÁ½ÉÐÍå¹}Á±åÝÉ¥¡Ð(áÁÐáÁÑ¥½¸éÉÑÕÉ¸ìÍÑÑÕÌèÍ­¥ÁÁ°ÉÍ½¸èA±åÝÉ¥¡Ð¹½Ð¥¹ÍÑ±±ô(ÉÉ½ÉÌõmt(Ý¥Ñ Íå¹}Á±åÝÉ¥¡Ð ¤ÌÀè(É½ÝÍÈõÀ¹¡É½µ¥Õ´¹±Õ¹ ¡¡±ÍÌõQÉÕ¤ìÁõÉ½ÝÍÈ¹¹Ý}Á ¤(Á¹½¸ ÁÉÉ½È±±µéÉÉ½ÉÌ¹ÁÁ¹¡ÍÑÈ¡¤¤¤(Á¹½Ñ¼ ¡ÁÉ½©Ð¼¥¹à¹¡Ñµ°¤¹Í}ÕÉ¤ ¤±Ý¥Ñ}Õ¹Ñ¥°ô±½¤ìÑ¥Ñ±õÁ¹Ñ¥Ñ± ¤ìÉ½ÝÍÈ¹±½Í ¤(ÉÑÕÉ¸ìÍÑÑÕÌèÁÍÍ¥¹½ÐÉÉ½ÉÌ±Í¥±°Ñ¥Ñ±éÑ¥Ñ±°Á}ÉÉ½ÉÌéÉÉ½ÉÍô(Á±½ä¡Í±±ÁÉ½©Ð¤è(¥¹½Ð½Ì¹Ñ¹Ø I9I}A%}-d¤½È¹½Ð½Ì¹Ñ¹Ø I9I}MIY%}%¤è(ÉÑÕÉ¸ìÍÑÑÕÌè±½­°ÉÍ½¸èMÐI9I}A%}-d¹I9I}MIY%}%Ñ¼¹±Á±½åµ¹Ð¸ô(ÉÑÕÉ¸ìÍÑÑÕÌèÉä°ÉÍ½¸èI¹ÈÉ¹Ñ¥±ÌÑÑ°ÍÉÙ¥}¥é½Ì¹Ñ¹Ø I9I}MIY%}%¥ô(ÍÑÑ¥µÑ¡½(ÁÉÍ}©Í½¸¡ÑáÐ¤è(¥¹½ÐÑáÐéÉÑÕÉ¸9½¹(ÑáÐõÑáÐ¹ÍÑÉ¥À ¤(¥ÑáÐ¹ÍÑÉÑÍÝ¥Ñ  ¤éÑáÐõÉ¹ÍÕ¡Èy üé©Í½¸¤ýqÌ©ñqÌ©°±ÑáÐ±±ÌõÉ¹%ñÉ¹L¤¹ÍÑÉ¥À ¤(ÑÉäéÉÑÕÉ¸©Í½¸¹±½Ì¡ÑáÐ¤(áÁÐáÁÑ¥½¸éÉÑÕÉ¸9½¹(ÍÑÑ¥µÑ¡½(¥¹É}¹µ¡ÉÅÕÍÐ¤è(ÉÑÕÉ¸´¹©½¥¸¡É¹¥¹±°¡ÈmµiµèÀ´åt¬±ÉÅÕÍÐ¹±½ÝÈ ¤¥lèÙt¤½È¤µÝµÁÉ½©Ð(ÍÑÑ¥µÑ¡½(Í±Õ¡Ù±Õ¤è(ÉÑÕÉ¸É¹ÍÕ¡ÈmyµèÀ´äµt¬°´±Ù±Õ¹±½ÝÈ ¤¤¹ÍÑÉ¥À ´¥lèØÁt½È¤µÝµÁÉ½©Ð(ÍÑÑ¥µÑ¡½(ÍÑÉÑÉ}¡Ñµ°¡ÉÅÕÍÐ¤è(Ñ¥Ñ±õ]Ù±½ÁÈ¹¥¹É}¹µ¡ÉÅÕÍÐ¤¹ÉÁ± ´°¤¹Ñ¥Ñ± ¤(ÉÑÕÉ¸ð½ÑåÁ¡Ñµ°øñ¡Ñµ°±¹ô¸øñ¡øñµÑ¡ÉÍÐôÕÑ´àøñµÑ¹µôÙ¥ÝÁ½ÉÐ½¹Ñ¹ÐôÝ¥Ñ õÙ¥µÝ¥Ñ ±¥¹¥Ñ¥°µÍ±ôÄøñÑ¥Ñ±ø­Ñ¥Ñ±¬ð½Ñ¥Ñ±øñ±¥¹¬É°ôÍÑå±Í¡Ð¡ÉôÍÑå±¹ÍÌøð½¡øñ½äøñµ¥¸±ÍÌôÍ¡±°øñ¹ØøñÍÑÉ½¹ø­Ñ¥Ñ±¬ð½ÍÑÉ½¹øñ¡Éô½¹ÑÐù½¹ÑÐð½øð½¹ØøñÍÑ¥½¸±ÍÌô¡É¼øñÀ±ÍÌôåÉ½Üù$µ¹ÉÑÝáÁÉ¥¹ð½Àøñ Äø­Ñ¥Ñ±¬ð½ ÄøñÀù	Õ¥±ÐÉ½´¹ÑÕÉ°µ±¹ÕÉÅÕÍÐ¸Q¡Ù±½ÁÈ¹Ð¸¥Ð°ÑÍÐ°ÉÁ¥È¹ÁÉÁÉÑ¡¥ÌÁÉ½©Ð½ÈÁ±½åµ¹Ð¸ð½ÀøñÕÑÑ½¸¥ôÑùÐÍÑÉÑð½ÕÑÑ½¸øð½ÍÑ¥½¸øñÍÑ¥½¸±ÍÌôÉ¥ô½¹ÑÐøñ ÈùAÉ½©ÐÉäð½ ÈøñÀùIÁ±Ñ¡¥ÌÍÑÉÑÈ½¹Ñ¹ÐÝ¥Ñ å½ÕÈÁÉ½ÕÐÉÅÕ¥Éµ¹ÑÌ¸ð½Àøð½ÍÑ¥½¸øð½µ¥¸øñÍÉ¥ÁÐÍÉôÁÀ¹©Ìøð½ÍÉ¥ÁÐøð½½äøð½¡Ñµ°ø(ÍÑÑ¥µÑ¡½(ÍÑÉÑÉ}ÍÌ ¤è(ÉÑÕÉ¸©í½àµÍ¥é¥¹é½ÉÈµ½áõ½åíµÉ¥¸èÀí½¹Ðµµ¥±äé%¹ÑÈ±ÍåÍÑ´µÕ¤±Í¹ÌµÍÉ¥í­É½Õ¹èÁÄÀÈÀí½±½ÈèÉô¹Í¡±±íµàµÝ¥Ñ èÄÀÔÁÁàíµÉ¥¸éÕÑ¼íÁ¥¹èÈÑÁáõ¹Ùí¥ÍÁ±äé±àí©ÕÍÑ¥äµ½¹Ñ¹ÐéÍÁµÑÝ¸íÁ¥¹èÄÁÁàÁô¹¡É½íÁ¥¹èÄÄÁÁàÀàÁÁàíµàµÝ¥Ñ èÜØÁÁáõ Åí½¹ÐµÍ¥éé±µÀ ÍÉ´°áÙÜ°ÙÉ´¤í±¥¹µ¡¥¡Ðè¸äÕô¹åÉ½Ýí½Á¥Ñäè¸ÜíÑáÐµÑÉ¹Í½É´éÕÁÁÉÍí±ÑÑÈµÍÁ¥¹è¸ÄÑµõÁí½¹ÐµÍ¥éèÄ¸ÀáÉ´í±¥¹µ¡¥¡ÐèÄ¸Üí½±½ÈèÕÅô¹ÉíÁ¥¹èÌÁÁàí½ÉÈèÅÁàÍ½±¥ÌÌÐÄÔÔí½ÉÈµÉ¥ÕÌèÈÑÁàí­É½Õ¹èÄÄÄàÈÝõÕÑÑ½¹í½ÉÈèÀí½ÉÈµÉ¥ÕÌèääåÁàíÁ¥¹èÄÑÁàÈÉÁàí½¹ÐµÝ¥¡ÐèÜÀÀíÕÉÍ½ÈéÁ½¥¹ÑÉô(ÍÑÑ¥µÑ¡½(ÍÑÉÑÉ}©Ì ¤è(ÉÑÕÉ¸½Õµ¹Ð¹Ñ±µ¹Ñ	å% Ñ¤ü¹Ù¹Ñ1¥ÍÑ¹È ±¥¬±Õ¹Ñ¥½¸ ¥í½Õµ¹Ð¹Ñ±µ¹Ñ	å% ½¹ÑÐ¤ü¹ÍÉ½±±%¹Ñ½Y¥Ü¡í¡Ù¥½ÈèÍµ½½Ñ ô¤íô¤ì