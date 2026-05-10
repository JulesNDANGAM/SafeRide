# SafeRide — Network Trust Score MVP

> Every ride, checked. Every journey, safe.

SafeRide is a hackathon MVP designed to make urban mobility safer by verifying driver trust signals before, during, and after a ride. The platform combines network-based signals, contextual checks, and an AI-assisted orchestration layer to help passengers choose safer drivers and help operators detect suspicious situations in real time.

## Key Features

- **FastAPI backend** powered by SafeRide's proprietary trust engine
- **Simulated CAMARA network signals** through a Nokia Network-as-Code inspired integration layer
- **AI-assisted orchestration** for adaptive checks, anomaly detection, and explainable operational logs
- **Post-ride safety verification** to detect abnormal trip behavior and trigger alerts when needed
- **Modern React + Vite frontend** with a responsive, polished user interface
- **French / English support** with a global language selector
- **Leaflet + OpenStreetMap mapping**
- **Passenger, Driver, Premium, Admin, and Concept views**
- **Driver trust buckets**: `Reliable`, `Attention`, and `Blocked`
- **Real-time ride monitoring simulation** for route deviation, network drops, location mismatch, and congestion
- **Supported cities**: Douala, Yaoundé, Lagos, Nairobi, and Dakar
- **XAF fare simulation** with an `8%` platform commission
- **Driver Premium subscription** at `5,000 FCFA/month`
- **Admin back office** with Bearer authentication, driver management, ride tracking, subscriptions, KPIs, and MRR

## Tech Stack

| Layer | Implementation |
| --- | --- |
| Frontend | React 18, Vite, Leaflet, i18n |
| Backend | FastAPI, Python |
| AI Layer | Python orchestration service |
| Network APIs | Local CAMARA-style simulation |
| Database | In-memory MVP storage |
| Mapping | OpenStreetMap + Leaflet |

## Getting Started

### 1. Run the backend

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
uvicorn app.main:app --reload --app-dir backend
```

Backend URL:

```txt
http://127.0.0.1:8000
```

API documentation:

```txt
http://127.0.0.1:8000/docs
```

### 2. Run the frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend URL:

```txt
http://127.0.0.1:5173
```

## Environment Variables

### Backend

```txt
SAFERIDE_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
SAFERIDE_ADMIN_TOKEN=your-secret-admin-token
SAFERIDE_APP_NAME=SafeRide API
SAFERIDE_USE_REAL_NAC=off
PYTHON_VERSION=3.12
```

### Frontend

Create `frontend/.env.production` for production builds:

```txt
VITE_API_BASE_URL=https://your-backend-url.example.com
```

## Main API Endpoints

| Method | Route | Description |
| --- | --- | --- |
| GET | `/health` | Health check |
| GET | `/cities` | List supported cities |
| GET | `/drivers?city=Douala` | Evaluate available drivers in a city |
| POST | `/rides/request` | Request a ride and receive trusted driver buckets |
| POST | `/rides/start` | Start a ride if the selected driver is eligible |
| POST | `/rides/{id}/monitor` | Simulate one monitoring cycle |
| POST | `/rides/{id}/complete` | Complete a ride |

## Production Deployment

The current deployment target is:

- **Frontend**: static hosting on LWS
- **Backend**: FastAPI web service on Render

Production frontend URL:

```txt
https://saferide.futureafri.com
```

Production backend URL:

```txt
https://saferide-api-xult.onrender.com
```

## Roadmap

- Connect the real Nokia Network-as-Code SDK
- Persist drivers, rides, and subscriptions in PostgreSQL
- Add Redis-backed ride sessions and real-time WebSocket monitoring
- Add push notifications for passengers and trusted contacts
- Add separate passenger and driver authentication
- Package the product as a React Native mobile app
