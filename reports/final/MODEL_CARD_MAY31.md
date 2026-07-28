# Model Card — AgriPredict AI, horizon 31 mai

## Identification

- Version : `1.0.0`
- Horizon : `may31`
- Modèle : `random_forest`
- Tâche : régression de la date de récolte du blé
- Sortie : jour de l’année
- Domaine : Centre-Val de Loire

## Sélection et validation

- Années de développement : 2020, 2021 et 2022
- Année de calibration : 2023
- Année de test : 2024
- Sélection : GroupKFold par identifiant physique stable `ID_PARCEL`, sans consultation du test

## Performance sur le test chronologique

- MAE : 8,493 jours
- RMSE : 10,356 jours
- R² : 0,105
- Prédictions à ±5 jours : 25,2 %
- Prédictions à ±7 jours : 52,8 %
- IC bootstrap à 95 % du MAE : [7,609 ; 9,363]

## Incertitude

- Méthode : split-conformal
- Couverture nominale : 90 %
- Couverture observée : 85,9 %
- Largeur moyenne : 31,17 jours

## Usage prévu

Aide à la planification logistique et à l’analyse expérimentale. Le modèle ne déclenche aucune récolte automatiquement.

## Usages interdits ou non validés

- autre culture ;
- autre région sans validation externe ;
- décision de récolte autonome ;
- interprétation causale des importances ;
- présentation de la cible dérivée comme une observation terrain directe.

## Données et risques

Les identifiants, variables de pic, variables DOY et agrégats AMJ à risque sont exclus du modèle officiel. Les détails figurent dans les métadonnées et le rapport final.
