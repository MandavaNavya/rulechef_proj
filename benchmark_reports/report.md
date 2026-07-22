# RuleChef Benchmark Report

Generated: 2026-07-22 13:44:10.332763

## Overall Metrics

|Metric|Value|
|---|---|
|coverage|0.7333|
|covered_samples|11|
|total_samples|15|
|accuracy|0.9091|
|precision_macro|0.9375|
|recall_macro|0.8750|
|f1_macro|0.8952|
|precision_micro|0.9091|
|recall_micro|0.9091|
|f1_micro|0.9091|
|precision_weighted|0.9205|
|recall_weighted|0.9091|
|f1_weighted|0.9056|

## Top Rules

|Rule|Precision|Recall|Coverage|
|---|---|---|---|
|Rule_Psoriasis_NailJointSpecific|2.000|1.000|0.267|
|Rule_VaricoseVeins_LegSwelling|2.000|0.571|0.133|
|Rule_VaricoseVeins_CrampsAndContext|2.000|0.286|0.067|
|Rule_Psoriasis_SkinSymptoms|1.400|0.875|0.333|
|Rule_VaricoseVeins_ExplicitVeins|1.000|0.286|0.133|

## Weak Rules

|Rule|Precision|Recall|Coverage|
|---|---|---|---|
|Rule_Psoriasis_WinterSensitivity|0.000|0.000|0.000|
|Rule_VaricoseVeins_LegRashWithoutPsoriasisMarkers|0.000|0.000|0.000|
|Rule_VaricoseVeins_LegPainFromActivity|0.000|0.000|0.000|

## Rule Improvement Suggestions

### Rule_Psoriasis_NailJointSpecific

- Rule looks stable.

### Rule_VaricoseVeins_LegSwelling

- Rule looks stable.

### Rule_VaricoseVeins_CrampsAndContext

- Consider adding alternative symptom patterns.

### Rule_Psoriasis_SkinSymptoms

- Rule looks stable.

### Rule_VaricoseVeins_ExplicitVeins

- Consider adding alternative symptom patterns.

### Rule_Psoriasis_WinterSensitivity

- Require additional symptoms before firing. Consider adding alternative symptom patterns.

### Rule_VaricoseVeins_LegRashWithoutPsoriasisMarkers

- Require additional symptoms before firing. Consider adding alternative symptom patterns.

### Rule_VaricoseVeins_LegPainFromActivity

- Require additional symptoms before firing. Consider adding alternative symptom patterns.


## Misclassified Samples

**Rule:** 2cbf1f6c

- True: varicose veins

- Predicted: psoriasis

- Text: the skin around the veins on my legs is dry and flaky. it seems there is a major bruise and my legs have started to swell.


## Rule Quality

|Rule|Quality|Score|
|---|---|---|
|Rule_Psoriasis_NailJointSpecific|Excellent|100|
|Rule_VaricoseVeins_LegSwelling|Excellent|100|
|Rule_VaricoseVeins_CrampsAndContext|Good|80|
|Rule_Psoriasis_SkinSymptoms|Excellent|100|
|Rule_VaricoseVeins_ExplicitVeins|Good|80|
|Rule_Psoriasis_WinterSensitivity|Poor|35|
|Rule_VaricoseVeins_LegRashWithoutPsoriasisMarkers|Poor|35|
|Rule_VaricoseVeins_LegPainFromActivity|Poor|35|