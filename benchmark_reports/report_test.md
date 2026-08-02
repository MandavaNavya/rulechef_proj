# RuleChef Benchmark Report

Dataset split: **test**

Generated: 2026-08-02 12:10:20.730353

## Overall Metrics

| Metric | Value |
|---|---|
| dataset | test |
| total_samples | 30 |
| covered_samples | 22 |
| unknown_samples | 8 |
| coverage | 0.7333 |
| overall_accuracy | 0.6000 |
| overall_precision_macro | 0.8571 |
| overall_recall_macro | 0.5938 |
| overall_f1_macro | 0.6706 |
| overall_precision_weighted | 0.8571 |
| overall_recall_weighted | 0.6000 |
| overall_f1_weighted | 0.6767 |
| covered_accuracy | 0.8182 |
| covered_precision_macro | 0.8571 |
| covered_recall_macro | 0.8512 |
| covered_f1_macro | 0.8516 |
| covered_precision_weighted | 0.8312 |
| covered_recall_weighted | 0.8182 |
| covered_f1_weighted | 0.8217 |

## Per-Class Performance

| Class | Support | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| psoriasis | 7 | 1.000 | 0.286 | 0.444 |
| varicose veins | 7 | 0.714 | 0.714 | 0.714 |
| typhoid | 8 | 1.000 | 0.750 | 0.857 |
| chicken pox | 8 | 0.714 | 0.625 | 0.667 |

## Rules

| Rule | Class | TP | FP | Precision | Recall | F1 |
|---|---|---:|---:|---:|---:|---:|
| typhoid_gi_fever_combination | typhoid | 6 | 0 | 1.000 | 0.750 | 0.857 |
| VaricoseVeins_VeinVisualSymptoms | varicose veins | 4 | 0 | 1.000 | 0.571 | 0.727 |
| ChickenPox_SystemicSymptoms | chicken pox | 2 | 0 | 1.000 | 0.250 | 0.400 |
| ChickenPox_RedSpots_Systemic | chicken pox | 3 | 0 | 1.000 | 0.375 | 0.545 |
| Psoriasis_NailIssues | psoriasis | 1 | 0 | 1.000 | 0.143 | 0.250 |
| Psoriasis_PalmsSolesFissures | psoriasis | 1 | 0 | 1.000 | 0.143 | 0.250 |
| VaricoseVeins_LegCramps | varicose veins | 1 | 0 | 1.000 | 0.143 | 0.250 |
| ChickenPox_FatigueEnergyLoss | chicken pox | 0 | 2 | 0.000 | 0.000 | 0.000 |
| Typhoid_SystemicAbdominal | typhoid | 0 | 0 | 0.000 | 0.000 | 0.000 |
| VaricoseVeins_LegRashSymptoms | varicose veins | 0 | 2 | 0.000 | 0.000 | 0.000 |
| ChickenPox_AppetiteLoss | chicken pox | 0 | 0 | 0.000 | 0.000 | 0.000 |
| ChickenPox_LymphNodes | chicken pox | 0 | 0 | 0.000 | 0.000 | 0.000 |
| Psoriasis_SpecificSkinManifestations | psoriasis | 0 | 0 | 0.000 | 0.000 | 0.000 |
| VaricoseVeins_UnexplainedBruisingLegs | varicose veins | 0 | 0 | 0.000 | 0.000 | 0.000 |
| ChickenPox_Rashes_Itch_NoNegs | chicken pox | 0 | 0 | 0.000 | 0.000 | 0.000 |
| VaricoseVeins_ActivityAggravatedLegDiscomfort | varicose veins | 0 | 0 | 0.000 | 0.000 | 0.000 |
| Psoriasis_JointPainSymptoms | psoriasis | 0 | 0 | 0.000 | 0.000 | 0.000 |

## False-Positive Examples

### ChickenPox_FatigueEnergyLoss

- **True:** varicose veins
- **Predicted:** chicken pox
- **Text:** my calves have been cramping up when i walk or stand for long periods of time. there are bruise marks on my calves, which is making me worried. i feel tired very soon.

- **True:** typhoid
- **Predicted:** chicken pox
- **Text:** i am having some diarrhea and constipation, which has been quite concerning. in my stomach, there is a severe, painful ache. i'm constantly exhausted and don't feel like eating anything.

### VaricoseVeins_LegRashSymptoms

- **True:** chicken pox
- **Predicted:** varicose veins
- **Text:** the rash on my skin is causing a lot of discomforts. it's red and inflamed, spreading all over my body. the rash is accompanied by intense itching, especially on my arms and legs.

- **True:** chicken pox
- **Predicted:** varicose veins
- **Text:** i have a skin rash that's red and inflamed, and it's spreading all over my body. i've been experiencing intense itching, especially on my arms and legs.

## True-Positive Examples

### typhoid_gi_fever_combination

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** i've lost a lot of weight in the last week because i couldn't eat much due to nausea and vomiting. this is followed by a high fever, headache, and stomach pain.

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** i've had a lot of bloating and constipation, which has been really painful. there is a lot of pressure and pain in my stomach area. i get a high fever and chills every night.

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** most of the time i feel fatigued. i don't want to eat anything. i get a high fever and chills every night. moreover, i have been vomiting since yesterday.

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** i've had a persistent headache for the past week, and it's been getting worse. it's been accompanied by belly aches, constipation and diarrhea.

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** i am experiencing extreme belly pain and constipation. every night, i have a severe fever along with chills and headaches. the last couple of days has been really uncomfortable.

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** i've also been experiencing some diarrhea and constipation, which has been really worrying. it feels like a sharp, stabbing pain in my belly area. i feel tired all the time.

### VaricoseVeins_VeinVisualSymptoms

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** my veins of legs have become more visible and swollen than normal. they are visible through my skin and it hurts when i move.

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** the veins on my legs are very noticeable and are causing me a lot of discomforts. they are swollen and protrude from my skin, making them visible through my clothing.

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** the veins on my legs are causing a lot of discomforts when i sit for long periods of time. they are swollen and protruding from my skin, making them painful and noticeable.

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** the skin around the veins on my legs is red and inflamed. i believe i can see some of the swollen blood vessels. i am really worried about it.

### ChickenPox_SystemicSymptoms

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i've had a mild fever for the past few days, and it's starting to worry me. the fever has been accompanied by a severe headache. i feel weak and lethargic.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** the itching is making it hard for me to sleep at night. i can't get any rest. i have also lost my appetite and feel lethargic.

### ChickenPox_RedSpots_Systemic

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i have red spots on my arms and legs and itching them makes it difficult for me to sleep at night. i also have severe headaches and a mild fever.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i have swollen lymph nodes and red spots all over my body, and they are causing discomfort. i also have a mild fever and feel tired most of the time.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** there are small red spots all over my body. the spots are itchy and uncomfortable. i also have a mild fever and headache.

### Psoriasis_NailIssues

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** my nails have small dents on them. even my joints have started to pain severely. there is a silver like dusting on my skin, particularly in my back.

### Psoriasis_PalmsSolesFissures

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** the skin on my palms and soles is thickened and has deep cracks. these cracks are painful and bleed easily.

### VaricoseVeins_LegCramps

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** the cramps in my calves have been making it difficult for me to walk and do my daily activities. they come on suddenly and last for several minutes.

## Weak Rules
- ChickenPox_FatigueEnergyLoss (chicken pox): precision=0.000, recall=0.000, FP=2
- Typhoid_SystemicAbdominal (typhoid): precision=0.000, recall=0.000, FP=0
- VaricoseVeins_LegRashSymptoms (varicose veins): precision=0.000, recall=0.000, FP=2
- ChickenPox_AppetiteLoss (chicken pox): precision=0.000, recall=0.000, FP=0
- ChickenPox_LymphNodes (chicken pox): precision=0.000, recall=0.000, FP=0
- Psoriasis_SpecificSkinManifestations (psoriasis): precision=0.000, recall=0.000, FP=0
- VaricoseVeins_UnexplainedBruisingLegs (varicose veins): precision=0.000, recall=0.000, FP=0
- ChickenPox_Rashes_Itch_NoNegs (chicken pox): precision=0.000, recall=0.000, FP=0
- VaricoseVeins_ActivityAggravatedLegDiscomfort (varicose veins): precision=0.000, recall=0.000, FP=0
- Psoriasis_JointPainSymptoms (psoriasis): precision=0.000, recall=0.000, FP=0

## Rule Improvement Suggestions

### typhoid_gi_fever_combination
- Rule looks stable.

### VaricoseVeins_VeinVisualSymptoms
- Rule looks stable.

### ChickenPox_SystemicSymptoms
- Consider adding alternative symptom patterns.

### ChickenPox_RedSpots_Systemic
- Consider adding alternative symptom patterns.

### Psoriasis_NailIssues
- Consider adding alternative symptom patterns.

### Psoriasis_PalmsSolesFissures
- Consider adding alternative symptom patterns.

### VaricoseVeins_LegCramps
- Consider adding alternative symptom patterns.

### ChickenPox_FatigueEnergyLoss
- Require additional symptoms before firing. Consider adding alternative symptom patterns. Inspect false-positive examples and refine the regex.

### Typhoid_SystemicAbdominal
- Require additional symptoms before firing. Consider adding alternative symptom patterns.

### VaricoseVeins_LegRashSymptoms
- Require additional symptoms before firing. Consider adding alternative symptom patterns. Inspect false-positive examples and refine the regex.

### ChickenPox_AppetiteLoss
- Require additional symptoms before firing. Consider adding alternative symptom patterns.

### ChickenPox_LymphNodes
- Require additional symptoms before firing. Consider adding alternative symptom patterns.

### Psoriasis_SpecificSkinManifestations
- Require additional symptoms before firing. Consider adding alternative symptom patterns.

### VaricoseVeins_UnexplainedBruisingLegs
- Require additional symptoms before firing. Consider adding alternative symptom patterns.

### ChickenPox_Rashes_Itch_NoNegs
- Require additional symptoms before firing. Consider adding alternative symptom patterns.

### VaricoseVeins_ActivityAggravatedLegDiscomfort
- Require additional symptoms before firing. Consider adding alternative symptom patterns.

### Psoriasis_JointPainSymptoms
- Require additional symptoms before firing. Consider adding alternative symptom patterns.