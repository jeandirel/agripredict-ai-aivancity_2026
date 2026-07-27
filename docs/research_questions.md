# AgriPredict AI — Questions de recherche et hypothèses

> **Cadre :** Clinique IA d’aivancity — Promotion 2026  
> **Version :** 2.0

## 1. Question de recherche principale

> **RQ0 — Dans quelle mesure la fusion de données de sol, Sentinel-1, Sentinel-2 et météorologiques permet-elle de prévoir la date de récolte du blé à l’échelle parcellaire en Centre-Val de Loire, et quel compromis existe-t-il entre une prévision arrêtée au 31 mai et une prévision arrêtée au 15 juin ?**

## 2. Questions prioritaires

### RQ1 — Valeur de l’information supplémentaire entre le 31 mai et le 15 juin

> Le dataset arrêté au 15 juin réduit-il significativement l’erreur de prédiction par rapport au dataset arrêté au 31 mai ?

**Hypothèse H1 :** le 15 juin améliore le MAE et le RMSE grâce à des signaux météo et phénologiques plus proches de la récolte.

**Expérience :**

- conserver uniquement les observations communes aux deux jeux ;
- utiliser exactement les mêmes splits ;
- appliquer le même budget de tuning ;
- comparer MAE, RMSE, MedAE et taux d’erreur à ±5 et ±7 jours ;
- rapporter le gain de précision et la perte de 15 jours d’anticipation.

### RQ2 — Valeur de la fusion multimodale

> La combinaison du sol, de Sentinel-1, de Sentinel-2 et de la météo surpasse-t-elle le meilleur modèle mono-source ?

**Hypothèse H2 :** la fusion complète obtient une erreur inférieure, mais le gain peut varier selon l’année et la date de coupure.

**Ablations obligatoires :**

1. identifiants temporels et parcelle uniquement ;
2. sol uniquement ;
3. Sentinel-2 uniquement ;
4. Sentinel-1 uniquement ;
5. météo uniquement ;
6. Sentinel-1 + Sentinel-2 ;
7. satellite + météo ;
8. satellite + sol ;
9. sol + météo ;
10. toutes modalités.

### RQ3 — Cible dérivée et validité scientifique

> La construction de `harvest_doy_derived` introduit-elle une circularité ou une fuite avec les variables utilisées pour l’apprentissage ?

**Hypothèse H3 :** certaines variables phénologiques pourraient être fortement liées à la procédure de dérivation de la cible et devront être identifiées, exclues ou analysées séparément.

**Expérience :**

- reconstituer la méthode de dérivation ;
- lister toutes les variables utilisées directement ou indirectement ;
- vérifier leur disponibilité aux dates de coupure ;
- entraîner un modèle avec et sans variables potentiellement circulaires ;
- comparer la cible dérivée à la référence régionale lorsque les clés le permettent.

### RQ4 — Généralisation temporelle

> Un modèle entraîné sur les premières années conserve-t-il une performance acceptable sur la dernière année disponible ?

**Hypothèse H4 :** le test chronologique sera plus difficile qu’un split aléatoire en raison de la variabilité interannuelle.

**Expérience :**

- train sur les premières années ;
- validation sur l’avant-dernière année ;
- test final sur la dernière année ;
- aucun tuning après consultation du test final.

### RQ5 — Généralisation par parcelle

> Les résultats restent-ils robustes lorsque toutes les observations d’une même parcelle sont placées dans un seul fold ?

**Hypothèse H5 :** un split aléatoire au niveau des lignes surestimera la généralisation si une parcelle apparaît sur plusieurs années.

**Expérience :**

- comparer split aléatoire, split chronologique et `GroupKFold` par `parcelle_uid` ;
- mesurer l’écart de MAE ;
- analyser les parcelles les plus difficiles.

### RQ6 — Modèles d’arbres contre réseaux neuronaux tabulaires

> Un réseau neuronal tabulaire compact apporte-t-il un gain stable par rapport à XGBoost, CatBoost et Extra Trees ?

**Hypothèse H6 :** les modèles d’arbres resteront très compétitifs sur un dataset de taille modérée et à forte structure tabulaire.

**Comparaison :**

- Ridge et ElasticNet ;
- Random Forest ;
- Extra Trees ;
- XGBoost ;
- CatBoost ;
- MLP régularisé ;
- TabNet ;
- FT-Transformer compact comme extension.

### RQ7 — Incertitude prédictive

> Peut-on produire des intervalles prédictifs dont la couverture réelle est proche du niveau annoncé sur une année future ?

**Hypothèse H7 :** la conformal prediction ou la régression quantile permettra d’obtenir un intervalle interprétable en jours, sous réserve d’une calibration séparée.

**Métriques :**

- couverture empirique ;
- largeur moyenne ;
- largeur par année ;
- couverture pour les dates précoces, moyennes et tardives ;
- proportion d’intervalles trop confiants.

## 3. Questions complémentaires

### RQ8 — Variables les plus informatives

> Quelles familles de variables et quels indicateurs contribuent le plus à la prédiction ?

**Méthodes :** SHAP, permutation importance, importance par groupe de modalités et stabilité des rangs entre folds.

### RQ9 — Robustesse aux données manquantes

> Quelle est la dégradation du modèle lorsque certaines variables ou une modalité entière sont absentes ?

**Scénarios :**

- 5 %, 10 % et 20 % de valeurs manquantes simulées ;
- suppression de Sentinel-1 ;
- suppression de Sentinel-2 ;
- suppression de la météo ;
- imputation simple contre modèle tolérant les valeurs manquantes.

### RQ10 — Comparaison cible dérivée / référence régionale

> La variante régionale peut-elle servir de baseline, de variable auxiliaire ou de contrôle externe de la cible dérivée ?

**Condition :** la définition et la granularité de `master_ml_regional` doivent être confirmées avant toute comparaison.

### RQ11 — Stabilité des explications

> Les variables identifiées comme importantes restent-elles cohérentes entre années, folds et familles de modèles ?

### RQ12 — Efficacité

> Le gain éventuel d’un modèle complexe justifie-t-il son coût d’entraînement, sa latence, sa mémoire et sa difficulté de maintenance ?

### RQ13 — Détection hors domaine

> Le système peut-il détecter une parcelle dont les caractéristiques sont très éloignées du domaine d’entraînement ?

### RQ14 — Utilité opérationnelle

> Une prévision au 31 mai avec une erreur légèrement plus élevée peut-elle être plus utile qu’une prévision plus précise au 15 juin ?

Cette question doit être discutée avec un expert ou un utilisateur métier, car la meilleure métrique n’est pas nécessairement le meilleur compromis opérationnel.

## 4. Matrice question–expérience–métrique

| Question | Expérience principale | Métriques |
|---|---|---|
| RQ1 | Comparaison 31 mai / 15 juin sur observations communes | MAE, RMSE, MedAE, ±5 j, ±7 j |
| RQ2 | Ablation des modalités | Delta MAE, RMSE, R² |
| RQ3 | Audit de cible et exclusion de variables suspectes | Delta MAE, corrélations, traçabilité |
| RQ4 | Test sur dernière année | MAE, biais, RMSE, R² |
| RQ5 | Random split vs GroupKFold parcelle | Écart de MAE et variance |
| RQ6 | Arbres vs réseaux tabulaires | MAE, stabilité, temps, mémoire |
| RQ7 | Conformal ou quantile | Couverture, largeur moyenne |
| RQ8 | SHAP et permutation par modalité | Stabilité des rangs |
| RQ9 | Perturbations et modalités manquantes | Dégradation relative |
| RQ10 | Dérivée vs régionale | Écart, corrélation, biais |
| RQ11 | Explications multi-folds | Corrélation de rang, variance |
| RQ12 | Profilage | Durée, RAM, latence, taille |
| RQ13 | OOD | AUROC OOD, taux de rejet |
| RQ14 | Analyse métier | Délai d’anticipation, acceptabilité |

## 5. Critères d’interprétation

- Une comparaison 31 mai / 15 juin n’est valide que sur les mêmes observations.
- Une amélioration n’est concluante que si elle est stable sur plusieurs folds ou seeds.
- Un split aléatoire ne suffit pas pour conclure à la généralisation.
- Une variable importante n’est pas nécessairement causale.
- Une excellente performance peut être invalide si la cible est dérivée des mêmes variables.
- Un réseau neuronal n’est pas supérieur parce qu’il est plus complexe.
- Les résultats doivent être accompagnés de leur variabilité et de leurs limites.
- Une performance moyenne correcte ne doit pas masquer des erreurs extrêmes sur certaines années ou parcelles.

## 6. Priorisation

### Obligatoire pour la soutenance

- RQ1 ;
- RQ2 ;
- RQ3 ;
- RQ4 ;
- RQ5 ;
- RQ6 ;
- RQ7 ;
- RQ8.

### Fortement recommandé

- RQ9 ;
- RQ10 ;
- RQ11 ;
- RQ12.

### Extension

- RQ13 ;
- RQ14.
