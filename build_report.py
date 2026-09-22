"""Bundle the computed results and presentation into a standalone offline HTML file."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent

def build():
    report=json.loads((ROOT/'results/benchmark.json').read_text())
    assert report['evaluation']=='validation_only' and report['test_evaluated'] is False
    text=(ROOT/'web/report.html').read_text()
    fields={'STYLE':(ROOT/'web/style.css').read_text(),
            'DATA':json.dumps(report,separators=(',',':'),allow_nan=False).replace('<','\\u003c'),
            'METRICS':(ROOT/'web/metrics.js').read_text(), 'APP':(ROOT/'web/app.js').read_text()}
    for name,value in fields.items(): text=text.replace('__'+name+'__',value)
    (ROOT/'docs/index.html').write_text(text)
    print('Built docs/index.html from computed validation results.')
if __name__=='__main__':build()
