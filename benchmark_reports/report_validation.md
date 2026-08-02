# RuleChef Benchmark Report

Dataset split: **validation**

Generated: 2026-08-02 12:10:20.632513

## Overall Metrics

| Metric | Value |
|---|---|
| dataset | validation |
| total_samples | 30 |
| covered_samples | 23 |
| unknown_samples | 7 |
| coverage | 0.7667 |
| overall_accuracy | 0.7000 |
| overall_precision_macro | 0.9187 |
| overall_recall_macro | 0.7143 |
| overall_f1_macro | 0.7846 |
| overall_precision_weighted | 0.9175 |
| overall_recall_weighted | 0.7000 |
| overall_f1_weighted | 0.7750 |
| covered_accuracy | 0.9130 |
| covered_precision_macro | 0.9187 |
| covered_recall_macro | 0.9143 |
| covered_f1_macro | 0.9085 |
| covered_precision_weighted | 0.9272 |
| covered_recall_weighted | 0.9130 |
| covered_f1_weighted | 0.9128 |

## Per-Class Performance

| Class | Support | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| psoriasis | 8 | 1.000 | 0.500 | 0.667 |
| varicose veins | 8 | 0.800 | 0.500 | 0.615 |
| typhoid | 7 | 1.000 | 0.857 | 0.923 |
| chicken pox | 7 | 0.875 | 1.000 | 0.933 |

## Rules

| Rule | Class | TP | FP | Precision | Recall | F1 |
|---|---|---:|---:|---:|---:|---:|
| typhoid_gi_fever_combination | typhoid | 6 | 0 | 1.000 | 0.857 | 0.923 |
| ChickenPox_RedSpots_Systemic | chicken pox | 4 | 0 | 1.000 | 0.571 | 0.727 |
| Psoriasis_NailIssues | psoriasis | 3 | 0 | 1.000 | 0.375 | 0.545 |
| Psoriasis_JointPainSymptoms | psoriasis | 1 | 0 | 1.000 | 0.125 | 0.222 |
| VaricoseVeins_LegCramps | varicose veins | 2 | 0 | 1.000 | 0.250 | 0.400 |
| ChickenPox_LymphNodes | chicken pox | 1 | 0 | 1.000 | 0.143 | 0.250 |
| VaricoseVeins_VeinVisualSymptoms | varicose veins | 1 | 0 | 1.000 | 0.125 | 0.222 |
| VaricoseVeins_ActivityAggravatedLegDiscomfort | varicose veins | 1 | 0 | 1.000 | 0.125 | 0.222 |
| ChickenPox_SystemicSymptoms | chicken pox | 2 | 1 | 0.667 | 0.286 | 0.400 |
| ChickenPox_FatigueEnergyLoss | chicken pox | 0 | 0 | 0.000 | 0.000 | 0.000 |
| Typhoid_SystemicAbdominal | typhoid | 0 | 0 | 0.000 | 0.000 | 0.000 |
| ChickenPox_AppetiteLoss | chicken pox | 0 | 0 | 0.000 | 0.000 | 0.000 |
| VaricoseVeins_LegRashSymptoms | varicose veins | 0 | 1 | 0.000 | 0.000 | 0.000 |
| ChickenPox_Rashes_Itch_NoNegs | chicken pox | 0 | 0 | 0.000 | 0.000 | 0.000 |
| Psoriasis_SpecificSkinManifestations | psoriasis | 0 | 0 | 0.000 | 0.000 | 0.000 |
| VaricoseVeins_UnexplainedBruisingLegs | varicose veins | 0 | 0 | 0.000 | 0.000 | 0.000 |
| Psoriasis_PalmsSolesFissures | psoriasis | 0 | 0 | 0.000 | 0.000 | 0.000 |

## False-Positive Examples

### ChickenPox_SystemicSymptoms

- **True:** typhoid
- **Predicted:** chicken pox
- **Text:** i have been feeling really fatigued and weak, and i can't seem to get rid of it. i have a mild fever and a strange pain in my abdominal area. i can't understand what is happening.

### VaricoseVeins_LegRashSymptoms

- **True:** psoriasis
- **Predicted:** varicose veins
- **Text:** i've seen a sudden peeling of skin on various regions of my body, mostly my arms, legs, and back. in addition, i have significant joint pain and skin rashes. the rash is spreading to different parts of my body.

## True-Positive Examples

### typhoid_gi_fever_combination

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** i have developed diarrhea. it is accompanied by severe pain in my belly area. i don't feel like eating anything, and most of the time, i have a mild headache.

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** i've been experiencing high fever, especially at night. it's been really uncomfortable. there is a mild headache along with constipation and diarrhea.

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** i've lost a lot of weight in the past week because i haven't been able to eat much due to nausea and vomiting. this is followed by mild fever, headache and belly pain. i'm really concerned about my health.

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** i have been experiencing diarrhea and have had loose, watery stools several times a day. i have lost my appetite and feel nauseated all the time. i am starting to get a mild fever too.

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** i've had a persistent stomach pain for the past week, and it is not healing even with medication. i feel like vomiting and can't eat anything, and because of which i have become extremely weak.

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** the stomach discomfort has been severe and frequent. vomiting and constipation have also happened. i'm concerned about my health.

### ChickenPox_RedSpots_Systemic

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i am starting to develop tiny red spots all over my face and neck area, and it itches when i touch them. the itching is making my day very uncomfortable.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i am exhausted and have lost my appetite. i feel vomiting and can't eat anything. in addition, little red spots are beginning to appear on my skin and near the neck. i am really worried about my health.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i'm worried about these red spots on my skin. it's spreading rapidly and causing a lot of problems. i also developed a mild fever and headache every night.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** there are small red spots all over my body that i can't explain. the bumps are itchy and uncomfortable and seem to spread rapidly. it's worrying me.

### Psoriasis_NailIssues

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** the skin around my mouth, nose, and eyes is red and inflamed. it is often itchy and uncomfortable. there is a noticeable inflammation in my nails.

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** i have experienced difficulty sleeping due to the itching and discomfort caused by the rash. there are small dents in my nails, which is really concerning.

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** my nails are starting to have small pits on them. i am worried and don't know what is causing it. also, my joints pain and there are rashes on my arms and back.

### Psoriasis_JointPainSymptoms

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** i have noticed a sudden peeling of skin at different parts of my body, mainly arms, legs and back. also, i face severe joint pain and skin rashes.

### VaricoseVeins_LegCramps

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** i have noticed cramps in my calves are becoming more frequent and intense. it is causing me a lot of discomforts. i am also overweight and my legs have started to swell.

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** walking is tough for me because of cramps in my calves. obesity, i believe, is the cause of this. after a while of working, i'm exhausted.

### ChickenPox_LymphNodes

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i have small lymph nodes on my arms and face. the itching is making my day very uncomfortable.

### VaricoseVeins_VeinVisualSymptoms

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** the prominent veins on my calves are causing self-consciousness and embarrassment. they are swollen and protrude from my skin, making them very noticeable.

### VaricoseVeins_ActivityAggravatedLegDiscomfort

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** standing or walking for long periods of time causes a lot of pain in my legs. i get cramps upon doing physical activities. there are bruise marks on my legs too.

### ChickenPox_SystemicSymptoms

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i have swollen red lymph nodes on my arms and legs that itch when i touch them. i'm also suffering from a terrible headache and a mild fever. i don't feel like eating anything and have lost my appetite.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** there are red swollen spots all over my body. it itches if i touch them. moreover, i also have a high fever and headache and always feel exhausted.

## Weak Rules
- ChickenPox_FatigueEnergyLoss (chicken pox): precision=0.000, recall=0.000, FP=0
- Typhoid_SystemicAbdominal (typhoid): precision=0.000, recall=0.000, FP=0
- ChickenPox_AppetiteLoss (chicken pox): precision=0.000, recall=0.000, FP=0
- VaricoseVeins_LegRashSymptoms (varicose veins): precision=0.000, recall=0.000, FP=1
- ChickenPox_Rashes_Itch_NoNegs (chicken pox): precision=0.000, recall=0.000, FP=0
- Psoriasis_SpecificSkinManifestations (psoriasis): precision=0.000, recall=0.000, FP=0
- VaricoseVeins_UnexplainedBruisingLegs (varicose veins): precision=0.000, recall=0.000, FP=0
- Psoriasis_PalmsSolesFissures (psoriasis): precision=0.000, recall=0.000, FP=0
- ChickenPox_SystemicSymptoms (chicken pox): precision=0.667, recall=0.286, FP=1

## Rule Improvement Suggestions

### typhoid_gi_fever_combination
- Rule looks stable.

### ChickenPox_RedSpots_Systemic
- Rule looks stable.

### Psoriasis_NailIssues
- Consider adding alternative symptom patterns.

### Psoriasis_JointPainSymptoms
- Consider adding alternative symptom patterns.

### VaricoseVeins_LegCramps
- Consider adding alternative symptom patterns.

### ChickenPox_LymphNodes
- Consider adding alternative symptom patterns.

### VaricoseVeins_VeinVisualSymptoms
- Consider adding alternative symptom patterns.

### VaricoseVeins_ActivityAggravatedLegDiscomfort
- Consider adding alternative symptom patterns.

### ChickenPox_SystemicSymptoms
- Consider adding alternative symptom patterns.

### ChickenPox_FatigueEnergyLoss
- Require additional symptoms before firing. Consider adding alternative symptom patterns.

### Typhoid_SystemicAbdominal
- Require additional symptoms before firing. Consider adding alternative symptom patterns.

### ChickenPox_AppetiteLoss
- Require additional symptoms before firing. Consider adding alternative symptom patterns.

### VaricoseVeins_LegRashSymptoms
- Require additional symptoms before firing. Consider adding alternative symptom patterns. Inspect false-positive examples and refine the regex.

### ChickenPox_Rashes_Itch_NoNegs
- Require additional symptoms before firing. Consider adding alternative symptom patterns.

### Psoriasis_SpecificSkinManifestations
- Require additional symptoms before firing. Consider adding alternative symptom patterns.

### VaricoseVeins_UnexplainedBruisingLegs
- Require additional symptoms before firing. Consider adding alternative symptom patterns.

### Psoriasis_PalmsSolesFissures
- Require additional symptoms before firing. Consider adding alternative symptom patterns.