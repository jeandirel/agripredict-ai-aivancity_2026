# AgriPredict AI — Plan expert de réalisation

> Projet développé dans le cadre de la **Clinique IA d’aivancity — 2026**.
>
> Objectif : construire une plateforme d’intelligence artificielle agricole **scientifiquement rigoureuse, reproductible, explicable, testée et déployée**, afin de viser un niveau d’excellence académique et professionnel.

Aucun plan ne peut garantir une note, mais cette feuille de route couvre les dimensions attendues d’un projet de très haut niveau : **data science, deep learning, géospatial, séries temporelles, MLOps, logiciel, produit, éthique, gouvernance et soutenance**.

---

## 1. Vision finale du projet

### Nom du projet

**AgriPredict AI — Multimodal Agricultural Intelligence Platform**

### Problématique scientifique principale

> Dans quelle mesure la fusion de données satellitaires, météorologiques, pédologiques et historiques permet-elle d’améliorer la prédiction des rendements agricoles, la prévision de la sécheresse et la recommandation des cultures par rapport à des modèles utilisant une seule source de données ?

### Positionnement fonctionnel

Le projet comporte trois modules complémentaires, avec une priorité scientifique claire :

| Priorité | Module | Problème IA | Sortie attendue |
|---|---|---|---|
| Cœur scientifique | Prédiction du rendement agricole | Régression multimodale | Rendement estimé + intervalle d’incertitude |
| Module avancé | Prévision de la sécheresse | Prévision de séries temporelles | Sévérité future + niveau de risque |
| Module opérationnel | Recommandation de cultures | Classification multiclasse | Top 3 cultures + probabilités |

Le cœur du rapport et de la soutenance doit rester la **prédiction multimodale du rendement**, afin de conserver une vraie profondeur scientifique. Les deux autres modules renforcent la plateforme sans diluer le sujet central.

### Données envisagées

- **Sentinel-2** : NDVI, EVI, bandes spectrales et indicateurs de végétation.
- **EOS-06 SCAT-3** : rétrodiffusion SH, SV et ratio SH/SV.
- **Données météorologiques** : température, précipitations, humidité, vent, point de rosée.
- **Données pédologiques** : N, P, K, pH, AWC, FC, WP, SWC.
- **Données historiques agricoles** : cultures, surfaces, productions, rendements, districts, années.
- **Masques de cultures et limites administratives** pour le traitement géospatial.

---

## 2. Livrable final attendu

À la fin du projet, le dépôt doit contenir :

1. une pipeline complète de préparation et de validation des données ;
2. trois pipelines de machine learning ;
3. des baselines classiques et des réseaux neuronaux adaptés ;
4. une comparaison scientifique reproductible ;
5. une API FastAPI ;
6. une interface web de démonstration ;
7. un système d’explicabilité et d’estimation d’incertitude ;
8. des tests automatisés ;
9. une image Docker ;
10. une documentation complète ;
11. un rapport scientifique ;
12. une présentation de soutenance ;
13. une démonstration exécutable ;
14. une release GitHub `v1.0.0`.

### Commande cible de reproductibilité

```bash
make reproduce
```

Cette commande devra idéalement :

- vérifier l’environnement ;
- préparer les données ;
- entraîner les modèles principaux ;
- générer les métriques et figures ;
- exécuter les tests ;
- produire les artefacts de rapport.

---

## 3. Architecture fonctionnelle cible

```text
Données satellitaires
Sentinel-2 + SCAT-3
          │
          ▼
Pipeline géospatiale
NDVI, EVI, SH, SV, SH/SV
          │
          ├────────────────────┐
          │                    │
Données météo           Données pédologiques
pluie, température,     N, P, K, pH, AWC,
humidité, vent          FC, WP, SWC
          │                    │
          └──────────┬─────────┘
                     ▼
             Feature Store unifié
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
Recommandation   Rendement      Sécheresse
des cultures     agricole       météorologique
       │             │             │
 RF/XGBoost     XGBoost +       XGBoost +
 TabNet/MLP     LSTM/TCN        LSTM/TabNet
       └─────────────┼─────────────┘
                     ▼
           Fusion / Ensemble Learning
                     ▼
     API FastAPI + Dashboard + Cartographie
```

---

# PHASES DE RÉALISATION

## 4. Phase 0 — Cadrage scientifique

### Objectif

Éviter de transformer le projet en accumulation de modèles sans fil conducteur.

### Documents à créer avant de coder

```text
docs/
├── project_charter.md
├── problem_statement.md
├── research_questions.md
├── success_metrics.md
├── risks_and_assumptions.md
└── data_sources.md
```

### Questions de recherche

#### RQ1 — Rendement

> La fusion des séries NDVI, EVI, SH, SV et des propriétés du sol améliore-t-elle la prédiction du rendement par rapport aux données satellitaires ou pédologiques utilisées séparément ?

#### RQ2 — Architecture neuronale

> Une architecture neuronale à deux branches, temporelle et statique, généralise-t-elle mieux qu’un modèle XGBoost sur des districts ou des années non observés ?

#### RQ3 — Sécheresse

> Un ensemble XGBoost–LSTM–TabNet améliore-t-il la prévision de la sévérité de la sécheresse par rapport à chaque modèle individuel ?

#### RQ4 — Explicabilité

> Quelles variables et quelles périodes du cycle de culture influencent le plus les prédictions ?

### Hypothèses principales

- La fusion multimodale doit surpasser les modèles mono-source.
- Les variables satellitaires temporelles doivent être particulièrement importantes pendant certaines phases phénologiques.
- XGBoost sera probablement très compétitif lorsque le dataset est limité.
- Les réseaux neuronaux seront réellement utiles seulement si la structure temporelle et le volume des données sont suffisants.
- L’incertitude et l’explicabilité doivent être intégrées au produit final, et non ajoutées à la fin.

### Gate de validation

La phase est terminée uniquement lorsque chaque module possède :

- une entrée précisément définie ;
- une cible ;
- une unité de mesure ;
- une métrique principale ;
- une méthode de validation ;
- un critère d’acceptation.

---

## 5. Phase 1 — Mise en place du dépôt professionnel

### Arborescence recommandée

```text
agripredict-ai-aivancity_2026/
├── README.md
├── LICENSE
├── pyproject.toml
├── requirements.lock
├── Makefile
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
│
├── configs/
│   ├── data/
│   ├── models/
│   ├── experiments/
│   └── deployment/
│
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── external/
│
├── notebooks/
│   ├── 01_data_audit.ipynb
│   ├── 02_geospatial_eda.ipynb
│   ├── 03_crop_recommendation.ipynb
│   ├── 04_yield_prediction.ipynb
│   └── 05_drought_forecasting.ipynb
│
├── src/agripredict/
│   ├── data/
│   ├── features/
│   ├── models/
│   ├── evaluation/
│   ├── explainability/
│   ├── monitoring/
│   └── utils/
│
├── pipelines/
│   ├── build_crop_dataset.py
│   ├── build_yield_dataset.py
│   ├── build_drought_dataset.py
│   ├── train_crop_model.py
│   ├── train_yield_model.py
│   └── train_drought_model.py
│
├── app/
│   ├── api/
│   └── dashboard/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── data_validation/
│
├── models/
├── reports/
├── docs/
└── .github/workflows/
```

### Stack technique recommandée

- Python 3.11 ;
- PyTorch ;
- scikit-learn ;
- XGBoost ;
- Optuna ;
- MLflow ;
- DVC ;
- Pandera ou Great Expectations ;
- GeoPandas, Rasterio, Xarray ;
- FastAPI ;
- Streamlit ou React/Next.js ;
- Pytest ;
- Ruff ;
- MyPy ;
- GitHub Actions ;
- Docker.

### Gate de validation

```bash
make install
make lint
make test
```

doivent fonctionner sur une machine propre.

---

## 6. Phase 2 — Audit et gouvernance des données

Cette phase détermine une grande partie de la qualité scientifique du projet.

### 6.1 Inventaire des datasets

#### Dataset A — Recommandation de cultures

Variables principales :

- azote ;
- phosphore ;
- potassium ;
- température ;
- humidité ;
- pH ;
- précipitations ;
- culture cible.

#### Dataset B — Rendement agricole

Le dataset principal devra réunir :

- État ;
- district ;
- année ;
- rendement ;
- NDVI par période ;
- EVI par période ;
- SH par période ;
- SV par période ;
- ratio SH/SV ;
- capacité au champ ;
- point de flétrissement ;
- teneur en eau disponible ;
- teneur en eau saturée ;
- variables météorologiques agrégées.

#### Dataset C — Sécheresse

Variables envisagées :

- température ;
- précipitations ;
- humidité ;
- vitesse du vent ;
- point de rosée ;
- région ;
- État ;
- durée de la sécheresse ;
- indice de sévérité ;
- date ou pas de temps.

### 6.2 Contrôles obligatoires

Pour chaque dataset :

- provenance ;
- licence ;
- période ;
- région ;
- définition de la cible ;
- unités ;
- taux de valeurs manquantes ;
- doublons ;
- incohérences ;
- valeurs extrêmes ;
- déséquilibre des classes ;
- risque de fuite de données ;
- représentativité géographique ;
- possibilité de reproduction.

### 6.3 Data contracts

Créer un schéma Pandera par dataset.

```python
import pandera.pandas as pa
from pandera.typing import Series


class YieldSchema(pa.DataFrameModel):
    state: Series[str]
    district: Series[str]
    year: Series[int]
    yield_t_ha: Series[float]
    ndvi_t1: Series[float]
    evi_t1: Series[float]
    soil_awc: Series[float]
```

### 6.4 Organisation Bronze–Silver–Gold

```text
Raw/Bronze     = fichiers originaux immuables
Interim/Silver = données nettoyées et harmonisées
Processed/Gold = tables prêtes pour l’entraînement
```

Ne jamais modifier manuellement les données brutes.

### Gate de validation

Un rapport automatique doit afficher :

- nombre de lignes et colonnes ;
- qualité des variables ;
- distribution des cibles ;
- valeurs manquantes ;
- anomalies ;
- conformité au schéma ;
- empreinte du dataset ;
- version DVC.

---

## 7. Phase 3 — Pipeline géospatiale et feature engineering

### 7.1 Traitement Sentinel-2

- contrôle du système de coordonnées ;
- harmonisation des résolutions ;
- suppression ou masquage des nuages ;
- calcul du NDVI ;
- calcul de l’EVI ;
- extraction par zone ;
- agrégation par district ;
- agrégation par fenêtres de quinze jours ;
- production de séries temporelles propres.

### 7.2 Traitement SCAT-3

- conversion des valeurs brutes en coefficient de rétrodiffusion ;
- alignement spatial ;
- application des masques de riz ;
- comparaison de plusieurs seuils de couverture ;
- extraction de SH et SV ;
- calcul du ratio SH/SV ;
- agrégation par district et période ;
- contrôle des valeurs aberrantes.

### 7.3 Gestion des données manquantes

Comparer scientifiquement :

1. suppression ;
2. interpolation temporelle ;
3. KNN Imputer ;
4. nearest neighbour spatial ;
5. stratégie hybride haute qualité + nearest neighbour ;
6. indicateurs binaires signalant les valeurs imputées.

### 7.4 Features avancées

Créer notamment :

- moyenne, minimum et maximum saisonniers ;
- tendance NDVI ;
- amplitude NDVI ;
- date du pic NDVI ;
- aire sous la courbe NDVI ;
- volatilité SH/SV ;
- anomalies par rapport aux moyennes régionales ;
- précipitations cumulées ;
- nombre de jours secs ;
- température moyenne et extrême ;
- interactions sol × précipitations ;
- interactions satellite × sol ;
- lags temporels ;
- moyennes glissantes ;
- indicateurs phénologiques.

### Gate de validation

Chaque feature doit avoir :

- une définition ;
- une formule ;
- une justification agronomique ;
- une unité ;
- un test automatique ;
- une vérification de l’absence de fuite de cible.

---

## 8. Phase 4 — Stratégie expérimentale

### Règle absolue

Ne jamais commencer par le modèle le plus complexe.

L’ordre scientifique correct est :

```text
Dummy baseline
→ modèle linéaire
→ modèle ML classique
→ réseau neuronal
→ ensemble
→ analyse d’ablation
```

### Traçabilité MLflow

Chaque expérience devra enregistrer :

- version du code ;
- version du dataset ;
- hyperparamètres ;
- seed ;
- métriques ;
- figures ;
- temps d’entraînement ;
- consommation mémoire ;
- modèle ;
- matrice de confusion ou résidus ;
- environnement logiciel ;
- protocole de split.

### Principes scientifiques

- Fixer les seeds.
- Conserver un jeu de test final réellement indépendant.
- Ne jamais tuner sur le jeu de test.
- Comparer les modèles avec les mêmes folds.
- Enregistrer aussi les modèles qui échouent.
- Répéter les expériences lorsque la variance est importante.
- Rapporter moyenne et écart-type des métriques.

---

## 9. Phase 5 — Module de recommandation des cultures

### Objectif

Retourner les trois cultures les plus adaptées, avec probabilités, facteurs explicatifs et avertissement de confiance.

### Modèles de référence

- DummyClassifier ;
- régression logistique ;
- KNN ;
- arbre de décision.

### Modèles performants

- Random Forest ;
- XGBoost ;
- LightGBM uniquement si autorisé dans le cadre du projet.

### Réseaux neuronaux

- MLP régularisé ;
- TabNet ;
- FT-Transformer comme expérimentation complémentaire.

Avec un dataset limité, un modèle très lourd risque de surapprendre. Le réseau devra être compact, régularisé et comparé honnêtement aux modèles d’arbres.

### Validation

- split stratifié ;
- cross-validation stratifiée ;
- vérification des doublons ;
- recherche d’hyperparamètres par Optuna ;
- calibration des probabilités.

### Métriques

- macro-F1 ;
- balanced accuracy ;
- précision macro ;
- rappel macro ;
- top-3 accuracy ;
- matrice de confusion ;
- Expected Calibration Error.

### Sortie API cible

```json
{
  "recommended_crops": [
    {"crop": "rice", "probability": 0.72},
    {"crop": "maize", "probability": 0.18},
    {"crop": "jute", "probability": 0.06}
  ],
  "main_factors": [
    "high rainfall",
    "acidic soil",
    "high humidity"
  ],
  "confidence_level": "high"
}
```

---

## 10. Phase 6 — Module principal de prédiction du rendement

### 10.1 Baselines

- moyenne globale ;
- moyenne par État ;
- moyenne par district ;
- régression linéaire ;
- Ridge ;
- ElasticNet.

### 10.2 Modèles classiques

- Random Forest Regressor ;
- XGBoost Regressor ;
- Extra Trees ;
- HistGradientBoosting.

### 10.3 Réseau neuronal multimodal recommandé

Le réseau doit respecter la structure des données. Les données décrites sont surtout des séries temporelles agrégées par district, enrichies de variables statiques.

#### Branche temporelle

Entrée :

```text
T = plusieurs périodes temporelles
Canaux = NDVI, EVI, SH, SV, SH/SV, météo
```

Modèles à comparer :

- LSTM bidirectionnel ;
- Temporal CNN 1D ;
- TCN résiduel ;
- Transformer temporel compact, seulement si le volume le justifie.

#### Branche statique

Entrée :

- AWC ;
- FC ;
- WP ;
- SWC ;
- État ;
- district ;
- caractéristiques géographiques ;
- statistiques historiques autorisées.

Traitement :

- embeddings pour les catégories ;
- couches fully connected ;
- batch normalization ;
- dropout.

#### Fusion

```text
Temporal Encoder ──────┐
                       ├── Concatenation
Static Encoder ────────┘
                              │
                         Attention/Gating
                              │
                         Dense Regression
                              │
                 Yield + intervalle d’incertitude
```

### 10.4 Fonctions de coût

Comparer :

- MSE ;
- Huber Loss ;
- Quantile Loss.

Huber Loss peut améliorer la robustesse aux valeurs extrêmes.

### 10.5 Protocoles de validation rigoureux

Un simple split aléatoire peut produire une estimation trop optimiste lorsque le même district apparaît dans les ensembles d’entraînement et de test.

#### Validation temporelle

```text
Train : années antérieures
Test  : année future
```

#### Validation géographique

```text
GroupKFold(group = district)
```

#### Validation de généralisation

```text
Leave-One-State-Out
```

Un modèle ne sera considéré comme robuste que s’il fonctionne sur une année, un district ou un État non observé.

### 10.6 Métriques

- MAE ;
- RMSE ;
- R² ;
- nRMSE ;
- biais moyen ;
- erreur par État ;
- erreur par district ;
- intervalle de confiance des métriques ;
- couverture des intervalles prédictifs.

### 10.7 Études d’ablation

Entraîner séparément :

1. sol uniquement ;
2. Sentinel-2 uniquement ;
3. SCAT-3 uniquement ;
4. météo uniquement ;
5. Sentinel-2 + SCAT-3 ;
6. satellite + sol ;
7. satellite + météo + sol ;
8. modèle complet sans attention ;
9. modèle complet sans embeddings géographiques.

L’étude d’ablation doit démontrer la valeur réelle de chaque modalité et de chaque choix d’architecture.

---

## 11. Phase 7 — Module de prévision de la sécheresse

### Définition précise

Prévoir un indice de sévérité à un horizon explicitement défini :

- J+7 ;
- J+30 ;
- mois suivant ;
- ou prochaine période disponible.

Ne pas utiliser le mot « forecasting » si les lignes sont indépendantes et qu’aucune chronologie n’est respectée.

### Préparation temporelle

- tri par région et date ;
- création des lags ;
- moyennes glissantes ;
- anomalies saisonnières ;
- séquences d’entrée ;
- prévention de l’utilisation d’informations futures ;
- contrôle des trous temporels.

### Baselines

- dernière valeur connue ;
- moyenne mobile ;
- régression linéaire ;
- XGBoost avec variables retardées.

### Réseaux

- LSTM ;
- GRU ;
- Temporal CNN ;
- TabNet pour les variables tabulaires ;
- Transformer temporel compact si le dataset est réellement longitudinal.

### Ensemble

Construire les prédictions hors-fold de :

- XGBoost ;
- LSTM ;
- TabNet.

Puis entraîner un méta-modèle uniquement sur ces prédictions hors-fold.

```text
XGBoost ───┐
LSTM ──────┼── XGBoost Meta-Regressor ── Sévérité finale
TabNet ────┘
```

### Validation

- walk-forward validation ;
- aucune permutation aléatoire temporelle ;
- test sur une période future ;
- test sur une région non observée.

### Métriques

- MAE ;
- RMSE ;
- R² ;
- NSE ;
- KGE ;
- macro-F1 après transformation en classes de sévérité ;
- matrice de transition des niveaux de sécheresse.

---

## 12. Phase 8 — Incertitude, explicabilité et robustesse

Cette partie différencie fortement un projet académique moyen d’un projet expert.

### 12.1 Incertitude

Exemple de sortie :

```text
Prévision : 4,2 t/ha
Intervalle à 90 % : [3,7 ; 4,8]
```

Méthodes possibles :

- quantile regression ;
- bootstrap ;
- conformal prediction ;
- Monte Carlo Dropout pour certains réseaux.

### 12.2 Explicabilité

- SHAP pour XGBoost ;
- permutation importance ;
- Partial Dependence Plots ;
- Integrated Gradients pour les réseaux ;
- analyse temporelle des contributions ;
- importance par période de culture ;
- Grad-CAM seulement si de vraies images sont traitées par CNN.

Ne jamais présenter les poids d’attention comme une preuve causale.

### 12.3 Robustesse

Tester :

- 10 % de valeurs manquantes ;
- bruit sur les mesures NPK ;
- absence d’une période satellitaire ;
- changement de région ;
- changement d’année ;
- données hors distribution ;
- dérive simulée des précipitations ou températures.

### 12.4 Analyse des erreurs

Créer une taxonomie :

- erreurs liées aux données manquantes ;
- erreurs géographiques ;
- erreurs sur valeurs extrêmes ;
- erreurs sur cultures rares ;
- erreurs pendant les épisodes climatiques atypiques ;
- erreurs de calibration ;
- erreurs de généralisation temporelle.

---

## 13. Phase 9 — API et application

### API FastAPI

Endpoints cibles :

```text
GET  /health
GET  /model-info
POST /predict/crop
POST /predict/yield
POST /forecast/drought
POST /explain
```

### Interface utilisateur

#### Page 1 — Vue générale

- indicateurs du projet ;
- carte des régions ;
- qualité des données ;
- performances des modèles ;
- version des modèles.

#### Page 2 — Recommandation de culture

- saisie NPK ;
- pH ;
- météo ;
- top 3 cultures ;
- probabilités ;
- facteurs explicatifs ;
- niveau de confiance.

#### Page 3 — Prédiction de rendement

- district ;
- année ;
- courbes NDVI/EVI ;
- prédiction ;
- intervalle d’incertitude ;
- comparaison régionale ;
- explication locale.

#### Page 4 — Sécheresse

- historique météo ;
- évolution prévue ;
- niveau de risque ;
- carte ;
- alerte ;
- horizon de prévision.

#### Page 5 — Laboratoire scientifique

- modèles comparés ;
- métriques ;
- ablations ;
- SHAP ;
- erreurs par région ;
- résultats de robustesse ;
- journal d’expériences.

---

## 14. Phase 10 — MLOps et qualité logicielle

### Versionnement

- Git pour le code ;
- DVC pour les données ;
- MLflow pour les expériences ;
- tags Git pour les releases ;
- artefacts versionnés pour les modèles.

### Tests unitaires

- calcul du NDVI ;
- calcul du ratio SH/SV ;
- agrégation temporelle ;
- préparation des séquences ;
- validation des schémas ;
- format des prédictions ;
- transformation des catégories ;
- calcul des métriques.

### Tests de données

- types ;
- plages ;
- valeurs manquantes ;
- catégories inconnues ;
- dérive de schéma ;
- contrôle des unités ;
- absence de fuite temporelle.

### Tests d’intégration

```text
raw data
→ preprocessing
→ features
→ model
→ prediction
→ API response
```

### CI GitHub Actions

À chaque pull request :

```text
lint
type checking
unit tests
data schema tests
security scan
Docker build
```

### Monitoring

Même pour une démonstration académique :

- latence ;
- taux d’erreurs ;
- distributions des entrées ;
- dérive des variables ;
- niveau de confiance ;
- version du modèle ;
- statistiques de prédiction.

---

## 15. Phase 11 — Éthique, gouvernance et limites

### Risques principaux

- recommandation inadaptée pouvant influencer une décision économique ;
- biais géographique ;
- dataset non représentatif ;
- dérive climatique ;
- incertitude mal communiquée ;
- surconfiance envers le modèle ;
- dépendance à des données historiques ;
- mauvais usage hors de la zone étudiée ;
- confusion entre corrélation et causalité.

### Mesures de maîtrise

- afficher les limites géographiques ;
- ne jamais présenter la prédiction comme une certitude ;
- fournir un intervalle d’incertitude ;
- conserver une validation humaine ;
- documenter chaque source ;
- produire une Model Card ;
- produire une Data Card ;
- journaliser les versions ;
- documenter l’impact environnemental de l’entraînement ;
- distinguer aide à la décision et décision automatique.

### Formulation à afficher dans l’application

> Cette estimation constitue un outil d’aide à la décision. Elle ne remplace pas une expertise agronomique ni une analyse locale du terrain.

---

## 16. Phase 12 — Rapport scientifique

### Structure recommandée

1. résumé exécutif ;
2. contexte et enjeux ;
3. problématique ;
4. état de l’art ;
5. données ;
6. méthodologie ;
7. pipeline géospatiale ;
8. modèles classiques ;
9. réseaux neuronaux ;
10. stratégie d’ensemble ;
11. protocole expérimental ;
12. résultats ;
13. ablations ;
14. explicabilité ;
15. robustesse ;
16. application ;
17. MLOps ;
18. éthique ;
19. limites ;
20. perspectives ;
21. bibliographie ;
22. annexes de reproductibilité.

### Tableaux indispensables

- caractéristiques des datasets ;
- comparaison des modèles ;
- comparaison des protocoles de validation ;
- résultats des ablations ;
- temps d’entraînement ;
- performances par région ;
- couverture des intervalles d’incertitude ;
- consommation des ressources.

### Figures indispensables

- architecture complète ;
- carte des zones étudiées ;
- distributions des cibles ;
- courbes temporelles ;
- prédictions vs valeurs réelles ;
- résidus ;
- SHAP ;
- performances par région ;
- matrice de confusion ;
- courbes de calibration ;
- résultats de robustesse ;
- comparaison des ablations.

---

## 17. Plan d’exécution sur 14 semaines

| Semaine | Travail | Livrable |
|---|---|---|
| 1 | Cadrage, problématique, questions de recherche | Project Charter |
| 2 | Initialisation GitHub, environnement, CI | Dépôt professionnel |
| 3 | Inventaire, audit et versionnement des données | Data Report |
| 4 | Pipeline de recommandation des cultures | Dataset Gold 1 |
| 5 | Pipeline géospatiale de rendement | Dataset Gold 2 |
| 6 | Pipeline temporelle de sécheresse | Dataset Gold 3 |
| 7 | Baselines des trois modules | Benchmark v1 |
| 8 | XGBoost, Random Forest, tuning Optuna | Benchmark v2 |
| 9 | LSTM, TCN, MLP, TabNet | Deep Learning v1 |
| 10 | Fusion multimodale et stacking | Modèles finaux |
| 11 | Ablations, incertitude, SHAP, robustesse | Rapport expérimental |
| 12 | API FastAPI et interface | Démo fonctionnelle |
| 13 | Docker, tests, documentation, Model Cards | Release candidate |
| 14 | Rapport, slides, répétition, release | `v1.0.0` |

---

## 18. Definition of Done

Le projet ne sera considéré comme terminé que lorsque :

- [ ] le dépôt s’installe depuis zéro ;
- [ ] les données sont versionnées ;
- [ ] les trois tâches ont une baseline ;
- [ ] chaque réseau est comparé à un modèle classique ;
- [ ] aucun split ne provoque de fuite temporelle ou géographique ;
- [ ] les expériences sont suivies dans MLflow ;
- [ ] les résultats sont reproductibles ;
- [ ] les ablations sont terminées ;
- [ ] les erreurs sont analysées ;
- [ ] les prédictions possèdent une mesure d’incertitude ;
- [ ] l’application fonctionne ;
- [ ] l’API est documentée ;
- [ ] Docker fonctionne ;
- [ ] les tests passent ;
- [ ] les limites sont écrites ;
- [ ] le rapport correspond exactement au code ;
- [ ] la démonstration peut être exécutée sans modification manuelle ;
- [ ] une release GitHub est publiée.

---

## 19. Erreurs à éviter absolument

- utiliser un CNN uniquement parce qu’il paraît sophistiqué ;
- annoncer une précision de 99 % sans vérifier les fuites ;
- faire un split aléatoire sur des séries temporelles ;
- utiliser les mêmes districts dans le train et le test sans justification ;
- présenter trois notebooks indépendants comme une plateforme ;
- ne pas versionner les données ;
- ne montrer que les meilleurs résultats ;
- ignorer les modèles qui échouent ;
- ne pas analyser les erreurs ;
- confondre corrélation et causalité ;
- oublier les incertitudes ;
- déployer un modèle différent de celui évalué ;
- présenter une belle interface sans profondeur scientifique ;
- présenter une recherche brillante sans démonstration fonctionnelle ;
- utiliser un modèle très lourd sans justification par le volume de données.

---

## 20. Premières actions à exécuter

### Jour 1

1. créer et structurer le dépôt ;
2. écrire la problématique ;
3. écrire les questions de recherche ;
4. créer le tableau des datasets ;
5. créer les premières issues GitHub ;
6. définir le protocole de validation.

### Jour 2

1. installer l’environnement ;
2. configurer Ruff, MyPy, Pytest et pre-commit ;
3. configurer DVC ;
4. créer les schémas de données ;
5. importer les fichiers bruts sans modification.

### Jour 3

1. produire l’audit automatique ;
2. identifier la cible de chaque module ;
3. implémenter les splits ;
4. créer un premier Dummy Model ;
5. enregistrer la première expérience MLflow.

### Première milestone recommandée

```text
M1 — Reproducible Data Foundation
```

### Première issue recommandée

```text
[DATA] Audit, validate and version all project datasets
```

---

## 21. Critères de qualité pour la soutenance

Le projet doit pouvoir répondre clairement aux questions suivantes :

1. Pourquoi ce problème est-il important ?
2. Quelle est la contribution scientifique du projet ?
3. Pourquoi ces données ont-elles été choisies ?
4. Comment les fuites de données ont-elles été évitées ?
5. Pourquoi le réseau neuronal est-il adapté à la structure des données ?
6. Le deep learning surpasse-t-il réellement XGBoost ?
7. Quelle modalité apporte le plus de valeur ?
8. Le modèle généralise-t-il à une nouvelle année ou région ?
9. Comment l’incertitude est-elle estimée ?
10. Comment expliquer une prédiction individuelle ?
11. Quelles sont les limites du modèle ?
12. Comment reproduire les résultats ?
13. Comment déployer et surveiller la solution ?
14. Comment éviter un usage dangereux ou abusif ?

---

## 22. Sources de travail initiales

Documents utilisés comme base de cadrage :

- `RYP_Content_Report.pdf` — intégration de données Sentinel-2, SCAT-3, sol et rendement du riz ;
- `Drought_Forecasting.pdf` — ensemble XGBoost, LSTM et TabNet pour la sécheresse ;
- `Predicting_Agriculture_Yields_Based_on_Machine_Lea_251008_101501.pdf` — comparaison de modèles ML/DL pour le rendement ;
- `Crop_prediction_using_machine_learning_251008_101410.pdf` — recommandation de cultures par apprentissage supervisé.

Les résultats publiés dans ces documents doivent être considérés comme des **points de comparaison**, et non comme des performances automatiquement reproductibles dans ce dépôt.

---

## Conclusion

Le niveau expert ne vient pas uniquement de l’utilisation de réseaux neuronaux puissants. Il vient de la combinaison cohérente de :

- données fiables et versionnées ;
- protocoles expérimentaux rigoureux ;
- modèles adaptés à la structure des données ;
- comparaison honnête avec des baselines ;
- généralisation temporelle et géographique ;
- explicabilité et incertitude ;
- qualité logicielle et MLOps ;
- produit démontrable ;
- gouvernance et éthique ;
- rapport scientifique reproductible.

Ce document constitue la feuille de route officielle du projet **AgriPredict AI — Clinique IA aivancity 2026**.
