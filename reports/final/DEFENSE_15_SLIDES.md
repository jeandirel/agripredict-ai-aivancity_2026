# Soutenance — plan de 15 diapositives

## 1. Titre
AgriPredict AI — Prédiction multimodale de la date de récolte du blé, Clinique IA aivancity 2026, Jean Direl NZE.

## 2. Problème métier
Anticiper la récolte pour organiser machines, équipes, collecte et stockage.

## 3. Question scientifique
Fusion sol + Sentinel-1 + Sentinel-2 + météo et compromis 31 mai / 15 juin.

## 4. Données
Centre-Val de Loire, parcelle × année, cible dérivée, 13 jeux Kaggle documentés.

## 5. Architecture des données
Bronze → Silver → Gold → modèles → API → interface.

## 6. Risque scientifique majeur
Fuite temporelle et circularité de `harvest_doy_derived` ; variables sensibles exclues.

## 7. Protocole final
Développement sur les années anciennes, calibration sur l’avant-dernière année, test sur 2024 et GroupKFold par `ID_PARCEL`.

## 8. Modèles
Dummy, Ridge, Random Forest, Extra Trees, HistGradientBoosting et MLP compact.

## 9. Résultat au 31 mai
MAE 8,49 jours, RMSE 10,36 et R² 0,105.

## 10. Résultat au 15 juin
MAE 8,29 jours, RMSE 10,21 et R² 0,130.

## 11. Comparaison appariée
Présenter le delta bootstrap, l’intervalle à 95 % et le compromis anticipation–précision. Le gain du 15 juin reste statistiquement non concluant car l’intervalle recouvre zéro.

## 12. Ablations et explicabilité
Montrer la contribution des modalités et les variables principales, sans causalité revendiquée.

## 13. Incertitude et robustesse
Intervalles conformes, données manquantes, bruit, modalité absente et diagnostic hors domaine.

## 14. Produit et MLOps
FastAPI, Streamlit, Docker, tests, CI, artefacts versionnés et documentation.

## 15. Limites et perspectives
Cible dérivée, région unique, validation terrain et extension à d’autres régions ou cultures.

## Répartition suggérée des 40 minutes

- Slides 1 à 3 : 6 min
- Slides 4 à 7 : 11 min
- Slides 8 à 12 : 15 min
- Slides 13 à 15 et démonstration : 8 min
- Questions : 10 min
