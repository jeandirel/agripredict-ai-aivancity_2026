# AgriPredict AI — Registre officiel des données

> **Cadre :** Clinique IA d’aivancity — Promotion 2026  
> **Responsable :** Jean Direl NZE  
> **Version :** 2.0  
> **Statut :** sources officielles du projet confirmées par le responsable du projet

## 1. Objet du registre

Ce document constitue la source de vérité de la Phase 0 pour les données d’AgriPredict AI. Il remplace le cadrage provisoire fondé sur un projet de rendement du riz en Inde.

Le projet réel porte sur des **parcelles de blé du Centre-Val de Loire** et sur la **prédiction de la date de récolte à l’échelle parcellaire**, à partir de données multimodales issues du sol, de Sentinel-1, de Sentinel-2, de la météorologie et de références agricoles.

La cible principale observée dans les tables ML est `harvest_doy_derived`, exprimée en **jour de l’année**. Sa méthode de construction doit être auditée à partir des rapports méthodologiques présents dans le dépôt avant tout entraînement final.

## 2. Architecture des données

```text
Sources originales
RPG / France data.gouv + NASA POWER + SoilGrids + Sentinel-1 + Sentinel-2 + Céré'Obs
                                  │
                                  ▼
                    Jeux bruts sans transformation
                                  │
                                  ▼
                  Tables brutes combinées et alignées
                                  │
                                  ▼
                 Tables prêtes pour le Machine Learning
                                  │
                                  ▼
                   Jeux finaux au 31 mai et au 15 juin
```

Cette architecture doit permettre deux niveaux de reproductibilité :

1. **reproductibilité scientifique rapide**, à partir des jeux ML finaux ;
2. **reproductibilité complète de la chaîne**, depuis les sources brutes jusqu’aux tables finales.

## 3. Jeux finaux à utiliser

| ID | Dataset | Rôle | URL officielle |
|---|---|---|---|
| FIN-031 | Dataset final au 31 mai | Prévision précoce de la récolte avec les informations disponibles au 31 mai | <http://kaggle.com/datasets/rgislikassi/master-ml-final-may31/data> |
| FIN-0615 | Dataset final au 15 juin | Prévision plus tardive avec un signal agronomique enrichi jusqu’au 15 juin | <https://www.kaggle.com/datasets/rgislikassi/master-ml-final-juin15> |

### Décision d’usage

- `master-ml-final-may31` est le dataset de **prévision précoce**.
- `master-ml-final-juin15` est le dataset de **prévision enrichie** et le candidat principal pour la meilleure performance.
- Les deux jeux doivent être évalués avec le même protocole afin de mesurer le compromis entre **anticipation** et **précision**.

### Question expérimentale associée

> Combien de jours de précision supplémentaire obtient-on en attendant le 15 juin, et ce gain justifie-t-il la réduction du délai d’anticipation par rapport à une prévision arrêtée au 31 mai ?

## 4. Jeux bruts sans transformation

Ces jeux proviennent des sources originales ou de leurs extractions directes. Ils constituent la couche Bronze du projet.

| ID | Dataset | Contenu principal | Couverture indiquée par le titre | URL officielle |
|---|---|---|---|---|
| RAW-SOIL | Soil Features Centre-Val de Loire — 1 500 parcelles | Propriétés pédologiques multi-profondeurs issues de SoilGrids | Environ 1 500 parcelles | <https://www.kaggle.com/datasets/rgislikassi/soil-features-centre-val-de-loire-1500-parcels/data> |
| RAW-RPG | `parcele_ble_cvl_300` | Parcelles de blé issues des données parcellaires françaises | Centre-Val de Loire | <https://www.kaggle.com/datasets/rgislikassi/parcele-ble-cvl-300/data> |
| RAW-METEO | Météo Centre-Val de Loire NASA POWER | Variables météorologiques et agroclimatiques | 2019–2024 | <https://www.kaggle.com/datasets/rgislikassi/meteo-centre-vale-de-loire-2019-2024-nasapower/data> |
| RAW-CEREOBS | `cereb_dataset` | Références Céré'Obs utilisées dans la construction ou la validation de la cible | À confirmer par audit | <https://www.kaggle.com/datasets/rgislikassi/cereb-dataset/data> |
| RAW-S2 | Sentinel-2 Indices CVL — 1 500 parcelles de blé | NDVI, EVI, NDWI et variables phénologiques optiques | 2019–2024 | <https://www.kaggle.com/datasets/rgislikassi/sentinel-2-indice-cvl-wheat-parcels-2019-2024> |
| RAW-S1 | Sentinel-1 SAR Backscatter CVL — 1 500 parcelles de blé | VV, VH, ratios et indicateurs radar | 2020–2024 | <https://www.kaggle.com/datasets/rgislikassi/sentinel-1-sar-backscatter-cvl-1500-wheat-parcels/data> |

## 5. Jeux bruts combinés

Ces tables correspondent à la couche Silver : sources jointes, alignées et structurées, mais pas nécessairement prêtes pour l’apprentissage final.

| ID | Dataset | Rôle | URL officielle |
|---|---|---|---|
| COMB-REG | `master_raw_regional` | Table brute combinée utilisant la référence régionale | <https://www.kaggle.com/datasets/rgislikassi/master-raw-regional> |
| COMB-DER | `master_raw_derived` | Table brute combinée utilisant la cible dérivée | <https://www.kaggle.com/datasets/rgislikassi/master-raw-derived> |

## 6. Jeux prêts pour le Machine Learning

Ces tables constituent la couche Gold. Elles doivent être auditées, versionnées et utilisées par les pipelines d’entraînement.

| ID | Dataset | Rôle | URL officielle |
|---|---|---|---|
| ML-DER-0615 | `master_ml_derived_june15` | Cible dérivée, variables disponibles jusqu’au 15 juin | <https://www.kaggle.com/datasets/rgislikassi/master-ml-derived-june15> |
| ML-DER-0531 | `master_ml_derived_may31` | Cible dérivée, variables disponibles jusqu’au 31 mai | <https://www.kaggle.com/datasets/rgislikassi/master-ml-derived-may31> |
| ML-REG | `master_ml_regional` | Variante utilisant la cible ou référence régionale | <https://www.kaggle.com/datasets/rgislikassi/master-ml-regional> |

## 7. Fichiers déjà présents dans le dépôt

```text
data/
├── master_ml_final_may31.csv
└── master_ml_final_june15.csv
```

L’audit initial du schéma montre des variables relatives :

- aux identifiants et surfaces de parcelles ;
- au sol et à plusieurs profondeurs ;
- aux indices Sentinel-2 ;
- aux rétrodiffusions Sentinel-1 ;
- aux variables météo et agroclimatiques ;
- à la région ;
- à la cible `harvest_doy_derived`.

## 8. Modalités de données

### 8.1 Identité et géographie

- `parcelle_uid` ;
- `ID_PARCEL` ;
- `year` ;
- `SURF_PARC` ;
- `region`.

### 8.2 Sol

- pH ;
- azote ;
- carbone organique ;
- argile, sable et limon ;
- capacité d’échange cationique ;
- densité apparente ;
- fragments grossiers ;
- rétention d’eau ;
- variables calculées à plusieurs profondeurs.

### 8.3 Sentinel-2

- NDVI ;
- EVI ;
- NDWI ;
- pics, amplitudes, moyennes saisonnières et écarts-types ;
- jours de pics phénologiques.

### 8.4 Sentinel-1

- VV ;
- VH ;
- ratio VV/VH ou indicateur équivalent selon le dictionnaire ;
- minima, maxima, moyennes, amplitudes et jours associés.

### 8.5 Météorologie et agroclimat

- température ;
- précipitations ;
- évapotranspiration de référence ;
- bilan hydrique ;
- degrés-jours de croissance ;
- gel ;
- stress thermique ;
- séquences sèches et humides ;
- rayonnement.

### 8.6 Cibles

- cible dérivée : `harvest_doy_derived` ;
- variante régionale : définition exacte à confirmer dans `master_ml_regional` et les rapports associés.

## 9. Périmètre géographique et temporel

- **Culture :** blé ;
- **Zone :** Centre-Val de Loire, France ;
- **Granularité :** parcelle × année ;
- **Couverture brute la plus large indiquée :** 2019–2024 ;
- **Intersection multimodale complète attendue :** probablement 2020–2024, car Sentinel-1 commence en 2020 ;
- **Nombre de parcelles annoncé par plusieurs sources :** environ 1 500.

Les nombres définitifs d’années, de parcelles et d’observations doivent être calculés depuis chaque fichier et non déduits uniquement du titre Kaggle.

## 10. Cible scientifique principale

### Définition opérationnelle

```text
Entrées  : sol + Sentinel-1 + Sentinel-2 + météo + parcelle + année
Cible    : harvest_doy_derived
Unité    : jour de l’année
Sortie   : date de récolte prévue + intervalle d’incertitude en jours
```

### Point critique

La cible est qualifiée de **dérivée**. Il faut donc démontrer :

1. comment elle a été produite ;
2. quelles sources ont contribué à sa construction ;
3. si certaines features ML ont aussi servi directement à fabriquer la cible ;
4. si le calcul utilise des informations postérieures à la date de coupure du 31 mai ou du 15 juin ;
5. si une fuite de cible est possible ;
6. comment elle se compare à la référence régionale.

Aucun résultat final ne sera accepté avant validation de cette analyse.

## 11. Relations à vérifier entre les variantes

Les noms suivants ne doivent pas être considérés comme synonymes sans preuve :

- `master_ml_final_may31` et `master_ml_derived_may31` ;
- `master_ml_final_juin15` et `master_ml_derived_june15` ;
- cible dérivée et cible régionale.

Pour chaque paire, l’audit doit comparer :

- hash SHA-256 ;
- nombre de lignes ;
- nombre et ordre des colonnes ;
- clés uniques ;
- périodes ;
- taux de valeurs manquantes ;
- définition de la cible ;
- transformations appliquées.

## 12. Provenance et gouvernance

Pour chaque dataset utilisé dans une expérience finale, enregistrer :

- URL Kaggle ;
- propriétaire Kaggle `rgislikassi` ;
- version Kaggle ou date de téléchargement ;
- nom exact des fichiers ;
- empreinte SHA-256 ;
- licence affichée ;
- sources originales ;
- transformations ;
- responsable de validation ;
- restrictions de redistribution.

Kaggle est ici une plateforme de distribution. La licence et les conditions des sources originales restent à documenter, notamment pour les données françaises, NASA POWER, SoilGrids et Copernicus.

## 13. Classification Bronze–Silver–Gold

| Couche | Contenu | Règle |
|---|---|---|
| Bronze | Jeux bruts sans transformation | Fichiers immuables, hashés et accompagnés de leur provenance |
| Silver | `master_raw_regional`, `master_raw_derived` | Jointures et harmonisations reproductibles, sans préparation spécifique au modèle |
| Gold | Jeux `master_ml_*` et jeux finaux | Schéma validé, cible documentée, split défini, fuite contrôlée |

## 14. Contrôles obligatoires avant modélisation

- téléchargement reproductible via l’API Kaggle ;
- calcul des hashes ;
- comparaison des versions 31 mai et 15 juin ;
- validation des types et unités ;
- unicité de `parcelle_uid` par année ;
- audit des doublons ;
- audit des valeurs manquantes ;
- audit des plages physiques ;
- distribution de `harvest_doy_derived` ;
- couverture par année ;
- couverture par parcelle ;
- couverture par région ;
- recherche de variables postérieures à la date de coupure ;
- recherche de fuite liée à la construction de la cible ;
- vérification des licences.

## 15. Décisions de Phase 0

| ID | Décision |
|---|---|
| DATA-D01 | Le projet est centré sur les parcelles de blé du Centre-Val de Loire. |
| DATA-D02 | La tâche principale est la prédiction de la date de récolte en jour de l’année. |
| DATA-D03 | Les horizons 31 mai et 15 juin sont comparés expérimentalement. |
| DATA-D04 | Le jeu du 15 juin est candidat principal pour la performance ; le jeu du 31 mai mesure la valeur de l’anticipation. |
| DATA-D05 | Les sources brutes et combinées servent à rendre la chaîne totalement reproductible. |
| DATA-D06 | La cible dérivée ne sera utilisée définitivement qu’après audit de sa construction et des fuites potentielles. |
| DATA-D07 | La variante régionale sert de référence, de comparaison ou d’analyse de sensibilité selon sa définition documentée. |

## 16. Gate données de la Phase 0

Le registre est validé lorsque :

- toutes les URLs officielles sont enregistrées ;
- les datasets finaux sont téléchargés et hashés ;
- les relations entre variantes sont clarifiées ;
- la cible dérivée est documentée ;
- les licences sont relevées ;
- la période réelle et le nombre d’observations sont mesurés ;
- le protocole de validation temporelle et par parcelle est fixé.
