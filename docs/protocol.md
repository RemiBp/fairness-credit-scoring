# Proposed evaluation protocol

Agree on this protocol before comparing models. It can be adapted if the group chooses another dataset.

## Data and target

Original target: `kredit=1` means good credit, `kredit=0` means bad credit. Define `y_bad = 1 - kredit`; a higher predicted probability then means greater bad-credit risk. Do not include `kredit`, row identifiers or the audit group as model inputs.

Use age below 25 versus 25 and above as the primary audit grouping, with a sensitivity analysis at 30. These are analytical cut-offs, not legal thresholds. Keep the age attribute for auditing even in models that exclude it from predictors.

## Splitting and preprocessing

Use a reproducible 60/20/20 train/validation/test split, stratified jointly by target and primary age group. Save the row identifiers and seed. Fit transformations on training data only. Tune hyperparameters and thresholds on validation; reserve the test set for the final frozen comparison.

For the initial logistic and Random Forest pipelines, treat coded variables as categories, including the ordinal codes. Duration, transformed amount and age are numeric. Scale numeric features for logistic regression. Document the preprocessing used by the foundation model. Compare all models on exactly the same evaluation records.

## Four assessment dimensions

### Statistical and economic performance

Report ROC-AUC, average precision, log-loss, Brier score, calibration and confusion matrices. Accept a case when `p_bad < threshold`. Select thresholds on validation data under bad-acceptance to good-refusal cost ratios of 1, 3 and 5.

Cost per 100 cases = `100 * (C_bad * bad_accepted + C_good * good_refused) / N`, with `C_good=1`. These units are illustrative. Costs and calibration refer to this oversampled historical sample, not a real bank portfolio.

### Interpretability

Report logistic coefficients and odds ratios with their feature definitions, and permutation importance for all three models. Explain the same individual cases across models. Document assumptions for local explanation methods, including how correlated predictors affect interpretation. Do not treat model associations as causal effects.

### Stability

Repeat training with different seeds and training samples. Compare probability variation, decision flips and importance rankings on fixed evaluation cases. Use validation during development and avoid choosing configurations based on the final test set. This is resampling stability, not temporal validation: the data lack usable longitudinal tracking.

### Fairness

By age group, report acceptance rate, refusal rate among good credits, and acceptance rate among bad credits, with denominators and between-group differences. Compare models with and without age; excluding age does not remove correlated proxies.

Use uncertainty intervals and paired resampling of evaluation records for model comparisons. State bootstrap strata and handle undefined denominators explicitly. Test-set subgroup estimates will be imprecise. Conditional evaluation uncertainty and variability across fitted models are different quantities and should be reported separately.

## Foundation model feasibility

TabPFN is proposed, not yet executed. Verify access to a specific version and checkpoint, its licence, and compute requirements. Record exact versions and weights. Check whether prior training or benchmarking may overlap this public dataset before making generalisation claims. Reference: https://github.com/PriorLabs/TabPFN

## Final recommendation

Recommend a model in the hypothetical client setting using all four dimensions, including operational constraints and limitations. Separate that educational recommendation from the further data, validation and governance needed for an actual deployment.

## First implementation, 22 September

The baseline implementation follows this split and target convention. Logistic regression and Random Forest, with/without age, have been fitted. No hyperparameter search was performed. Thresholds are explored on validation and their displayed costs are explicitly development estimates. The test set has not been scored.

Global importance uses 10 permutations per original feature. Local logistic terms sum exactly to the logit; the forest uses one-variable median/mode replacement sensitivity, not SHAP. Initial stability uses 12 outcome-stratified bootstrap training resamples. Fairness rates have Wilson intervals conditional on the model and threshold; intervals for between-group differences, explanation-rank stability and the foundation model remain to be added.
