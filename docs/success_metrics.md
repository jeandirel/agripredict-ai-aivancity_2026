# AgriPredict AI — Critères de succès et Quality Gates

> **Cadre :** Clinique IA d’aivancity — Promotion 2026  
> **Version :** 2.0

## 1. Principe général

Le succès du projet ne dépend pas uniquement du meilleur score. Il doit démontrer simultanément :

- la validité de la cible ;
- la qualité et la traçabilité des données ;
- une expérimentation rigoureuse ;
- une généralisation temporelle et par parcelle ;
- une comparaison équitable entre horizons et modèles ;
- une incertitude calibrée ;
- une ingénierie reproductible ;
- une démonstration fonctionnelle ;
- une communication honnête des limites.

Les seuils ci-dessous sont des objectifs de pilotage. Ils pourront être ajustés après l’audit programmatique, mais toute modification devra être tracée.

## 2. Critères globaux

| Dimension | Minimum acceptable | Cible d’excellence |
|---|---|---|
| Cadrage | Cible, zone et horizons définis | Questions, décisions, hypothèses et critères entièrement traçables |
| Données | Jeux finaux auditables | Chaîne Bronze–Silver–Gold, hashes, licences, Data Cards et tests |
| Validité | Cible décrite | Construction reproduite, fuite exclue et variante régionale analysée |
| Science | Baselines et modèle final | Ablations, validation temporelle et groupée, incertitude et robustesse |
| Logiciel | Code exécutable | Architecture modulaire, typage, tests, CI et Docker |
| MLOps | Modèles sauvegardés | DVC, MLflow, versionnement des données et reproductibilité complète |
| Produit | Démo locale | API, interface, explications, intervalle et gestion OOD |
| Soutenance | Résultats présentés | Démonstration fluide et choix scientifiquement défendables |

## 3. Métriques prédictives

### 3.1 Métrique principale

- **MAE en jours** sur `harvest_doy_derived`.

Cette métrique est directement interprétable : un MAE de 5 signifie que l’erreur absolue moyenne est de cinq jours.

### 3.2 Métriques secondaires

- RMSE en jours ;
- erreur médiane absolue ;
- R² ;
- biais moyen en jours ;
- erreur au 90e percentile ;
- proportion de prédictions à ±3 jours ;
- proportion à ±5 jours ;
- proportion à ±7 jours ;
- proportion à ±10 jours ;
- métriques par année ;
- métriques par plage de date de récolte ;
- métriques par disponibilité de modalités ;
- temps d’entraînement ;
- latence d’inférence ;
- mémoire consommée.

## 4. Comparaison 31 mai / 15 juin

La comparaison doit être faite sur :

- les mêmes parcelles-années ;
- les mêmes splits ;
- la même cible ;
- le même protocole de preprocessing ;
- le même budget de tuning ;
- les mêmes métriques.

### Indicateurs obligatoires

- MAE au 31 mai ;
- MAE au 15 juin ;
- gain absolu en jours ;
- gain relatif en pourcentage ;
- évolution du taux à ±5 et ±7 jours ;
- largeur des intervalles prédictifs ;
- coût de la perte de 15 jours d’anticipation.

### Critère scientifique

Le jeu du 15 juin n’est pas automatiquement supérieur au sens métier. Le rapport doit discuter si le gain de précision compense réellement le délai supplémentaire.

## 5. Critères d’acceptation scientifique

Le modèle final doit :

1. battre la baseline moyenne ou médiane sur tous les protocoles principaux ;
2. être évalué sur une année future non utilisée pour le tuning ;
3. être évalué avec séparation des parcelles ;
4. inclure une étude d’ablation ;
5. inclure une comparaison 31 mai / 15 juin ;
6. fournir une analyse des erreurs ;
7. fournir un intervalle prédictif ;
8. documenter la stabilité entre folds ou seeds ;
9. démontrer l’absence de fuite de cible ;
10. relier chaque résultat du rapport à un run reproductible.

## 6. Objectifs quantitatifs de pilotage

Ces objectifs seront recalibrés après le premier benchmark :

- améliorer le MAE d’au moins **5 %** par rapport à la meilleure baseline simple ;
- améliorer de manière stable le meilleur modèle mono-source grâce à la fusion, ou documenter honnêtement l’absence de gain ;
- atteindre une couverture empirique proche de 90 % pour un intervalle nominal à 90 % ;
- produire les métriques pour 100 % des années testées ;
- mesurer les erreurs extrêmes au 90e percentile ;
- obtenir une latence API inférieure à 1 seconde par observation, hors chargement initial ;
- éviter qu’un seul fold ou seed soit utilisé comme preuve finale.

Une amélioration inférieure à 5 % reste intéressante si elle est stable, obtenue sur un protocole plus strict ou accompagnée d’un meilleur intervalle d’incertitude.

## 7. Validité de la cible

Avant tout entraînement final :

| Contrôle | Critère de réussite |
|---|---|
| Définition | Méthode de calcul de `harvest_doy_derived` documentée |
| Temporalité | Aucune information postérieure à la coupure utilisée |
| Circularité | Variables servant à fabriquer la cible identifiées |
| Sensibilité | Modèle entraîné avec et sans variables potentiellement circulaires |
| Comparaison | Variante régionale analysée lorsque compatible |
| Traçabilité | Code, rapport et sources de construction reliés |

Aucun score ne sera considéré comme valide tant que ces contrôles ne sont pas satisfaits.

## 8. Qualité des données

| Contrôle | Critère |
|---|---|
| Provenance | 100 % des fichiers utilisés ont une URL et une source documentées |
| Version | Version ou date Kaggle et SHA-256 enregistrés |
| Licence | Statut relevé pour chaque dataset et source originale |
| Schéma | Data contract pour chaque table Gold |
| Types | Colonnes critiques validées automatiquement |
| Valeurs manquantes | Taux et traitement documentés par variable |
| Doublons | Audit exact et quasi-doublons réalisé |
| Unités | Unités documentées ou explicitement marquées inconnues |
| Clé | Unicité de `parcelle_uid` × `year` vérifiée |
| Date de coupure | Aucune feature après le 31 mai ou le 15 juin dans le jeu correspondant |
| Fuite | Checklist validée avant chaque modèle final |

## 9. Validation

### 9.1 Validation temporelle

- dernière année réservée au test final ;
- tuning sur les années antérieures uniquement ;
- aucun retour sur le test final après sélection du modèle.

### 9.2 Validation groupée

- `parcelle_uid` utilisé comme groupe ;
- aucune parcelle commune entre train et test dans ce protocole ;
- variance entre folds rapportée.

### 9.3 Comparaison équitable

- même dataset ;
- même split ;
- mêmes features autorisées ;
- même budget de tuning ;
- métriques identiques ;
- seeds contrôlées.

## 10. Incertitude

### Métriques

- couverture empirique ;
- largeur moyenne de l’intervalle ;
- largeur médiane ;
- couverture par année ;
- couverture par plage de récolte ;
- couverture OOD si mesurable.

### Cible de pilotage

Pour un intervalle nominal à 90 %, viser une couverture réelle comprise approximativement entre 87 % et 93 %, sans produire des intervalles inutilement larges.

## 11. Explicabilité

Le projet doit fournir :

- une explication globale du meilleur modèle ;
- une importance par famille de modalités ;
- une analyse locale d’au moins cinq parcelles ;
- une analyse d’au moins cinq erreurs importantes ;
- une étude de stabilité entre folds ;
- un avertissement clair : importance prédictive ≠ causalité.

## 12. Robustesse

Scénarios obligatoires :

1. 5 %, 10 % et 20 % de valeurs manquantes simulées ;
2. bruit sur certaines variables numériques ;
3. suppression d’une modalité ;
4. année future ;
5. parcelles non observées ;
6. observations hors plage typique.

Le succès consiste à mesurer et expliquer la dégradation, pas à prétendre qu’elle n’existe pas.

## 13. Reproductibilité et logiciel

### Critères minimaux

- installation documentée ;
- dépendances figées ;
- configuration externalisée ;
- scripts séparés des notebooks ;
- seeds contrôlées ;
- données versionnées ;
- modèles sauvegardés avec métadonnées.

### Cibles

- `make test` passe ;
- `make lint` passe ;
- `make reproduce` reconstruit les résultats principaux ;
- couverture de tests ≥ 70 % sur le code critique ;
- 100 % des endpoints principaux ont un test d’intégration ;
- image Docker construite automatiquement ;
- aucune clé ou donnée sensible dans Git.

## 14. Suivi des expériences

Chaque run final doit enregistrer :

- identifiant ;
- commit Git ;
- dataset et version ;
- hash des données ;
- horizon 31 mai ou 15 juin ;
- split ;
- seed ;
- configuration ;
- hyperparamètres ;
- métriques globales et segmentées ;
- artefacts ;
- durée ;
- environnement ;
- modèle produit.

**Critère :** 100 % des tableaux et figures du rapport sont reliés à un run reproductible.

## 15. API et interface

### API

- `GET /health` ;
- `GET /model-info` ;
- `POST /predict/harvest-date` ;
- `POST /explain` ;
- validation stricte des entrées ;
- version du modèle retournée ;
- horizon du modèle retourné ;
- erreurs structurées ;
- documentation OpenAPI.

### Interface

- sélection du modèle 31 mai ou 15 juin ;
- affichage du DOY ;
- conversion en date calendaire ;
- intervalle en jours ;
- facteurs explicatifs ;
- avertissement OOD ;
- démonstration sans modification manuelle du code.

## 16. Éthique et gouvernance

Le projet est acceptable uniquement si :

- le système est présenté comme une aide à la planification ;
- le domaine Centre-Val de Loire / blé est affiché ;
- la nature dérivée de la cible est visible ;
- les limites sont documentées ;
- les biais temporels et parcellaires sont mesurés ;
- une stratégie OOD est prévue ;
- les licences sont respectées ;
- une Data Card et une Model Card sont produites.

## 17. Quality Gates

| Gate | Condition de passage |
|---|---|
| G0 — Cadrage | Sources officielles, cible, horizons, questions et risques alignés |
| G1 — Fondation | Dépôt installable, lint et tests initiaux |
| G2 — Données | Téléchargement, hashes, schémas, audit de cible et tables Gold validés |
| G3 — Baselines | Baselines 31 mai et 15 juin reproductibles |
| G4 — Modèles | Arbres et réseaux compacts comparés équitablement |
| G5 — Validation | Temporel, parcelle, ablations, incertitude et robustesse terminés |
| G6 — Produit | API et interface fonctionnelles |
| G7 — Livraison | Docker, rapport, slides, démo et release `v1.0.0` |

## 18. Définition finale de réussite

Le projet est terminé lorsque :

- la cible est scientifiquement défendable ;
- la chaîne de données est reproductible ;
- les deux horizons sont comparés ;
- les résultats sont validés temporellement et par parcelle ;
- la fusion multimodale est évaluée par ablation ;
- les modèles complexes sont comparés à de fortes baselines ;
- l’incertitude et l’explicabilité sont intégrées ;
- l’application fonctionne ;
- les tests et la CI passent ;
- le rapport est entièrement reproductible ;
- une release versionnée est publiée.
