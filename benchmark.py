"""Reproducible development benchmark. No predictions are made on the test set."""
from pathlib import Path
import json
import hashlib
import platform
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score, log_loss, brier_score_loss
import audit

ROOT = Path(__file__).resolve().parent
SEED = 20260922
LABELS = dict(laufkont='Checking account', laufzeit='Duration (months)', moral='Credit history',
 verw='Loan purpose', hoehe='Transformed amount', sparkont='Savings', beszeit='Employment duration',
 rate='Instalment rate band', famges='Personal status', buerge='Other debtors', wohnzeit='Residence duration',
 verm='Property', alter='Age (years)', weitkred='Other instalment plans', wohn='Housing', bishkred='Number of credits',
 beruf='Job', pers='Dependants band', telef='Telephone', gastarb='Foreign worker')


def load_data():
    path = ROOT/'data/SouthGermanCredit.asc'
    if hashlib.sha256(path.read_bytes()).hexdigest() != audit.SHA256:
        raise ValueError('Source checksum changed')
    frame = pd.read_csv(path, sep=r'\s+')
    y = (1-frame.pop('kredit')).to_numpy()
    return frame, y


def split_data(X, y):
    ids = np.arange(len(y))
    strata = y*2 + (X['alter'].to_numpy()<25).astype(int)
    dev, test = train_test_split(ids, test_size=.2, random_state=SEED, stratify=strata)
    train, valid = train_test_split(dev, test_size=.25, random_state=SEED+1, stratify=strata[dev])
    return {'train': sorted(train.tolist()), 'validation': sorted(valid.tolist()), 'test': sorted(test.tolist())}


def make_model(kind, include_age=True, seed=SEED):
    numeric = ['laufzeit', 'hoehe'] + (['alter'] if include_age else [])
    categorical = [c for c in LABELS if c not in ['laufzeit','hoehe','alter']]
    preprocessing = ColumnTransformer([
        ('numeric', StandardScaler(), numeric),
        ('categorical', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical)
    ], remainder='drop')
    if kind=='logistic':
        estimator=LogisticRegression(C=1.0, max_iter=2000, random_state=seed)
    else:
        estimator=RandomForestClassifier(n_estimators=250, min_samples_leaf=5, max_features='sqrt',
                                         random_state=seed, n_jobs=1)
    return Pipeline([('preprocess',preprocessing),('model',estimator)])


def decisions(y, p, threshold=.5, ratio=3):
    y=np.asarray(y); p=np.asarray(p)
    accept=p<threshold
    bad_accept=int(np.sum(accept & (y==1)))
    good_refuse=int(np.sum(~accept & (y==0)))
    good_accept=int(np.sum(accept & (y==0)))
    bad_refuse=int(np.sum(~accept & (y==1)))
    return dict(n=len(y), accepted=int(accept.sum()), bad_accepted=bad_accept,
                good_refused=good_refuse, good_accepted=good_accept, bad_refused=bad_refuse,
                cost_per_100=100*(ratio*bad_accept+good_refuse)/len(y))


def metrics(y,p):
    return dict(auc=float(roc_auc_score(y,p)), average_precision=float(average_precision_score(y,p)),
                log_loss=float(log_loss(y,p)), brier=float(brier_score_loss(y,p)))


def rate(k,n):
    return {'events':int(k),'n':int(n),'rate':float(k/n) if n else None,
            'wilson_95':audit.wilson(int(k),int(n)) if n else None}


def fairness(y,p,ages,threshold=.5,cut=25):
    groups={}
    for label,mask in [('below',ages<cut),('at_or_above',ages>=cut)]:
        yy=y[mask]; accept=p[mask]<threshold
        groups[label]={'n':int(mask.sum()), 'acceptance':rate(accept.sum(),len(yy)),
                       'good_refusal':rate(np.sum(~accept & (yy==0)),np.sum(yy==0)),
                       'bad_acceptance':rate(np.sum(accept & (yy==1)),np.sum(yy==1))}
    return groups


def best_threshold(y,p,ratio):
    grid=np.linspace(0,1,101)
    costs=[decisions(y,p,t,ratio)['cost_per_100'] for t in grid]
    minimum=min(costs)
    tied=[i for i,c in enumerate(costs) if np.isclose(c,minimum)]
    # Tie rule fixed in advance: nearest to 0.5, then lower threshold.
    i=min(tied,key=lambda i:(abs(grid[i]-.5),grid[i]))
    return {'ratio':ratio,'threshold':float(grid[i]),'validation_cost_per_100':minimum}


def calibration(y,p):
    result=[]
    edges=np.linspace(0,1,6)
    for i in range(5):
        mask=(p>=edges[i]) & ((p<edges[i+1]) if i<4 else (p<=edges[i+1]))
        if mask.any():
            result.append({'n':int(mask.sum()),'mean_prediction':float(p[mask].mean()),
                           'bad_rate':float(y[mask].mean()),'lower':float(edges[i]),'upper':float(edges[i+1])})
    return result


def stratified_bootstrap(y,rng):
    return np.concatenate([rng.choice(np.flatnonzero(y==v),sum(y==v),replace=True) for v in (0,1)])


def local_explanation(pipe,row,kind,Xtrain):
    if kind=='logistic':
        pre=pipe.named_steps['preprocess']; est=pipe.named_steps['model']
        values=pre.transform(row)[0]*est.coef_[0]
        features=pre.get_feature_names_out()
        terms=[{'feature':str(f),'contribution':float(v)} for f,v in zip(features,values)]
        logit=float(est.intercept_[0]+sum(values))
        expected=float(pipe.predict_proba(row)[0,1])
        if not np.isclose(1/(1+np.exp(-logit)),expected):
            raise AssertionError('Local contributions do not reconstruct score')
        return {'method':'Exact additive log-odds contributions', 'intercept':float(est.intercept_[0]),
                'logit':logit,'terms':sorted(terms,key=lambda d:abs(d['contribution']),reverse=True)}
    base=float(pipe.predict_proba(row)[0,1]); terms=[]
    for col in LABELS:
        replacement=float(Xtrain[col].median()) if col in ['laufzeit','hoehe','alter'] else int(Xtrain[col].mode()[0])
        modified=row.copy(); modified[col]=replacement
        terms.append({'feature':LABELS[col], 'reference_value':replacement,
                      'contribution':base-float(pipe.predict_proba(modified)[0,1])})
    return {'method':'One-variable replacement sensitivity (not SHAP, not additive)',
            'terms':sorted(terms,key=lambda d:abs(d['contribution']),reverse=True)}


def run():
    X,y=load_data(); split=split_data(X,y)
    tr=split['train']; va=split['validation']; Xtr=X.iloc[tr]; Xva=X.iloc[va]; yt=y[tr]; yv=y[va]
    age=Xva['alter'].to_numpy()
    report={'seed':SEED,'source_sha256':audit.SHA256,'evaluation':'validation_only',
            'split':{k:len(v) for k,v in split.items()},'test_evaluated':False,
            'versions':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'sklearn':sklearn.__version__},
            'baseline':metrics(yv,np.full(len(yv),yt.mean())),
            'models':{},'cases':[]}
    predictions={}; fitted={}
    for kind in ['logistic','forest']:
        for include_age in [True,False]:
            key=kind+('' if include_age else '_no_age')
            pipe=make_model(kind,include_age); pipe.fit(Xtr,yt)
            p=pipe.predict_proba(Xva)[:,1]; predictions[key]=p; fitted[key]=pipe
            report['models'][key]={'name':('Logistic regression' if kind=='logistic' else 'Random Forest')+('' if include_age else ' (without age)'),
                'metrics':metrics(yv,p),'threshold_05':decisions(yv,p),
                'cost_thresholds':[best_threshold(yv,p,r) for r in [1,3,5]],
                'fairness_25':fairness(yv,p,age),'fairness_30':fairness(yv,p,age,cut=30),
                'calibration':calibration(yv,p),'include_age':include_age}
            if include_age:
                imp=permutation_importance(pipe,Xva,yv,scoring='roc_auc',n_repeats=10,random_state=SEED,n_jobs=1)
                report['models'][key]['importance']=sorted([
                    {'feature':LABELS[c],'column':c,'mean':float(m),'std':float(s)}
                    for c,m,s in zip(X.columns,imp.importances_mean,imp.importances_std)],key=lambda d:d['mean'],reverse=True)
                boot=[]
                for k in range(12):
                    rng=np.random.default_rng(SEED+100+k); idx=stratified_bootstrap(yt,rng)
                    rep=make_model(kind,True,SEED+100+k); rep.fit(Xtr.iloc[idx],yt[idx]); boot.append(rep.predict_proba(Xva)[:,1])
                boot=np.asarray(boot)
                report['models'][key]['stability']={'fits':12,'mean_probability_sd':float(boot.std(axis=0,ddof=1).mean()),
                    'decision_disagreement_at_05':float(np.mean((boot>=.5)!=(p[None,:]>=.5))),
                    'auc_range':[float(min(roc_auc_score(yv,b) for b in boot)),float(max(roc_auc_score(yv,b) for b in boot))]}
            print(key, report['models'][key]['metrics'],flush=True)
    rng=np.random.default_rng(SEED)
    samples=[stratified_bootstrap(yv,rng) for _ in range(1000)]
    for key,p in predictions.items():
        values=[roc_auc_score(yv[ix],p[ix]) for ix in samples]
        report['models'][key]['auc_interval_95']=np.quantile(values,[.025,.975]).tolist()
    differences=[roc_auc_score(yv[ix],predictions['forest'][ix])-roc_auc_score(yv[ix],predictions['logistic'][ix]) for ix in samples]
    report['paired_auc_difference']={'forest_minus_logistic':report['models']['forest']['metrics']['auc']-report['models']['logistic']['metrics']['auc'],
                                     'interval_95':np.quantile(differences,[.025,.975]).tolist(),'bootstrap_samples':1000}
    # Every validation record is selectable; outcome remains visible as retrospective evidence.
    for i,rid in enumerate(va):
        report['cases'].append({'row_id':rid+1,'age':int(age[i]),'y_bad':int(yv[i]),
            'duration':int(Xva.iloc[i]['laufzeit']),'amount_transformed':int(Xva.iloc[i]['hoehe']),
            'scores':{key:float(p[i]) for key,p in predictions.items()}})
    # Fixed examples selected by source order, never by best-looking prediction.
    for i in range(3):
        case=report['cases'][i]
        case['explanations']={kind:local_explanation(fitted[kind],Xva.iloc[[i]],kind,Xtr) for kind in ['logistic','forest']}
    results=ROOT/'results'; results.mkdir(exist_ok=True)
    (results/'benchmark.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    (results/'split.json').write_text(json.dumps({'seed':SEED,'indexing':'zero-based data row, excluding header','rows':split},indent=2)+'\n')
    pd.DataFrame([{'row_id':c['row_id'],'y_bad':c['y_bad'],'age':c['age'],**c['scores']} for c in report['cases']]).to_csv(results/'validation_predictions.csv',index=False)
    # Persist fitted pipelines locally for later application work; regenerate rather than download pickle files.
    import joblib
    models=ROOT/'models'; models.mkdir(exist_ok=True)
    for key,pipe in fitted.items(): joblib.dump(pipe,models/(key+'.joblib'))
    (results/'model_spec.json').write_text(json.dumps({'logistic':{'C':1,'max_iter':2000},'forest':{'n_estimators':250,'min_samples_leaf':5,'max_features':'sqrt'},
          'preprocessing':'one-hot categories; standardised duration, amount and age; train-fit only',
          'hyperparameter_search':False,'threshold_grid_step':.01,'stability_bootstrap_fits':12},indent=2)+'\n')
    print('Validation benchmark exported. Test set remains unevaluated.',flush=True)

if __name__=='__main__': run()
