# AgriPredict AI — Guide de déploiement

## 1. Préparation

```bash
python -m venv .venv
# macOS / Linux : source .venv/bin/activate
# PowerShell    : & .\.venv\Scripts\Activate.ps1
make install
make final
```

`make final` entraîne les modèles, produit les intervalles, les analyses et tous les rapports finaux.

## 2. Lancement local

`make install` installe les dépendances Python et frontend. Lancer ensuite deux
terminaux depuis la racine du dépôt.

Terminal 1 — API :

```bash
make api
```

Terminal 2 — application React :

```bash
make dashboard
```

Services :

- API : `http://localhost:8000`
- OpenAPI : `http://localhost:8000/docs`
- Dashboard : `http://localhost:8501`

L’ancien dashboard Streamlit reste disponible pour la période de transition :

```bash
make dashboard-legacy
```

## 3. Docker Compose

Les modèles doivent d’abord exister dans `artifacts/models`. Compose construit
deux images indépendantes : FastAPI avec Python, puis la SPA avec Node et Nginx.
Nginx sert l’interface sur le port 8501 et relaie `/api/*` vers le service API.

```bash
make final
make docker-up
```

Arrêt :

```bash
make docker-down
```

## 4. Variables d’environnement

| Variable | Usage | Valeur par défaut |
|---|---|---|
| `AGRIPREDICT_MODEL_DIR` | Répertoire des modèles | `artifacts/models` |
| `AGRIPREDICT_CORS_ORIGINS` | Origines autorisées, séparées par des virgules, pour un frontend déployé séparément | aucune |
| `KAGGLE_USERNAME` | API Kaggle | aucune |
| `KAGGLE_KEY` | API Kaggle | aucune |

Ne jamais commiter les secrets Kaggle.

## 5. Contrôles avant livraison

```bash
make audit
make final
make quality
docker build -t agripredict-ai:1.0.0 .
docker build -t agripredict-observatory:1.0.0 frontend
```

`make quality` exécute Ruff, pytest, les tests frontend, le lint TypeScript et
le build de production. Les contrôles frontend peuvent aussi être lancés
séparément avec `make frontend-test`, `make frontend-lint` et
`make frontend-build`.

Vérifier ensuite :

```bash
curl http://localhost:8000/health
curl http://localhost:8000/readiness
curl http://localhost:8000/model-info
```

## 6. Déploiement cloud recommandé

### Azure

- Azure Container Registry ;
- Azure Container Apps ou AKS ;
- Azure Blob Storage pour les modèles ;
- Application Insights et Log Analytics ;
- Key Vault pour les secrets ;
- Front Door ou Application Gateway pour TLS et répartition de charge.

### AWS

- Amazon ECR ;
- ECS Fargate ou EKS ;
- S3 versionné pour les modèles ;
- CloudWatch ;
- Secrets Manager ;
- Application Load Balancer.

Le choix Azure ou AWS ne change pas le protocole scientifique. Les données et modèles doivent rester versionnés et les logs ne doivent pas exposer de géométries ou d’identifiants sensibles.

## 7. Monitoring de production à prévoir

- disponibilité et latence ;
- taux d’erreurs ;
- taux de variables manquantes ;
- distribution des entrées ;
- taux d’observations hors domaine ;
- largeur moyenne des intervalles ;
- dérive des variables ;
- erreur réelle lorsque la date de récolte devient disponible ;
- version du modèle utilisée pour chaque prédiction.

## 8. Retour arrière

Chaque modèle doit être stocké avec :

- version ;
- date de génération ;
- hash des données ;
- commit Git ;
- métriques ;
- liste des features ;
- Model Card.

Un rollback consiste à redéployer le dernier artefact validé et à vérifier `/readiness` avant de rétablir le trafic.
