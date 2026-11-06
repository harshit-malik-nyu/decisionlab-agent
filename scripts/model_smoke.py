"""Run real local inference and preserve evidence; never substitute a mock."""
import base64
import gzip
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import urllib.request
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from decisionlab.evaluate import evaluate
from decisionlab.runner import LocalModel

output=Path('evaluation');output.mkdir(exist_ok=True)
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def request(path,payload=None,timeout=120):
    data=None if payload is None else json.dumps(payload).encode()
    req=urllib.request.Request('http://127.0.0.1:11434'+path,data=data,headers={'Content-Type':'application/json'})
    with opener.open(req,timeout=timeout) as r:return json.load(r)

runtime=Path(sys.argv[1]).resolve()
env={**os.environ,'OLLAMA_HOST':'127.0.0.1:11434','OLLAMA_MODELS':str(runtime/'models'),'OLLAMA_NUM_PARALLEL':'1','OLLAMA_CONTEXT_LENGTH':'4096'}
model=os.environ.get('DECISIONLAB_MODEL','qwen2.5:3b')
with (output/'runtime.log').open('w') as logs:
    server=subprocess.Popen([str(runtime/'bin/ollama'),'serve'],env=env,stdout=logs,stderr=logs)
    try:
        for _ in range(60):
            try:version=request('/api/version',timeout=2);break
            except OSError:time.sleep(.5)
        else:raise RuntimeError('Local inference server did not start')
        request('/api/pull',{'model':model,'stream':False},timeout=360)
        meta={'runtime':version,'models':request('/api/tags'),'platform':platform.platform(),
              'processor':platform.processor(),'cpu_count':os.cpu_count(),
              'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
              'scope':'Six authored development cases; one run each; no held-out or superiority claim.'}
        (output/'environment.json').write_text(json.dumps(meta,indent=2)+'\n')
        result=evaluate(LocalModel(model),output/'model-smoke.json')
        summary={'model':model,'correct':result['correct'],'total':len(result['results']),
                 'failed':sum(r['status']=='failed' for r in result['results']),
                 'cases':[{'case':r['case'],'status':r['status'],'grade':r['grade'],'seconds':r['elapsed_seconds']} for r in result['results']]}
        (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
        print('MEASURED_SUMMARY '+json.dumps(summary),flush=True)
        # Public synthetic evidence only; compressed log copy supplements artifact retention.
        evidence={'environment':meta,'report':result}
        print('EVIDENCE_GZIP_BASE64 '+base64.b64encode(gzip.compress(json.dumps(evidence).encode())).decode(),flush=True)
    finally:
        server.terminate()
        try:server.wait(timeout=10)
        except subprocess.TimeoutExpired:server.kill();server.wait()
