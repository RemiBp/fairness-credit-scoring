# Credit scoring: performance, explanations and fairness

A proposal for the ISAF group project, using the corrected South German Credit dataset. The goal is to compare three approaches to binary credit scoring and explain which trade-offs matter for a hypothetical lender.

**Current status:** logistic regression and Random Forest have been trained, each with and without age. A standalone interactive report shows the computed validation results, costs, explanations and initial stability checks. Group adoption and instructor pre-validation are pending. The tabular foundation model and final recommendation remain to be completed.

**[Open the interactive report](https://remibp.github.io/fairness-credit-scoring/)** or download [docs/index.html](docs/index.html) and open it locally. It works offline.

## Start here

- [Initial two-page dataset proposal, prepared before model development](docs/dataset-proposal.pdf)
- [Computed results and methodology](docs/results.md)
- [Analysis protocol](docs/protocol.md)
- [Work remaining and deadlines](docs/work-plan.md)
- [Audit results](audit/report.json)
- [Column summary](audit/column_summary.csv) and [original coding table](data/codetable.txt)

## What is already done

The original file has been checked against a recorded SHA-256 digest. The audit confirms 1,000 records, 20 predictors and a binary outcome: 700 good and 300 bad credits. There are no duplicate rows, incomplete records or invalid categorical codes. Source categories such as unknown/no savings remain valid categories, not evidence of fully observed information.

For the proposed age comparison, 150 records are below 25 and 850 are 25 or older. A sensitivity check at 30 produces groups of 369 and 631. Only two records are below 20, which is too small for useful subgroup inference.

## Reproduce the audit

Python 3.10 or later; no third-party packages required.

```sh
git clone https://github.com/RemiBp/fairness-credit-scoring.git
cd fairness-credit-scoring
python3 audit.py
```

This regenerates `audit/report.json` and `audit/column_summary.csv`. The source data are unchanged. An unexpected file checksum, schema or category code stops the audit.

## Reproduce the models and report

Tested with Python 3.14.6. Dependencies are pinned in `requirements.txt`.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python benchmark.py
python build_report.py
python -m unittest discover -s tests -v
node tests/test_browser_metrics.cjs
```

Open `docs/index.html` in a browser. The report contains the data it needs and makes no external network requests. Model fitting creates four local `models/*.joblib` pipelines, excluded from Git; regenerate them from the source rather than loading untrusted model files.

`results/split.json` records the fixed 600/200/200 partition. Only validation cases receive predictions in this benchmark. Test rows are reserved for a later frozen evaluation. The HTML explores precomputed validation scores; arbitrary new-profile scoring is not yet implemented.

## Current model comparison

| Model | Role | Status |
|---|---|---|
| Regularised logistic regression | Interpretable baseline | Trained, with/without age |
| Random Forest | Machine-learning comparison | Trained, with/without age |
| Tabular foundation model, TabPFN proposed | Pretrained tabular comparison | Access, version and compute to confirm |

Each model will be assessed on statistical and simulated economic performance, global and local interpretability, stability, and fairness. The final work must discuss trade-offs and make a justified recommendation, rather than rank models by accuracy alone.

## Contributing

First agree on the dataset and divide the work. If the team already has a different dataset, the evaluation protocol can be adapted. Proposed work packages are listed in [the work plan](docs/work-plan.md); no contributor has been assigned a role in advance.

For code changes, use a branch and a pull request. Include a command that reproduces the result and explain any change to the data split or metric definitions. Keep private messages, account details and credentials out of the repository. Anyone can read this public repository; direct pushes require collaborator access. Forks and pull requests are also possible.

## Data and limitations

South German Credit [Dataset] (2020), UCI Machine Learning Repository. [DOI: 10.24432/C5QG88](https://doi.org/10.24432/C5QG88). Dataset licence: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The files in `data/` are unchanged copies of the source files; this repository adds the audit and proposal.

The records are from 1973-1975 and bad credits were oversampled. They do not establish current population default rates. Credit amounts were transformed, so economic comparisons use simulated cost units. Sex cannot reliably be reconstructed from the combined personal-status field. Observed outcome differences between age groups alone do not establish discrimination. This is an educational benchmark, not a production lending system.
