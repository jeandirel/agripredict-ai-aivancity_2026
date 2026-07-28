# Data Card — AgriPredict AI

## Périmètre

- Culture : blé
- Région : Centre-Val de Loire, France
- Unité : parcelle × année
- Cible : `harvest_doy_derived`
- Nature de la cible : dérivée
- Parcelles-années communes aux deux horizons : 1363

## Sources

- données parcellaires françaises ;
- SoilGrids ;
- NASA POWER ;
- Sentinel-1 ;
- Sentinel-2 ;
- Céré'Obs et références régionales ;
- jeux combinés et ML distribués via Kaggle.

Le registre détaillé des URLs figure dans `docs/data_sources.md` et `configs/data/datasets.json`.

## Horizons

- 31 mai : variables disponibles ou supposées disponibles avant le 31 mai ;
- 15 juin : variables disponibles ou supposées disponibles avant le 15 juin.

## Contrôles

- unicité de `parcelle_uid × year` ;
- alignement des cibles entre horizons ;
- exclusion des identifiants ;
- exclusion conservatrice des pics, DOY et agrégats AMJ non prouvés ;
- test chronologique ;
- validation groupée par parcelle ;
- suivi des valeurs manquantes et des modalités.

## Limites

La construction complète de la cible dérivée doit rester documentée et auditée. Les données ne démontrent pas une généralisation nationale ou internationale. Les données distribuées sur Kaggle restent soumises aux licences des jeux et sources originales.
