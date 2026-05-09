# SafeRide — Présentation Business

## 1. Vision

SafeRide est le premier moteur de **confiance réseau** dédié à la mobilité urbaine en Afrique subsaharienne. Là où Uber et Bolt se contentent d’évaluations subjectives entre passagers et chauffeurs, SafeRide s’appuie sur des **signaux réseau objectifs et inaltérables** exposés par les opérateurs télécoms via les APIs CAMARA standardisées et Nokia Network-as-Code.

Notre slogan : *Every ride, checked. Every journey, safe.*

## 2. Problème

Le marché du VTC en Afrique subsaharienne devrait atteindre **14 milliards USD en 2030** (PDF section 2.2). Trois problèmes critiques freinent son adoption :

1. **Sécurité passager** — De faux chauffeurs utilisent des comptes compromis après un SIM swap, ce qui mène à des agressions et à des vols.
2. **Fraude opérationnelle** — Des chauffeurs falsifient leur géolocalisation pour accepter des courses sans être physiquement présents.
3. **Discontinuité de service** — La qualité réseau insuffisante interrompt le suivi GPS et la communication passager-chauffeur.

## 3. Données clés (sources GSMA / CAMARA / opérateurs)

| Indicateur                                    | Valeur          |
| --------------------------------------------- | --------------- |
| Incidents SIM Swap en Afrique sub. (2023)     | **+340 % vs 2020** |
| Pertes financières liées à la fraude mobile (2023) | **> 1,2 Mrd USD** |
| Confiance dans les apps de VTC                | **42 %** (GSMA 2024) |
| Pénétration mobile en Afrique sub.            | **49 %** et en hausse |

## 4. Solution : Deux boucliers, avant et après la course

SafeRide ne se contente pas de vérifier le chauffeur au départ. Le projet couvre **deux moments critiques** que personne d'autre ne protège :

### 4.1 Avant la course — Le bouclier d'entrée (Network Trust Score)

SafeRide calcule un **Network Trust Score (SCR)** dynamique de 0 à 100 **avant que le passager ne monte**, en orchestrant plusieurs signaux CAMARA via un agent IA et un moteur propriétaire.

Trois niveaux de confiance :

| Score   | Statut    | Action système                                |
| ------- | --------- | --------------------------------------------- |
| 70–100  | Reliable  | Course autorisée, suivi standard              |
| 40–69   | Attention | Course proposée avec avertissement passager   |
| 0–39    | Blocked   | Chauffeur exclu, alerte équipe SafeRide       |

**Ce que ça empêche** : faux chauffeur après SIM swap, GPS truqué, compte piraté, device suspect. Le passager sait **avant de monter** si le chauffeur est vérifié par l'opérateur télécom.

### 4.2 Après la course — Le bouclier de sortie (Vérification de fin de trajet)

C'est ici que SafeRide apporte une **plus-value unique et invisible** chez Uber, Bolt ou Yango : la vérification que la course s'est **réellement et normalement** déroulée.

**Problème réel** : Aujourd'hui, si un incident survient pendant une course (détournement, agression, course non effectuée), le passager est seul. L'application VTC ne sait pas que quelque chose s'est mal passé. Elle ne peut pas alerter qui que ce soit en temps réel.

**Solution SafeRide** : À la fin de chaque course, l'IA vérifie automatiquement la cohérence du trajet :

| Signal vérifié | Comment | Déclencheur d'alerte |
| -------------- | ------- | -------------------- |
| Arrivée à destination | Geofencing (position réseau vs destination) | Chauffeur ou passager pas dans le rayon de 200m |
| Itinéraire suivi | Comparaison route réelle vs route prévue | Déviation > 30% ou arrêts suspects |
| Durée vs estimée | Ratio temps réel / temps estimé | Durée anormale (> 2x ou < 0.3x) |
| Connectivité maintenue | Quality on Demand | Chute réseau prolongée = possible zone à risque |
| Position passager | Location Verification (si consentement) | Passager loin de la destination finale |

**Si anomalie détectée → Alerte automatique** :

```
┌─────────────────────────────────────────────────────────────┐
│               SYSTÈME D'ALERTE SAFERIDE                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Anomalie détectée sur course #12345                         │
│  Type : Déviation itinéraire + arrêt suspect 4 min           │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  ALERTE FLOTTE    │  │  ALERTE PERSONNE  │                │
│  │  (si chauffeur    │  │  DE CONFIANCE     │                │
│  │   en flotte)      │  │  (si chauffeur    │                │
│  │                   │  │   indépendant)    │                │
│  │  → SMS/Appel au   │  │  → SMS/Appel au   │                │
│  │    gérant flotte  │  │    contact urgent  │                │
│  │  → Log incident   │  │    du passager    │                │
│  │  → GPS en temps   │  │  → Log incident   │                │
│  │    réel partagé   │  │  → GPS en temps   │                │
│  │                   │  │    réel partagé    │                │
│  └──────────────────┘  └──────────────────┘                │
│                                                              │
│  + Alerte équipe SafeRide Ops (si sévérité CRITICAL)        │
│  + Conservation preuves pour enquête / assurances            │
└─────────────────────────────────────────────────────────────┘
```

**Pourquoi c'est crucial** :
- **Flotte** : Le gérant est alerté en temps réel, peut intervenir ou alerter les autorités. Il a la traçabilité pour les assurances.
- **Personne de confiance** : Le passager désigne un contact (famille, ami) qui reçoit une alerte avec la position GPS en temps réel. Même principe que « Partagez votre trajet » sur Uber, **mais déclenché automatiquement par l'IA** quand une anomalie est détectée — pas manuellement.
- **Preuves légales** : Les données réseau (impossibles à falsifier) servent de preuves en cas de plainte ou enquête policière.

### 4.3 Pendant la course — Monitoring continu

**Quality on Demand**, **Congestion Insights** et **Geofencing** assurent un suivi continu et la détection des anomalies en temps réel, alimentant le bouclier de sortie (section 4.2).

## 5. Différenciation concurrentielle

| Critère                          | Bolt / Uber / Yango   | **SafeRide**                          |
| -------------------------------- | --------------------- | ------------------------------------- |
| Vérification d'identité          | KYC papier            | **KYC réseau via opérateur (CAMARA)** |
| Détection SIM swap               | ❌                     | ✅ (35 % du score)                    |
| Détection GPS truqué             | ❌                     | ✅ (cross-check réseau)               |
| Garantie de connectivité         | Best effort           | ✅ Quality on Demand                  |
| Vérification fin de course       | ❌ (notation seule)   | ✅ IA vérifie cohérence trajet        |
| Alerte automatique si anomalie   | ❌ (partage manuel)   | ✅ flotte ou personne de confiance    |
| Preuves réseau inaltérables      | ❌                     | ✅ données opérateur pour enquêtes    |
| Commission                       | 15 – 25 %             | **8 %**                               |
| Adapté à l'Afrique subsaharienne | Partiel               | ✅ FCFA, langues locales, 2G/3G/4G    |

### 5.1 Pourquoi Uber, Bolt et Yango ne peuvent PAS mettre cela sur pied

C'est la question centrale. La réponse tient en **4 barrières structurelles** :

**1. Conflit d'intérêt — Ils ne peuvent pas être juge et partie**

Uber et Bolt sont des plateformes de mise en relation. Leur modèle repose sur le **volume de courses**. Si elles bloquent un chauffeur pour fraude, elles perdent un revenu. SafeRide, en tant que **tiers de confiance indépendant**, n'a pas ce conflit : on est payé pour la vérification, pas pour le nombre de courses. C'est le même principe qu'un audit externe — l'auditeur est indépendant précisément parce qu'il n'a pas intérêt à cacher les problèmes.

**2. Expertise télécom — Ce n'est pas leur métier**

Uber connaît le transport, le matching passager-chauffeur, le pricing dynamique. Mais intégrer les APIs CAMARA nécessite une expertise télécom profonde : comprendre les flows CIBA vs Authorization Code, gérer le consentement opérateur, optimiser les coûts d'appels API, négocier avec MTN et Orange. C'est un **savoir-faire complètement différent**. C'est comme demander à un constructeur automobile de fabriquer des radars routiers — ce n'est pas son cœur de métier.

**3. Accès opérateur — Ils n'ont pas les partenariats NaC**

Les APIs CAMARA ne sont pas des APIs publiques comme Google Maps. Elles nécessitent des **accords commerciaux avec chaque opérateur** via Nokia Network-as-Code ou l'Open Gateway GSMA. SafeRide se positionne dès le départ comme partenaire des opérateurs (MTN, Orange, Safaricom). Uber n'a pas ces accords et n'a pas vocation à les signer — ils sont du côté « consommateur » du réseau, pas du côté « partenaire infrastructure ».

**4. IA adaptative — L'avantage qui s'auto-renforce**

Même si Uber copiait l'architecture, ils n'auraient pas l'**IA entraînée sur les patterns de fraude africains**. SafeRide accumule des données historiques sur les fraudes par ville, par heure, par opérateur. Plus on a de données, plus l'IA est précise, plus on attire de clients, plus on a de données. C'est un **effet réseau** qui se renforce avec le temps. Uber ne peut pas rattraper ce retard sans repartir de zéro.

**Analogie** : Uber pourrait théoriquement développer son propre système de paiement... mais ils utilisent Stripe. De même, ils pourraient développer leur propre vérification réseau... mais ils utiliseront SafeRide.

### 5.2 L'IA comme plus-value fondamentale

L'IA n'est pas un gadget marketing chez SafeRide — elle est **le cœur du moteur de confiance**. Sans IA, les signaux réseau CAMARA sont juste des données brutes. L'IA les transforme en décisions intelligentes :

| Sans IA (règles fixes) | Avec IA SafeRide (adaptatif) |
| ---------------------- | --------------------------- |
| Règles fixes identiques partout | Pondérations adaptées par ville et contexte |
| Alerte si déviation > 500m | Alerte si déviation anormale **pour ce trajet** (contexte : embouteillages, détour raisonnable) |
| Même score pour tous les chauffeurs | Score pondéré par historique, heure, zone de fraude connue |
| Faux positifs fréquents (30%) | Faux positifs réduits à < 5% par apprentissage continu |
| Pas d'apprentissage | Feedback loop : chaque course alimente le modèle |
| Optimisation API statique | Early stopping dynamique selon le profil chauffeur (économie 25-75%) |

**Les 5 rôles de l'IA dans SafeRide** :

1. **Orchestration intelligente** — L'IA décide l'ordre d'appel des APIs selon la ville, l'heure, l'historique. À Lagos, elle commence par Location Verification (GPS truqué fréquent). À Douala, par SIM Swap (fraude SIM dominante).
2. **Scoring adaptatif** — Les pondérations du Trust Score ne sont pas fixes. L'IA les ajuste en fonction des patterns de fraude observés. Un modèle RandomForest (Phase 1) puis un réseau neuronal (Phase 2) apprennent des incidents passés.
3. **Détection d'anomalies post-course** — L'IA compare le trajet réel au trajet prévu en tenant compte du contexte (circulation, météo, travaux). Elle distingue un détour raisonnable d'une déviation suspecte.
4. **Prédiction de risque** — Avant même que le passager commande, l'IA identifie les zones et les créneaux à risque élevé dans la ville, permettant un pricing de sécurité ou un renforcement du monitoring.
5. **Explicabilité** — Chaque décision de l'IA est accompagnée d'un log explicable (pourquoi ce score, pourquoi cette alerte). C'est crucial pour la confiance des flottes et la conformité réglementaire.

**Barrière à l'entrée** : L'IA SafeRide s'améliore avec les données africaines. Plus de courses = plus de données = IA plus précise = moins de fraude = plus de clients. Un concurrent qui démarre aujourd'hui aura 12-18 mois de retard sur le modèle.

## 6. Modèle économique

Quatre flux de revenus :

1. **Commission par course** — `8 %` du tarif (vs 15–25 % pour Bolt/Uber).
2. **Abonnement Premium chauffeur** — `5 000 FCFA / mois` (encaissé via **Chariow**) : accès prioritaire aux courses à haut score, visibilité boostée, rapport mensuel détaillé, support prioritaire.
3. **Licence B2B SafeRide Trust Score API** — SaaS vendu aux apps logistique, livraison, fintech, santé qui doivent vérifier des prestataires mobiles.
4. **Partenariat opérateur** — Rémunération par l'opérateur mobile pour chaque appel API généré via NaC (modèle Open Gateway).

### 6.1 Architecture B2B SaaS (Mentor Feedback)

SafeRide propose son moteur de confiance en tant que **API SaaS** pour les entreprises qui emploient des prestataires mobiles (livreurs, agents de terrain, chauffeurs) :

**Architecture technique** :
```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT B2B (ex: HelloFood)                │
│  ┌─────────────┐         ┌─────────────┐                   │
│  │ Android App │         │   iOS App   │                   │
│  │  + SDK      │         │   + SDK     │                   │
│  └──────┬──────┘         └──────┬──────┘                   │
└─────────┼──────────────────────┼────────────────────────────┘
          │                      │
          ▼                      ▼
┌─────────────────────────────────────────────────────────────┐
│              SafeRide B2B SDK (Lightweight)                  │
│  • Collecte téléphone anonymisé                            │
│  • Hash SHA-256 (privacy)                                  │
│  • Appel API SafeRide SaaS                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS/TLS 1.3
                       ▼
┌─────────────────────────────────────────────────────────────┐
│               SafeRide SaaS Backend                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   API Key    │  │   Rate       │  │  Billing     │     │
│  │   Auth       │  │   Limiting   │  │  per Call    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐   │
│  │         Trust Score Engine (shared)                 │   │
│  │   (ML model + Nokia NaC integration)                │   │
│  │   • Matrice de décision optimisée                   │   │
│  │   • Early stopping sur fraude évidente              │   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Use cases B2B** :

| Client B2B | Besoin | Intégration |
|------------|--------|-------------|
| **HelloFood/Jumia** | Vérifier livreurs (pas seulement chauffeurs) | SDK livreur app |
| **Pharmacies mobiles** | Livraison médicaments sécurisée | API directe |
| **Banques mobiles** | Vérifier agents field banking | SDK agent |
| **Logistics** | Camions et transport marchandises | API flotte |

**Pricing tiers publics** (endpoint: `GET /b2b/pricing`):

| Tier | Frais mensuel | Par appel | Appels inclus |
|------|---------------|-----------|---------------|
| Starter | 0 € | 0.12 € | 0 |
| Standard | 99 € | 0.08 € | 1 000 |
| Enterprise | 499 € | 0.05 € | 10 000 |

### 6.2 Optimisation des coûts API (Mentor Feedback)

SafeRide implémente une **matrice de décision** pour réduire les coûts API de 25-75% :

**Séquence optimisée** (early stopping) :
1. **SIM Swap** (CIBA) → Si fraude détectée : **STOP** (1 seul appel, économie API)
2. **Device Status** (CIBA) → Continue si étape 1 OK
3. **Location** (CIBA) → Vérifie cohérence position
4. **Number Verify** (Authorization) → Seulement si étapes 1-3 OK

**Matrice des cas** :

| Cas | SIM Swap | Action | APIs appelés | Économie |
|-----|----------|--------|--------------|----------|
| Fraude évidente | Swap récent | **BLOCK** | 1 | 75% |
| Device suspect | Clean | REVIEW | 4 | 0% |
| Location mismatch | Clean | REVIEW | 3 | 25% |
| Conducteur Premium | Clean + historique | **ALLOW** | 1 | 75% |
| Normal | Clean | ALLOW | 4 | 0% |

**Calcul d'économies** (endpoint: `GET /trust-matrix/savings-calculation`):
- 1 000 évaluations, 15% fraude, 20% Premium
- Sans optimisation : 4 000 appels API
- Avec optimisation : ~2 800 appels API
- **Économie : 30%** (soit ~60€/mois à 0.05€/appel)

**Impact sur les revenus** :
- Marge nette augmentée de 15% à 22%
- Compétitivité prix B2B améliorée
- Avantage durable (barrière à l'entrée par l'optimisation algorithmique)

### Hypothèses 12 mois (PDF section 7)

| KPI                          | Cible 12 mois     |
| ---------------------------- | ----------------- |
| Utilisateurs actifs          | **100 000** (3 villes) |
| Taux de fraude               | **< 0,5 %**       |
| NPS                          | **> 70**          |
| Chauffeurs Premium ciblés    | 10 % de la flotte |
| Clients B2B                  | **5** (logistics, delivery) |
| API calls B2B mensuels       | **50 000** |

### 6.3 Revenus B2B projetés

Hypothèses B2B (12 mois) :
- 5 clients Enterprise (499€/mois + 0.05€/appel)
- 10 clients Standard (99€/mois + 0.08€/appel)
- Volume moyen : 5 000 appels/client/mois

```
Revenus Enterprise = 5 × 499 + (5 × 5 000 × 0.05) = 2 495 + 1 250 = 3 745 €/mois
Revenus Standard   = 10 × 99 + (10 × 5 000 × 0.08) = 990 + 4 000 = 4 990 €/mois
TOTAL B2B mensuel = 8 735 € ≈ 5 800 000 FCFA
```

### Calcul indicatif des revenus mensuels (Phase 2)

Hypothèse : 10 000 utilisateurs actifs, 12 courses/mois/utilisateur, panier moyen 2 500 FCFA, 8 % commission, 1 000 chauffeurs Premium.

```
Commission courses = 10 000 × 12 × 2 500 × 0.08 = 24 000 000 FCFA / mois
Abonnements Premium = 1 000 × 5 000          =  5 000 000 FCFA / mois
TOTAL ≈ 29 MFCFA / mois (≈ 44 000 EUR / mois)
```

## 7. Marché cible et roadmap

| Phase    | Période                  | Objectif                                                                |
| -------- | ------------------------ | ----------------------------------------------------------------------- |
| Phase 0  | **24 avr. – 10 mai 2026** | Hackathon : prototype + intégration 5 APIs CAMARA via simulateurs NaC   |
| Phase 1  | Juin – août 2026         | **Pilote Douala** : 500 chauffeurs, partenariat MTN Cameroun, tests réels |
| Phase 2  | Sept. – déc. 2026        | Extension Yaoundé + Lagos, 10 000 utilisateurs, lancement Premium       |
| Phase 3  | 2027                     | Expansion régionale (Dakar, Nairobi, Abidjan), licence B2B Trust Score  |

## 8. Alignement GSMA Open Gateway

| Pilier                             | Comment SafeRide s’y aligne                                          |
| ---------------------------------- | -------------------------------------------------------------------- |
| Pilier 1 — Connectivité avancée    | QoD garantit la continuité de service en 4G/5G                       |
| Pilier 2 — Identité numérique      | SIM Swap + Number Verification créent un KYC réseau natif            |
| Pilier 3 — Innovation ouverte      | Le SDK Nokia NaC permet une intégration en quelques heures           |
| Pilier 4 — Impact local            | FCFA, langues locales, réseaux mixtes 2G/3G/4G                       |

## 9. Équipe & exécution

- Une équipe pluridisciplinaire (mobilité, télécoms, IA agentique, design produit).
- Approche *lean* : MVP fonctionnel en 16 jours, pilote 6 mois, scale en 12 mois.
- Open Source friendly : composants compatibles CAMARA, déployables sur n’importe quel opérateur GSMA.

## 10. Demande d'investissement (Phase 1)

Pour le pilote de Douala :

- **Infrastructure cloud** (PostgreSQL HA + Redis + observabilité)
- **Partenariats opérateurs** (intégration NaC, support 24/7)
- **Acquisition chauffeurs** (campagne ciblée sur les flottes de mototaxis et VTC)
- **Conformité** (DPO, RGPD-like local, certification ISO 27001)
- **Équipe support** (3 city managers à Douala)

Estimé : **120 000 – 180 000 EUR** sur 9 mois.

## 11. Pourquoi maintenant ?

- Les opérateurs africains (MTN, Orange, Safaricom, Vodacom) déploient massivement les APIs CAMARA via Nokia NaC depuis 2024.
- L’adoption des moyens de paiement digitaux (Chariow, Wave, Orange Money) rend possible un onboarding 100 % à distance.
- La GSMA pousse Open Gateway comme la référence mondiale pour les APIs télécoms : SafeRide est une démonstration phare.
- La fraude SIM swap explose (+340 % en 3 ans) : la fenêtre de marché est ouverte.

> *SafeRide ne se contente pas de transporter des passagers : il protège chaque course avant, pendant et après — et transforme chaque trajet en preuve d'identité réseau qu'aucune plateforme VTC ne peut reproduire.*
