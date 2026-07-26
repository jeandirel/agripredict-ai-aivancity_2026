# AgriPredict AI — Critères de succès et Quality Gates

> **Cadre :** Clinique IA d’aivancity — 2026  
> **Version :** 1.0

## 1. Principe général

Le succès du projet ne sera pas évalué uniquement par la meilleure métrique prédictive. Le projet doit démontrer simultanément :

- une contribution scientifique claire ;
- une expérimentation rigoureuse ;
- une ingénierie reproductible ;
- une démonstration fonctionnelle ;
- une communication honnête des limites ;
- une gouvernance responsable des données et des modèles.

Les seuils ci-dessous sont des **objectifs de pilotage**. Ils pourront être ajustés après l’audit des données, mais toute modification devra être justifiée et tracée.

## 2. Critères globaux de réussite

| Dimension | Minimum acceptable | Cible d’excellence |
|---|---|---|
| Cadrage | Problématique et périmètre définis | Questions, hypothèses, décisions et critères d’acceptation entièrement traçables |
| Données | Données nettoyées et documentées | Data contracts, versionnement, provenance, licence, tests et Data Cards |
| Science | Baselines et modèle final comparés | Ablations, validation géographique/temporelle, incertitude, robustesse et analyse statistique |
| Logiciel | Code exécutable | Architecture modulaire, typage, tests, CI et Docker |
| MLOps | Modèles sauvegardés | DVC + MLflow + reproductibilité + monitoring prévu |
| Produit | Démo locale | API, interface, explications, incertitude et gestion des erreurs |
| Éthique | Limites mentionnées | Model Cards, domaine d’usage, biais, OOD et avertissements utilisateur |
| Soutenance | Résultats présentés | Narration scientifique, démonstration fluide et réponses défendables |

## 3. Module principal — Rendement agricole

### 3.1 Métrique principale

- **MAE en tonnes par hectare**, après confirmation de l’unité de la cible.

### 3.2 Métriques secondaires

- RMSE ;
- R² ;
- nRMSE ;
- biais moyen ;
- erreur médiane absolue ;
- métriques par État, district, année et niveau de rendement ;
- temps d’entraînement ;
- latence d’inférence ;
- consommation mémoire.

### 3.3 Critères d’acceptation scientifique

Le modèle final doit :

1. battre une baseline naïve sur tous les protocoles principaux ;
2. être évalué sur une année future ou la période la plus récente ;
3. être évalué sur des groupes géographiques non observés ;
4. inclure une étude d’ablation des modalités ;
5. fournir une analyse des erreurs par région ;
6. fournir un intervalle prédictif ;
7. documenter la stabilité entre plusieurs seeds ou folds.

### 3.4 Objectifs quantitatifs de pilotage

Ces valeurs seront recalibrées après l’audit :

- amélioration du MAE d’au moins **5 %** par rapport à la meilleure baseline simple ;
- amélioration mesurable de la fusion multimodale par rapport au meilleur modèle mono-source ;
- écart de performance géographique documenté pour 100 % des régions testées ;
- au moins 90 % de couverture empirique pour un intervalle nominal à 90 %, avec analyse de sa largeur ;
- latence d’inférence API inférieure à 1 seconde pour une observation standard, hors chargement initial.

Une amélioration inférieure à 5 % peut rester scientifiquement intéressante si elle est stable, robuste et obtenue sur un protocole de généralisation plus difficile.

## 4. Module sécheresse

### 4.1 Métrique principale

- RMSE sur l’indice futur de sévérité.

### 4.2 Métriques secondaires

- MAE ;
- R² ;
- NSE ;
- KGE ;
- macro-F1 après discrétisation en classes de risque ;
- performance par horizon ;
- performance par région.

### 4.3 Critères d’acceptation

- horizon de prévision explicitement défini ;
- split chronologique strict ;
- baseline de persistance obligatoire ;
- aucune variable future utilisée ;
- comparaison entre XGBoost-lags, modèle séquentiel et ensemble ;
- test walk-forward ;
- résultat régional documenté.

### 4.4 Objectifs de pilotage

- battre la baseline de persistance sur RMSE et MAE ;
- montrer que le stacking n’utilise que des prédictions hors-fold ;
- documenter toute dégradation sur une région ou une période extrême ;
- fournir une classe de risque avec une matrice de confusion.

## 5. Module recommandation de cultures

### 5.1 Métrique principale

- macro-F1.

### 5.2 Métriques secondaires

- balanced accuracy ;
- précision macro ;
- rappel macro ;
- Top-3 accuracy ;
- Brier Score ;
- Expected Calibration Error ;
- matrice de confusion ;
- performance par culture.

### 5.3 Critères d’acceptation

- split stratifié ;
- contrôle des doublons ;
- comparaison Dummy, KNN, arbre, Random Forest, XGBoost et au moins un réseau tabulaire ;
- probabilités calibrées ;
- sortie Top 3 ;
- alerte pour les entrées hors distribution.

### 5.4 Objectifs de pilotage

- macro-F1 supérieure à la baseline majoritaire et aux modèles simples ;
- Top-3 accuracy supérieure à la Top-1 accuracy de manière cohérente ;
- réduction de l’ECE après calibration ;
- aucune classe complètement ignorée sans analyse explicite.

## 6. Qualité des données

| Contrôle | Critère |
|---|---|
| Provenance | 100 % des fichiers ont une source documentée |
| Licence | Statut connu pour 100 % des datasets utilisés dans le rapport |
| Schéma | Data contract défini pour chaque table Gold |
| Types | 100 % des colonnes critiques validées automatiquement |
| Valeurs manquantes | Taux mesuré et stratégie documentée par variable |
| Doublons | Audit et règle de traitement documentés |
| Unités | Unité connue ou marquée « à confirmer » avant modélisation |
| Cible | Définition exacte, période et méthode de mesure documentées |
| Fuite | Checklist de fuite validée avant chaque entraînement final |
| Version | Empreinte ou version DVC disponible pour chaque expérience finale |

## 7. Reproductibilité et logiciel

### 7.1 Critères minimaux

- installation documentée ;
- configuration externalisée ;
- seeds contrôlées ;
- dépendances figées ;
- modèles sauvegardés avec métadonnées ;
- scripts séparés des notebooks.

### 7.2 Cibles

- `make test` passe sans erreur ;
- `make lint` passe sans erreur ;
- `make reproduce` reconstruit les principaux résultats ;
- couverture de tests supérieure ou égale à 70 % sur le code critique ;
- 100 % des endpoints principaux couverts par des tests d’intégration ;
- image Docker construite automatiquement ;
- aucune clé ou donnée sensible dans Git.

## 8. Suivi des expériences

Chaque expérience finale doit enregistrer :

- identifiant de run ;
- commit Git ;
- version du dataset ;
- seed ;
- configuration ;
- hyperparamètres ;
- métriques globales et segmentées ;
- artefacts graphiques ;
- durée ;
- environnement ;
- modèle produit.

**Critère de succès :** 100 % des résultats utilisés dans le rapport doivent être reliés à une expérience reproductible.

## 9. Explicabilité

### Critères

- explication globale du meilleur modèle ;
- explication locale d’au moins cinq cas représentatifs ;
- analyse d’au moins trois erreurs importantes ;
- stabilité des principales variables sur plusieurs folds ou seeds ;
- importance temporelle pour le module rendement ;
- avertissement explicite : importance prédictive ≠ causalité.

## 10. Robustesse

Le modèle principal doit être testé sous au moins quatre scénarios :

1. valeurs manquantes simulées ;
2. bruit sur variables numériques ;
3. suppression d’une modalité ;
4. région ou année non observée.

**Critère de succès :** la dégradation relative doit être mesurée, expliquée et intégrée aux limites du système.

## 11. API et interface

### API

- endpoints `/health`, `/model-info`, `/predict/crop`, `/predict/yield`, `/forecast/drought` et `/explain` ;
- validation stricte des entrées ;
- erreurs structurées ;
- documentation OpenAPI ;
- version du modèle retournée ;
- latence mesurée.

### Interface

- parcours fonctionnel pour les trois modules ;
- affichage de l’incertitude ;
- explication des résultats ;
- avertissement sur les limites ;
- gestion des entrées invalides ;
- démonstration sans modification manuelle du code.

## 12. Éthique et gouvernance

Le projet est acceptable uniquement si :

- le système est présenté comme un outil d’aide à la décision ;
- le domaine géographique et agronomique de validité est affiché ;
- les limites des données sont documentées ;
- les biais régionaux sont mesurés ;
- une stratégie OOD ou de rejet est prévue ;
- les données personnelles sont absentes ou traitées selon une base légale documentée ;
- les licences de données sont respectées ;
- une Model Card et une Data Card sont produites.

## 13. Quality Gates par phase

| Gate | Condition de passage |
|---|---|
| G0 — Cadrage | Six documents de Phase 0 complets et points à confirmer identifiés |
| G1 — Fondation | Dépôt installable, lint et tests initiaux opérationnels |
| G2 — Données | Tables Gold validées, versionnées et documentées |
| G3 — Baselines | Baselines reproductibles enregistrées dans MLflow |
| G4 — Modèles | Modèles classiques et neuronaux comparés équitablement |
| G5 — Validation | Tests temporels, géographiques, ablations et robustesse terminés |
| G6 — Produit | API et interface fonctionnelles et testées |
| G7 — Livraison | Docker, rapport, slides, démo et release `v1.0.0` terminés |

## 14. Définition finale de réussite

Le projet est terminé lorsque :

- les résultats du rapport peuvent être reproduits ;
- les trois modules ont une baseline ;
- le module rendement possède une validation scientifique complète ;
- l’incertitude et l’explicabilité sont intégrées ;
- les risques et limites sont transparents ;
- l’application fonctionne ;
- les tests et la CI passent ;
- la démonstration est exécutable ;
- le dépôt contient une release versionnée.
