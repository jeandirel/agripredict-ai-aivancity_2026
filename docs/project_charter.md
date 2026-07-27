# AgriPredict AI — Charte de projet

> **Cadre :** Clinique IA d’aivancity — Promotion 2026  
> **Responsable du projet :** Jean Direl NZE  
> **Version :** 2.0  
> **Statut :** cadrage scientifique aligné sur les données officielles

## 1. Finalité

AgriPredict AI est un projet d’intelligence artificielle agricole multimodale visant à **prédire la date de récolte du blé à l’échelle parcellaire dans la région Centre-Val de Loire**.

Le système combine :

- propriétés du sol ;
- données radar Sentinel-1 ;
- indices optiques Sentinel-2 ;
- données météorologiques NASA POWER ;
- informations parcellaires et temporelles ;
- références agricoles utilisées pour construire ou comparer la cible.

La sortie principale est une estimation du **jour de l’année de la récolte**, accompagnée d’un intervalle d’incertitude exprimé en jours et d’une explication des facteurs prédictifs.

## 2. Problématique directrice

> Dans quelle mesure la fusion de données pédologiques, satellitaires et météorologiques permet-elle de prévoir avec précision et suffisamment tôt la date de récolte du blé à l’échelle parcellaire, tout en assurant une généralisation temporelle, une explicabilité et une estimation fiable de l’incertitude ?

## 3. Contribution scientifique centrale

Le projet compare deux horizons opérationnels :

1. **prévision arrêtée au 31 mai**, afin de maximiser l’anticipation ;
2. **prévision arrêtée au 15 juin**, afin d’exploiter davantage d’informations proches de la récolte.

La contribution ne consiste donc pas uniquement à rechercher le meilleur score, mais à mesurer le compromis entre :

- délai d’anticipation ;
- précision en jours ;
- robustesse ;
- généralisation à une année future ;
- généralisation à des parcelles non observées ;
- coût et complexité du modèle.

## 4. Objectifs

### 4.1 Objectifs scientifiques

- Auditer et documenter la cible `harvest_doy_derived`.
- Vérifier l’absence de fuite liée à la construction de cette cible.
- Comparer les jeux du 31 mai et du 15 juin sous un protocole identique.
- Mesurer la valeur de chaque modalité par étude d’ablation.
- Comparer baselines, modèles d’arbres et réseaux neuronaux tabulaires compacts.
- Évaluer la généralisation temporelle et par parcelle.
- Produire des intervalles prédictifs calibrés.
- Expliquer les prédictions globalement et localement.

### 4.2 Objectifs d’ingénierie

- Rendre le téléchargement des jeux Kaggle reproductible.
- Versionner les données et leurs hashes.
- Construire une pipeline Bronze–Silver–Gold.
- Séparer clairement préparation, entraînement, évaluation et inférence.
- Mettre en place tests, CI, Docker, DVC et MLflow.
- Produire une API FastAPI et une interface de démonstration.

### 4.3 Objectifs produit

L’utilisateur doit pouvoir fournir ou sélectionner les caractéristiques d’une parcelle et obtenir :

- le jour de récolte prédit ;
- la date calendaire correspondante ;
- un intervalle d’incertitude en jours ;
- les principaux facteurs influents ;
- un avertissement lorsque l’observation est hors du domaine connu.

## 5. Périmètre confirmé

| Élément | Décision |
|---|---|
| Culture | Blé |
| Zone | Centre-Val de Loire, France |
| Granularité | Parcelle × année |
| Période brute | 2019–2024 selon les jeux sources |
| Intersection multimodale attendue | 2020–2024, à confirmer par audit |
| Nombre de parcelles annoncé | Environ 1 500 selon plusieurs jeux sources |
| Cible principale | `harvest_doy_derived` |
| Unité | Jour de l’année |
| Horizons de données | 31 mai et 15 juin |
| Type de problème | Régression tabulaire multimodale |

## 6. Sources officielles

Le registre complet est disponible dans [`docs/data_sources.md`](data_sources.md).

Les familles de données sont :

- SoilGrids ;
- données parcellaires françaises ;
- NASA POWER ;
- Céré'Obs ;
- Sentinel-2 ;
- Sentinel-1 ;
- tables brutes combinées ;
- tables ML dérivées et régionales ;
- jeux finaux au 31 mai et au 15 juin.

## 7. Périmètre inclus

- audit de la cible et des données ;
- comparaison des versions 31 mai / 15 juin ;
- reconstruction reproductible depuis les sources brutes ;
- feature engineering contrôlé ;
- baselines statistiques ;
- Random Forest, Extra Trees, XGBoost et CatBoost ;
- MLP, TabNet ou FT-Transformer compact comme expériences neuronales ;
- validation temporelle et groupée par parcelle ;
- étude d’ablation ;
- incertitude prédictive ;
- explicabilité ;
- analyse d’erreurs ;
- API, interface, tests, CI et Docker ;
- rapport scientifique et soutenance.

## 8. Hors périmètre initial

- prédiction du rendement en tonnes par hectare ;
- recommandation générale de cultures ;
- prévision autonome de sécheresse comme projet séparé ;
- utilisation de CNN ou Vision Transformers sans images brutes préparées pour ce besoin ;
- pilotage automatique d’engins agricoles ;
- recommandation prescriptive sans validation agronomique ;
- déploiement hors Centre-Val de Loire sans validation externe ;
- interprétation causale des importances de variables.

## 9. Modèles à comparer

### Baselines

- moyenne globale ;
- moyenne par année ;
- moyenne par région si plusieurs sous-zones sont disponibles ;
- régression linéaire, Ridge et ElasticNet.

### Modèles d’arbres

- Random Forest ;
- Extra Trees ;
- XGBoost ;
- CatBoost.

### Réseaux neuronaux tabulaires

- MLP régularisé ;
- TabNet ;
- FT-Transformer compact, uniquement si la taille et le protocole le justifient.

Un modèle complexe ne sera retenu que si son gain est stable et défendable face aux modèles d’arbres.

## 10. Protocoles de validation obligatoires

- split chronologique avec la dernière année réservée au test final ;
- `GroupKFold` ou équivalent par `parcelle_uid` ;
- aucun preprocessing ajusté sur le test ;
- tuning uniquement sur les données d’entraînement ;
- comparaison 31 mai / 15 juin sur les mêmes observations communes ;
- plusieurs seeds ou folds ;
- résultats segmentés par année et par sous-population pertinente.

## 11. Livrables obligatoires

1. registre des datasets et licences ;
2. audit programmatique des CSV et jeux Kaggle ;
3. rapport sur la construction de la cible ;
4. pipeline de téléchargement et de versionnement ;
5. pipeline de préparation Bronze–Silver–Gold ;
6. baselines reproductibles ;
7. comparaison de modèles classiques et neuronaux ;
8. comparaison 31 mai / 15 juin ;
9. étude d’ablation des modalités ;
10. validation temporelle et par parcelle ;
11. incertitude et explicabilité ;
12. analyse d’erreurs et de robustesse ;
13. API et interface ;
14. tests, CI et Docker ;
15. Data Card et Model Card ;
16. rapport, slides, démonstration et release `v1.0.0`.

## 12. Principes non négociables

- Reproductibilité avant performance brute.
- Aucune fuite de cible tolérée.
- Les dates de coupure du 31 mai et du 15 juin doivent être respectées.
- Les modèles complexes sont comparés équitablement à des baselines fortes.
- Les résultats négatifs sont documentés.
- Une prédiction est toujours accompagnée de son domaine de validité.
- Les explications sont associatives et non causales.
- Les licences des données distribuées sur Kaggle et des sources originales sont documentées.

## 13. Parties prenantes

| Rôle | Partie prenante | Responsabilité |
|---|---|---|
| Responsable projet | Jean Direl NZE | Cadrage, data, expérimentation, développement, documentation et soutenance |
| Encadrement académique | Clinique IA d’aivancity | Validation méthodologique et évaluation |
| Expert agronome | À identifier | Relecture de la cible, des features et de l’interprétation |
| Utilisateurs cibles | Agriculteurs, coopératives, analystes agricoles | Évaluation de l’utilité et de la compréhension |
| Fournisseurs de données | France data.gouv, NASA POWER, SoilGrids, Copernicus, Céré'Obs, Kaggle | Données selon leurs conditions d’usage |

## 14. Gate de fin de Phase 0

La Phase 0 est validée lorsque :

- la liste des datasets et URLs est figée ;
- les fichiers finaux sont téléchargés et hashés ;
- le lien entre jeux `final`, `derived` et `regional` est clarifié ;
- la cible dérivée est documentée ;
- les licences sont relevées ;
- les années, parcelles et observations sont comptées ;
- la stratégie de split est approuvée ;
- les questions de recherche et critères de succès sont alignés sur ce périmètre.

## 15. Décisions officielles

| ID | Décision | Justification |
|---|---|---|
| D-001 | La prédiction de la date de récolte du blé est le cœur scientifique | Correspond aux données disponibles et à la cible réelle |
| D-002 | Les horizons 31 mai et 15 juin sont comparés | Permet de mesurer le compromis anticipation–précision |
| D-003 | Le MAE en jours est la métrique principale | Directement interprétable pour l’usage métier |
| D-004 | La validation est temporelle et groupée par parcelle | Limite la surestimation liée à des observations proches |
| D-005 | La cible dérivée doit être auditée avant modélisation finale | Risque potentiel de circularité ou de fuite |
| D-006 | Les modèles d’arbres sont les références fortes | Taille et structure tabulaire des données |
| D-007 | Les réseaux neuronaux restent compacts et justifiés | Éviter le surapprentissage et la complexité artificielle |
