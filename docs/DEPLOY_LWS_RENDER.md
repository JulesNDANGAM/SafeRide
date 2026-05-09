# SafeRide — Déploiement LWS (Frontend) + Render.com (Backend)

## Architecture

```
┌─────────────────────────────────────────────┐
│  FRONTEND (React statique)                   │
│  saferide.futureafri.com  (LWS mutualisé)    │
│  • Fichiers HTML/CSS/JS statiques            │
│  • .htaccess pour SPA routing                │
│  • Hébergement existant, pas de coût extra   │
└──────────────────┬──────────────────────────┘
                   │ API calls (HTTPS)
                   ▼
┌─────────────────────────────────────────────┐
│  BACKEND (FastAPI Python)                    │
│  saferide-api.onrender.com  (Render Free)    │
│  • 750h/mois gratuit                         │
│  • S'endort après 15 min inactivité          │
│  • ~30 sec pour se réveiller                 │
└─────────────────────────────────────────────┘
```

---

## ÉTAPE 1 — Déployer le Backend sur Render.com

### 1.1 Prérequis : Créer un repo GitHub

```bash
cd c:\Users\JulesNDANGA\Videos\saferide
git init
git add .
git commit -m "SafeRide MVP - Africa Ignite Hackathon"
```

Créer un repo sur https://github.com/new (ex: `julesndanga/saferide`)

```bash
git remote add origin https://github.com/julesndanga/saferide.git
git branch -M main
git push -u origin main
```

### 1.2 Créer le service backend sur Render

1. Aller sur https://dashboard.render.com → **Sign Up** (avec GitHub)
2. Cliquer **"New +"** → **"Web Service"**
3. Connecter le repo `saferide`
4. Remplir :

| Champ | Valeur |
|-------|--------|
| **Name** | `saferide-api` |
| **Region** | Frankfurt (le plus proche de l'Afrique) |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | Free |

5. Ajouter les variables d'environnement (onglet **Environment**) :

| Key | Value |
|-----|-------|
| `SAFERIDE_ALLOWED_ORIGINS` | `https://saferide.futureafri.com,http://localhost:5173` |
| `SAFERIDE_APP_NAME` | `SafeRide API` |

> ⚠️ Remplace `saferide.futureafri.com` par ton vrai sous-domaine LWS

6. Cliquer **"Create Web Service"** → Render build et déploie (2-3 min)

7. **URL obtenue** : `https://saferide-api.onrender.com`

8. Vérifier : ouvrir `https://saferide-api.onrender.com/docs` → Swagger doit s'afficher

---

## ÉTAPE 2 — Build le Frontend en local

### 2.1 Installer Node.js (si pas encore fait)

Télécharger : https://nodejs.org/ → version LTS → installer

Redémarrer le terminal après installation.

### 2.2 Configurer l'URL du backend

Créer le fichier `frontend/.env.production` :

```
VITE_API_BASE_URL=https://saferide-api.onrender.com
```

> ⚠️ Utilise l'URL Render obtenue à l'étape 1.2

### 2.3 Build

```bash
cd c:\Users\JulesNDANGA\Videos\saferide\frontend
npm install
npm run build
```

Résultat : dossier `frontend/dist/` contient les fichiers statiques (HTML, CSS, JS).

### 2.4 Ajouter le fichier .htaccess pour le SPA

Créer le fichier `frontend/dist/.htaccess` :

```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /index.html [L]
</IfModule>

# Cache statique (performance)
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType text/css "access plus 1 year"
  ExpiresByType application/javascript "access plus 1 year"
  ExpiresByType image/png "access plus 1 year"
  ExpiresByType image/svg+xml "access plus 1 year"
</IfModule>

# Compression gzip
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json image/svg+xml
</IfModule>

# Sécurité headers
<IfModule mod_headers.c>
  Header set X-Content-Type-Options "nosniff"
  Header set X-Frame-Options "SAMEORIGIN"
  Header set X-XSS-Protection "1; mode=block"
</IfModule>
```

---

## ÉTAPE 3 — Déployer le Frontend sur LWS

### 3.1 Créer le sous-domaine sur LWS

1. Se connecter à https://panel.lws.fr
2. Aller dans **Hébergement** → **Domaines** → **Sous-domaines**
3. Créer un sous-domaine : `saferide.futureafri.com`
4. Pointage : vers le dossier `/www/saferide/`
5. Attendre la propagation DNS (5-30 min)

### 3.2 Uploader les fichiers via FTP

**Option A : FTP avec FileZilla**

1. Télécharger FileZilla : https://filezilla-project.org/
2. Se connecter au FTP LWS :
   - Hôte : `ftp.futureafri.com`
   - Utilisateur : ton identifiant LWS
   - Mot de passe : ton mot de passe LWS
   - Port : 21
3. Naviguer vers `/www/saferide/` (ou le dossier du sous-domaine)
4. Uploader **tout le contenu** du dossier `frontend/dist/`
   - ✅ `index.html`
   - ✅ Dossier `assets/` (CSS, JS)
   - ✅ `.htaccess`
   - ✅ `_redirects`

**Option B : Gestionnaire de fichiers LWS**

1. Dans le panel LWS → **Gestionnaire de fichiers**
2. Naviguer vers `/www/saferide/`
3. Uploader les fichiers un par un (plus lent)

### 3.3 Vérifier

Ouvrir `https://saferide.futureafri.com` → l'app SafeRide doit s'afficher.

---

## ÉTAPE 4 — Mettre à jour les CORS du backend

Une fois le frontend en ligne sur LWS, mettre à jour Render :

1. Aller sur https://dashboard.render.com
2. Service `saferide-api` → **Environment**
3. Mettre à jour `SAFERIDE_ALLOWED_ORIGINS` :
   ```
   https://saferide.futureafri.com,http://localhost:5173
   ```
4. Render redémarre le backend automatiquement

---

## ÉTAPE 5 — Forcer HTTPS sur LWS

### 5.1 Activer le SSL

1. Panel LWS → **Hébergement** → **SSL**
2. Activer Let's Encrypt pour `saferide.futureafri.com`
3. Attendre la génération du certificat (5-10 min)

### 5.2 Forcer HTTPS via .htaccess

Ajouter en haut du `.htaccess` :

```apache
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
```

---

## URLs de démo pour la soumission Hackathon

| Service | URL |
|---------|-----|
| **Frontend (démo live)** | `https://saferide.futureafri.com` |
| **Backend API (Swagger)** | `https://saferide-api.onrender.com/docs` |
| **Backend Health** | `https://saferide-api.onrender.com/health` |
| **Backend Cost Combinations** | `https://saferide-api.onrender.com/trust-matrix/cost-combinations` |

---

## Checklist finale avant soumission

- [ ] Repo GitHub créé et poussé
- [ ] Backend déployé sur Render → `/docs` fonctionne
- [ ] Frontend build avec `.env.production` (URL Render)
- [ ] `.htaccess` créé dans `dist/`
- [ ] Sous-domaine LWS créé
- [ ] Fichiers uploadés sur LWS via FTP
- [ ] HTTPS activé sur LWS
- [ ] CORS mis à jour sur Render avec l'URL LWS
- [ ] Frontend accessible en ligne → carte Douala visible
- [ ] Screenshots pris pour le Pitch Deck PPT
- [ ] Pitch Deck PPT créé

---

## Dépannage

### Le frontend affiche une page blanche

- Vérifier que `index.html` est à la racine du dossier LWS
- Vérifier le `.htaccess` (SPA routing)
- Ouvrir la console navigateur (F12) → regarder les erreurs

### Les appels API échouent (CORS)

- Vérifier `SAFERIDE_ALLOWED_ORIGINS` sur Render
- L'URL LWS doit être exacte (avec https://)
- Attendre le redémarrage de Render après modification

### Le backend est lent au premier appel

- Normal : Render free tier s'endort après 15 min d'inactivité
- Premier appel = ~30 sec de réveil
- **Astuce** : ouvrir `https://saferide-api.onrender.com/health` 1 min avant la démo

### Les assets CSS/JS ne chargent pas

- Vérifier que le dossier `assets/` est bien uploadé
- Vérifier que `vite.config.js` a `base: '/'`
- Rebuild le frontend : `npm run build`
