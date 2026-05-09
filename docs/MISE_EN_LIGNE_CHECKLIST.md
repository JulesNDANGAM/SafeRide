# SafeRide — Checklist finale de mise en ligne

## 1. État du projet

- Frontend React/Vite prêt pour build statique LWS.
- Backend FastAPI prêt pour Render.com.
- Build frontend généré dans `frontend/dist/`.
- `.htaccess` inclus dans `frontend/dist/` pour HTTPS et routing SPA.
- API locale vérifiée via `/health`.

## 2. Backend Render.com

Créer un service Render **Web Service** depuis GitHub.

### Option recommandée : configuration manuelle

| Champ | Valeur |
|---|---|
| Name | `saferide-api` |
| Runtime | `Python 3` |
| Region | `Frankfurt` |
| Branch | `main` |
| Root Directory | laisser vide |
| Build Command | `pip install -r backend/requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT --app-dir backend` |
| Instance Type | `Free` |

### Variables d'environnement Render

| Key | Value |
|---|---|
| `SAFERIDE_ALLOWED_ORIGINS` | `https://saferide.futureafri.com,http://localhost:5173,http://127.0.0.1:5173` |
| `SAFERIDE_ADMIN_TOKEN` | choisir un token secret fort |
| `SAFERIDE_APP_NAME` | `SafeRide API` |
| `SAFERIDE_USE_REAL_NAC` | `off` |
| `PYTHON_VERSION` | `3.12` |

Remplacer `https://saferide.futureafri.com` par le vrai sous-domaine LWS.

## 3. Frontend LWS

Le dossier à uploader sur LWS est :

```txt
frontend/dist/
```

Uploader **le contenu** de `frontend/dist/`, pas le dossier lui-même.

Fichiers attendus :

- `index.html`
- `.htaccess`
- `_redirects`
- `favicon.svg`
- `assets/`

## 4. Accès après mise en ligne

| Page | URL |
|---|---|
| Application passager | `https://saferide.futureafri.com` |
| Admin | `https://saferide.futureafri.com/#admin` |
| API Swagger | `https://saferide-api.onrender.com/docs` |
| Health API | `https://saferide-api.onrender.com/health` |

## 5. Vérifications finales

- Ouvrir `https://saferide-api.onrender.com/health` : doit retourner `status: ok`.
- Ouvrir le frontend LWS : la page passager doit s'afficher.
- Commander une course test.
- Ouvrir `/#admin` et entrer le token admin Render.
- Si erreur CORS : vérifier `SAFERIDE_ALLOWED_ORIGINS` sur Render.
- Si page blanche LWS : vérifier que `.htaccess` et `assets/` sont bien à la racine du sous-domaine.

## 6. Important pour la démo

Render Free peut s'endormir après inactivité. Avant la démo, ouvrir :

```txt
https://saferide-api.onrender.com/health
```

Attendre 30 à 60 secondes si le service se réveille.
