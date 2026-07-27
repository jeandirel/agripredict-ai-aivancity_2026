# AgriPredict AI — Éthique, gouvernance et conformité

## 1. Positionnement

AgriPredict AI est un **outil d’aide à la planification**. Il ne doit pas prendre de décision autonome de récolte et ne remplace ni l’observation terrain, ni l’expertise agronomique, ni la responsabilité de l’exploitant.

## 2. Gouvernance des données

Pour chaque dataset :

- origine et URL documentées ;
- version et date d’acquisition enregistrées ;
- hash SHA-256 ;
- licence et restrictions de redistribution ;
- transformations traçables ;
- responsable de validation ;
- couche Bronze, Silver ou Gold ;
- schéma et unités ;
- taux de valeurs manquantes ;
- période de disponibilité.

Les identifiants et géométries parcellaires ne doivent pas être exposés publiquement au-delà de ce que leurs licences autorisent.

## 3. Nature de la cible

La cible `harvest_doy_derived` est **dérivée**. Elle ne doit jamais être présentée comme une vérité terrain parcellaire directement mesurée si ce n’est pas démontré.

Mesures obligatoires :

- documenter la méthode de dérivation ;
- identifier les variables utilisées pour construire la cible ;
- empêcher leur réutilisation circulaire comme entrées ;
- vérifier qu’aucune donnée postérieure à l’horizon n’est utilisée ;
- comparer la cible à une référence régionale lorsque possible ;
- conserver une analyse de sensibilité avec et sans variables à risque.

## 4. Biais et domaine de validité

Le modèle est limité à :

- la culture du blé ;
- la région Centre-Val de Loire ;
- les années et conditions représentées dans les données ;
- les variables disponibles aux horizons du 31 mai et du 15 juin.

Une performance moyenne ne garantit pas une performance équivalente pour :

- toutes les tailles de parcelles ;
- les dates de récolte très précoces ou tardives ;
- une année climatique exceptionnelle ;
- une autre région ;
- une autre culture.

Les métriques segmentées et le diagnostic hors domaine doivent être consultés avant tout élargissement.

## 5. Transparence utilisateur

Chaque prédiction doit afficher :

- le modèle et l’horizon ;
- la date prédite et le DOY ;
- un intervalle d’incertitude ;
- le domaine de validité ;
- le caractère dérivé de la cible ;
- un avertissement en cas de données incomplètes ou hors période ;
- l’obligation de supervision humaine.

## 6. Explicabilité

Les importances par permutation et les ablations sont des outils d’explication prédictive. Elles ne prouvent pas qu’une variable cause directement une date de récolte plus précoce ou plus tardive.

Les explications doivent être :

- accompagnées de leur méthode ;
- comparées entre folds ou années ;
- présentées avec prudence ;
- validées par un expert avant toute interprétation agronomique forte.

## 7. Protection des données

Le projet ne nécessite pas de données personnelles pour fonctionner. Les risques principaux portent plutôt sur :

- la précision géographique des parcelles ;
- l’identification d’exploitations par recoupement ;
- les secrets d’accès aux plateformes ;
- les journaux d’inférence pouvant contenir des identifiants.

Mesures :

- ne pas journaliser d’identifiant parcellaire inutile ;
- séparer secrets et code ;
- chiffrer les échanges ;
- limiter les droits d’accès ;
- définir une politique de conservation ;
- purger les données non nécessaires.

## 8. RGPD

Le RGPD s’applique seulement si les données peuvent être reliées à une personne physique identifiable. Avant un déploiement réel :

- réaliser une analyse de qualification des données ;
- identifier la base légale ;
- appliquer minimisation, limitation de finalité et durée de conservation ;
- documenter les droits des personnes si des données personnelles apparaissent ;
- réaliser une AIPD si le traitement présente un risque élevé.

Le prototype ne revendique pas une conformité RGPD complète sans cette analyse contextuelle.

## 9. Règlement européen sur l’IA

La classification réglementaire dépend du contexte d’usage réel. Le prototype académique ne doit pas être présenté comme certifié ou automatiquement conforme.

Mesures de gouvernance déjà intégrées :

- documentation des données ;
- traçabilité des expériences ;
- supervision humaine ;
- transparence des limites ;
- mesure de robustesse ;
- contrôle des fuites ;
- gestion des versions ;
- journalisation de la version du modèle ;
- possibilité de rollback.

Une analyse juridique spécifique reste nécessaire avant commercialisation.

## 10. Sécurité

- secrets Kaggle dans GitHub Secrets ou un coffre-fort ;
- scan de dépendances ;
- image conteneur minimale ;
- validation stricte des entrées ;
- endpoints de health/readiness ;
- modèle chargé depuis un répertoire contrôlé ;
- limitation des logs ;
- mises à jour de sécurité régulières ;
- contrôle d’accès et TLS en production.

## 11. Responsabilités

| Acteur | Responsabilité |
|---|---|
| Responsable du projet | qualité scientifique, documentation et limites |
| Encadrement aivancity | validation pédagogique et méthodologique |
| Expert agronome | validation métier et interprétation |
| Exploitant du service | sécurité, disponibilité et conformité |
| Utilisateur final | décision finale et prise en compte du terrain |

## 12. Conditions minimales avant production

- validation de la cible par une source terrain ou indépendante ;
- test externe sur une nouvelle campagne ;
- validation agronomique ;
- audit des licences ;
- analyse RGPD et AI Act selon l’usage ;
- monitoring ;
- procédure d’incident ;
- seuils de rejet hors domaine ;
- documentation utilisateur ;
- validation de la disponibilité et de la sécurité.
