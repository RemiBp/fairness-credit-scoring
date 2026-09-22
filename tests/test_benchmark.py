import json
from pathlib import Path
import unittest
import numpy as np
from benchmark import load_data,split_data,make_model,decisions,fairness,best_threshold,local_explanation,ROOT

class BenchmarkChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.X,cls.y=load_data(); cls.split=split_data(cls.X,cls.y)
        cls.report=json.loads((ROOT/'results/benchmark.json').read_text())

    def test_split_is_disjoint_complete_and_reproducible(self):
        parts=[set(v) for v in self.split.values()]
        self.assertEqual([len(p) for p in parts],[600,200,200])
        self.assertEqual(set.union(*parts),set(range(1000)))
        for i in range(3):
            for j in range(i): self.assertFalse(parts[i]&parts[j])
        saved=json.loads((ROOT/'results/split.json').read_text())['rows']
        self.assertEqual(self.split,saved)
        for key in self.split:
            indices=self.split[key]
            self.assertEqual(set(self.y[indices]),{0,1})
            self.assertEqual(set((self.X.iloc[indices]['alter']<25).astype(int)),{0,1})

    def test_acceptance_direction_cost_and_threshold_boundary(self):
        y=np.array([0,1,0,1]);p=np.array([.1,.2,.5,.9])
        d=decisions(y,p,.5,3)
        self.assertEqual((d['good_accepted'],d['bad_accepted'],d['good_refused'],d['bad_refused']),(1,1,1,1))
        self.assertEqual(d['cost_per_100'],100)
        self.assertEqual(decisions(y,p,0)['accepted'],0)
        self.assertEqual(decisions(y,p,1)['accepted'],4)

    def test_undefined_group_error_rate_is_not_zero(self):
        result=fairness(np.array([0,0,1]),np.array([.1,.8,.9]),np.array([21,22,40]))
        self.assertIsNone(result['below']['bad_acceptance']['rate'])
        self.assertIsNone(result['below']['bad_acceptance']['wilson_95'])

    def test_preprocessing_only_fits_training_and_excludes_target(self):
        ids=self.split['train']; Xtr=self.X.iloc[ids]
        pipe=make_model('logistic');pipe.fit(Xtr,self.y[ids])
        scaler=pipe.named_steps['preprocess'].named_transformers_['numeric']
        np.testing.assert_allclose(scaler.mean_,Xtr[['laufzeit','hoehe','alter']].mean().to_numpy())
        self.assertFalse(any('kredit' in n for n in pipe.named_steps['preprocess'].get_feature_names_out()))
        unseen=self.X.iloc[self.split['validation'][:1]].copy();unseen['verw']=999
        self.assertTrue(np.isfinite(pipe.predict_proba(unseen)).all())
        exp=local_explanation(pipe,Xtr.iloc[[0]],'logistic',Xtr)
        score=1/(1+np.exp(-exp['logit']))
        self.assertAlmostEqual(score,pipe.predict_proba(Xtr.iloc[[0]])[0,1])

    def test_no_age_model_really_ignores_age(self):
        ids=self.split['train'];pipe=make_model('logistic',False);pipe.fit(self.X.iloc[ids],self.y[ids])
        original=self.X.iloc[self.split['validation'][:5]].copy()
        changed=original.copy();changed['alter']=999
        np.testing.assert_array_equal(pipe.predict_proba(original),pipe.predict_proba(changed))

    def test_exports_exclude_test_predictions(self):
        r=self.report
        self.assertFalse(r['test_evaluated'])
        self.assertEqual({c['row_id']-1 for c in r['cases']},set(self.split['validation']))
        for c in r['cases']:
            self.assertTrue(all(0<=p<=1 for p in c['scores'].values()))
            self.assertEqual(c['y_bad'],int(self.y[c['row_id']-1]))
        self.assertEqual(set(r['models']),{'logistic','forest','logistic_no_age','forest_no_age'})

    def test_exported_decisions_and_threshold_costs(self):
        r=self.report;y=np.array([c['y_bad'] for c in r['cases']])
        for key,m in r['models'].items():
            p=np.array([c['scores'][key] for c in r['cases']])
            self.assertEqual(decisions(y,p),m['threshold_05'])
            for threshold in m['cost_thresholds']:
                self.assertEqual(best_threshold(y,p,threshold['ratio']),threshold)

    def test_report_is_standalone_and_contains_same_results(self):
        import re
        html=(ROOT/'docs/index.html').read_text()
        encoded=re.search(r'<script id="benchmark-data" type="application/json">(.*?)</script>',html,re.S).group(1)
        self.assertEqual(json.loads(encoded),self.report)
        self.assertNotRegex(html,r'<script[^>]+src=')
        self.assertNotIn('Duvo',html)
        self.assertNotIn('__DATA__',html)

if __name__=='__main__': unittest.main()
