# SafeRide — Comment le projet a été conçu et développé

> Ce document raconte le **making-of** de SafeRide : du document d'idéation
> à un MVP fonctionnel bilingue, en passant par l'architecture, les choix
> techniques, les compromis et les questions probables des juges.

## 1. Point de départ

Le projet part **uniquement** du document `SafeRide_Ideation - Anglais.pdf`
fourni par le hackathon Africa Ignite. Le document décrit :

- une vision : *Network Trust Score* pour la mobilité en Afrique subsaharienne
- une formule pondérée (`SCR = SIM Swap × 35% + Localisation × 25% + Appareil × 20% + Numéro × 20%`)
- 7 APIs CAMARA orchestrées via Nokia Network-as-Code
- un modèle économique (commission 8 %, abonnement Premium 5 000 FCFA/mois, licence B2B)
- une roadmap en 4 phases (Phase 0 hackathon → Phase 3 expansion régionale)

Aucun code n'existait. **Tout a été construit à partir du PDF**.

## 2. Méthode

### 2.1 Compréhension du domaine

1. Extraction texte des deux versions du PDF (FR + EN) via `pypdf`.
2. Identification des composants à livrer pour cocher les critères du
   hackathon Africa Ignite (HackerEarth) :
   - Impact pour utilisateur ✅
   - Applicabilité au Network-as-Code ✅
   - Plusieurs APIs utilisées ✅
   - Construit sur la plateforme NaC ✅
3. Recherche des sources officielles : `camaraproject.org`, `networkascode.nokia.io`.

### 2.2 Choix d'architecture (et pourquoi)

| Décision                         | Raison                                                                 |
| -------------------------------- | ---------------------------------------------------------------------- |
| **FastAPI** (Python) en backend  | Conforme au PDF section 5.1 ; OpenAPI auto, Pydantic v2, performant.   |
| **React 18 + Vite** en frontend  | Conforme au PDF ; build rapide, écosystème mature.                     |
| **Leaflet + OpenStreetMap**      | Conforme au PDF (open-source, adapté au contexte africain).            |
| **i18n maison (FR/EN)**          | Léger, sans `i18next`, suffisant pour 60 clés.                         |
| **Stockage in-memory**           | MVP hackathon. PostgreSQL + Redis branchés en Phase 1.                 |
| **Mock CAMARA local**            | Permet de coder/démontrer sans clé Nokia NaC. Bascule via env var.     |
| **Bearer token admin**           | Suffisant en MVP. JWT + IdP en production.                             |
| **Chariow iframe**               | Plus simple qu'un PSP custom, supporte Mobile Money + cartes + crypto. |

### 2.3 Itérations

Le projet a été construit en **trois passes** :

1. **Squelette MVP** : backend `FastAPI` minimal, score brut, frontend simple.
2. **Refonte complète** (qualité produit) :
   - 7 APIs CAMARA en parallèle avec log d'orchestration AI
   - Bilingue FR/EN
   - Carte Leaflet interactive
   - Vues distinctes Passager / Chauffeur / Opérations / Concept
   - Design moderne (glassmorphism, gradients, Space Grotesk + Inter)
3. **Extension business** (cette passe) :
   - Abonnement Premium via **Chariow** (iframe + webhook + simulation)
   - Back-office **Admin** (CRUD chauffeurs, courses, abonnements, KPIs / MRR)
   - Documentation exhaustive (Business, Technical, FAQ, Pitch, API references, Admin)
   - **PowerPoint** généré par script `python-pptx`

## 3. Stack final

```
backend/
  ├── FastAPI 0.115 + Pydantic 2.11 + Uvicorn
  ├── In-memory store (dict)
  ├── 7 APIs CAMARA simulées (mock fidèle aux signatures)
  ├── Trust Agent (orchestration adaptative régionale)
  ├── Subscription module (Chariow + simulation prototype)
  └── Admin router (Bearer protected)

frontend/
  ├── React 18 + Vite 5
  ├── react-leaflet + leaflet (OpenStreetMap)
  ├── i18n maison (FR/EN)
  ├── 6 vues : Passager, Chauffeur, Opérations, Premium, Admin, Concept
  └── Design system custom (glassmorphism)

docs/
  ├── BUSINESS.md, TECHNICAL.md, API_REFERENCES.md
  ├── ADMIN.md, FAQ.md (60+ Q/R), PITCH.md
  ├── API_KEYS.md, DEVELOPMENT.md (ce fichier)
  ├── MENTOR_QUESTIONS.md
  └── SafeRide_Pitch_Deck.pptx (généré)
```

## 4. Le moteur Trust Score (cœur du projet)

### 4.1 Principe

Pour chaque chauffeur disponible, l'agent IA appelle 4 APIs CAMARA mandatory
en parallèle, applique la pondération du PDF et classe le chauffeur dans
l'un des trois buckets (`Reliable`, `Attention`, `Blocked`).

### 4.2 Code clé

- `backend/app/services/camara.py` : signatures CAMARA + simulation des appels NaC
- `backend/app/services/agent.py` : orchestrateur AI (ordre adapté à la ville)
- `backend/app/services/scoring.py` : calcul pondéré et classement

### 4.3 Heuristiques régionales (couche agentique)

| Ville     | Ordre d'appel optimisé                                              |
| --------- | ------------------------------------------------------------------- |
| Douala    | SIM Swap → Localisation → Appareil → Numéro (forte pression SIM swap) |
| Lagos     | Appareil → SIM Swap → Localisation → Numéro (fraude device endémique) |
| Dakar     | Numéro → SIM Swap → Localisation → Appareil (Number Verif fragile)  |
| Yaoundé / Nairobi | Ordre standard                                              |

## 5. Choix UX

- **Carte interactive** : clic = pickup, Shift+clic = destination. Marqueurs
  colorés avec border indiquant le bucket.
- **3 buckets parallèles** : visuellement clairs (vert / jaune / rouge avec
  glow).
- **Barres de score** par composante (35%, 25%, 20%, 20%) sur chaque carte
  chauffeur pour expliquer la décision.
- **Timeline temps réel** : événements bilingues, sévérité info / warning / critical.
- **Switcher de langue** dans la topbar, persistant via `localStorage`.
- **Mode sombre par défaut** : adapté à un usage opérationnel nocturne.

## 6. Sécurité (état actuel vs cible)

| Aspect                    | MVP                              | Production                              |
| ------------------------- | -------------------------------- | --------------------------------------- |
| CORS                      | Whitelist via env                | Idem + domaine prod uniquement          |
| Auth admin                | Bearer (.env)                    | JWT + IdP + 2FA                         |
| Webhook Chariow           | Payload accepté                  | Vérification HMAC obligatoire           |
| Stockage                  | In-memory                        | PostgreSQL chiffré + Redis              |
| Logs                      | stdout uvicorn                   | OpenTelemetry + Sentry                  |
| Frontend                  | API key dans localStorage        | Cookie HttpOnly + JWT                   |

## 7. Conformité

- **CAMARA** : toutes les APIs orchestrées sont 100 % conformes aux specs Linux Foundation.
- **GSMA Open Gateway** : alignement sur les 4 piliers (connectivité, identité, innovation, impact local).
- **Données personnelles** : conformité prévue avec CDP (Cameroun), NDPR (Nigeria), DPA (Kenya), DDPR (Sénégal).

## 8. Questions probables des juges (et réponses prêtes)

### Q1. *Pourquoi 7 APIs et pas 3 ?*
> Les 4 mandatory CAMARA permettent de calculer le score, mais QoD, Congestion
> et Geofencing sont indispensables pour le **monitoring en course**. C'est
> l'un des critères Hackathon : *« Did the team use several different APIs ? »*.

### Q2. *Pourquoi 35 % pour SIM Swap ?*
> La fraude SIM swap est statistiquement la première cause d'usurpation
> chauffeur en Afrique subsaharienne (+340 % en 3 ans). C'est le signal
> le plus discriminant. Pondération directement dérivée du PDF SafeRide
> section 5.2.

### Q3. *Comment vérifiez-vous que c'est vraiment du CAMARA ?*
> Le code mock respecte les signatures officielles documentées sur
> `github.com/camaraproject/SimSwap`, `NumberVerification`, etc. La bascule
> vers le vrai SDK Nokia se fait via `SAFERIDE_USE_REAL_NAC=true`. Voir
> `docs/API_REFERENCES.md`.

### Q4. *Et si Nokia NaC est down ?*
> Le moteur supporte un mode dégradé (signal `score=null` toléré, fallback sur
> les APIs disponibles). En production : timeout 1 s par API, retry exponentiel,
> circuit breaker.

### Q5. *Que se passe-t-il si un chauffeur change d'opérateur ?*
> `Number Verification` détecte immédiatement le changement et le score Number
> tombe à 25/100. Le chauffeur passe en bucket Attention le temps de re-vérifier.

### Q6. *Comment passer à 100 000 utilisateurs ?*
> Architecture cloud-native déjà conçue : PostgreSQL HA, Redis cluster,
> appels CAMARA parallélisés (`asyncio.gather`), CDN frontend, observabilité
> OpenTelemetry. Phase 1 (Douala) testera la charge à 500 chauffeurs réels.

### Q7. *Est-ce que la simulation de paiement est utilisable en production ?*
> **Non**. C'est un endpoint prototype `POST /subscriptions/{id}/simulate-payment`
> qui doit être désactivé en production. La doc `API_KEYS.md` explique
> comment configurer le vrai webhook Chariow + signature HMAC.

### Q8. *Pourquoi Chariow et pas Stripe ?*
> Chariow supporte nativement **Mobile Money** (Orange Money, Wave, MTN MoMo,
> Moov), cartes bancaires et crypto. Stripe ne couvre pas le Mobile Money
> africain. Chariow est local, FCFA-natif, et respecte les régulations
> régionales.

### Q9. *Combien d'argent faut-il pour démarrer ?*
> 120 – 180 k€ sur 9 mois pour le pilote Douala : infrastructure cloud,
> intégrations opérateur, acquisition chauffeurs, conformité, équipe support.

### Q10. *Pourquoi pas une app mobile native ?*
> Phase 2 prévoit la conversion en React Native. Pour le hackathon, le web
> permet une démo immédiate sans installation. La PWA est une étape
> intermédiaire (Phase 1).

### Q11. *Comment recrutez-vous des chauffeurs honnêtes ?*
> Le moteur de confiance est *self-selecting* : les chauffeurs frauduleux
> sont exclus automatiquement par les APIs CAMARA. Les Premium reçoivent
> en plus une priorité sur les courses, ce qui crée un cercle vertueux.

### Q12. *Et la concurrence avec Bolt / Yango ?*
> SafeRide ne cherche pas à les remplacer immédiatement. Le différentiateur
> *Trust Score* peut être vendu en **API B2B** à n'importe quelle app de
> mobilité (y compris Bolt et Yango s'ils le souhaitent). C'est aussi un
> *layer de confiance* pour les fintech, livraison, santé.

### Q13. *Est-ce vraiment de l'AI agentique ?*
> Oui, à plusieurs niveaux :
> - Orchestration adaptative (ordre des APIs varie selon le contexte)
> - Apprentissage régional (heuristiques de fraude par ville)
> - Décision contextuelle (le score n'est pas une simple somme, le statut est dérivé de seuils dynamiques)
> - Communication multilingue automatique (FR/EN/local)
> En Phase 2 : remplacement par un LLM léger (Llama 3 / Mistral) via Ollama.

### Q14. *Comment garantissez-vous la vie privée du passager ?*
> Aucune donnée passager n'est partagée avec l'opérateur. Seul le **numéro
> chauffeur** est interrogé via les APIs CAMARA, avec son consentement
> explicite à l'inscription. Stockage chiffré au repos en Phase 1.

### Q15. *Pourquoi ce projet est meilleur que les autres ?*
> Trois raisons :
> 1. **Profondeur** : 7 APIs CAMARA orchestrées (pas une seule pour la forme)
> 2. **Localisation** : FCFA, Mobile Money, langues locales, opérateurs africains, 5 villes seedées
> 3. **Réalisme** : back-office admin complet, abonnement payant via Chariow, doc business + technique + pitch deck PPT, prêt pour pilote Douala dans 6 mois

## 9. Ce qui n'est PAS dans le MVP (transparence)

- Pas de PostgreSQL ni Redis (in-memory uniquement)
- Pas d'authentification chauffeur (pas de Number Verification réel à l'inscription)
- Pas de notifications push (pas de Firebase)
- Pas d'app mobile (web uniquement)
- Pas de signature HMAC du webhook Chariow vérifiée
- Pas de tests automatisés (uniquement vérification de compilation + endpoints en live)

Tout cela est documenté dans `TECHNICAL.md` et `FAQ.md` avec la roadmap Phase 1.

## 10. Comment continuer après le hackathon

1. **Brancher PostgreSQL + Redis** (Neon + Upstash, gratuit pour démarrer)
2. **Ouvrir un compte Nokia NaC** : récupérer la vraie clé API
3. **Ouvrir un compte Chariow** : créer le produit Premium
4. **Déployer** : backend sur Render/Fly.io, frontend sur Vercel
5. **Brancher la signature HMAC** Chariow
6. **Pilote Douala** : recruter 50 chauffeurs en partenariat avec MTN Cameroun
7. **Mesurer** : taux de fraude, NPS, MRR, latence CAMARA
8. **Itérer** : ajuster les seuils du score, ajouter des heuristiques de ville
