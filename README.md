# Credit scoring: performance, explanations and fairness

A proposal for the ISAF group project, using the corrected South German Credit dataset. The goal is to compare three approaches to binary credit scoring and explain which trade-offs matter for a hypothetical lender.

**Current status:** dataset proposal and reproducible audit. Group adoption and instructor pre-validation are pending. No models have been trained; no model performance or final deployment recommendation is claimed.

## Start here

- [Two-page dataset proposal](docs/dataset-proposal.pdf)
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

## Proposed comparison

| Model | Role | Status |
|---|---|---|
| Regularised logistic regression | Interpretable baseline | Planned |
| Random Forest | Machine-learning comparison | Planned |
| Tabular foundation model, TabPFN proposed | Pretrained tabular comparison | Access, version and compute to confirm |

Each model will be assessed on statistical and simulated economic performance, global and local interpretability, stability, and fairness. The final work must discuss trade-offs and make a justified recommendation, rather than rank models by accuracy alone.

## Contributing

First agree on the dataset and divide the work. If the team already has a different dataset, the evaluation protocol can be adapted. Proposed work packages are listed in [the work plan](docs/work-plan.md); no contributor has been assigned a role in advance.

For code changes, use a branch and a pull request. Include a command that reproduces the result and explain any change to the data split or metric definitions. Keep private messages, account details and credentials out of the repository. Anyone can read this public repository; direct pushes require collaborator access. Forks and pull requests are also possible.

## Data and limitations

South German Credit [Dataset] (2020), UCI Machine Learning Repository. [DOI: 10.24432/C5QG88](https://doi.org/10.24432/C5QG88). Dataset licence: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The files in `data/` are unchanged copies of the source files; this repository adds the audit and proposal.

The records are from 1973-1975 and bad credits were oversampled. They do not establish current population default rates. Credit amounts were transformed, so economic comparisons use simulated cost units. Sex cannot reliably be reconstructed from the combined personal-status field. Observed outcome differences between age groups alone do not establish discrimination. This is an educational benchmark, not a production lending system.
