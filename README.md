# SafeRide — Network Trust Score MVP

> Every ride, checked. Every journey, safe. — *Chaque course, vérifiée. Chaque trajet, sécurisé.*

Prototype hackathon basé sur le document `SafeRide_Ideation - Anglais.pdf`. SafeRide orchestre **5 APIs CAMARA** via **Nokia Network-as-Code (simulé)** pour calculer en temps réel un **Network Trust Score** avant et pendant chaque course, puis vérifier automatiquement après la course que le trajet s'est bien déroulé — en alertant la flotte ou la personne de confiance du passager si anomalie détectée par l'IA.

## Fonctionnalités / Features

- **Backend FastAPI** avec moteur de score (`SIM Swap × 35% + Localisation × 25% + Appareil × 20% + Numéro × 20%`)
- **5 APIs CAMARA simulées** : `SIM Swap`, `Location Verification`, `Device Status`, `Number Verification`, `Quality on Demand` + `Congestion Insights` + `Geofencing`
- **Agent IA** (orchestration intelligente, ordre adapté à la ville/heuristique régionale, scoring adaptatif, détection d'anomalies post-course, log explicable)
- **Vérification post-course** : l'IA vérifie la cohérence du trajet, alerte automatiquement la flotte ou la personne de confiance du passager si anomalie
- **Frontend React + Vite** moderne (glassmorphism, gradients, animations)
- **Bilingue FR / EN** avec sélecteur global
- **Carte Leaflet + OpenStreetMap** (conforme aux specs du PDF)
- **Vues** : Passager, Chauffeur, Opérations, Premium, Admin, Concept
- **Cartes des chauffeurs** triés par bucket (`Reliable` / `Attention` / `Blocked`)
- **Monitoring temps réel** : simulation des alertes (déviation, chute réseau, mismatch GPS, congestion)
- **5 villes** : Douala, Yaoundé, Lagos, Nairobi, Dakar (avec opérateur partenaire)
- **Fares en XAF**, commission `8%`
- **Abonnement Premium** chauffeur `5 000 FCFA/mois` via **Chariow** (iframe + webhook)
- **Back-office admin** complet (auth Bearer, CRUD chauffeurs, courses, abonnements, KPIs / MRR)

## Lancer le projet

### 1. Backend

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
uvicorn app.main:app --reload --app-dir backend
```

API : http://127.0.0.1:8000 — Docs auto : http://127.0.0.1:8000/docs

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Interface : http://127.0.0.1:5173

## Endpoints clés

| Méthode | Route                       | Description                                  |
| ------- | --------------------------- | -------------------------------------------- |
| GET     | `/health`                   | Healthcheck                                  |
| GET     | `/cities`                   | Villes supportées                            |
| GET     | `/drivers?city=Douala`      | Évalue tous les chauffeurs d'une ville       |
| POST    | `/rides/request`            | Buckets `reliable / attention / blocked`     |
| POST    | `/rides/start`              | Démarre une course (refuse si `blocked`)     |
| POST    | `/rides/{id}/monitor`       | Simule un cycle de monitoring                |
| POST    | `/rides/{id}/complete`      | Termine la course                            |

## Architecture (alignée sur le PDF, section 5)

| Layer       | Implementation                                       |
| ----------- | ---------------------------------------------------- |
| Frontend    | React 18 + Vite + Leaflet + i18n FR/EN               |
| Backend     | FastAPI (Python)                                     |
| AI Agent    | Orchestrateur Python (stub LLM, log explicable)      |
| Nokia NaC   | Mock local conforme aux signatures CAMARA            |
| DB          | In-memory (à brancher PostgreSQL + Redis en Phase 1) |
| Mapping     | OpenStreetMap + Leaflet (open-source)                |

## Documentation complète

| Document                                          | Pour qui                          |
| ------------------------------------------------- | --------------------------------- |
| [`docs/README.md`](docs/README.md)                | Index global                      |
| [`docs/BUSINESS.md`](docs/BUSINESS.md)            | Investisseurs / partenaires       |
| [`docs/TECHNICAL.md`](docs/TECHNICAL.md)          | Développeurs / architectes        |
| [`docs/API_REFERENCES.md`](docs/API_REFERENCES.md) | Sources officielles CAMARA, Nokia NaC, Chariow |
| [`docs/ADMIN.md`](docs/ADMIN.md)                  | Équipe Ops SafeRide               |
| [`docs/FAQ.md`](docs/FAQ.md)                      | 60+ questions/réponses            |
| [`docs/PITCH.md`](docs/PITCH.md)                  | Pitch hackathon en 5 minutes      |

## Roadmap suivante

- Brancher le **vrai SDK Nokia Network-as-Code** (`networkascode.nokia.io`)
- Persister les profils chauffeurs dans **PostgreSQL**
- Sessions de course en **Redis** + WebSockets temps réel
- **Firebase Cloud Messaging** pour notifications passager
- Auth séparée Passager / Chauffeur
- Conversion en app mobile React Native
