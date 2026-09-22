# First computed results

Development results on 200 validation cases. The 200 test cases remain unevaluated. Dataset approval and group adoption are pending.

| Model | ROC-AUC | Average precision | Log-loss | Brier |
|---|---:|---:|---:|---:|
| Logistic regression | 0.8049 | 0.6487 | 0.4842 | 0.1579 |
| Logistic regression (without age) | 0.8013 | 0.6458 | 0.4896 | 0.1592 |
| Random Forest | 0.8121 | 0.6711 | 0.4943 | 0.1621 |
| Random Forest (without age) | 0.8051 | 0.6480 | 0.4965 | 0.1630 |

Forest minus logistic AUC is 0.0073, with a paired 95% bootstrap interval [-0.0289, 0.0451]. The interval includes zero. Logistic regression has lower log-loss and Brier score on this split. This is not enough to select a production model.

## What the report includes

- Logistic regression and Random Forest, plus versions without age.
- Constant probability baseline, calibration, and costs for three illustrative error-cost ratios.
- Interactive threshold and age-group comparisons, with denominators and Wilson intervals.
- Global permutation importance; exact local logistic contributions and forest replacement sensitivity for three fixed examples.
- Twelve bootstrap training resamples for score and decision stability.
- One thousand paired bootstrap validation samples for AUC intervals.

## Interpretation limits

Validation is used for development and threshold selection. The lowest-cost threshold and its displayed cost are evaluated on the same data and may be optimistic. The test partition is reserved for frozen decisions. No claim of real-world probability calibration, profit or discrimination is justified by this historical oversampled benchmark.

The foundation model, explanation-rank stability, richer uncertainty analysis, arbitrary new-profile scoring and final slides still need work. The interactive report is a working example, not the final assignment.

## Sources and reproduction

Data: [South German Credit](https://doi.org/10.24432/C5QG88), UCI, CC BY 4.0. Implementation: [scikit-learn permutation importance](https://scikit-learn.org/1.7/modules/permutation_importance.html), [OneHotEncoder](https://scikit-learn.org/1.7/modules/generated/sklearn.preprocessing.OneHotEncoder.html).

Run `python benchmark.py` and `python build_report.py` after installing `requirements.txt`. Exact model parameters, versions, partition and per-case validation predictions are in `results/`.
