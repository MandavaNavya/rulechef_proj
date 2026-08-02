# RuleChef Benchmark Report

Dataset split: **train**

Generated: 2026-08-02 12:10:20.524535

## Overall Metrics

| Metric | Value |
|---|---|
| dataset | train |
| total_samples | 140 |
| covered_samples | 113 |
| unknown_samples | 27 |
| coverage | 0.8071 |
| overall_accuracy | 0.7643 |
| overall_precision_macro | 0.9562 |
| overall_recall_macro | 0.7643 |
| overall_f1_macro | 0.8405 |
| overall_precision_weighted | 0.9562 |
| overall_recall_weighted | 0.7643 |
| overall_f1_weighted | 0.8405 |
| covered_accuracy | 0.9469 |
| covered_precision_macro | 0.9562 |
| covered_recall_macro | 0.9477 |
| covered_f1_macro | 0.9492 |
| covered_precision_weighted | 0.9531 |
| covered_recall_weighted | 0.9469 |
| covered_f1_weighted | 0.9471 |

## Per-Class Performance

| Class | Support | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| psoriasis | 35 | 1.000 | 0.657 | 0.793 |
| varicose veins | 35 | 0.957 | 0.629 | 0.759 |
| typhoid | 35 | 1.000 | 0.829 | 0.906 |
| chicken pox | 35 | 0.868 | 0.943 | 0.904 |

## Rules

| Rule | Class | TP | FP | Precision | Recall | F1 |
|---|---|---:|---:|---:|---:|---:|
| typhoid_gi_fever_combination | typhoid | 24 | 0 | 1.000 | 0.686 | 0.814 |
| Typhoid_SystemicAbdominal | typhoid | 5 | 0 | 1.000 | 0.143 | 0.250 |
| VaricoseVeins_VeinVisualSymptoms | varicose veins | 13 | 0 | 1.000 | 0.371 | 0.542 |
| ChickenPox_RedSpots_Systemic | chicken pox | 12 | 0 | 1.000 | 0.343 | 0.511 |
| Psoriasis_NailIssues | psoriasis | 10 | 0 | 1.000 | 0.286 | 0.444 |
| Psoriasis_JointPainSymptoms | psoriasis | 4 | 0 | 1.000 | 0.114 | 0.205 |
| Psoriasis_SpecificSkinManifestations | psoriasis | 8 | 0 | 1.000 | 0.229 | 0.372 |
| ChickenPox_LymphNodes | chicken pox | 3 | 0 | 1.000 | 0.086 | 0.158 |
| VaricoseVeins_UnexplainedBruisingLegs | varicose veins | 3 | 0 | 1.000 | 0.086 | 0.158 |
| VaricoseVeins_LegCramps | varicose veins | 2 | 0 | 1.000 | 0.057 | 0.108 |
| Psoriasis_PalmsSolesFissures | psoriasis | 1 | 0 | 1.000 | 0.029 | 0.056 |
| VaricoseVeins_ActivityAggravatedLegDiscomfort | varicose veins | 1 | 0 | 1.000 | 0.029 | 0.056 |
| ChickenPox_Rashes_Itch_NoNegs | chicken pox | 7 | 1 | 0.875 | 0.200 | 0.326 |
| ChickenPox_SystemicSymptoms | chicken pox | 8 | 2 | 0.800 | 0.229 | 0.356 |
| VaricoseVeins_LegRashSymptoms | varicose veins | 3 | 1 | 0.750 | 0.086 | 0.154 |
| ChickenPox_FatigueEnergyLoss | chicken pox | 2 | 1 | 0.667 | 0.057 | 0.105 |
| ChickenPox_AppetiteLoss | chicken pox | 1 | 1 | 0.500 | 0.029 | 0.054 |

## False-Positive Examples

### ChickenPox_Rashes_Itch_NoNegs

- **True:** psoriasis
- **Predicted:** chicken pox
- **Text:** the skin on my genitals is red and inflamed. it is often itchy, burning, and uncomfortable. there are rashes on different parts of the body too.

### ChickenPox_SystemicSymptoms

- **True:** typhoid
- **Predicted:** chicken pox
- **Text:** i am experiencing a lot of nausea and vomiting, and it's been quite difficult for me to eat anything. i've entirely lost my appetite, and as a result, i have become quite weak.

- **True:** typhoid
- **Predicted:** chicken pox
- **Text:** i've been having diarrhoea and loose, watery stools many times a day. i've lost my appetite and am always sick. i'm also developing a mild fever. also, my abdominal part pains a lot. i don't know what the reason behind all of these is.

### VaricoseVeins_LegRashSymptoms

- **True:** psoriasis
- **Predicted:** varicose veins
- **Text:** i have been experiencing a skin rash on my arms, legs, and torso for the past few weeks. it is red, itchy, and covered in dry, scaly patches.

### ChickenPox_FatigueEnergyLoss

- **True:** psoriasis
- **Predicted:** chicken pox
- **Text:** i have experienced fatigue and a general feeling of malaise. i often feel tired and have a lack of energy, even after a good night's sleep.

### ChickenPox_AppetiteLoss

- **True:** typhoid
- **Predicted:** chicken pox
- **Text:** i have lost my appetite and have noticed a significant weight loss. i have abdominal pain, especially in the area of my stomach and intestines. i am concerned about my health.

## True-Positive Examples

### typhoid_gi_fever_combination

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** i am having a terrible pain in my abdominal part, and i've been feeling really nauseated. i'm also experiencing a mild fever. i am really worried.

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** i've been having a lot of trouble keeping hydrated because of the vomiting and diarrhea. there is a mild fever along with constipation and headache.

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** i am experiencing constipation and stomach ache, which has been really difficult. the discomfort has gotten worse, and it is seriously interfering with my everyday life.

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** there is a distinct pain in my abdominal part. i am not sure what it is. i am also going through constant vomiting and feel nauseous.

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** i've been feeling exhausted and weak, and i can't seem to get rid of it. because of the vomiting and nausea, i've entirely lost my appetite. my belly pains which are causing me concern.

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** i've had a high fever, particularly at night. it's been quite unpleasant. there is a little headache, as well as constipation and diarrhea. i don't feel like eating anything.

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** i've been having a lot of trouble staying hydrated because of the vomiting and diarrhea. i have a high fever, constipation, and a headache. i am also starting to get a strange pain in my stomach area and i can't do anything physical.

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** diarrhea has been really watery and foul-smelling, and it's been accompanied by abdominal pain. i feel like vomiting most of the time.

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** i have had a fever for the last couple of days. now, i am starting to experience a severe pain in my stomach area and suffering from constipation.

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** i am experiencing a lot of belly pain and constipation, which has been really annoying. sometimes, i feel a strong urge to vomit, and because of all of these, i am feeling very weak.

### Typhoid_SystemicAbdominal

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** i've been having a lot of trouble sleeping because of the high fever, headache and chills. i wake up every day having a terrible pain in my belly area.

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** i've been experiencing chills, fever, and extreme stomach discomfort. i've been generally unhappy, and i can't seem to get rid of these symptoms.

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** i am having severe stomach discomfort and diarrhoea. i have a high fever along with a headache. the previous several days have been really unpleasant.

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** i am having a lot of trouble sleeping because of the high fever and the headache. moreover, i have constant belly pain, because of which i can't go to work.

- **True:** typhoid
- **Predicted:** typhoid
- **Text:** i have been experiencing chills and fever, along with severe abdominal pain. i've been feeling really miserable overall, and i just can't seem to shake these symptoms.

### VaricoseVeins_VeinVisualSymptoms

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** i have a rash on my legs that is causing a lot of discomforts. it seems there is a cramp and i can see prominent veins on the calf. also, i have been feeling very tired and fatigued in the past couple of days.

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** the blood vessels on my legs are quite visible and give me a lot of pain. they're large and protrude from my skin. it is unusual and i am worried about it.

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** the prominent blood vessels on my calves are causing self-consciousness and embarrassment. i believe the problem is because of my overweight.

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** as i am overweight, i have noticed that my legs are swollen and the blood vessels are more visible than usual. the swelling seems to be getting worse over time.

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** my legs have been causing a lot of discomforts when i exercise. they feel heavy and swollen, and the veins are prominent and painful. i feel fatigued all the time.

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** i am overweight and have noticed that my legs are swollen and the blood vessels are visible. my legs have swollen and i can see a stream of swollen veins on my calves.

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** the veins in my calves are protruding out quite unusually. i am worried about it. also, i am overweight and i believe this is the reason behind all of this.

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** the swelling in my legs is causing me to have difficulty fitting into my shoes. i can't sprint or stand for long periods of time. i can see some swollen blood vessels.

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** i have a rash on my legs that is giving me a lot of pain. there appears to be a cramp, and i can see visible veins on the calf.

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** the veins on my calves have become very prominent and causing discomfort. i can't stand for long periods of time, as it causes pain in my legs, similar to cramps.

### ChickenPox_RedSpots_Systemic

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i'm feeling really sick and lost my appetite. i've seen little red patches on my arms, neck and face that itch when i touch them.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** there are red spots all over my body that i can't explain. the spots are itchy and starting to swell, and they are spreading rapidly.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i've been suffering from severe itching all over my body, along with a fever and headache. the red spots are starting to swell and it is getting really uncomfortable every day.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i have a high fever and a severe headache. i can't seem to eat anything and feel like vomiting. there are also some red spots developing on my arms. i am really worried.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i feel tired every day. there are red spots all over my arms and back and it itches if i touch them. i am really worried and not sure what to do.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i have no energy and have lost my appetite. i'm feeling really sick and don't know what's wrong. also, there are small red spots starting to show on my skin.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** there are small red spots all over my body that i can't explain. it's worrying me. i feel extremely tired and experience a mild fever every night.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i have little red spots all over my body that i don't understand. it worries me. i have lost my appetite and every night, i am exhausted and have a severe headache.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i'm feeling really sick and uncomfortable like something is wrong inside. i don't know what it could be. i noticed small red spots on my arms, which itches if i touch them.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** my skin rash is causing me a great deal of pain. there are also small red spots developing near my neck. since yesterday, i have had a severe fever, headache and fatigue.

### Psoriasis_NailIssues

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** my nails have small dents or pits in them, and they often feel inflammatory and tender to the touch. even there are minor rashes on my arms.

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** my skin is peeling in places, especially on my knees, elbows, and arms. this peeling is often accompanied by a painful or burning sensation. i am also developing small dents on my nails, which is really concerning.

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** my arms, face and back are all red and irritated. it is frequently irritating and unpleasant. my nails have a strange inflammation and have developed small dents. i have never seen anything like this.

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** my skin is extremely sensitive and quickly irritated by changes in temperature or humidity. my nails have developed dents on them. i am worried about this sudden change.

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** i am starting to have rashes on my skin. the rash often bleeds when i scratch or rub it. moreover, i have noticed small dents in my nails.

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** i've had trouble sleeping because of the itching and pain produced by the rash. my nails have little dents. i am also experiencing skin peeling in different parts of my body.

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** i am starting to have rashes on my arms and neck. the rash often bleeds and hurts when i scratch it. i have also developed small dents in my nails, which is very strange.

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** i've had trouble sleeping because of the itching and pain produced by the rash. my nails have little dents, which is really alarming. there is a noticeable inflammation in my nails.

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** i've had trouble sleeping because of the itching and pain produced by the rash. my nails have little dents, which is really alarming. moreover, my joints pain everyday and i have no idea what is causing it.

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** my skin is breaking out in rashes. when i scratch or rub the rash, it frequently bleeds. in addition, i've observed little dents in my nails. there is a noticeable inflammation in my nails.

### Psoriasis_JointPainSymptoms

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** there is strange pain in my joints. also, i have noticed strange peeling of skin in different parts of my body. i am afraid there is something wrong going on with my body.

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** my genital skin is red and irritated. it is frequently irritating, burning, and unpleasant. there are also rashes in various places of the body. also, i have a strange pain in my joints.

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** i have been experiencing joint pain in my fingers, wrists, and knees. the pain is often achy and throbbing, and it gets worse when i move my joints.

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** my skin rash gets worse in the winter when the air is dry. to keep my skin moisturized, i have to moisturize more regularly and use humidifiers. i am also facing joint pain.

### Psoriasis_SpecificSkinManifestations

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** because of dry, flaky areas on my skin, i am prone to infections. my joints are in excruciating agony. the skin on my knees and elbows is beginning to flake.

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** my skin rash has extended to other areas of my body, including my chest and belly. it is irritating and unpleasant, and it is frequently worst at night. i'm also experiencing skin flaking.

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** because of dry, flaky areas on my skin, i am prone to infections. my joints are in extreme pain . my knees and elbows' skin are starting to peel off.

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** my skin is prone to infections due to dry, flaky patches. i am experiencing a strong pain in my joints. the skin on my knees and elbows is starting to peel off.

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** for the past few weeks, i've had a skin rash on my arms, legs, and chest. it's red and irritating, with dry, scaly spots. i have a strange pain in my joints too.

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** my nails are slightly dented. even my joints are now experiencing excruciating discomfort. my skin has a silver-like powder, especially on my back and elbows.

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** my skin has a silvery film, particularly on my back, arms and scalp. this dusting is composed of tiny scales that easily peel off when scratched.

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** i've observed that my skin is more sensitive now than it used to be. my skin has a silvery film, especially on my back and elbows.

### ChickenPox_LymphNodes

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** my arms and neck have large lymph nodes, which itch when i touch them. the itching has made my day extremely uncomfortable.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** my arms and face have small lymph nodes, which are starting to swell. my day has been made really miserable by the constant itching and pain.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** enlarged lymph nodes are giving me a great deal of pain. i have rashes all over my body and because of which i cannot sleep all night.

### VaricoseVeins_UnexplainedBruisingLegs

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** i am experiencing too many cramps in the last couple of days. i think something is not right. i believe there is a small bruise on my calves, but i am not sure about it.

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** there is bruising on my legs that i cannot explain. i can see strange blood vessels below the skin. also, i am slightly obese and i am really worried.

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** i have noticed that there are bruises on my legs that i cannot explain. they are not painful but are concerning to me.

### VaricoseVeins_LegCramps

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** the cramps in my calves are making it difficult for me to walk. i feel fatigued after working for some time. i believe obesity is the reason behind this.

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** the cramps in my calves are becoming more frequent and intense, making it difficult for me to walk and do my daily activities.

### Psoriasis_PalmsSolesFissures

- **True:** psoriasis
- **Predicted:** psoriasis
- **Text:** my palms and soles have grown and developed severe fissures. these cracks are unpleasant and frequently bleed. also, the skin is starting to peel off.

### VaricoseVeins_ActivityAggravatedLegDiscomfort

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** standing or walking for long periods of time has been causing a lot of pain in my legs. it feels like a cramp and becomes worse the longer i am on my feet.

### ChickenPox_Rashes_Itch_NoNegs

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i've been experiencing intense itching all over my skin, and it's driving me crazy. i also have a rash that's red and inflamed.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i have seen rashes on my arms and neck and it itches if i scratch them. i've also had a high fever for a few days. i have no idea what is causing it. the itching is causing me a lot of discomforts.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i'm worried about this rash on my skin. it's spreading rapidly and causing a lot of discomforts. i can hardly sleep at night because of the itching,

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i've been suffering from severe itching all over my body, and it's driving me insane. i also have a red and irritating rash.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** the itching is making it hard for me to sleep at night. i can't seem to get any rest because the rash is so itchy and uncomfortable. i'm feeling really tired and exhausted.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** my skin rash is giving me a lot of pain and discomfort. it's red and swollen, and it's spreading throughout my body.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i have a skin rash that's red and swollen, and it's spreading all over my body. i have a mild fever and it is causing me a lot of discomforts.

### ChickenPox_SystemicSymptoms

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i have no energy and have lost my appetite. i have a high fever and severe headache and don't know what's wrong.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** the high fever and swollen lymph nodes are causing me much discomfort. i have a headache and feel weak and fatigued. it's hard for me to concentrate because of the fever.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i have no energy and have lost my appetite. i'm feeling really sick and don't know what's wrong.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** the high fever, swollen lymph nodes and headache are causing me a lot of trouble. i don't feel like eating anything and feel weak and fatigued. it's hard for me to concentrate on my daily life.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i have a high fever and a mild headache. i'm tired most of the time and completely lost my appetite.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i have lost my appetite completely and can't seem to eat anything. i feel like vomiting and feel exhausted. i noticed rashes on my skin, which is really concerning me.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i'm really exhausted and lacking in energy. i can hardly keep my eyes open during the day. i have a mild fever and don't feel like eating anything. i think i have lost my appetite.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i'm feeling really nauseous and uneasy. i'm not sure what it might be. i've seen rashes on my arms and legs. i have lost my appetite and feel exhausted every day.

### VaricoseVeins_LegRashSymptoms

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** i have been experiencing a rash on my legs that is causing a lot of irritation and discomfort. it is red and inflamed and appears to be spreading.

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** the rash on my legs is spreading and becoming more severe. it has become very difficult for me to run.

- **True:** varicose veins
- **Predicted:** varicose veins
- **Text:** the rash on my legs is spreading and becoming more severe. it is red, inflamed, and itchy, causing a lot of discomfort and difficulty sleeping at night.

### ChickenPox_FatigueEnergyLoss

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i'm feeling fatigued and have no energy. i can barely keep my eyes open during the day, and i've been feeling lethargic and unable to motivate myself.

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i'm feeling fatigued and have no energy. i can barely keep my eyes open during the day, and i've been feeling lethargic and unable to motivate myself.

### ChickenPox_AppetiteLoss

- **True:** chicken pox
- **Predicted:** chicken pox
- **Text:** i've lost my appetite and can't seem to eat anything. i'm worried about my health.

## Weak Rules
- ChickenPox_AppetiteLoss (chicken pox): precision=0.500, recall=0.029, FP=1
- ChickenPox_FatigueEnergyLoss (chicken pox): precision=0.667, recall=0.057, FP=1

## Rule Improvement Suggestions

### typhoid_gi_fever_combination
- Rule looks stable.

### Typhoid_SystemicAbdominal
- Consider adding alternative symptom patterns.

### VaricoseVeins_VeinVisualSymptoms
- Consider adding alternative symptom patterns.

### ChickenPox_RedSpots_Systemic
- Consider adding alternative symptom patterns.

### Psoriasis_NailIssues
- Consider adding alternative symptom patterns.

### Psoriasis_JointPainSymptoms
- Consider adding alternative symptom patterns.

### Psoriasis_SpecificSkinManifestations
- Consider adding alternative symptom patterns.

### ChickenPox_LymphNodes
- Consider adding alternative symptom patterns.

### VaricoseVeins_UnexplainedBruisingLegs
- Consider adding alternative symptom patterns.

### VaricoseVeins_LegCramps
- Consider adding alternative symptom patterns.

### Psoriasis_PalmsSolesFissures
- Consider adding alternative symptom patterns.

### VaricoseVeins_ActivityAggravatedLegDiscomfort
- Consider adding alternative symptom patterns.

### ChickenPox_Rashes_Itch_NoNegs
- Consider adding alternative symptom patterns.

### ChickenPox_SystemicSymptoms
- Consider adding alternative symptom patterns.

### VaricoseVeins_LegRashSymptoms
- Consider adding alternative symptom patterns.

### ChickenPox_FatigueEnergyLoss
- Consider adding alternative symptom patterns.

### ChickenPox_AppetiteLoss
- Require additional symptoms before firing. Consider adding alternative symptom patterns.