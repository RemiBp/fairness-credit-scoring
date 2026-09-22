const D=JSON.parse(document.getElementById('benchmark-data').textContent);
const $=id=>document.getElementById(id);
const fmt=(n,d=3)=>n===null?'n/a':Number(n).toFixed(d);
const pct=n=>n===null?'n/a':(100*n).toFixed(1)+'%';
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const interval=(a,p=false)=>a?(p?pct(a[0])+' to '+pct(a[1]):fmt(a[0])+' to '+fmt(a[1])):'n/a';
for(const [key,m] of Object.entries(D.models)) {
  $('model').add(new Option(m.name,key));
  $('comparison-rows').insertAdjacentHTML('beforeend',`<tr><td>${esc(m.name)}</td><td><b>${fmt(m.metrics.auc)}</b><span class="small">95%: ${interval(m.auc_interval_95)}</span></td><td>${fmt(m.metrics.average_precision)}</td><td>${fmt(m.metrics.log_loss)}</td><td>${fmt(m.metrics.brier)}</td></tr>`);
}
$('comparison-rows').insertAdjacentHTML('beforeend',`<tr><td>Constant training-rate baseline</td><td>${fmt(D.baseline.auc)}</td><td>${fmt(D.baseline.average_precision)}</td><td>${fmt(D.baseline.log_loss)}</td><td>${fmt(D.baseline.brier)}</td></tr>`);
const best=Object.values(D.models).reduce((a,b)=>a.metrics.auc>b.metrics.auc?a:b);
$('best-auc').textContent=fmt(best.metrics.auc)+' ROC-AUC';
$('best-label').textContent=best.name+' · validation';
const diff=D.paired_auc_difference;
$('comparison-summary').textContent=`AUC gap: ${fmt(diff.forest_minus_logistic)} (95%: ${interval(diff.interval_95)}). ${diff.interval_95[0]<=0&&diff.interval_95[1]>=0?'No clear ranking advantage.':'Validation comparison only.'} Logistic regression has lower probability error.`;
function calibrationChart(rows) {
  const x=p=>35+p*260,y=p=>185-p*160;
  return `<svg viewBox="0 0 330 218" role="img" aria-label="Calibration: mean predicted bad-credit probability versus observed bad-credit rate"><line x1="35" y1="185" x2="295" y2="25" stroke="#b8c9be" stroke-dasharray="4 4"/><path d="M35 25V185H295" fill="none" stroke="#aab3ad"/>${[0,.5,1].map(p=>`<text class="chart-label" x="${x(p)}" y="202" text-anchor="middle">${p}</text><text class="chart-label" x="24" y="${y(p)+4}" text-anchor="end">${p}</text>`).join('')}${rows.map(r=>`<circle cx="${x(r.mean_prediction)}" cy="${y(r.bad_rate)}" r="${3+Math.sqrt(r.n)/2}" fill="#1b4a38" fill-opacity=".75"><title>n=${r.n}; predicted ${pct(r.mean_prediction)}; observed ${pct(r.bad_rate)}</title></circle>`).join('')}<text class="chart-label" x="165" y="216" text-anchor="middle">Mean predicted bad-credit probability</text></svg>`;
}
function rateCell(r) {return `<b>${pct(r.rate)}</b><span class="small">${r.events}/${r.n}; 95% ${interval(r.interval,true)}</span>`;}
function current(){return {key:$('model').value,t:Number($('threshold').value),ratio:Number($('ratio').value),cut:Number($('age-cut').value)};}
function update() {
  const {key,t,ratio,cut}=current(),m=D.models[key],d=Metrics.decision(D.cases,key,t,ratio);
  if(document.activeElement!==$('threshold-number')) $('threshold-number').value=t.toFixed(2);
  $('policy-stats').innerHTML=`<div class="stat"><b>${d.accepted} / ${d.n}</b><span>Cases accepted at threshold ${t.toFixed(2)}</span></div><div class="stat"><b>${d.bad_accepted} bad credits</b><span>Accepted under this policy</span></div><div class="stat warn"><b>${fmt(d.cost_per_100,1)} units</b><span>Simulated cost per 100 cases</span></div>`;
  $('confusion').innerHTML=`<tr><th>Good credit</th><td>${d.good_accepted}</td><td>${d.good_refused}</td></tr><tr><th>Bad credit</th><td>${d.bad_accepted}</td><td>${d.bad_refused}</td></tr>`;
  $('cost-note').textContent=`Cost per 100 = 100 × (${ratio} × ${d.bad_accepted} + ${d.good_refused}) / ${d.n}. Simulated units.`;
  $('calibration').innerHTML=calibrationChart(m.calibration);
  const groups=Metrics.groups(D.cases,key,t,cut),labels=[`Below ${cut}`,`${cut} or above`];
  $('fairness-context').textContent=`${m.name} · threshold ${t.toFixed(2)} · n = ${groups[0].n} / ${groups[1].n}`;
  $('fairness-rows').innerHTML=groups.map((g,i)=>`<tr><th>${labels[i]}<span class="small">n=${g.n}</span></th><td>${rateCell(g.acceptance)}</td><td>${rateCell(g.good_refusal)}</td><td>${rateCell(g.bad_acceptance)}</td></tr>`).join('');
  const gap=100*(groups[0].acceptance.rate-groups[1].acceptance.rate);
  $('fairness-gap').textContent=`Acceptance gap, younger minus older: ${gap>=0?'+':''}${gap.toFixed(1)} percentage points.`;
  updateCase();
}
function bars(id,items,formatter,max) {
  const scale=max||Math.max(...items.map(d=>Math.abs(d.contribution??d.mean)),.001);
  $(id).innerHTML=items.map(d=>{let value=d.contribution??d.mean;return `<div class="bar-row"><span>${esc(d.feature)}</span><div class="bar-track"><div class="bar-fill" style="width:${Math.min(100,100*Math.abs(value)/scale)}%;background:${value<0?'#9bb8a6':'#1b4a38'}"></div></div><span class="value">${formatter(value)}</span></div>`;}).join('');
}
const importanceScale=Math.max(...['logistic','forest'].flatMap(k=>D.models[k].importance.map(v=>Math.abs(v.mean))));
for(const kind of ['logistic','forest']) {
  bars(kind+'-importance',D.models[kind].importance.slice(0,6),v=>fmt(v),importanceScale);
  const s=D.models[kind].stability;
  $('stability-rows').insertAdjacentHTML('beforeend',`<tr><td>${esc(D.models[kind].name)}</td><td>${fmt(100*s.mean_probability_sd,1)} pp</td><td>${pct(s.decision_disagreement_at_05)}</td><td>${interval(s.auc_range)}</td></tr>`);
}
for(const c of D.cases.slice(0,3)) $('case-select').add(new Option(`Source row ${c.row_id} · age ${c.age}`,String(c.row_id)));
function updateCase() {
  const c=D.cases.find(c=>c.row_id===Number($('case-select').value));if(!c) return;
  const {t}=current();
  $('case-info').innerHTML=`<strong>Source row ${c.row_id}.</strong> Age ${c.age}; loan duration ${c.duration} months; transformed amount ${c.amount_transformed}. Observed outcome: <strong>${c.y_bad?'bad credit':'good credit'}</strong>.<br>Logistic score ${pct(c.scores.logistic)}: ${c.scores.logistic<t?'accepted':'refused'}. Forest score ${pct(c.scores.forest)}: ${c.scores.forest<t?'accepted':'refused'} at threshold ${t.toFixed(2)}. Models include age.`;
  const lr=c.explanations.logistic;
  bars('logistic-local',lr.terms.slice(0,5).map(d=>({...d,feature:d.feature.replace('numeric__','').replace('categorical__','')})),v=>(v>=0?'+':'')+fmt(v,2));
  $('logistic-local').insertAdjacentHTML('beforeend',`<p class="note">Top five log-odds terms. Intercept ${fmt(lr.intercept)}; total ${fmt(lr.logit)}. Original column codes.</p>`);
  bars('forest-local',c.explanations.forest.terms.slice(0,5),v=>(v>=0?'+':'')+fmt(100*v,1)+' pp');
  $('forest-local').insertAdjacentHTML('beforeend','<p class="note">Positive: original score exceeds the replacement score. Bars show absolute change.</p>');
}
$('threshold').addEventListener('input',update);
$('threshold-number').addEventListener('input',()=>{const value=Number($('threshold-number').value);$('threshold').value=Number.isFinite(value)?Math.max(0,Math.min(1,value)):.5;update();});
for(const id of ['model','ratio','age-cut']) $(id).addEventListener('change',update);
$('optimal').addEventListener('click',()=>{const {key,ratio}=current();$('threshold').value=D.models[key].cost_thresholds.find(c=>c.ratio===ratio).threshold;update();});
$('reset').addEventListener('click',()=>{$('threshold').value=.5;update();});
$('case-select').addEventListener('change',updateCase);
$('notes').addEventListener('click',()=>{const open=[...document.querySelectorAll('details')].some(d=>!d.open);document.querySelectorAll('details').forEach(d=>d.open=open);$('notes').textContent=open?'Collapse notes':'Expand notes';});
$('print').addEventListener('click',()=>window.print());
$('versions').textContent=`Recorded environment: Python ${D.versions.python}, scikit-learn ${D.versions.sklearn}, NumPy ${D.versions.numpy}, pandas ${D.versions.pandas}. Split seed ${D.seed}. Source SHA-256: ${D.source_sha256}.`;
update();
