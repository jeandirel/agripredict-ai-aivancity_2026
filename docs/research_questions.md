# AgriPredict AI — Questions de recherche et hypothèses

> **Cadre :** Clinique IA d’aivancity — 2026  
> **Version :** 1.0

## 1. Question de recherche principale

> **RQ0 — Dans quelle mesure une architecture d’intelligence artificielle multimodale combinant données satellitaires, météorologiques, pédologiques, géographiques et historiques améliore-t-elle la prédiction agricole par rapport à des approches mono-source, tout en conservant une généralisation, une explicabilité et une incertitude fiables ?**

## 2. Questions de recherche — Module rendement

### RQ1 — Valeur de la fusion multimodale

> La fusion des séries NDVI, EVI, SH, SV, des variables météorologiques et des propriétés du sol réduit-elle significativement l’erreur de prédiction du rendement par rapport aux meilleurs modèles mono-source ?

**Hypothèse H1 :** la fusion multimodale obtient un MAE et un RMSE inférieurs aux configurations utilisant uniquement le satellite, la météo ou le sol.

**Expérience :** étude d’ablation avec les configurations suivantes :

1. sol uniquement ;
2. météo uniquement ;
3. Sentinel-2 uniquement ;
4. SCAT-3 uniquement ;
5. Sentinel-2 + SCAT-3 ;
6. satellite + sol ;
7. satellite + météo ;
8. satellite + météo + sol.

### RQ2 — Modèle classique contre réseau neuronal

> Une architecture neuronale à deux branches, temporelle et statique, généralise-t-elle mieux qu’un modèle XGBoost sur des années, districts ou États non observés ?

**Hypothèse H2 :** le réseau multimodal peut mieux représenter la dynamique temporelle, mais XGBoost restera très compétitif lorsque le volume de données est limité.

**Expérience :** comparaison équitable entre :

- Ridge / ElasticNet ;
- Random Forest ;
- XGBoost ;
- TCN ou LSTM bidirectionnel ;
- architecture multimodale temporelle + statique ;
- ensemble des meilleurs modèles.

### RQ3 — Importance de la validation géographique

> Les performances obtenues avec un split aléatoire surestiment-elles la performance réelle sur des zones géographiques non observées ?

**Hypothèse H3 :** les métriques seront moins favorables avec GroupKFold par district et Leave-One-State-Out qu’avec un split aléatoire.

**Expérience :** exécuter le même modèle et le même espace d’hyperparamètres sous plusieurs protocoles de validation.

### RQ4 — Importance de la validation temporelle

> Un modèle entraîné sur les années antérieures conserve-t-il ses performances sur une année future ?

**Hypothèse H4 :** la dérive climatique et interannuelle dégradera les performances par rapport à une validation aléatoire.

**Expérience :** entraînement sur les années antérieures et test sur la dernière année disponible.

### RQ5 — Phases phénologiques

> Quelles périodes du cycle cultural contribuent le plus à la prédiction du rendement ?

**Hypothèse H5 :** les périodes correspondant à la croissance végétative et reproductive seront plus informatives que les périodes très précoces ou tardives.

**Expérience :** importance temporelle, permutation par fenêtre, ablation d’une période et Integrated Gradients sur les modèles neuronaux.

### RQ6 — Gestion des valeurs manquantes

> Une stratégie hybride de comblement des données satellitaires améliore-t-elle la robustesse sans introduire un biais excessif ?

**Hypothèse H6 :** le comblement hybride permettra une meilleure couverture que la suppression, avec une erreur plus faible qu’une imputation naïve.

**Expérience :** comparer suppression, interpolation temporelle, KNN, nearest-neighbour spatial et méthode hybride, tout en conservant un indicateur d’imputation.

### RQ7 — Incertitude prédictive

> Les intervalles produits par quantile regression ou conformal prediction atteignent-ils leur niveau de couverture nominal sur des données futures et géographiquement nouvelles ?

**Hypothèse H7 :** la calibration devra être effectuée séparément du jeu de test pour atteindre une couverture proche de la cible.

**Expérience :** mesurer la couverture empirique, la largeur moyenne des intervalles et la couverture par région.

## 3. Questions de recherche — Module sécheresse

### RQ8 — Apprentissage temporel

> Les modèles séquentiels améliorent-ils la prévision de la sévérité de la sécheresse par rapport à XGBoost entraîné sur des variables retardées ?

**Hypothèse H8 :** un LSTM, GRU ou TCN pourra mieux capturer certaines dépendances temporelles, sous réserve d’une chronologie suffisamment longue et régulière.

### RQ9 — Ensemble de modèles

> Un ensemble XGBoost–LSTM–TabNet améliore-t-il la prévision de la sécheresse par rapport à chaque modèle individuel ?

**Hypothèse H9 :** un stacking entraîné sur des prédictions hors-fold réduira le RMSE sans fuite de données.

### RQ10 — Généralisation régionale

> Le modèle de sécheresse conserve-t-il une performance acceptable sur une région absente de l’entraînement ?

**Hypothèse H10 :** les performances varieront selon les régimes climatiques et nécessiteront une analyse régionale détaillée.

## 4. Questions de recherche — Module recommandation de cultures

### RQ11 — Modèles d’arbres contre réseaux tabulaires

> Sur un dataset tabulaire de taille limitée, Random Forest et XGBoost sont-ils plus robustes que MLP ou TabNet ?

**Hypothèse H11 :** les modèles d’arbres égaleront ou dépasseront les réseaux lorsque le nombre d’observations est faible.

### RQ12 — Calibration du Top 3

> Les probabilités du Top 3 sont-elles suffisamment calibrées pour informer l’utilisateur sur le niveau de confiance ?

**Hypothèse H12 :** une calibration post-hoc améliorera le Brier Score et l’Expected Calibration Error sans dégrader fortement la macro-F1.

### RQ13 — Données hors distribution

> Le système peut-il détecter des combinaisons NPK, pH et météo éloignées du domaine d’entraînement ?

**Hypothèse H13 :** un détecteur simple fondé sur la distance ou la densité permettra d’éviter des recommandations excessivement confiantes.

## 5. Questions transversales

### RQ14 — Explicabilité

> Les explications globales et locales sont-elles stables entre plusieurs seeds, folds et familles de modèles ?

### RQ15 — Robustesse

> Quel est l’impact du bruit, des valeurs manquantes et de l’absence d’une modalité sur les performances ?

### RQ16 — Coût et efficacité

> Le gain de performance d’un modèle complexe justifie-t-il son coût d’entraînement, sa latence et sa consommation mémoire ?

### RQ17 — Utilité produit

> Les sorties de l’interface sont-elles compréhensibles et actionnables sans masquer les limites du modèle ?

## 6. Matrice question–expérience–métrique

| Question | Expérience principale | Métriques |
|---|---|---|
| RQ1 | Ablation des modalités | MAE, RMSE, R², nRMSE |
| RQ2 | XGBoost vs réseau multimodal | MAE, RMSE, temps, mémoire |
| RQ3 | Random split vs GroupKFold | Écart de MAE/RMSE |
| RQ4 | Test sur année future | MAE, biais, R² |
| RQ5 | Ablation temporelle | Delta MAE, importance temporelle |
| RQ6 | Comparaison des imputations | MAE, couverture, biais |
| RQ7 | Calibration d’incertitude | Couverture, largeur d’intervalle |
| RQ8 | XGBoost-lags vs séquentiel | RMSE, MAE, NSE, KGE |
| RQ9 | Modèles individuels vs stacking | RMSE, MAE, R² |
| RQ10 | Région non observée | Métriques par région |
| RQ11 | Arbres vs réseaux tabulaires | Macro-F1, balanced accuracy |
| RQ12 | Calibration | ECE, Brier Score, Top-3 accuracy |
| RQ13 | OOD | AUROC OOD, taux de rejet |
| RQ14 | Stabilité des explications | Rang de corrélation, variance |
| RQ15 | Tests de perturbation | Dégradation relative |
| RQ16 | Profilage | Latence, RAM, durée, taille modèle |
| RQ17 | Test utilisateur | Taux de compréhension, erreurs d’interprétation |

## 7. Règles d’interprétation

- Une amélioration doit être mesurée sur le même jeu de test et avec le même protocole.
- Une différence observée sur une seule seed n’est pas considérée comme concluante.
- Les résultats doivent être présentés avec leur variabilité.
- Une meilleure moyenne ne suffit pas si le modèle échoue sur certaines régions.
- Les explications ne doivent pas être interprétées comme des relations causales.
- Un modèle plus complexe n’est retenu que si son gain est mesurable et justifiable.

## 8. Priorisation

### Obligatoire pour la soutenance

- RQ1, RQ2, RQ3, RQ4, RQ5, RQ7 et RQ14.

### Fortement recommandé

- RQ6, RQ8, RQ9, RQ11, RQ12 et RQ15.

### Extension si le temps et les données le permettent

- RQ10, RQ13, RQ16 et RQ17.
