# AgriPredict AI — Plan expert de réalisation

> Projet développé dans le cadre de la **Clinique IA d’aivancity — Promotion 2026**.

## 1. Vision finale

AgriPredict AI doit devenir une solution complète de **prévision multimodale de la date de récolte du blé à l’échelle parcellaire en Centre-Val de Loire**.

La plateforme doit exploiter :

- les propriétés du sol ;
- Sentinel-1 ;
- Sentinel-2 ;
- NASA POWER ;
- les caractéristiques parcellaires ;
- les années culturales ;
- les références agricoles utilisées pour définir ou comparer la cible.

La sortie finale doit comprendre :

- un jour de récolte prédit ;
- une date calendaire ;
- un intervalle d’incertitude en jours ;
- une explication des facteurs prédictifs ;
- un indicateur de domaine de validité.

## 2. Expérience centrale

Le cœur scientifique est la comparaison entre :

- le dataset arrêté au **31 mai** ;
- le dataset arrêté au **15 juin**.

La question centrale est :

> Quel gain de précision obtient-on en attendant le 15 juin, et ce gain compense-t-il la perte de quinze jours d’anticipation ?

## 3. Architecture de données

```text
Données françaises de parcelles
SoilGrids
NASA POWER
Sentinel-1
Sentinel-2
Céré'Obs
        │
        ▼
Jeux bruts Kaggle
        │
        ▼
master_raw_regional / master_raw_derived
        │
        ▼
master_ml_regional / master_ml_derived_*
        │
        ▼
master_ml_final_may31 / master_ml_final_june15
        │
        ▼
Modèles + incertitude + explicabilité
        │
        ▼
API FastAPI + interface web
```

## 4. Phase 0 — Cadrage scientifique

### Objectif

Établir une base scientifiquement défendable avant tout entraînement.

### Livrables

- `docs/project_charter.md` ;
- `docs/problem_statement.md` ;
- `docs/research_questions.md` ;
- `docs/success_metrics.md` ;
- `docs/risks_and_assumptions.md` ;
- `docs/data_sources.md`.

### Travaux obligatoires

1. figer les URLs officielles ;
2. télécharger les datasets ;
3. calculer les hashes ;
4. comparer les variantes `final`, `derived` et `regional` ;
5. documenter la cible `harvest_doy_derived` ;
6. vérifier la disponibilité temporelle de chaque feature ;
7. identifier les variables postérieures aux dates de coupure ;
8. fixer le protocole de split ;
9. relever les licences ;
10. faire valider le cadrage par l’encadrement.

### Gate G0

La Phase 0 est terminée lorsque la cible, les horizons, les données, les risques et les critères de validation sont entièrement alignés.

## 5. Phase 1 — Fondation logicielle

### Arborescence cible

```text
agripredict-ai-aivancity_2026/
├── README.md
├── pyproject.toml
├── requirements.lock
├── Makefile
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .pre-commit-config.yaml
├── configs/
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── notebooks/
├── src/agripredict/
│   ├── data/
│   ├── features/
│   ├── models/
│   ├── evaluation/
│   ├── uncertainty/
│   ├── explainability/
│   └── utils/
├── pipelines/
├── app/
│   ├── api/
│   └── dashboard/
├── tests/
├── reports/
└── .github/workflows/
```

### Outils

- Python 3.11 ;
- pandas, NumPy, scikit-learn ;
- XGBoost et CatBoost ;
- PyTorch ;
- Optuna ;
- MLflow ;
- DVC ;
- Pandera ;
- FastAPI ;
- Streamlit ou React ;
- Pytest ;
- Ruff et MyPy ;
- GitHub Actions.

### Gate G1

```bash
make install
make lint
make test
```

doivent fonctionner sur une machine propre.

## 6. Phase 2 — Téléchargement et audit des données

### Pipeline de téléchargement

Créer un script utilisant l’API Kaggle et un manifeste YAML contenant :

- slug Kaggle ;
- nom du dataset ;
- couche Bronze, Silver ou Gold ;
- version ;
- date de téléchargement ;
- hash SHA-256 ;
- licence ;
- fichiers attendus.

### Audit programmatique

Pour chaque table :

- forme ;
- types ;
- valeurs manquantes ;
- doublons ;
- clés ;
- années ;
- parcelles uniques ;
- régions ;
- distribution de la cible ;
- plages physiques ;
- corrélations suspectes ;
- colonnes constantes ;
- différences de schéma.

### Comparaisons obligatoires

- final 31 mai vs derived 31 mai ;
- final 15 juin vs derived 15 juin ;
- derived vs regional ;
- couverture 31 mai vs 15 juin ;
- observations communes ;
- années communes ;
- parcelles communes.

### Gate G2

Aucune modélisation finale avant :

- validation du schéma ;
- audit de la cible ;
- contrôle des dates de coupure ;
- séparation des données définie.

## 7. Phase 3 — Audit de la cible

### Question critique

Comment `harvest_doy_derived` a-t-elle été calculée ?

### Contrôles

- identifier toutes les sources ;
- reproduire la formule ou la pipeline ;
- vérifier les variables utilisées ;
- rechercher une circularité ;
- vérifier les dates disponibles ;
- comparer à la référence régionale ;
- produire un rapport de sensibilité.

### Expériences

1. modèle avec toutes les variables ;
2. modèle sans variables potentiellement utilisées pour dériver la cible ;
3. modèle satellite uniquement ;
4. modèle météo + sol ;
5. comparaison à la référence régionale.

### Gate G2.5

La cible est déclarée :

- valide ;
- valide sous conditions ;
- exploratoire seulement ;
- ou à reconstruire.

## 8. Phase 4 — Feature engineering

### Groupes de variables

- parcelle et temps ;
- sol ;
- Sentinel-2 ;
- Sentinel-1 ;
- météo ;
- interactions contrôlées.

### Features possibles

- différences entre profondeurs du sol ;
- moyennes pondérées par profondeur ;
- anomalies par rapport à l’année ;
- ratios radar ;
- amplitudes phénologiques ;
- écarts entre dates de pics ;
- bilans hydriques ;
- degrés-jours ;
- interactions sol × météo ;
- indicateurs de valeurs manquantes.

Toute feature doit avoir :

- définition ;
- unité ;
- justification ;
- date de disponibilité ;
- test automatique ;
- statut de risque de fuite.

## 9. Phase 5 — Baselines

### Baselines naïves

- moyenne globale ;
- médiane globale ;
- moyenne par année ;
- référence régionale si compatible.

### Baselines statistiques

- régression linéaire ;
- Ridge ;
- ElasticNet.

### Gate G3

Les baselines 31 mai et 15 juin doivent être enregistrées dans MLflow avant tout modèle complexe.

## 10. Phase 6 — Modèles d’arbres

Comparer :

- Random Forest ;
- Extra Trees ;
- HistGradientBoosting ;
- XGBoost ;
- CatBoost.

### Tuning

- nested cross-validation ou validation interne stricte ;
- Optuna ;
- budget identique par modèle ;
- aucune consultation du test final ;
- early stopping lorsque applicable.

## 11. Phase 7 — Réseaux neuronaux

Les données actuelles sont tabulaires et de taille modérée. Les réseaux doivent donc rester compacts.

Comparer :

- MLP avec batch normalization et dropout ;
- TabNet ;
- FT-Transformer compact comme extension.

Ne pas utiliser arbitrairement :

- CNN 2D sans images ;
- LSTM sans vraies séquences ;
- gros Transformer sans volume suffisant.

### Gate G4

Un réseau n’est retenu que s’il présente un gain stable ou une propriété utile démontrée face à XGBoost et CatBoost.

## 12. Phase 8 — Validation scientifique

### Validation temporelle

- train sur les premières années ;
- validation sur l’avant-dernière ;
- test final sur la dernière.

### Validation groupée

- `GroupKFold` par `parcelle_uid` ;
- aucune parcelle commune entre train et test.

### Comparaison des horizons

- intersection exacte des lignes ;
- même split ;
- même cible ;
- même protocole ;
- mêmes métriques.

### Métriques

- MAE ;
- RMSE ;
- MedAE ;
- R² ;
- biais ;
- ±3, ±5, ±7 et ±10 jours ;
- erreur au 90e percentile.

## 13. Phase 9 — Ablations

Entraîner séparément :

1. parcelle + année ;
2. sol ;
3. Sentinel-2 ;
4. Sentinel-1 ;
5. météo ;
6. Sentinel-1 + Sentinel-2 ;
7. satellite + météo ;
8. satellite + sol ;
9. météo + sol ;
10. fusion complète.

Cette étude doit prouver la contribution de chaque modalité.

## 14. Phase 10 — Incertitude

Comparer :

- quantile regression ;
- bootstrap ;
- conformal prediction.

Produire :

- intervalle à 90 % ;
- couverture réelle ;
- largeur moyenne ;
- couverture par année ;
- couverture par plage de récolte.

## 15. Phase 11 — Explicabilité

- SHAP pour les arbres ;
- permutation importance ;
- importance par modalité ;
- explications locales ;
- stabilité entre folds ;
- analyse d’au moins cinq erreurs majeures.

Ne jamais présenter l’importance comme une causalité.

## 16. Phase 12 — Robustesse

Tester :

- valeurs manquantes simulées ;
- bruit numérique ;
- suppression d’une modalité ;
- année future ;
- parcelles inconnues ;
- observations hors distribution.

## 17. Phase 13 — API et interface

### API

```text
GET  /health
GET  /model-info
POST /predict/harvest-date
POST /explain
```

### Interface

- choix du modèle 31 mai ou 15 juin ;
- sélection ou saisie d’une parcelle ;
- DOY prédit ;
- date calendaire ;
- intervalle en jours ;
- facteurs explicatifs ;
- avertissement OOD.

## 18. Phase 14 — MLOps

- Git pour le code ;
- DVC pour les données ;
- MLflow pour les expériences ;
- configurations YAML ;
- CI GitHub Actions ;
- Docker ;
- tests unitaires, données et intégration ;
- Model Card et Data Card.

## 19. Phase 15 — Rapport et soutenance

Le rapport doit inclure :

1. contexte agronomique ;
2. problématique ;
3. sources et lineage ;
4. audit de cible ;
5. préparation des données ;
6. protocoles de validation ;
7. baselines ;
8. modèles d’arbres ;
9. réseaux tabulaires ;
10. comparaison 31 mai / 15 juin ;
11. ablations ;
12. incertitude ;
13. explicabilité ;
14. robustesse ;
15. produit ;
16. limites ;
17. perspectives.

## 20. Calendrier indicatif sur 12 semaines

| Semaine | Travail | Livrable |
|---|---|---|
| 1 | Clôture Phase 0 et téléchargement | Registre et manifeste |
| 2 | Audit des jeux | Rapport de données |
| 3 | Audit de cible | Rapport de validité |
| 4 | Pipeline et features | Tables Gold validées |
| 5 | Baselines | Benchmark v1 |
| 6 | Modèles d’arbres | Benchmark v2 |
| 7 | Réseaux compacts | Benchmark v3 |
| 8 | 31 mai vs 15 juin | Étude centrale |
| 9 | Ablations et validation | Rapport scientifique |
| 10 | Incertitude et explicabilité | Artefacts finaux |
| 11 | API, interface et Docker | Démo |
| 12 | Rapport, slides et release | `v1.0.0` |

## 21. Definition of Done

Le projet est terminé lorsque :

- la cible est documentée et défendable ;
- les datasets sont téléchargeables et hashés ;
- la chaîne Bronze–Silver–Gold est reproductible ;
- les baselines sont enregistrées ;
- les modèles sont comparés équitablement ;
- les horizons 31 mai et 15 juin sont comparés ;
- la validation temporelle et par parcelle est terminée ;
- les ablations sont terminées ;
- l’incertitude est calibrée ;
- l’explicabilité et la robustesse sont documentées ;
- l’API et l’interface fonctionnent ;
- les tests et la CI passent ;
- le rapport correspond au code ;
- une release `v1.0.0` est publiée.
