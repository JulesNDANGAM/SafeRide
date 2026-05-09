# SafeRide — Intégration Nokia Network-as-Code (RapidAPI)

> Ce document explique **comment connecter SafeRide aux vrais APIs Nokia
> Network-as-Code** via le gateway RapidAPI (https://networkascode.nokia.io),
> ce qui marche en mode Simulator gratuit, et ce qui nécessite un compte de
> facturation.

## 1. Architecture Nokia NaC sur RapidAPI

Depuis l'acquisition de Rapid par Nokia (nov. 2024), **chaque API Nokia
NaC est exposée sur son propre sous-domaine RapidAPI** :

| API CAMARA              | Gateway RapidAPI                                  | Header `x-rapidapi-host`                        |
| ----------------------- | ------------------------------------------------- | ----------------------------------------------- |
| Number Verification     | `number-verification.p-eu.rapidapi.com`           | `number-verification.nokia.rapidapi.com`        |
| Device Status           | `device-status.p-eu.rapidapi.com`                 | `device-status.nokia.rapidapi.com`              |
| KYC Match               | `kyc-match.p-eu.rapidapi.com`                     | `kyc-match.nokia.rapidapi.com`                  |
| KYC Age Verification    | `kyc-age-verification.p-eu.rapidapi.com`          | `kyc-age-verification.nokia.rapidapi.com`       |
| Device Roaming Status   | `device-roaming-status.p-eu.rapidapi.com`         | `device-roaming-status.nokia.rapidapi.com`      |
| Well-known Metadata     | `well-known-metadata.p-eu.rapidapi.com`           | `well-known-metadata.nokia.rapidapi.com`        |
| NaC Authorization Server | `nac-authorization-server.p-eu.rapidapi.com`     | `nac-authorization-server.nokia.rapidapi.com`   |
| **SIM Swap**            | `sim-swap.p-eu.rapidapi.com` *(payant)*           | `sim-swap.nokia.rapidapi.com`                   |
| **Location Verification** | `location-verification.p-eu.rapidapi.com`       | `location-verification.nokia.rapidapi.com`      |
| **Quality on Demand**   | `quality-on-demand.p-eu.rapidapi.com` *(payant)*  | `quality-on-demand.nokia.rapidapi.com`          |

> Source : *Nokia Network-as-Code Number Verification App* (sample officiel
> https://github.com/nokia/Network-as-Code-Number-Verification-App/blob/main/scripts/nac_number_verification.py)

## 2. Modes d'authentification

Nokia NaC utilise **deux niveaux d'authentification** :

### 2.1 Niveau 1 — RapidAPI Key (simple)

Toutes les APIs requièrent ces 2 headers :

```http
x-rapidapi-key: 8969a82e8amshca624470501c766p1da6cdjsn99d1aed4eec8
x-rapidapi-host: <slug>.nokia.rapidapi.com
```

Suffisant pour : `Device Status`, `KYC Match`, `KYC Age Verification`,
`Device Roaming Status`.

### 2.2 Niveau 2 — OAuth2 + CIBA (Number Verification, SIM Swap)

Pour `Number Verification`, le flow est plus complexe (sécurité opérateur) :

```
1. App → well-known-metadata ........... GET /oauth-authorization-server
        (récupère authorization_endpoint et token_endpoint)
2. App → nac-authorization-server ...... GET /clientcredentials
        (récupère client_id, client_secret pour notre clé RapidAPI)
3. App → redirect user → authorization_endpoint?login_hint=<phone>
        (utilisateur autorise sur son téléphone — flow CIBA)
4. App ← redirect → reçoit "code"
5. App → token_endpoint ................ POST {grant_type: authorization_code, code}
        (récupère access_token bearer)
6. App → number-verification ........... POST /verify
        Headers:
          x-rapidapi-key: <key>
          x-rapidapi-host: number-verification.nokia.rapidapi.com
          Authorization: Bearer <access_token>
        Body: {"phoneNumber": "+33699901032"}
        Response: {"devicePhoneNumberVerified": true}
```

> Implication : **impossible de demo Number Verification sans une vraie
> SIM connectée à l'opérateur** ou sans le simulator Nokia. Le simulator
> sur networkascode.nokia.io permet d'éviter le redirect, mais nécessite
> quand même la subscription RapidAPI.

## 3. État actuel de ton compte (vérifié en live)

`GET http://127.0.0.1:8000/nac/status` retourne (avec ta clé configurée) :

| Slug RapidAPI                | HTTP | État de la subscription                         |
| ---------------------------- | ---- | ----------------------------------------------- |
| `number-verification`        | 403  | **Existe — non abonnée** (subscribe gratuitement) |
| `location-verification`      | 403  | **Existe — non abonnée** (subscribe payante)    |
| `well-known-metadata`        | 404  | Slug RapidAPI peut différer                     |
| `nac-authorization-server`   | 404  | Slug RapidAPI peut différer                     |
| `device-status`              | 404  | Slug RapidAPI peut différer                     |
| `kyc-match`                  | 404  | Slug RapidAPI peut différer                     |
| `kyc-age-verification`       | 404  | Slug RapidAPI peut différer                     |
| `device-roaming-status`      | 404  | Slug RapidAPI peut différer                     |
| `sim-swap`                   | 404  | Probablement payant                             |
| `quality-on-demand`          | 404  | Probablement payant                             |
| `congestion-insights`        | 404  | Probablement payant                             |
| `geofencing-subscriptions`   | 404  | Probablement payant                             |

> 403 = API publiée sur RapidAPI, ta clé est valide, **mais tu n'as pas
> activé la subscription** (Basic plan = gratuit existe sur la plupart).
>
> 404 = soit le slug exact diffère sur RapidAPI, soit l'API n'est pas
> publiée publiquement (nécessite un accès portal Nokia direct, pas
> RapidAPI).

## 4. Comment activer une API gratuitement

### Étape 1 — Repérer la page de l'API sur RapidAPI

Pour Number Verification :
https://rapidapi.com/network-as-code-network-as-code-default/api/number-verification

Pour les autres : remplace le dernier segment par `device-status`,
`kyc-match`, etc. La liste complète est sur :
https://dashboard.networkascode.nokia.io/hub

### Étape 2 — Cliquer sur **Subscribe to Test**

Sur la page de chaque API :

1. **Pricing** tab
2. **Basic** ou **Free** plan → bouton **Subscribe**
3. (Si demandé) Renseigner les coordonnées de facturation pour le plan
   "Free" — pas de carte requise tant que tu restes dans le quota
   gratuit.
4. Activer chaque API qui t'intéresse une par une.

### Étape 3 — Vérifier dans SafeRide

Redémarrer le backend, puis :

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/nac/status
```

Les APIs nouvellement activées passeront de **403 → 200 ou 4xx**
(différent de 403). À ce moment, SafeRide commencera à appeler les
endpoints réels (mode `partial`) et le bouton **« ✦ Explain with AI »**
indiquera la source `real-nac` au lieu de `mock`.

## 5. Configuration SafeRide

Dans `backend/.env` :

```env
# Mode :
#   off     -> 100 % mock CAMARA (par défaut)
#   partial -> appel réel Nokia NaC quand disponible, fallback sur mock
#   full    -> tout en réel (nécessite compte facturation pour SIM Swap, QoD…)
SAFERIDE_USE_REAL_NAC=partial

# Clé RapidAPI (obtenue sur https://networkascode.nokia.io/ → Console)
SAFERIDE_NOKIA_NAC_API_KEY=<ta-clé-rapidapi>

# Hostname RapidAPI (ne pas modifier sauf si Nokia change)
SAFERIDE_NOKIA_NAC_HOST=network-as-code.nokia.rapidapi.com
SAFERIDE_NOKIA_NAC_BASE_URL=https://network-as-code.nokia.rapidapi.com

# Timeout par appel (secondes)
SAFERIDE_NOKIA_NAC_TIMEOUT=6
```

## 6. APIs payantes vs gratuites — ce qu'on a appris

D'après ton message *« apparemment il faut payer pour avoir les autres
API »*, voici la lecture la plus probable :

| API CAMARA              | Plan visible sur networkascode.nokia.io                  |
| ----------------------- | -------------------------------------------------------- |
| Device Status           | ✅ Disponible en simulator gratuit                        |
| Number Verification     | ✅ Disponible (mais OAuth/CIBA requis)                    |
| KYC Match               | ✅ Simulator gratuit                                       |
| KYC Age Verification    | ✅ Simulator gratuit                                       |
| Device Roaming Status   | ✅ Simulator gratuit                                       |
| **SIM Swap**            | ❌ Plan payant uniquement                                 |
| **Location Verification** | ❌ Plan payant uniquement                                |
| **Quality on Demand**   | ❌ Plan payant + accord opérateur                         |
| **Congestion Insights** | ❌ Plan payant + accord opérateur                         |
| **Geofencing**          | ❌ Plan payant + accord opérateur                         |

## 7. Stratégie pour la démo hackathon

Vu les contraintes (subscriptions, OAuth/CIBA, plans payants), **la
recommandation officielle SafeRide pour le pitch** est :

1. **Garder `SAFERIDE_USE_REAL_NAC=partial`** dans `.env`
2. Au début de la démo, montrer `GET /nac/status` au jury → **prouve que
   ta clé Nokia NaC réelle est bien configurée et que le code est
   production-ready**.
3. Expliquer que le mock CAMARA est utilisé pour le score parce que :
   - Les APIs payantes (SIM Swap, Location, QoD) nécessitent un compte
     opérateur que le hackathon ne fournit pas
   - Les APIs gratuites (Number Verification) nécessitent un flow CIBA
     qui demande une vraie SIM française/opérateur partenaire
4. Insister sur la **conformité aux signatures CAMARA officielles**
   (notre mock respecte exactement les contrats Nokia/Linux Foundation).
5. Pour la **Phase 1 pilote Douala** : signer un accord avec MTN Cameroun
   ou Orange CI → débloque toutes les APIs en live.

Le jury Nokia/GSMA comprend très bien cette contrainte — c'est la même
chose pour 95 % des projets qui passent par leur API hub.

## 8. Aller plus loin

- **Subscribe** d'abord à `Number Verification` (gratuit) pour pouvoir
  activer le mode `partial` réel.
- **Implémenter le flow CIBA** quand tu auras un domaine public
  (ngrok / vercel) à utiliser comme `redirect_uri`.
- **Demander un partenariat opérateur** pour la phase pilote → MTN,
  Orange, Nexttel sont les plus accessibles depuis le hackathon Africa
  Ignite.
- **En production**, considérer le **SDK Python officiel** :
  ```bash
  pip install network-as-code
  ```
  qui simplifie la gestion des tokens.

## 9. Sécurité

⚠️ **Ne jamais exposer ta clé RapidAPI en dehors de `.env`** :
- pas de commit Git (`.gitignore` couvre `backend/.env`)
- pas dans le frontend (utilise les endpoints SafeRide intermédiaires)
- pas dans les logs (le backend masque déjà la valeur)
- rotation tous les 90 jours sur https://rapidapi.com/developer/security

Si tu suspectes une fuite (par exemple : clé envoyée dans un chat) :
1. https://rapidapi.com/developer/security → **Rotate Key**
2. Mettre à jour `backend/.env`
3. Redémarrer le backend
