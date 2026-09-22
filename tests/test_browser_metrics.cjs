const assert=require('node:assert/strict');
const fs=require('node:fs');
const M=require('../web/metrics.js');
const d=JSON.parse(fs.readFileSync('results/benchmark.json','utf8'));
function almost(a,b){assert.ok(Math.abs(a-b)<1e-10,`${a} != ${b}`)}
for(const [key,model] of Object.entries(d.models)) {
  assert.deepEqual(M.decision(d.cases,key,.5,3),model.threshold_05);
  for(const cut of [25,30]) {
    const js=M.groups(d.cases,key,.5,cut);
    const py=model['fairness_'+cut];
    ['below','at_or_above'].forEach((label,i)=>{
      for(const metric of ['acceptance','good_refusal','bad_acceptance']) {
        const a=js[i][metric],b=py[label][metric];
        assert.equal(a.n,b.n);assert.equal(a.events,b.events);
        almost(a.rate,b.rate);a.interval.forEach((v,j)=>almost(v,b.wilson_95[j]));
      }
    });
  }
  assert.equal(M.decision(d.cases,key,0,3).accepted,0);
  assert.equal(M.decision(d.cases,key,1,3).accepted,200);
}
assert.equal(M.wilson(0,0),null);
console.log('Browser calculations match Python: four models, both age cut-offs, costs, intervals and boundary thresholds.');
