# Demo Talk Track

## 20-second reveal

“The reported census says 234 of 240 beds are occupied. Reconciliation shows 18 stale system states, so physical occupancy is 216. That data correction creates decision room, but it does not explain away 92 boarders waiting over four hours. The response is therefore two-track: repair the fact base and use trusted capacity to drive owned flow actions.”

## Five-minute path

1. **Current State:** show 234 → 216 and state that data quality and operational congestion coexist.
2. **Data & ETL:** show the raw-to-curated path, explain preview versus full export, download the 1,500-row curated data, and show one SQL result.
3. **Bottlenecks:** use the unit pressure map to locate where operators should investigate first without claiming automated placement.
4. **Forecast & Statistics:** distinguish forecast, regression, holdout evaluation, and hypothesis testing. State that the regression fails to beat the simple baseline and should not be operationalized.
5. **R companion:** explain `read.csv()` → validation → feature preparation → `lm()` → `predict()` → MAE comparison. State that Python is executed; R is an educational, runtime-unverified translation.
6. **What-if & Action:** change one scenario input, distinguish assumptions from a forecast, then close on owner, deadline, success measure, and human decision.

Use [INTERVIEW_DEMO_GUIDE.md](INTERVIEW_DEMO_GUIDE.md) for the detailed technique explanations, likely interview questions, limitations, and phrases not to overclaim.
