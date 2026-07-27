# Contribuer à AgriPredict AI

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
make install
```

## Branche et commits

- créer une branche courte depuis `main` ;
- utiliser des commits atomiques ;
- ne jamais commiter de secret ou de données sans licence validée ;
- ouvrir une pull request avec justification scientifique et technique.

## Vérifications obligatoires

```bash
make lint
make test
```

Pour une modification de modèle ou de données :

```bash
make reproduce
```

## Règles scientifiques

Toute modification affectant un résultat doit préciser :

- dataset et hash ;
- variables utilisées ;
- date de disponibilité des variables ;
- split ;
- seed ;
- métriques globales et segmentées ;
- impact sur les fuites potentielles ;
- impact sur la cible dérivée ;
- coût de calcul.

Le jeu de test final ne doit pas guider la sélection du modèle ou le tuning.

## Revue de code

La revue vérifie :

- lisibilité et typage ;
- tests ;
- absence de fuite ;
- reproductibilité ;
- gestion des erreurs ;
- sécurité ;
- documentation ;
- cohérence entre code, rapport et interface.
