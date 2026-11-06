from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'site/runs.json').read_text())
payload=json.dumps(data,separators=(',',':')).replace('<','\\u003c')
(root/'site/index.html').write_text((root/'site/template.html').read_text().replace('__RUN_DATA__',payload))
print('Offline replay built from measured rule-policy traces.')
