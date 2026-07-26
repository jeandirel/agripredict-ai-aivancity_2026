# AgriPredict AI — Registre des risques et hypothèses

> **Cadre :** Clinique IA d’aivancity — 2026  
> **Version :** 1.0  
> **Responsable du suivi :** Jean Direl NZE

## 1. Méthode de cotation

- **Probabilité :** Faible, Moyenne, Élevée.
- **Impact :** Faible, Moyen, Élevé, Critique.
- **Priorité :** appréciation combinée de la probabilité et de l’impact.
- **Déclencheur :** signal concret indiquant que le risque devient actif.

Le registre doit être revu chaque semaine et à la fin de chaque phase.

## 2. Registre des risques

| ID | Risque | Probabilité | Impact | Priorité | Déclencheur | Mesures préventives | Plan de réponse |
|---|---|---:|---:|---:|---|---|---|
| R-001 | Données principales indisponibles ou incomplètes | Élevée | Critique | Critique | Fichiers manquants, accès refusé, couverture insuffisante | Inventaire immédiat, sources alternatives, dataset minimal viable | Réduire le périmètre géographique ou temporel sans changer la question scientifique |
| R-002 | Licence incompatible avec la redistribution GitHub | Moyenne | Élevé | Élevée | Licence absente, restrictive ou incertaine | Documenter chaque licence avant commit | Stocker uniquement scripts, métadonnées et instructions de téléchargement |
| R-003 | Définition de la cible rendement ambiguë | Moyenne | Critique | Critique | Unités incohérentes ou méthodologie inconnue | Valider unité, période, agrégation et provenance | Suspendre l’entraînement final jusqu’à clarification |
| R-004 | Trop peu d’années pour une vraie validation temporelle | Élevée | Élevé | Critique | Une ou deux années seulement | Rechercher une extension historique, utiliser GroupKFold géographique | Présenter clairement la limite et éviter de sur-vendre le forecasting |
| R-005 | Fuite de données temporelle ou géographique | Moyenne | Critique | Critique | Même district ou information future présente dans train et test | Pipelines séparés, splits avant preprocessing, revue de fuite | Invalider les résultats concernés et réentraîner |
| R-006 | Réseau neuronal surdimensionné pour le volume de données | Élevée | Élevé | Critique | Écart train-test important, forte variance | Baselines obligatoires, architecture compacte, régularisation | Retenir XGBoost ou un réseau plus simple si mieux justifié |
| R-007 | Fusion multimodale n’améliore pas les performances | Moyenne | Moyen | Élevée | Ablation complète sans gain significatif | Hypothèses explicites, analyse par région et période | Valoriser le résultat négatif et expliquer quand chaque modalité aide |
| R-008 | Données satellitaires trop manquantes ou bruitées | Élevée | Élevé | Critique | Forte couverture nuageuse, nombreuses valeurs nulles | Masques qualité, stratégie d’imputation comparée | Réduire les fenêtres, utiliser micro-ondes ou indicateurs d’imputation |
| R-009 | Résolutions spatiales incompatibles | Élevée | Élevé | Critique | Alignement incorrect des rasters et districts | CRS contrôlé, tests géospatiaux, resampling documenté | Refaire la pipeline à partir des données brutes validées |
| R-010 | Données météo non alignées avec les zones et périodes | Moyenne | Élevé | Élevée | Dates, coordonnées ou unités incohérentes | Data contracts et tables de correspondance | Exclure temporairement la modalité météo et documenter l’impact |
| R-011 | Résultats excellents mais non reproductibles | Moyenne | Critique | Critique | Notebook manuel, seed absente, dépendances flottantes | Scripts, configurations, DVC, MLflow, lockfile | Ne pas utiliser le résultat dans le rapport tant qu’il n’est pas reproduit |
| R-012 | Tuning sur le jeu de test | Moyenne | Critique | Critique | Modifications guidées par les scores de test | Jeux train/validation/test séparés | Recréer un test final non consulté |
| R-013 | Métriques globales masquant des échecs régionaux | Élevée | Élevé | Critique | Grande dispersion des erreurs entre régions | Métriques segmentées obligatoires | Ajouter calibration ou modèles spécialisés, sinon limiter le domaine d’usage |
| R-014 | Intervalles d’incertitude mal calibrés | Moyenne | Élevé | Élevée | Couverture réelle inférieure à la cible | Jeu de calibration séparé, conformal prediction | Recalibrer ou afficher un niveau de confiance plus prudent |
| R-015 | Explications instables ou trompeuses | Moyenne | Élevé | Élevée | Variables importantes changeant selon seed/fold | Stabilité des rangs, plusieurs méthodes | Présenter les explications comme associatives et signaler l’instabilité |
| R-016 | Temps de calcul ou mémoire insuffisants | Moyenne | Élevé | Élevée | OOM, entraînements trop longs | Profilage précoce, traitement par blocs, modèles compacts | Réduire la résolution, échantillonner, utiliser cloud ou CPU optimisé |
| R-017 | Dérive du périmètre vers trois projets indépendants | Élevée | Élevé | Critique | Trois notebooks sans architecture commune | Rendement prioritaire, composants partagés, backlog priorisé | Geler les extensions et terminer le cœur scientifique |
| R-018 | Interface esthétique mais faible profondeur scientifique | Moyenne | Élevé | Élevée | Temps excessif consacré au front avant validation | Gate scientifique avant produit | Reporter les améliorations visuelles non essentielles |
| R-019 | Difficulté à défendre les choix en soutenance | Moyenne | Élevé | Élevée | Choix non documentés, code opaque | Decision log, commentaires, fiches modèles | Préparer questions-réponses et démonstrations d’ablation |
| R-020 | Absence d’expertise agronomique | Élevée | Élevé | Critique | Variables ou résultats interprétés sans validation métier | Identifier un relecteur métier | Limiter les conclusions et marquer les interprétations à confirmer |
| R-021 | Utilisateur interprétant la sortie comme une prescription certaine | Moyenne | Critique | Critique | Interface sans avertissement ni incertitude | Avertissements, intervalles, domaine de validité | Bloquer ou dégrader la recommandation en cas d’OOD |
| R-022 | Données personnelles ou sensibles ajoutées par erreur | Faible | Critique | Élevée | Identifiants, coordonnées sensibles, clés | Scan de secrets, revue des fichiers | Retirer, révoquer, purger l’historique et documenter l’incident |
| R-023 | Dépendances logicielles vulnérables | Moyenne | Moyen | Moyenne | Alertes de sécurité | Dependabot, scan CI | Mettre à jour ou remplacer la dépendance |
| R-024 | Démo instable le jour de la soutenance | Moyenne | Critique | Critique | Dépendance réseau ou service externe | Mode local, cache, Docker, données de démonstration | Préparer vidéo et captures comme solution de secours |

## 3. Hypothèses structurantes

| ID | Hypothèse | Statut | Comment la vérifier | Conséquence si fausse |
|---|---|---|---|---|
| A-001 | Les données de rendement disposent d’une unité cohérente | À confirmer | Audit des fichiers et documentation | Réviser la cible ou normaliser les unités |
| A-002 | Les observations peuvent être reliées à un district et une année | Probable | Vérification des clés | Repenser le niveau d’agrégation |
| A-003 | Les séries NDVI/EVI et SH/SV sont disponibles sur des périodes communes | À confirmer | Jointure temporelle et audit de couverture | Utiliser sous-ensembles communs ou modèles à modalités manquantes |
| A-004 | Les variables météo sont accessibles pour les mêmes zones | À confirmer | Cartographie des stations/grilles | Retirer ou approximer la modalité météo |
| A-005 | Les propriétés du sol sont suffisamment stables à l’échelle étudiée | Probable | Documentation de la source | Limiter l’interprétation temporelle du sol |
| A-006 | L’agrégation par périodes de quinze jours reste agronomiquement pertinente | À confirmer métier | Revue bibliographique et expert | Tester d’autres fenêtres temporelles |
| A-007 | Le volume est suffisant pour au moins un réseau compact | À confirmer | Comptage après nettoyage | Garder les réseaux comme expérimentation secondaire |
| A-008 | Une année ou région peut être réservée pour le test final | À confirmer | Inventaire des données | Utiliser nested CV et expliciter la limite |
| A-009 | Le dataset sécheresse contient une vraie dimension temporelle | À confirmer | Vérification des timestamps et séquences | Requalifier le problème en régression, pas forecasting |
| A-010 | Les 22 classes de cultures sont suffisamment représentées | Probable | Distribution par classe | Regroupement, pondération ou collecte complémentaire |
| A-011 | Les ressources de calcul permettent le traitement géospatial | À confirmer | Benchmark sur un échantillon | Traitement par tuiles, cloud ou réduction de résolution |
| A-012 | Le dépôt peut rester public | À confirmer | Revue des licences et données | Passer les données hors dépôt ou rendre certaines ressources privées |
| A-013 | Un référent académique validera le cadrage | Probable | Revue formelle Phase 0 | Documenter les décisions en autonomie et demander validation ultérieure |
| A-014 | Un expert métier peut relire les conclusions | Incertain | Identifier un contact | Renforcer les réserves et limiter les recommandations métier |

## 4. Risques éthiques spécifiques

### 4.1 Biais géographique

Un modèle entraîné sur certaines régions peut être moins fiable dans des zones présentant d’autres pratiques agricoles, sols ou climats.

**Mesures :**

- métriques par région ;
- Leave-One-Region-Out ;
- avertissement de domaine ;
- rejet OOD.

### 4.2 Surconfiance

Une prédiction numérique précise en apparence peut masquer une forte incertitude.

**Mesures :**

- intervalle prédictif ;
- calibration ;
- explication des limites ;
- pas de recommandation automatique irréversible.

### 4.3 Corrélation et causalité

Les variables importantes pour un modèle ne prouvent pas qu’elles causent directement le rendement.

**Mesures :**

- vocabulaire prudent ;
- ne pas formuler de prescription agronomique causale ;
- validation métier.

### 4.4 Usage hors domaine

Le modèle pourrait être appliqué à une culture, une année, une zone ou un type de sol absent de l’entraînement.

**Mesures :**

- domaine de validité dans la Model Card ;
- détection OOD ;
- blocage ou avertissement fort.

## 5. Plan de contingence par niveau

### Niveau 1 — Ajustement mineur

- Corriger une source.
- Modifier une feature.
- Réentraîner sans changer la problématique.

### Niveau 2 — Réduction contrôlée du périmètre

- Réduire le nombre de régions.
- Se concentrer sur une culture.
- Limiter les modules secondaires.

### Niveau 3 — Recentrage scientifique

- Conserver uniquement le module rendement.
- Transformer un module secondaire en étude exploratoire.
- Remplacer un réseau lourd par une baseline mieux justifiée.

### Niveau 4 — Blocage critique

- Suspendre les conclusions.
- Documenter l’impossibilité de répondre avec les données disponibles.
- Livrer une pipeline reproductible et un protocole expérimental prêt à être exécuté dès disponibilité des données.

## 6. Revue hebdomadaire

À chaque revue :

1. vérifier les nouveaux risques ;
2. mettre à jour la probabilité et l’impact ;
3. associer une action et une échéance ;
4. fermer les risques résolus avec preuve ;
5. escalader tout risque critique affectant la cible, la licence ou la validité scientifique.

## 7. Risques bloquants avant la Phase 1

Les éléments suivants doivent être clarifiés ou explicitement acceptés comme hypothèses :

- données réellement accessibles ;
- licence et droit de redistribution ;
- définition exacte des cibles ;
- zone, culture et période définitives ;
- capacité de validation temporelle ;
- disponibilité des ressources de calcul ;
- présence ou absence d’un expert agronome.
