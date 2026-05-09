# SafeRide — Où mettre les clés API ?

> Réponse courte : **toutes les clés se mettent dans `backend/.env`** (jamais dans le frontend, jamais commité dans Git).

## 1. Structure du fichier `.env`

Copier le modèle :

```powershell
Copy-Item backend/.env.example backend/.env
```

Puis éditer `backend/.env` :

```env
# ──────────────────────────────────────────────
# Nokia Network-as-Code (CAMARA APIs)
# ──────────────────────────────────────────────
SAFERIDE_USE_REAL_NAC=true
SAFERIDE_NOKIA_NAC_BASE_URL=https://network-as-code.p-eu.rapidapi.com
SAFERIDE_NOKIA_NAC_API_KEY=<colle ici la clé Nokia NaC>

# ──────────────────────────────────────────────
# Chariow (paiement)
# ──────────────────────────────────────────────
SAFERIDE_CHARIOW_CHECKOUT_URL=https://chariow.com/<vendeur>/<produit>
# Webhook secret (pour vérifier la signature HMAC en production)
SAFERIDE_CHARIOW_WEBHOOK_SECRET=<secret HMAC fourni par Chariow>

# ──────────────────────────────────────────────
# OpenRouter (LLM gratuit pour l'agent IA SafeRide)
# ──────────────────────────────────────────────
SAFERIDE_OPENROUTER_API_KEY=<clé OpenRouter `sk-or-v1-...`>
SAFERIDE_OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free
# Optionnel : SAFERIDE_OPENROUTER_BASE_URL, SAFERIDE_OPENROUTER_REFERER, SAFERIDE_OPENROUTER_APP_NAME

# ──────────────────────────────────────────────
# Admin
# ──────────────────────────────────────────────
SAFERIDE_ADMIN_TOKEN=<token long et aléatoire>
```

> ⚠️ Le fichier `.env` est exclu du dépôt Git (voir `.gitignore`). Ne jamais le commiter.

## 2. Comment obtenir les clés Nokia Network-as-Code

1. Créer un compte sur **https://networkascode.nokia.io/**
2. Aller dans le portail développeur → **My Apps**
3. Créer une nouvelle application SafeRide
4. Récupérer la **clé API** (token bearer) générée
5. Activer les APIs nécessaires : `SIM Swap`, `Number Verification`, `Location Verification`, `Device Swap`, `Quality on Demand`, `Congestion Insights`, `Geofencing`
6. (Optionnel) Activer le **mode sandbox** pour tester sans coût opérateur
7. Coller la clé dans `SAFERIDE_NOKIA_NAC_API_KEY`

## 3. Comment obtenir l'URL Chariow

1. Créer un compte vendeur sur **https://chariow.com**
2. Créer un produit *SafeRide Premium Driver — 5 000 FCFA / mois*
3. Activer dans le produit l'option « Accès direct au paiement »
4. Copier le **lien personnalisé** du produit
5. Le coller dans `SAFERIDE_CHARIOW_CHECKOUT_URL`
6. Configurer dans Chariow l'URL **webhook** :
   ```
   POST https://api.saferide.app/subscriptions/webhook/chariow
   ```
7. Récupérer le **secret HMAC** dans les paramètres webhook → `SAFERIDE_CHARIOW_WEBHOOK_SECRET`

## 4. Vérification que les clés sont chargées

Démarrer le backend puis :

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/health
```

Réponse attendue :

```json
{ "status": "ok", "service": "SafeRide API", "version": "1.0.0" }
```

Tester un appel CAMARA réel (avec `SAFERIDE_USE_REAL_NAC=true`) :

```powershell
Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:8000/drivers?city=Douala"
```

Si la clé est bonne, les snapshots renvoyés contiennent les vrais signaux NaC. Sinon, le backend log une erreur d'authentification 401 vers Nokia NaC.

## 5. Bascule mock ↔ réel

| `SAFERIDE_USE_REAL_NAC` | Comportement                                         |
| ----------------------- | ---------------------------------------------------- |
| `false` (par défaut)    | Utilise le mock local conforme aux signatures CAMARA |
| `true`                  | Forwarde les appels au SDK Nokia NaC officiel        |

Pour la **soumission hackathon** : laisser `false` (les juges peuvent tester sans clé). Pour le **pilote Douala** : passer à `true`.

## 6. Sécurité — règles d'or

1. **Ne jamais** mettre une clé dans le frontend (Vite expose `VITE_*` en clair dans le bundle).
2. **Ne jamais** commiter `.env`. Utiliser `.env.example` pour la doc.
3. En production, utiliser un **gestionnaire de secrets** (AWS Secrets Manager, HashiCorp Vault, Doppler, GCP Secret Manager).
4. Roter les clés tous les 90 jours (ou après chaque départ d'un membre de l'équipe).
5. Activer les **logs d'audit** côté Nokia NaC et Chariow.
6. Vérifier la **signature HMAC** des webhooks Chariow avant de faire confiance au payload.
7. Restreindre `SAFERIDE_ALLOWED_ORIGINS` au domaine de prod uniquement.

## 7. Récapitulatif des variables d'environnement

| Variable                              | Où l'obtenir                                                         |
| ------------------------------------- | -------------------------------------------------------------------- |
| `SAFERIDE_NOKIA_NAC_API_KEY`          | https://networkascode.nokia.io/ → My Apps → Create app               |
| `SAFERIDE_NOKIA_NAC_BASE_URL`         | Fourni par Nokia (`*.nokia.io` ou `network-as-code.p-eu.rapidapi.com`) |
| `SAFERIDE_USE_REAL_NAC`               | `true` pour activer les vrais appels                                 |
| `SAFERIDE_CHARIOW_CHECKOUT_URL`       | Dashboard Chariow → produit → lien personnalisé                      |
| `SAFERIDE_CHARIOW_WEBHOOK_SECRET`     | Dashboard Chariow → webhook settings                                 |
| `SAFERIDE_ADMIN_TOKEN`                | À générer (ex : `openssl rand -hex 32`)                              |

## 8. Pendant le hackathon (mode prototype)

Si tu n'as pas encore de clés, **aucun problème** : laisse `SAFERIDE_USE_REAL_NAC=false`, et le projet tourne avec le mock local (14 chauffeurs seedés, scores calculés en temps réel, monitoring simulé). Le **bouton « Simuler le paiement »** dans la vue Premium permet de débloquer l'abonnement sans Chariow réel pour la démo.
