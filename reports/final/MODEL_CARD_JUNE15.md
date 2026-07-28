# Model Card — AgriPredict AI, horizon 15 juin

## Identification

- Version : `1.0.0`
- Horizon : `june15`
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

- MAE : 8,294 jours
- RMSE : 10,212 jours
- R² : 0,130
- Prédictions à ±5 jours : 32,5 %
- Prédictions à ±7 jours : 44,2 %
- IC bootstrap à 95 % du MAE : [7,410 ; 9,205]

## Incertitude

- Méthode : split-conformal
- Couverture nominale : 90 %
- Couverture observée : 85,3 %
- Largeur moyenne : 29,46 jours

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
