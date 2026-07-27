# Phase 0 — Décisions officielles sur les données

> Date de mise à jour : 28 juillet 2026  
> Responsable : Jean Direl NZE

## Décisions confirmées

- Culture : blé.
- Zone : Centre-Val de Loire, France.
- Granularité : parcelle × année.
- Tâche : prédiction de la date de récolte.
- Cible principale : `harvest_doy_derived`.
- Unité : jour de l’année.
- Horizons comparés : 31 mai et 15 juin.
- Dataset final précoce : `master-ml-final-may31`.
- Dataset final enrichi : `master-ml-final-juin15`.
- Sources brutes : parcelles françaises, SoilGrids, NASA POWER, Céré'Obs, Sentinel-1 et Sentinel-2.
- Tables combinées : `master_raw_regional` et `master_raw_derived`.
- Tables ML : `master_ml_derived_may31`, `master_ml_derived_june15` et `master_ml_regional`.

## Points non encore clos

- méthode exacte de construction de `harvest_doy_derived` ;
- correspondance entre jeux `final` et `derived` ;
- définition exacte de la variante régionale ;
- années réellement communes à toutes les modalités ;
- nombre réel de parcelles et d’observations ;
- disponibilité temporelle de chaque feature ;
- licences et droits de redistribution ;
- split temporel final ;
- séparation définitive par `parcelle_uid`.

## Règle

Aucun entraînement présenté comme résultat final ne doit être réalisé avant l’audit de la cible et des dates de disponibilité des variables.
