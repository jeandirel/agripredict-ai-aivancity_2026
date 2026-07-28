# Checklist de reproductibilité

- [x] Données finales présentes dans `data/`.
- [x] Manifeste des sources Kaggle.
- [x] Audit automatisé.
- [x] Seeds fixées.
- [x] Test chronologique séparé.
- [x] Sélection du modèle sans test.
- [x] GroupKFold par identifiant physique stable `ID_PARCEL`.
- [x] Intervalles conformes.
- [x] Ablations.
- [x] Robustesse.
- [x] Diagnostic hors domaine.
- [x] API et interface.
- [x] Tests et CI.
- [x] Docker.
- [x] Data Card et Model Cards.
- [x] Rapport et plan de soutenance.

## Commande unique

```bash
make final
```

## Services

```bash
docker compose up --build
```
