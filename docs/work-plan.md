# Work plan

This is a starting proposal for the team. Dataset selection and role allocation require group agreement.

## Assignment requirements

The ISAF project description specifies groups of six, constituted by the student representatives. Confirm the official group composition before submission.

- Binary scoring problem for a hypothetical client.
- Three models: one white-box model, one machine-learning model and one tabular foundation model.
- For each: statistical and economic performance, global and local interpretability, stability and fairness.
- Explain trade-offs and justify a recommendation to the client.
- Deliver slides, complete analysis code/notebook and an interactive application or website.
- Presentation: 15 minutes plus 10 minutes of questions. Every member must understand the entire project.

The assignment does not explicitly require a public repository or a production server. The application must let the client interact with, use and test the models. A tested, documented launch procedure is part of the planned handover; confirm any hosting preference with the instructor.

## Official deadlines

| Date, Paris time | Requirement |
|---|---|
| Thursday 24 September 2026, 09:40 | Submit the dataset for instructor pre-validation |
| Monday 28 September 2026, 09:40 | Send all final deliverables by email to the instructor |
| Monday 28 September 2026, 09:40-17:50 | Presentations; individual slot to be confirmed |

Source: ISAF Project Description, HEC Paris, 2026-2027. Refer to the course channel for the original assignment and instructor contact. This repository is a collaboration space, not evidence of submission or acceptance.

## Suggested work packages

| Package | Output | Current state |
|---|---|---|
| Data and protocol | Source checks, coding, fixed split, common metric definitions | Audit, proposal and fixed 600/200/200 split implemented |
| Logistic regression | Reproducible baseline and explanations | Trained; exact local log-odds contributions |
| Random Forest | Comparable baseline and explanations | Trained; permutation importance and local sensitivity |
| Foundation model | Third model, pinned version/checkpoint, shared evaluation cases | Feasibility to confirm |
| Stability and fairness | Common analyses with uncertainty and limitations | Initial resampling, age metrics and intervals implemented; explanation-rank stability pending |
| Application and integration | Interactive comparison, slides and reproducible handover | Offline HTML explorer implemented; free-form scoring, third model and slides pending |

Suggested contribution from Rémi: data preparation and initial logistic/Random Forest benchmark, subject to the team's plans. Packages need not map one-to-one to members, and everyone must review the final work.

## Completion checks

- Another member can reproduce the analysis from a clean checkout.
- All three models use the same held-out cases; no tuning uses test outcomes.
- Scores, target direction, thresholds and costs are explicit.
- Explanations, stability and fairness are evaluated, not only described.
- Application starts from documented commands and reproduces the saved results.
- Slides match computed results and fit the presentation time.
- All members can answer questions beyond their own section.

## Development report

The current HTML report uses validation results only. The initial PDF proposal remains as a dated record of the dataset choice. No final project has been submitted and no instructor approval is claimed.
