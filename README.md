# Credit scoring

First results for the ISAF group project.

**[Open the interactive report](https://remibp.github.io/fairness-credit-scoring/)** · [HTML file](docs/index.html) · [Dataset proposal](docs/dataset-proposal.pdf)

## Current work

- Logistic regression and Random Forest, each with and without age.
- Validation metrics, simulated costs, age-group comparisons and explanations.
- Initial stability checks and an offline HTML report.

**Still to do:** foundation model, final analysis, new-profile scoring and slides. Dataset approval is pending.

The split is 600 training / 200 validation / 200 test records. The test set has not been scored.

## Reproduce

Tested with Python 3.14.6. The HTML also opens directly, without installation.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python benchmark.py
python build_report.py
```

Open `docs/index.html`. Fitted pipelines are saved locally in `models/` and excluded from Git.

Checks: `python -m unittest discover -s tests -v` and `node tests/test_browser_metrics.cjs`.

## Project files

[Results](docs/results.md) · [Protocol](docs/protocol.md) · [Work plan and deadlines](docs/work-plan.md) · [Source coding table](data/codetable.txt)

Dataset pre-validation: **24 September, 09:40**. Final delivery: **28 September, 09:40**, Paris time.

Contribute through a branch and pull request. Agree on the dataset and roles with the group first.

## Data

[South German Credit](https://doi.org/10.24432/C5QG88), UCI (2020), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The files in `data/` are unchanged; the audit, code and report are additions. Run `python audit.py` to reproduce the source checks without external packages.

Historical data from 1973-1975, oversampled bad credits and transformed amounts. The combined personal-status field cannot reliably identify sex. Results describe this sample, not a current lending population. See the [protocol](docs/protocol.md) for analysis limits.
