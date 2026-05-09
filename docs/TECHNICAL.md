# SafeRide — Documentation technique

## 1. Stack

| Couche             | Technologie                              | Source / version            |
| ------------------ | ---------------------------------------- | --------------------------- |
| Frontend (web)     | React 18 + Vite + react-leaflet          | npm                         |
| i18n               | Solution maison (FR / EN) via context    | `src/i18n/`                 |
| Cartographie       | OpenStreetMap + Leaflet                  | https://leafletjs.com/      |
| Backend API        | FastAPI (Python 3.12) + Uvicorn          | https://fastapi.tiangolo.com |
| Validation données | Pydantic v2                              | https://docs.pydantic.dev   |
| Stockage MVP       | In-memory (à remplacer par PostgreSQL + Redis en Phase 1) |   |
| Paiement           | Chariow (iframe + webhook)               | https://chariow.com         |
| Réseau / KYC       | Nokia Network-as-Code (CAMARA APIs)      | https://networkascode.nokia.io |
| Auth admin         | Bearer token (.env) — JWT recommandé en prod              |       |

## 2. Arborescence

```
saferide/
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── main.py              # routes publiques + mount admin
│       ├── config.py            # settings (env)
│       ├── auth.py              # bearer admin
│       ├── admin.py             # router admin (CRUD chauffeurs, courses, abonnements, stats)
│       ├── subscriptions.py     # logique Chariow + plans
│       ├── schemas.py           # Pydantic models
│       ├── store.py             # seeds + dictionnaires en mémoire
│       └── services/
│           ├── camara.py        # mock NaC + références CAMARA
│           ├── agent.py         # Trust Agent (orchestration AI)
│           └── scoring.py       # calcul du Network Trust Score
├── frontend/
│   ├── package.json
│   ├── index.html               # charge Leaflet CSS, fonts
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── api.js               # client REST
│       ├── styles.css           # design system
│       ├── i18n/                # FR / EN
│       └── components/
│           ├── TopBar.jsx
│           ├── MapView.jsx
│           ├── DriverCard.jsx
│           ├── PassengerView.jsx
│           ├── DriverView.jsx
│           ├── OpsView.jsx
│           ├── AboutView.jsx
│           ├── PremiumView.jsx  # Chariow checkout (iframe)
│           └── AdminView.jsx    # back-office
├── docs/                        # documentation (ce dossier)
├── README.md
└── SafeRide_Ideation*.pdf
```

## 3. Flux Network Trust Score

```
Passager demande une course
        │
        ▼
Backend identifie les chauffeurs dans la ville cible
        │
        ▼
TrustAgent.orchestrate(driver) ─► appelle 4 APIs CAMARA en parallèle :
        SIM Swap (35%) + Localisation (25%) + Appareil (20%) + Numéro (20%)
        + 3 APIs supplémentaires : QoD, Congestion Insights, Geofencing
        │
        ▼
TrustScoringService.evaluate ─► SCR = pondération + statut + anomalies
        │
        ▼
Frontend affiche 3 buckets : Reliable / Attention / Blocked
        │
        ▼
Passager choisit un chauffeur fiable ─► /rides/start ─► course active
        │
        ▼
Toutes les 60 s : monitoring (QoD + Congestion + Geofencing)
        │
        ▼
Anomalie ─► RideEvent (severity: warning|critical) + alerte passager
```

Implémentations clés :

- `backend/app/services/agent.py` : orchestration adaptée à la ville (heuristiques régionales, log explicable).
- `backend/app/services/scoring.py` : pondération `35/25/20/20`, calcul distance Haversine, ETA, tarif XAF.
- `backend/app/main.py` : `POST /rides/request`, `POST /rides/start`, `POST /rides/{id}/monitor`, `POST /rides/{id}/complete`.

## 4. Configuration (variables d'environnement)

Toutes les variables sont préfixées `SAFERIDE_`. Voir `backend/.env.example`.

| Variable                              | Défaut                                       | Description                                              |
| ------------------------------------- | -------------------------------------------- | -------------------------------------------------------- |
| `SAFERIDE_APP_NAME`                   | `SafeRide API`                               | Nom affiché                                              |
| `SAFERIDE_ALLOWED_ORIGINS`            | `http://localhost:5173,http://127.0.0.1:5173` | CORS                                                     |
| `SAFERIDE_FARE_PER_KM_XAF`            | `350`                                        | Tarif au km                                              |
| `SAFERIDE_BASE_FARE_XAF`              | `500`                                        | Forfait de prise en charge                               |
| `SAFERIDE_COMMISSION_RATE`            | `0.08`                                       | Commission SafeRide                                      |
| `SAFERIDE_PREMIUM_XAF`                | `5000`                                       | Prix abonnement Premium chauffeur                        |
| `SAFERIDE_ADMIN_TOKEN`                | `saferide-admin-dev`                         | Token bearer pour l'admin                                |
| `SAFERIDE_CHARIOW_CHECKOUT_URL`       | URL placeholder                              | URL produit Chariow (cf. dashboard Chariow)              |
| `SAFERIDE_USE_REAL_NAC`               | `false`                                      | Active le SDK Nokia NaC réel à la place du mock          |
| `SAFERIDE_NOKIA_NAC_API_KEY`          | (vide)                                       | Clé Nokia NaC                                            |

## 5. Authentification

- **Public (passager)** : pas d’auth nécessaire pour le MVP. En production : JWT signé côté backend après vérification Number Verification (CAMARA).
- **Chauffeur** : prochainement, magic link + Number Verification.
- **Admin** : `Authorization: Bearer <SAFERIDE_ADMIN_TOKEN>`. À remplacer par un IdP (Auth0/Keycloak) + rôles (`admin`, `ops`, `support`).

## 6. Endpoints API

### Public

| Méthode | Route                                | Description                                  |
| ------- | ------------------------------------ | -------------------------------------------- |
| GET     | `/health`                            | Healthcheck                                  |
| GET     | `/cities`                            | Villes supportées (5 villes seedées)         |
| GET     | `/drivers?city=Douala`               | Snapshots Trust Score d'une ville            |
| POST    | `/rides/request`                     | Buckets reliable / attention / blocked       |
| POST    | `/rides/start`                       | Démarre une course (refuse si Blocked)       |
| GET     | `/rides/{id}`                        | État d’une course                            |
| POST    | `/rides/{id}/monitor`                | Cycle de monitoring (simulé)                 |
| POST    | `/rides/{id}/complete`               | Termine la course                            |
| GET     | `/subscriptions/plans`               | Liste des plans                              |
| POST    | `/subscriptions`                     | Crée un abonnement (renvoie URL Chariow)     |
| GET     | `/subscriptions/{id}`                | État d’un abonnement                         |
| POST    | `/subscriptions/webhook/chariow`     | Webhook Chariow (active l'abonnement)        |

### Admin (Bearer obligatoire)

| Méthode | Route                                       |
| ------- | ------------------------------------------- |
| GET     | `/admin/login`                              |
| GET     | `/admin/stats`                              |
| GET     | `/admin/drivers`                            |
| POST    | `/admin/drivers`                            |
| PUT     | `/admin/drivers/{id}`                       |
| DELETE  | `/admin/drivers/{id}`                       |
| GET     | `/admin/rides`                              |
| GET     | `/admin/subscriptions`                      |
| POST    | `/admin/subscriptions/{id}/cancel`          |

Documentation OpenAPI auto : `http://127.0.0.1:8000/docs`.

## 7. Sécurité

- **Pas de secret en clair** : utiliser un gestionnaire (`.env` local, AWS Secrets Manager / Vault en prod).
- **CORS** : whitelist explicite via `SAFERIDE_ALLOWED_ORIGINS`.
- **Webhook Chariow** : vérifier la signature HMAC (TODO ; champ `X-Chariow-Signature` à valider — fonction `handle_chariow_webhook` est le point d’extension).
- **Admin** : ne jamais exposer le token dans le bundle frontend ; il est saisi à la connexion et stocké en `localStorage` côté navigateur (à remplacer par un cookie HttpOnly + JWT en prod).

## 8. Roadmap technique (extrait du PDF section 5)

| Cible                                 | Phase | Action                                                            |
| ------------------------------------- | ----- | ----------------------------------------------------------------- |
| Stockage durable                      | 1     | PostgreSQL (profils chauffeurs, courses, abonnements)              |
| Sessions temps réel                   | 1     | Redis + WebSocket (suivi course)                                   |
| Notifications passager                | 1     | Firebase Cloud Messaging                                           |
| SDK Nokia NaC                         | 1     | Activer `SAFERIDE_USE_REAL_NAC=true` + clé API                     |
| Auth chauffeur Number Verification    | 1     | KYC réseau natif via API CAMARA                                    |
| Application mobile                    | 2     | React Native (passager + chauffeur)                                |
| AI agent LLM réel                     | 2     | Llama 3 ou Mistral via Ollama, RAG sur historique fraude           |
| Observabilité                         | 1     | OpenTelemetry + Grafana / Loki                                     |

## 9. Tests

- Tests manuels : `python -m compileall backend/app` (compilation), endpoints testés via PowerShell `Invoke-WebRequest` (cf. README).
- Pour l'avenir : `pytest` + `httpx.AsyncClient` ; tests E2E `playwright` sur le frontend.

## 10. Déploiement (suggestion)

| Composant   | Plateforme                          |
| ----------- | ----------------------------------- |
| Backend     | Render / Fly.io / Railway (Docker)  |
| Frontend    | Vercel / Netlify (Vite static)      |
| PostgreSQL  | Neon / Supabase                     |
| Redis       | Upstash                             |
| Webhook URL | https://api.saferide.app/subscriptions/webhook/chariow |
