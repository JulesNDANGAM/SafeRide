# SafeRide — Agent IA (OpenRouter + LLM gratuit)

> *« Lightweight LLM (Llama) for intelligent API orchestration and scoring »*
> — SafeRide Ideation PDF, section 5.1 *Technical Architecture*

Ce document explique comment l'**agent IA** de SafeRide fonctionne, comment
il s'intègre à OpenRouter, et comment le configurer (clés API, modèles,
fallback).

## 1. Pourquoi OpenRouter ?

OpenRouter (**https://openrouter.ai**) est un **routeur unifié** vers des
dizaines de LLM (Llama, Mistral, Gemini, Qwen, GPT, Claude, etc.) avec :

- **Une seule clé API**, un seul SDK (compatible OpenAI Chat Completions)
- **Plusieurs modèles gratuits** (`:free`) parfaits pour un prototype
- Bascule modèle = changement d'une variable d'environnement
- Crédits progressifs, pas de carte bancaire requise pour les modèles `:free`

C'est exactement ce dont SafeRide a besoin pour la phase hackathon.

## 2. Modèles gratuits supportés

Toujours valider la disponibilité sur https://openrouter.ai/models?max_price=0 — la liste évolue souvent (rate limits upstream, nouveaux modèles).

**Modèles vérifiés fonctionnels** au moment du développement de SafeRide
(testés avec `GET /openrouter.ai/api/v1/models` + appel réel) :

| Modèle (slug OpenRouter)                                   | Forces                                  |
| ---------------------------------------------------------- | --------------------------------------- |
| `openai/gpt-oss-20b:free` *(défaut SafeRide)*              | JSON propre, rapide, FR/EN, ne wrap pas |
| `openai/gpt-oss-120b:free`                                 | Plus précis, JSON propre                |
| `z-ai/glm-4.5-air:free`                                    | OK mais wrap parfois en ```json…```     |
| `minimax/minimax-m2.5:free`                                | OK avec extracteur JSON tolérant        |
| `meta-llama/llama-3.3-70b-instruct:free`                   | Souvent rate-limité upstream (429)      |
| `qwen/qwen3-next-80b-a3b-instruct:free`                    | Souvent rate-limité upstream            |

> Le client SafeRide intègre un **extracteur JSON tolérant** (markdown
> fences + extraction de bloc `{...}`) donc tous ces modèles fonctionnent
> même s'ils n'utilisent pas strictement `response_format=json_object`.

> Si un modèle renvoie 429 (rate-limited upstream), il suffit de changer
> `SAFERIDE_OPENROUTER_MODEL` dans `.env` et de redémarrer le backend.

> ⚠️ Les modèles `:free` ont un quota journalier limité par OpenRouter.
> Pour un pilote production, prévoir un compte avec crédits payants ou
> basculer vers un Llama auto-hébergé (Ollama).

## 3. Ce que fait l'agent IA

D'après le PDF section 6 *Innovation Layer: Agentic AI*, l'agent doit :

| Capacité PDF                          | Implémentation SafeRide                                    |
| ------------------------------------- | ---------------------------------------------------------- |
| Intelligent orchestration             | `services/agent.py` — ordre des APIs adapté à la ville     |
| Learning fraud patterns               | Heuristiques régionales (Douala SIM-first, Lagos Device-first, Dakar Number-first) |
| Predictive Analytics                  | Combiné LLM + Congestion Insights (extension Phase 2)       |
| **Passenger Communication multilingue** | **`services/llm.py` — message FR/EN généré par OpenRouter** |

Aujourd'hui, le LLM OpenRouter est utilisé pour produire à la demande,
pour un chauffeur donné, **un message bilingue (FR/EN) + une recommandation**
(`accept` / `review` / `reject`) qui explique au passager la décision du
moteur de confiance.

## 4. Comment ça marche techniquement

### 4.1 Schéma de flux

```
Frontend (DriverCard) ── click "✦ Explain with AI"
        │
        ▼
POST /drivers/{id}/explain?city=Douala
        │
        ▼
TrustScoringService.evaluate(driver, with_llm=True)
        │
        ▼
OpenRouterAgent.explain(snapshot_dict)
        │
        ├── if API key set ──► POST openrouter.ai/api/v1/chat/completions
        │                         · model = $SAFERIDE_OPENROUTER_MODEL
        │                         · response_format = json_object
        │                         ▼
        │                       { message_fr, message_en, recommendation }
        │
        └── else ────────────► fallback bilingual template (no network call)
        │
        ▼
DriverTrustSnapshot.llm_insight ─► JSON renvoyé au frontend
        │
        ▼
DriverCard affiche un panneau cyan avec le message + badge recommandation
```

### 4.2 Prompt système

```text
You are SafeRide's Trust Agent. SafeRide computes a Network Trust Score
(0-100) for ride-hailing drivers in Sub-Saharan Africa using CAMARA APIs
via Nokia Network-as-Code. You explain the trust decision in 1 sentence
to passengers. Always respond with strict JSON of the form:
{"message_fr": "...", "message_en": "...", "recommendation": "accept|review|reject"}.
Tone: clear, calm, factual. Do not invent data. If the score is high, be
reassuring; if low, be cautious and protective.
```

### 4.3 Données envoyées au LLM

Pour chaque chauffeur, on transmet **uniquement** :

```json
{
  "driver_name": "Chantal E.",
  "city": "Douala",
  "carrier": "MTN Cameroon",
  "trust_score": 32.0,
  "status": "blocked",
  "anomalies": ["SIM swap detected within last 72h", "..."],
  "monitoring_alerts": ["High network congestion - tracking risk"],
  "breakdown": { "sim_swap": 0, "location": 75, "device": 10, "number": 25 }
}
```

> Aucune donnée passager, aucun numéro de téléphone, aucune coordonnée
> précise n'est envoyée au LLM. Conforme RGPD-like Africa.

## 5. Configuration

### 5.1 Obtenir une clé OpenRouter

1. Aller sur **https://openrouter.ai** → *Sign in* (Google / GitHub).
2. Aller sur https://openrouter.ai/keys
3. **Create Key** → copier la clé qui commence par `sk-or-v1-...`
4. (Optionnel) Activer le mode `:free` only dans les *Settings* pour
   garantir qu'aucun crédit ne sera consommé.

### 5.2 Renseigner `backend/.env`

```env
SAFERIDE_OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SAFERIDE_OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free
# (optionnel)
SAFERIDE_OPENROUTER_REFERER=https://saferide.app
SAFERIDE_OPENROUTER_APP_NAME=SafeRide
SAFERIDE_OPENROUTER_TIMEOUT=8
```

Redémarrer ensuite le backend :

```powershell
python -m uvicorn app.main:app --app-dir backend --reload
```

### 5.3 Vérifier la configuration

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/ai/status
```

Sortie attendue (clé configurée) :

```json
{
  "configured": true,
  "model": "meta-llama/llama-3.2-3b-instruct:free",
  "base_url": "https://openrouter.ai/api/v1"
}
```

### 5.4 Tester un appel LLM réel

```powershell
Invoke-WebRequest -UseBasicParsing -Method POST `
  "http://127.0.0.1:8000/drivers/drv-103/explain?city=Douala"
```

Le snapshot renvoyé contient un `llm_insight` avec :

```json
{
  "message_fr": "Chantal E. est bloqué...",
  "message_en": "Chantal E. is blocked...",
  "recommendation": "reject",
  "model": "meta-llama/llama-3.2-3b-instruct:free",
  "used_llm": true
}
```

Si `used_llm: false`, c'est qu'il y a eu un fallback (clé absente, timeout,
quota dépassé, modèle indisponible). Le projet **continue à fonctionner**
avec un message templatisé.

## 6. Utilisation côté UI

Dans n'importe quelle vue qui affiche une `DriverCard` (Passager,
Opérations, Admin), un bouton **« ✦ Explain with AI »** apparaît. Au clic :

1. Affichage de l'état "AI is thinking…"
2. Appel à `POST /drivers/{id}/explain`
3. Affichage d'un panneau cyan avec :
   - Le message dans la langue active (FR ou EN)
   - Un badge de recommandation (`accept` / `review` / `reject`)
   - Le **modèle utilisé** + indicateur de fallback si applicable

## 7. Coûts & quotas

| Cas                          | Coût                                                    |
| ---------------------------- | ------------------------------------------------------- |
| Modèles `:free` OpenRouter   | **0 €** (quota journalier d'environ 50 requêtes / IP)   |
| Modèles payants OpenRouter   | À partir de 0,0001 €/token (Llama-3.1-8b)               |
| Fallback templatisé          | 0 € (ne sort pas du backend)                            |
| Hosting Llama auto (Phase 2) | Coût VM GPU (Ollama sur RunPod ~ 0,30 €/h)              |

## 8. Sécurité & vie privée

- **Pas de données passager** envoyées au LLM (voir §4.3).
- La clé API n'est **jamais exposée** au frontend.
- En production, ajouter un **rate-limiter** sur `/drivers/{id}/explain`
  (FastAPI + slowapi) pour éviter les abus.
- Activer dans OpenRouter **les seuls modèles autorisés** (whitelist).
- Roter la clé tous les 90 jours.

## 9. Évolutions futures (Phase 2)

- **Auto-hébergement** Llama 3.2 sur Ollama pour 0 quota
- **RAG** sur l'historique des fraudes régionales (vector DB)
- **Tool calling** : permettre au LLM de déclencher lui-même des appels
  CAMARA additionnels (ex. relancer Number Verification)
- **Streaming** : réponses progressives via SSE
- **Multilingue local** : ajouter Wolof, Lingala, Pidgin, Swahili
- **Détection d'anomalies prédictive** : croiser Congestion Insights et
  GPS history pour anticiper les coupures de course

## 10. FAQ

**Q. Que se passe-t-il sans clé OpenRouter ?**
> Le backend retombe sur des templates bilingues. Tout fonctionne, le
> bouton "Explain with AI" affiche juste *Fallback mode (OpenRouter key
> not configured)*.

**Q. Le LLM a-t-il accès à des données sensibles ?**
> Non. Voir §4.3.

**Q. Pourquoi pas OpenAI ou Anthropic directement ?**
> OpenRouter offre une **interface unifiée** vers des dizaines de
> fournisseurs. On peut tester Llama, Mistral, Gemini, Qwen avec la même
> clé sans changer de SDK. Plus pertinent pour un hackathon multi-modèles.

**Q. Comment changer de modèle sans redéployer ?**
> Modifier `SAFERIDE_OPENROUTER_MODEL` dans `.env` et redémarrer le
> backend (rechargement à chaud avec `--reload`).

**Q. Le LLM peut-il bloquer une décision ?**
> Non. Le **score CAMARA reste la source de vérité**. Le LLM ne fait
> qu'expliquer la décision et émettre une **recommandation indicative**
> (`accept`/`review`/`reject`).
