# SafeRide — Pitch (5 minutes)

> *Every ride, checked. Every journey, safe.*

## Slide 1 — Le problème (45 s)

> 3 millions de courses VTC par jour en Afrique subsaharienne. **+340 % d'incidents SIM swap** en 3 ans. **42 % seulement** de confiance dans les apps de mobilité (GSMA 2024). Bolt et Uber détectent la fraude *après* qu'elle a eu lieu.

## Slide 2 — Notre insight (30 s)

> Les opérateurs mobiles **savent** si une SIM a été échangée, si un GPS est truqué, si un device est suspect. Mais ces signaux étaient verrouillés. **CAMARA + Nokia Network-as-Code** les ouvrent. **SafeRide** est le premier produit grand public qui les transforme en valeur d'usage.

## Slide 3 — Ce qu'on fait : deux boucliers (60 s)

> SafeRide protège chaque course **AVANT et APRÈS** :
>
> **Bouclier d'entrée (AVANT)** — Network Trust Score (0–100) calculé en temps réel via 5 APIs CAMARA :
> - SIM Swap (35 %) + Localisation réseau (25 %) + Statut device (20 %) + Vérification numéro (20 %)
> - + Quality on Demand, Congestion Insights, Geofencing pour le suivi en course
>
> **Bouclier de sortie (APRÈS)** — L'IA vérifie que le trajet s'est bien déroulé :
> - Itinéraire suivi ? Arrivée à destination ? Durée cohérente ?
> - Si anomalie → **alerte automatique** à la flotte du chauffeur ou à la personne de confiance du passager
> - Données réseau = preuves légales inaltérables (assurances, police)

## Slide 4 — Démo (90 s)

1. Onglet **Passager** : carte Douala, 5 chauffeurs autour de moi, classés Reliable/Attention/Blocked.
2. Sélection d'un chauffeur Reliable → course démarrée, monitoring temps réel.
3. Simulation d'une chute QoD → alerte critique, événement bilingue.
4. Onglet **Chauffeur** : journal d'orchestration AI, 7 signaux CAMARA détaillés.
5. Onglet **Premium** : paiement 5 000 FCFA via Chariow embarqué (Mobile Money / cartes / crypto).
6. Onglet **Admin** : KPIs, MRR, gestion CRUD des chauffeurs.

## Slide 5 — Différenciation (30 s)

| Critère              | Bolt / Uber / Yango | **SafeRide**             |
| -------------------- | ----------- | ------------------------ |
| Détection SIM swap   | ❌          | ✅ 35 % du score         |
| Cross-check GPS      | ❌          | ✅ via opérateur         |
| Continuité connexion | best effort | ✅ Quality on Demand     |
| Vérification fin de course | ❌ (notation seule) | ✅ IA vérifie trajet |
| Alerte auto si anomalie | ❌ (partage manuel) | ✅ flotte / personne de confiance |
| Preuves réseau inaltérables | ❌ | ✅ pour enquêtes / assurances |
| Commission           | 15–25 %     | **8 %**                  |
| IA adaptative        | ❌          | ✅ scoring par ville, détection contextuelle |

## Slide 5b — Pourquoi ils ne peuvent PAS le faire (20 s)

> **4 barrières** : (1) Conflit d'intérêt — ils gagnent sur le volume, pas la sécurité. (2) Expertise télécom — ce n'est pas leur métier. (3) Accès opérateur — ils n'ont pas les accords NaC. (4) IA adaptative — notre modèle s'améliore avec les données africaines, effet réseau. **SafeRide = Stripe de la sécurité transport.**

## Slide 6 — Modèle économique (30 s)

- 8 % de commission par course
- 5 000 FCFA / mois Premium chauffeur (Chariow)
- Licence B2B SafeRide Trust Score API
- Partenariat opérateur (revenu sur appels NaC)

> **MRR projeté Phase 2 (10 000 utilisateurs) : ≈ 29 MFCFA / mois**

## Slide 7 — Roadmap (30 s)

- Phase 0 (avr.–mai 2026) : prototype hackathon ✅
- Phase 1 (juin–août 2026) : pilote Douala, 500 chauffeurs, MTN Cameroun
- Phase 2 (sept.–déc. 2026) : Yaoundé + Lagos, 10 000 utilisateurs
- Phase 3 (2027) : Dakar, Nairobi, Abidjan, licence B2B

## Slide 8 — Pourquoi nous (15 s)

> Une équipe pluridisciplinaire (mobilité, télécoms, IA, design produit), MVP fonctionnel **en 16 jours**, architecture cloud-native compatible avec **tout opérateur GSMA Open Gateway**.

## Slide 9 — Demande (10 s)

> 120 000 – 180 000 EUR pour le pilote Douala (9 mois). Partenariat opérateur en parallèle.

## One-liner final

> **SafeRide ne transporte pas que des passagers : il protège chaque course avant, pendant et après — et transforme chaque trajet en preuve d'identité réseau qu'aucune plateforme VTC ne peut reproduire.**
