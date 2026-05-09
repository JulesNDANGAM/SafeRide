# SafeRide — Documentation

> *Every ride, checked. Every journey, safe.* — *Chaque course, vérifiée. Chaque trajet, sécurisé.*

Cette documentation accompagne le prototype hackathon SafeRide. Elle est organisée pour répondre à toutes les questions techniques, business et opérationnelles du projet.

## Sommaire

| Document                                | Audience                          | Contenu                                                                 |
| --------------------------------------- | --------------------------------- | ----------------------------------------------------------------------- |
| [`BUSINESS.md`](./BUSINESS.md)          | Investisseurs, partenaires        | Vision, marché, modèle économique, projections, GTM                     |
| [`TECHNICAL.md`](./TECHNICAL.md)        | Développeurs, architectes         | Architecture, stack, flux de données, déploiement                       |
| [`API_REFERENCES.md`](./API_REFERENCES.md) | Intégrateurs                    | Liens officiels CAMARA, Nokia NaC, exemples d'appels, webhooks Chariow  |
| [`ADMIN.md`](./ADMIN.md)                | Équipe Ops SafeRide               | Utilisation du back-office, gestion chauffeurs, abonnements             |
| [`FAQ.md`](./FAQ.md)                    | Tous publics                      | 60+ questions/réponses (technique, business, sécurité, conformité)      |
| [`PITCH.md`](./PITCH.md)                | Jury hackathon, pitch investisseur| Pitch deck textuel exécutable en 5 minutes                              |
| [`SafeRide_Pitch_Deck.pptx`](./SafeRide_Pitch_Deck.pptx) | Africa Ignite Hackathon | **Présentation PowerPoint 9 slides** (problème, solution, archi, business, équipe, valeur, APIs, roadmap) |
| [`generate_pitch_deck.py`](./generate_pitch_deck.py) | Devs | Script `python-pptx` pour régénérer le deck |
| [`API_KEYS.md`](./API_KEYS.md)                     | Devs / DevOps  | **Où mettre les clés API réelles** (Nokia NaC, Chariow, Admin) |
| [`DEVELOPMENT.md`](./DEVELOPMENT.md)               | Auteur / Jury  | Making-of du projet + 15 questions probables avec réponses prêtes |
| [`MENTOR_QUESTIONS.md`](./MENTOR_QUESTIONS.md)     | Auteur         | 60+ questions à poser à mon mentor du hackathon                   |
| [`AI_AGENT.md`](./AI_AGENT.md)                     | Devs / Jury    | **Agent IA OpenRouter** (config, modèles gratuits, fallback, sécurité) |
| [`NOKIA_NAC.md`](./NOKIA_NAC.md)                   | Devs / DevOps  | **Intégration Nokia Network-as-Code RapidAPI** (subscriptions, OAuth/CIBA, mode partial/full) |

## Lancer le projet en 60 secondes

```powershell
# 1. Backend
pip install -r backend/requirements.txt
python -m uvicorn app.main:app --app-dir backend --reload

# 2. Frontend (autre terminal)
cd frontend
npm install
npm run dev
```

- API : http://127.0.0.1:8000 (docs auto : `/docs`)
- UI  : http://127.0.0.1:5173
- Admin token par défaut : `saferide-admin-dev` (à changer en prod)

## Provenance des APIs utilisées

Toutes les APIs sont des **APIs CAMARA** standardisées par la **Linux Foundation**, exposées par les opérateurs mobiles via la plateforme **Nokia Network-as-Code (NaC)**. Voir [`API_REFERENCES.md`](./API_REFERENCES.md) pour les liens officiels.

| API                       | Source officielle                                                  |
| ------------------------- | ------------------------------------------------------------------ |
| SIM Swap                  | https://camaraproject.org/sim-swap/                                |
| Number Verification       | https://github.com/camaraproject/NumberVerification                |
| Device Status             | https://github.com/camaraproject/DeviceStatus                      |
| Location Verification     | https://github.com/camaraproject/DeviceLocation                    |
| Quality on Demand (QoD)   | https://github.com/camaraproject/QualityOnDemand                   |
| Congestion Insights       | https://github.com/camaraproject/CongestionInsights                |
| Geofencing Subscriptions  | https://github.com/camaraproject/Geofencing                        |
| Nokia Network-as-Code SDK | https://networkascode.nokia.io/                                    |

## Paiement (Chariow)

L’abonnement Premium chauffeur (5 000 FCFA / mois, voir PDF section 8) est encaissé via **Chariow** (Mobile Money + cartes + crypto).
Le frontend intègre la page de paiement dans une `iframe`, et le backend reçoit les notifications via webhook : voir [`API_REFERENCES.md`](./API_REFERENCES.md#chariow).
