/* Shared browser calculations; tested against independently exported Python results. */
const Metrics = (() => {
  function wilson(k,n) {
    if (!n) return null;
    const z=1.959963984540054, p=k/n, d=1+z*z/n;
    const center=(p+z*z/(2*n))/d;
    const half=z*Math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d;
    return [center-half,center+half];
  }
  function rate(k,n) { return {events:k,n,rate:n?k/n:null,interval:wilson(k,n)}; }
  function decision(cases,key,t,ratio) {
    let ga=0, ba=0, gr=0, br=0;
    for(const c of cases) {
      const accepted=c.scores[key]<t;
      if(c.y_bad) accepted?ba++:br++; else accepted?ga++:gr++;
    }
    return {n:cases.length,accepted:ga+ba,good_accepted:ga,bad_accepted:ba,good_refused:gr,bad_refused:br,
      cost_per_100:100*(ratio*ba+gr)/cases.length};
  }
  function groups(cases,key,t,cut) {
    return [cases.filter(c=>c.age<cut),cases.filter(c=>c.age>=cut)].map(rows=>{
      const d=decision(rows,key,t,1);
      return {n:rows.length,acceptance:rate(d.accepted,d.n),good_refusal:rate(d.good_refused,d.good_refused+d.good_accepted),
        bad_acceptance:rate(d.bad_accepted,d.bad_accepted+d.bad_refused)};
    });
  }
  return {wilson,decision,groups};
})();
if(typeof module !== 'undefined') module.exports=Metrics;
