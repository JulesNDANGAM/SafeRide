# SafeRide - Workflow Simple (Sans Application Mobile)

## Le Concept en 3 Phrases

1. **SafeRide vérifie les chauffeurs via les opérateurs télécoms** (MTN, Orange) avant chaque course
2. **Le passager utilise le site web** pour voir les chauffeurs disponibles et leur score de confiance
3. **Le chauffeur est informé par SMS/Appel/WhatsApp** quand une course lui est attribuée

---

## Architecture Simple (Web Seulement)

```
┌─────────────────────────────────────────────────────────────┐
│  PASSAGER (Téléphone/Ordinateur)                             │
│  • Ouvre le site SafeRide                                    │
│  • Choisit ville, quartier départ, quartier arrivée          │
│  • Voir la liste des chauffeurs avec leur "Score de Confiance"│
│  • Choisit un chauffeur et clique "Commander"                │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼ (Internet)
┌─────────────────────────────────────────────────────────────┐
│  PLATEFORME SAFERIDE (Backend)                               │
│  • Vérifie le chauffeur auprès de MTN/Orange                 │
│    - SIM Swap ? (vol de carte SIM)                           │
│    - Position réelle ? (GPS truqué ?)                         │
│    - Téléphone correct ?                                    │
│  • Calcule le "Trust Score" (0-100)                          │
│  • Envoie SMS au chauffeur : "Nouvelle course de [Passager]" │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼ (SMS/Appel)
┌─────────────────────────────────────────────────────────────┐
│  CHAUFFEUR (Téléphone basique ou smartphone)                 │
│  • Reçoit SMS : "Course de Akwa vers Bonapriso - 2500 FCFA"  │
│  • Répond par SMS : "OUI" pour accepter ou "NON" pour refuser│
│  • Appelle le passager pour confirmer le lieu précis         │
│  • Pendant la course : SafeRide surveille la position GPS    │
│  • Fin de course : SMS automatique "Course terminée"         │
└─────────────────────────────────────────────────────────────┘
```

---

## Les 3 Scores de Confiance (Très Simple)

Quand le passager voit les chauffeurs, il voit un score et une couleur :

| Score | Couleur | Signification | Action Passager |
|-------|---------|---------------|-----------------|
| **85-100** | 🟢 Vert | Chauffeur vérifié, tout est OK | **Réserver sans souci** |
| **50-84** | 🟡 Orange | Attention, quelque chose est étrange | Peut réserver, mais reste vigilant |
| **0-49** | 🔴 Rouge | Problème détecté (SIM swap, faux GPS, etc.) | **Ne pas réserver** - SafeRide bloque ce chauffeur |

**Comment est calculé le score ?**
SafeRide demande à l'opérateur télécom (MTN/Orange) 4 infos :

1. **SIM Swap** (35% du score) : Est-ce que le chauffeur a changé de carte SIM récemment ? (fraude classique)
2. **Position** (25% du score) : Est-ce que le GPS du téléphone correspond à la vraie position réseau ?
3. **Appareil** (20% du score) : Est-ce que le téléphone est normal ou suspect ?
4. **Numéro** (20% du score) : Est-ce que le numéro appartient bien au chauffeur ?

**Formule simple** :  
`Score = (SIM Swap × 0.35) + (Position × 0.25) + (Appareil × 0.20) + (Numéro × 0.20)`

Exemple : Si SIM Swap = 100 (OK), Position = 80, Appareil = 90, Numéro = 95  
→ Score = (100×0.35) + (80×0.25) + (90×0.20) + (95×0.20) = **35 + 20 + 18 + 19 = 92** ✅

---

## Workflow Détaillé : Du Début à la Fin

### ÉTAPE 1 : Le Chauffeur S'Inscrit (Une Seule Fois)

**Comment ça marche :**
1. Le chauffeur va sur le site SafeRide (ou s'inscrit via un agent)
2. Il remplit : Nom, Numéro de téléphone, Ville, Type de véhicule, Plaque
3. Il donne son **consentement** : "J'autorise SafeRide à vérifier mes infos avec MTN/Orange"
4. SafeRide enregistre ce consentement (valable 12 mois)

**Technique** : C'est l'API **Consent Info** de Nokia NaC qui gère ça.

---

### ÉTAPE 2 : Le Passager Commande une Course

**Ce que voit le passager sur le site :**

```
┌─────────────────────────────────────────┐
│  SafeRide - Commander une course        │
├─────────────────────────────────────────┤
│                                         │
│  Ville : [Douala ▼]                     │
│                                         │
│  Je pars de : [Akwa ▼]                 │
│                                         │
│  Je vais à : [Bonapriso ▼]              │
│                                         │
│  [🔍 Chercher les chauffeurs]           │
│                                         │
└─────────────────────────────────────────┘
```

**Après avoir cliqué "Chercher" :**

```
┌─────────────────────────────────────────┐
│  Chauffeurs disponibles près d'Akwa     │
├─────────────────────────────────────────┤
│                                         │
│  🟢 Amina N. - Toyota Yaris             │
│     Score: 92/100 - Vérifiée           │
│     3 min - 2 500 FCFA                 │
│     [Commander Amina]                  │
│                                         │
│  🟡 Blaise T. - Hyundai Accent         │
│     Score: 65/100 - Attention          │
│     5 min - 2 500 FCFA                 │
│     [Commander Blaise]                 │
│                                         │
│  🔴 Chantal E. - Toyota Corolla        │
│     Score: 35/100 - Bloquée            │
│     Ce chauffeur n'est pas disponible   │
│                                         │
└─────────────────────────────────────────┘
```

**Ce qui se passe en arrière-plan :**
1. SafeRide demande à l'opérateur : "Vérifie le chauffeur drv-101"
2. L'opérateur répond avec les 4 scores (SIM, Position, Appareil, Numéro)
3. SafeRide calcule le score final
4. SafeRide affiche les chauffeurs par ordre de score

---

### ÉTAPE 3 : Le Chauffeur Reçoit la Course

**Parce qu'il n'y a pas encore d'application mobile, on utilise SMS/WhatsApp.**

**SMS envoyé au chauffeur :**
```
SafeRide : Nouvelle course !
De : Akwa
Vers : Bonapriso
Prix : 2 500 FCFA
Passager : Jules N.
Tél : 677123456

Répondez OUI pour accepter
ou NON pour refuser
(dans les 2 minutes)
```

**Si le chauffeur répond OUI :**
- SafeRide envoie au passager : "Amina N. arrive dans 3 min, Toyota Yaris, plaque CE 421 AB"
- La course commence

**Si le chauffeur répond NON ou ne répond pas :**
- SafeRide propose au passager le chauffeur suivant dans la liste

---

### ÉTAPE 4 : Pendant la Course (Surveillance)

**Ce que fait SafeRide automatiquement :**

Toutes les 60 secondes, SafeRide vérifie :
1. **Le chauffeur est-il encore sur la route prévue ?** (Geofencing)
2. **Sa connexion internet est-elle bonne ?** (Quality on Demand)
3. **Y a-t-il des embouteillages ?** (Congestion Insights)

**Si problème détecté :**
- SMS au passager : "Alerte : le chauffeur a quitté l'itinéraire prévu. Vérifiez votre position."
- SMS au chauffeur : "Vous êtes hors trajet. Revenez sur la route principale."

**Le passager peut voir sur le site :**
```
Votre course avec Amina N.
Status : En cours 🟢
Position : En route vers Bonapriso
Temps restant : 5 minutes
Dernière vérification : Il y a 30 secondes
```

---

### ÉTAPE 5 : Fin de Course — Vérification automatique par l'IA

**C'est ici que SafeRide fait ce que personne d'autre ne fait.**

Quand la course se termine, l'IA vérifie **automatiquement** que tout s'est bien passé :

| Ce que l'IA vérifie | Comment | Problème si... |
|---------------------|---------|----------------|
| Le chauffeur est arrivé à destination ? | Geofencing (position réseau) | Pas dans un rayon de 200m |
| L'itinéraire prévu a été suivi ? | Comparaison route réelle vs prévue | Déviation > 30% ou arrêts suspects |
| La durée est normale ? | Ratio temps réel / temps estimé | Trop long (> 2x) ou trop court (< 0.3x) |
| Le passager est à destination ? | Location Verification (si consentement) | Passager loin de l'arrivée |

**Si tout est normal → Course terminée, tout le monde est content.**

**Si anomalie détectée → Alerte automatique :**

```
┌─────────────────────────────────────────────────────────────┐
│  ALERTE AUTOMATIQUE SAFERIDE                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Course #12345 - Anomalie détectée                          │
│  Type : Déviation itinéraire + arrêt suspect                │
│                                                              │
│  ┌─────────────────────┐  ┌─────────────────────┐          │
│  │  CHAUFFEUR EN FLOTTE │  │  CHAUFFEUR INDÉPENDANT│          │
│  │                      │  │                      │          │
│  │  → SMS/Appel au      │  │  → SMS/Appel à la     │          │
│  │    GÉRANT DE FLOTTE  │  │    PERSONNE DE        │          │
│  │  → Position GPS      │  │    CONFIANCE du       │          │
│  │    en temps réel     │  │    PASSAGER           │          │
│  │  → Log pour          │  │  → Position GPS       │          │
│  │    assurances        │  │    en temps réel      │          │
│  └─────────────────────┘  └─────────────────────┘          │
│                                                              │
│  + Alerte SafeRide Ops si sévérité CRITICAL                 │
│  + Preuves réseau conservées (assurances, police)           │
└─────────────────────────────────────────────────────────────┘
```

**Pourquoi c'est différent de Uber/Bolt/Yango ?**

Sur Uber, le passager peut **manuellement** partager son trajet avec un contact. Mais :
- Il faut y penser AVANT le problème
- Si le passager est en danger, il ne peut pas prendre son téléphone
- C'est 100% manuel

Sur SafeRide :
- L'IA détecte le problème **automatiquement**
- L'alerte est envoye **sans action du passager**
- La flotte ou la personne de confiance reçoit la position GPS en temps réel
- Les données réseau sont des **preuves légales** impossibles à falsifier

**Le passager n'a rien à faire. SafeRide veille pour lui.**

---

## Le Business Model Simplifié

SafeRide gagne de l'argent de 4 façons :

### 1. Commission sur chaque course (8%)
- Course à 2 500 FCFA → SafeRide prend 200 FCFA
- Moins que Uber/Bolt (qui prennent 15-25%)

### 2. Abonnement Premium Chauffeur (5 000 FCFA/mois)
- Les chauffeurs payent pour apparaître en haut de la liste
- Ils ont accès aux courses "haut score" en priorité

### 3. Vente de l'API à d'autres entreprises (B2B)
- HelloFood, Jumia, pharmacies qui livrent...
- Payent pour vérifier leurs livreurs avec notre système

### 4. Partenariat avec les opérateurs
- MTN/Orange nous paient quand on utilise leurs APIs

---

## Avantages pour Chacun

### Pour le Passager
- ✅ **Sécurité AVANT** : Les chauffeurs sont vérifiés par les opérateurs télécoms (impossible à truquer)
- ✅ **Sécurité PENDANT** : Alertes si le chauffeur quitte l'itinéraire ou si problème réseau
- ✅ **Sécurité APRÈS** : L'IA vérifie que la course s'est bien passée, alerte automatiquement la personne de confiance si anomalie
- ✅ **Transparence** : Voir le score de confiance avant de monter
- ✅ **Pas besoin d'application** : Fonctionne sur n'importe quel téléphone avec internet

### Pour le Chauffeur
- ✅ **Commission faible** : 8% vs 15-25% chez la concurrence
- ✅ **Pas besoin d'application mobile complexe** : Juste SMS/WhatsApp
- ✅ **Plus de clients** : Les passagers choisissent les chauffeurs avec bon score

### Pour la Société
- ✅ **Moins de fraudes** : Détection automatique des faux chauffeurs
- ✅ **Moins d'agressions** : Vérification d'identité fiable
- ✅ **Emplois locaux** : On travaille avec les opérateurs africains

---

## Questions Fréquentes (FAQ Simple)

**Q : Pourquoi utiliser les opérateurs télécoms ?**  
R : Parce qu'ils ont des données impossibles à falsifier : la vraie position du téléphone via les antennes réseau, l'historique des changements de carte SIM, etc.

**Q : Que se passe-t-il si le chauffeur n'a pas de smartphone ?**  
R : Pas de problème ! Il reçoit des SMS et répond par SMS. Même un téléphone basique suffit.

**Q : Comment SafeRide sait que le chauffeur est vraiment là où il dit ?**  
R : On compare son GPS (qu'il peut truquer) avec la position réseau de l'opérateur (impossible à truquer). Si ça ne correspond pas, on le sait.

**Q : C'est cher d'utiliser les APIs des opérateurs ?**  
R : On a optimisé : si on détecte une fraude évidente au premier test, on s'arrête là. Économie moyenne : 26%.

**Q : Et si l'opérateur ne répond pas ?**  
R : On a un mode "fallback" qui utilise des algorithmes alternatifs (moins précis mais fonctionnels).

**Q : Que se passe-t-il après la course ?**  
R : L'IA vérifie automatiquement que le trajet s'est bien déroulé (itinéraire suivi, arrivée à destination, durée normale). Si anomalie, elle alerte automatiquement la flotte du chauffeur ou la personne de confiance du passager — sans aucune action manuelle.

**Q : C'est quoi la plus-value de l'IA ?**  
R : Sans IA, les signaux réseau sont juste des données brutes. L'IA les rend intelligentes : elle adapte le scoring par ville (Lagos ≠ Douala), distingue un détour raisonnable d'une déviation suspecte, prédit les zones à risque, et optimise les coûts API. C'est ce qui rend SafeRide impossible à copier.

**Q : Pourquoi Uber/Yango ne peut pas faire la même chose ?**  
R : 4 raisons : (1) Conflit d'intérêt — ils gagnent sur le volume de courses, pas la sécurité. (2) Pas d'expertise télécom. (3) Pas d'accès aux APIs CAMARA via Nokia NaC. (4) Pas d'IA entraînée sur les fraudes africaines — notre modèle s'améliore avec les données, c'est un effet réseau.

---

## Pour le Hackathon : Ce Qu'on Démontre

1. **Le site web** où le passager voit les chauffeurs avec leurs scores
2. **Le backend** qui parle aux APIs Nokia NaC (même si c'est en mode simulation pour le hackathon)
3. **La logique de scoring** qui calcule le Trust Score
4. **Le système SMS** (simulé par des notifications web pour la démo)

**Ce qui est réel** : Le backend, les APIs, la logique de scoring.  
**Ce qui est simulé** : Les vraies données opérateur (on utilise des données de test), les vrais SMS (on montre des notifications à l'écran).

---

## Prochaines Étapes Après le Hackathon

| Phase | Quand | Quoi |
|-------|-------|------|
| **1** | Juin 2026 | Pilote à Douala avec 50 chauffeurs réels |
| **2** | Sept 2026 | Application mobile simple pour les chauffeurs (optionnelle) |
| **3** | 2027 | Expansion Yaoundé, Lagos, Dakar |

---

*Document créé pour expliquer simplement SafeRide sans jargon technique*
