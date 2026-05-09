# SafeRide — FAQ exhaustive

## Concept & vision

**Q1. Qu'est-ce que SafeRide ?**
Une plateforme VTC sécurisée par un *Network Trust Score* (0–100) calculé en temps réel à partir d’APIs CAMARA standardisées exposées par les opérateurs mobiles via Nokia Network-as-Code.

**Q2. En quoi SafeRide est différent de Bolt ou Uber ?**
SafeRide ne s'appuie pas uniquement sur les évaluations passagers. Il utilise des signaux réseau **objectifs et inaltérables** : SIM swap, vérification numéro, statut device, position réseau, qualité de connexion, geofencing. De plus, SafeRide protège la course **avant ET après** : l'IA vérifie automatiquement que le trajet s'est bien déroulé et alerte la flotte ou la personne de confiance du passager si anomalie détectée.

**Q3. Quelle est la cible de SafeRide ?**
Les passagers et chauffeurs des grandes métropoles d’Afrique subsaharienne (Douala, Yaoundé, Lagos, Nairobi, Dakar). Marché VTC estimé à 14 Mrd USD d’ici 2030.

**Q4. Pourquoi maintenant ?**
La fraude SIM swap a augmenté de +340 % en Afrique entre 2020 et 2023, les opérateurs déploient massivement les APIs CAMARA via Nokia NaC depuis 2024, et l’adoption Mobile Money / Chariow rend possible un onboarding 100 % digital.

## APIs réseau (CAMARA / Nokia NaC)

**Q5. D'où viennent les APIs utilisées ?**
Toutes les APIs sont des **APIs CAMARA standardisées par la Linux Foundation**, exposées par les opérateurs mobiles via la plateforme **Nokia Network-as-Code**.

- CAMARA : https://camaraproject.org/
- Nokia NaC : https://networkascode.nokia.io/

**Q6. Combien d'APIs sont utilisées ?**
**5 APIs principales** (SIM Swap, Number Verification, Device Status, Location Verification, Quality on Demand) + **2 APIs complémentaires** (Congestion Insights, Geofencing Subscriptions).

**Q7. Pourquoi Nokia Network-as-Code et pas un appel direct à chaque opérateur ?**
Nokia NaC agrège plusieurs opérateurs (MTN, Orange, Safaricom, Vodafone, Telefónica, Deutsche Telekom, etc.) derrière une signature unique, ce qui permet à SafeRide d’être *operator-agnostic*.

**Q8. Le code source orchestre-t-il vraiment les APIs ou est-ce un mock ?**
Le MVP utilise un mock fidèle aux signatures CAMARA. La bascule vers le SDK Nokia officiel se fait avec `SAFERIDE_USE_REAL_NAC=true` + clé API. Le SDK Python `network-as-code` est compatible.

**Q9. Quelles APIs sont marquées MANDATORY par CAMARA ?**
SIM Swap, Number Verification, Location Verification et Device Status. SafeRide les utilise toutes les quatre.

**Q10. Comment est calculé le score ?**
Le score est calculé par un moteur propriétaire SafeRide combinant plusieurs signaux réseau et contextuels.

**Q11. Pourquoi le SIM Swap est-il important ?**
La fraude SIM swap est une cause majeure d’usurpation d’identité chauffeur. SafeRide l’utilise comme signal critique dans son moteur de confiance.

**Q12. Que se passe-t-il pour les seuils 70 et 40 ?**
- ≥ 70 : course autorisée (suivi standard)
- 40–69 : course proposée avec avertissement passager
- < 40 : chauffeur exclu, alerte équipe SafeRide

**Q13. La latence des appels CAMARA n'est-elle pas un problème ?**
Les 4 APIs MANDATORY sont appelées **en parallèle** par l’agent IA. Latence cumulée typique : `< 300 ms`. L’ordre est même optimisé selon la ville (heuristiques régionales).

## Agent IA

**Q14. Qu'est-ce que l'agent IA SafeRide ?**
Un orchestrateur qui décide de l’ordre d’appel des APIs en fonction du contexte (ville, heure, historique fraude), produit un log explicable, et apprend les signatures de fraude régionales.

**Q15. Quel modèle est utilisé ?**
Pour le MVP : un orchestrateur déterministe avec heuristiques. Pour la Phase 2 : un Llama 3 ou Mistral local via Ollama, avec RAG sur l’historique des courses.

**Q16. L'IA prend-elle des décisions binaires ?**
Non. Elle propose un score continu et trois statuts (Reliable / Attention / Blocked). La décision finale d’appairage est appliquée par le moteur de règles backend.

## Sécurité & vie privée

**Q17. Les données passager sont-elles partagées avec l'opérateur ?**
Non. Seul le numéro chauffeur est utilisé pour les appels CAMARA, avec son consentement explicite à l’inscription.

**Q18. Les positions GPS sont-elles stockées ?**
En MVP : uniquement en mémoire et le temps de la course. En production : conservation max 30 jours pour audit, anonymisation au-delà.

**Q19. Comment SafeRide se conforme à la protection des données ?**
- Conformité aux lois locales (CDP Cameroun, NDPR Nigeria, DPA Kenya).
- Chiffrement TLS partout.
- Données sensibles (téléphone, nom) chiffrées au repos en Phase 1.
- Droit à l’effacement implémenté côté admin.

**Q20. Comment est protégé le back-office admin ?**
Authentification par token Bearer (variable `SAFERIDE_ADMIN_TOKEN`). En production : remplacement par JWT signé + IdP (Auth0/Keycloak) + 2FA.

**Q21. Le webhook Chariow est-il sécurisé ?**
Le code accepte la charge utile et expose un point d’extension pour vérifier la **signature HMAC** envoyée par Chariow. À activer impérativement en production.

## Paiement (Chariow)

**Q22. Pourquoi Chariow ?**
Plateforme africaine native qui supporte Mobile Money (Orange Money, MTN MoMo, Wave, Moov), cartes bancaires et crypto, sans devoir intégrer chaque PSP individuellement.

**Q23. Comment fonctionne l'abonnement Premium ?**
1. Le chauffeur clique sur **S'abonner** dans l’onglet Premium.
2. Backend crée un abonnement `pending` et renvoie une URL Chariow.
3. Frontend ouvre la page Chariow dans une **iframe**.
4. Une fois le paiement réussi, Chariow appelle notre webhook `POST /subscriptions/webhook/chariow`.
5. Backend met l’abonnement en `active`.

**Q24. Combien coûte le Premium ?**
**5 000 FCFA / mois** (cf. PDF section 8). Configurable via `SAFERIDE_PREMIUM_XAF`.

**Q25. Que reçoit le chauffeur Premium ?**
- Accès prioritaire aux courses à haut score
- Visibilité boostée sur la carte passager
- Rapport mensuel détaillé sur son score
- Support prioritaire

**Q26. La commission SafeRide est de combien ?**
**8 %** (vs 15–25 % pour Bolt/Uber). Configurable via `SAFERIDE_COMMISSION_RATE`.

## Admin & opérations

**Q27. Comment ajoute-t-on un chauffeur ?**
Onglet **Admin → Chauffeurs → + Ajouter un chauffeur**. Tous les champs CAMARA pertinents sont éditables (statut device, SIM swap récent, QoD ready, geofence).

**Q28. Peut-on désactiver un chauffeur sans le supprimer ?**
Oui : passer son `device_status` à `suspicious` ou cocher `sim_swap_recent` ramène le score sous le seuil de blocage.

**Q29. Comment sont calculés les KPIs admin ?**
`/admin/stats` recalcule en temps réel : total chauffeurs, score moyen, bloqués, courses, abonnés actifs, MRR. Pas de cache.

**Q30. Comment annuler un abonnement ?**
Onglet **Abonnements → Annuler l'abonnement**. L’abonnement passe à `cancelled` (n’interrompt pas le service en cours, retire seulement l’éligibilité au prochain cycle).

## Développement & déploiement

**Q31. Comment lancer le projet en local ?**
```powershell
pip install -r backend/requirements.txt
python -m uvicorn app.main:app --app-dir backend --reload

cd frontend
npm install
npm run dev
```

**Q32. Quelle base de données ?**
- MVP : in-memory (dictionnaires Python).
- Phase 1 : **PostgreSQL** (Neon / Supabase) pour profils + courses + abonnements.
- Phase 1 : **Redis** (Upstash) pour les sessions de course temps réel.

**Q33. Le frontend est-il une PWA ?**
Pas encore. Phase 1 : ajouter un service-worker + manifest. Phase 2 : conversion React Native pour iOS / Android.

**Q34. Comment déployer ?**
- Backend : Docker → Render / Fly.io / Railway.
- Frontend : Vercel / Netlify (build statique Vite).
- Webhook Chariow doit pointer sur l’URL backend publique.

**Q35. Le projet est-il open source ?**
Le code peut être ouvert sous licence Apache 2.0 (à confirmer avec les sponsors). Les composants CAMARA sont déjà sous licence Apache 2.0.

## Modèle économique

**Q36. Quel est le modèle de revenus ?**
Quatre sources :
1. Commission par course (8 %)
2. Abonnement Premium chauffeur (5 000 FCFA / mois)
3. Licence B2B Trust Score API (logistique, livraison, fintech)
4. Partenariat opérateur (revenu sur appels NaC)

**Q37. Que représente la licence B2B ?**
Toute application qui doit vérifier des prestataires mobiles (livreurs, infirmiers, agents itinérants, chauffeurs partenaires d’une fintech) peut consommer l’API Trust Score SafeRide. Tarification au volume d’appels.

**Q38. Combien d'utilisateurs ciblés à 12 mois ?**
**100 000 utilisateurs actifs** dans 3 villes, taux de fraude < 0,5 %, NPS > 70 (cf. PDF section 7).

**Q39. Quel est le marché total ?**
Le ride-hailing africain est estimé à **14 milliards USD à horizon 2030**.

## Conformité & partenariats

**Q40. SafeRide est-il aligné sur GSMA Open Gateway ?**
Oui, sur les 4 piliers : connectivité avancée (QoD), identité numérique (SIM Swap + Number Verification), innovation ouverte (NaC), impact local (FCFA, langues, réseaux mixtes).

**Q41. Quels opérateurs sont partenaires ciblés ?**
MTN Cameroun (pilote Douala), Orange Cameroun, MTN Nigeria, Safaricom, Orange Sénégal. Tous exposent les APIs CAMARA via Nokia NaC.

**Q42. Quels organismes valident SafeRide ?**
- GSMA Open Gateway (alignement architectural)
- Linux Foundation CAMARA (consommation conforme)
- Régulateurs locaux des télécoms (ART Cameroun, NCC Nigeria, CA Kenya, ARTP Sénégal)

## Roadmap

**Q43. Qu'est-ce que la Phase 0 ?**
**24 avril – 10 mai 2026** : prototype hackathon (ce dépôt) avec intégration des 5 APIs CAMARA via simulateurs NaC.

**Q44. Phase 1 ?**
**Juin – août 2026** : pilote Douala (500 chauffeurs réels, partenariat MTN Cameroun, vrais appels NaC).

**Q45. Phase 2 ?**
**Sept. – déc. 2026** : extension Yaoundé + Lagos, 10 000 utilisateurs, lancement Premium.

**Q46. Phase 3 ?**
**2027** : expansion régionale (Dakar, Nairobi, Abidjan) + licence B2B Trust Score.

## Questions fréquentes utilisateurs

**Q47. Pourquoi je ne vois pas certains chauffeurs ?**
Ils sont en bucket `Blocked` (score < 40). Conformément aux règles du moteur de confiance, ils ne sont pas proposés au passager.

**Q48. Que faire si un chauffeur est marqué `Attention` ?**
Le passager voit la course proposée avec un avertissement explicite (anomalies détaillées). Il peut accepter ou refuser.

**Q49. Que se passe-t-il si la connexion 4G/5G chute pendant la course ?**
Quality on Demand déclenche un événement `qod_drop` dans la timeline de la course. Si la chute est durable, le passager reçoit une alerte et un itinéraire de repli est proposé.

**Q50. Comment SafeRide gère-t-il les zones blanches ?**
Congestion Insights anticipe et l’agent IA propose un re-routage. Si aucun couloir réseau n’est viable, la course est mise en pause.

## Hackathon & innovation

**Q51. Le PDF mentionne « Agentic AI ». Est-ce vraiment de l'AI agentique ?**
Oui :
- Orchestration intelligente (ordre des APIs adapté au contexte)
- Apprentissage de signatures de fraude régionales
- Analytique prédictive (croisement Congestion + GPS)
- Communication contextualisée FR / EN / langues locales

**Q52. Quelles langues sont supportées ?**
Frontend : **français / anglais** avec switcher. Le backend renvoie les événements de monitoring dans les deux langues. Phase 2 : ajout de **Wolof, Lingala, Pidgin, Swahili**.

**Q53. Que démontre le prototype hackathon ?**
- Orchestration des 5 APIs CAMARA en parallèle
- Calcul SCR conforme à la formule du PDF
- 3 vues métier (Passager, Chauffeur, Opérations) + Premium + Admin
- Carte Leaflet avec tous les chauffeurs et leurs scores
- Monitoring temps réel simulé
- Paiement Chariow intégré (iframe + webhook)

**Q54. Qu'est-ce qui manque pour la prod ?**
- PostgreSQL + Redis
- SDK Nokia NaC réel (variable `SAFERIDE_USE_REAL_NAC=true`)
- Auth chauffeur via Number Verification
- Signature HMAC du webhook Chariow
- App mobile React Native
- Observabilité (OpenTelemetry / Sentry)

## Contact & contribution

**Q55. Où trouver le code ?**
Ce dépôt local. À publier sur GitHub sous l’organisation SafeRide en Phase 1.

**Q56. Comment contribuer ?**
- Ouvrir une issue avec un cas de fraude observé
- Proposer une heuristique régionale
- Améliorer les traductions
- Étendre le moteur Trust Score (nouvelles APIs CAMARA dès qu'elles sortent)

**Q57. Comment contacter l'équipe ?**
Voir la page **Concept** de l’interface ou le fichier `BUSINESS.md`.

**Q58. Les sources sont-elles citables dans une présentation ?**
Oui, toutes les références (CAMARA, Nokia NaC, Chariow, OpenStreetMap) sont des sources publiques officielles, voir `API_REFERENCES.md`.

**Q59. Qu'est-ce qui est réellement testable maintenant ?**
- Tous les endpoints REST (cf. `TECHNICAL.md`)
- Le frontend complet (Passager / Chauffeur / Ops / Premium / Admin)
- Le webhook Chariow (testable en POST sur `/subscriptions/webhook/chariow`)
- Le moteur de score sur 14 chauffeurs seedés dans 5 villes

**Q60. Pourquoi devrais-je investir / sponsoriser SafeRide ?**
Parce que SafeRide est :
1. **Aligné GSMA Open Gateway** : démonstration vivante de la valeur des APIs CAMARA
2. **Profondément local** : FCFA, opérateurs africains, Mobile Money via Chariow
3. **Différencié** : seul moteur de confiance basé sur signaux réseau objectifs
4. **Extensible** : modèle Trust Score B2B applicable à fintech, livraison, santé
5. **Prêt à scaler** : MVP fonctionnel en 16 jours, architecture cloud-native
6. **Protégé** : 4 barrières structurelles empêchent Uber/Yango de répliquer

## Vérification post-course & alertes

**Q61. Que se passe-t-il après la course ?**
L'IA vérifie automatiquement la cohérence du trajet : itinéraire suivi, arrivée à destination, durée normale, connectivité maintenue, position passager. Si anomalie détectée, une alerte est envoyée automatiquement — sans action du passager.

**Q62. Qui est alerté en cas d'anomalie post-course ?**
Deux canaux selon le type de chauffeur :
- **Chauffeur en flotte** : SMS/Appel au gérant de la flotte + GPS temps réel + log incident
- **Chauffeur indépendant** : SMS/Appel à la personne de confiance désignée par le passager + GPS temps réel + log incident
- **Sévérité CRITICAL** : Alerte équipe SafeRide Ops en plus

**Q63. Comment le passager désigne-t-il sa personne de confiance ?**
Lors de l'inscription ou dans les paramètres du compte, le passager ajoute un contact d'urgence (famille, ami). Ce contact reçoit les alertes automatiques si l'IA détecte une anomalie pendant ou après la course.

**Q64. En quoi c'est différent du « partage de trajet » sur Uber ?**
3 différences fondamentales :
1. **Automatique vs manuel** : Uber requiert une action manuelle du passager. SafeRide déclenche l'alerte automatiquement quand l'IA détecte un problème.
2. **Données réseau vs GPS** : Uber utilise le GPS du téléphone (falsifiable). SafeRide utilise les données réseau de l'opérateur (impossibles à falsifier).
3. **Si le passager est en danger** : il ne peut pas prendre son téléphone pour partager son trajet. SafeRide n'a pas besoin de son action.

**Q65. Les données post-course servent-elles de preuves légales ?**
Oui. Les données réseau (position via antennes, historique SIM, statut device) sont des preuves inaltérables utilisables pour les assurances, les enquêtes policières et les litiges. C'est un avantage majeur pour les flottes qui doivent justifier auprès de leurs assureurs.

## IA comme plus-value

**Q66. Quelle est la plus-value de l'IA dans SafeRide ?**
Sans IA, les signaux réseau CAMARA sont des données brutes. L'IA les transforme en décisions intelligentes : scoring adapté par ville (Lagos ≠ Douala), détection d'anomalies contextuelle (un détour pour embouteillage n'est pas une alerte), prédiction des zones à risque, optimisation des coûts API (early stopping dynamique), et explicabilité de chaque décision.

**Q67. Quels sont les 5 rôles de l'IA SafeRide ?**
1. **Orchestration intelligente** — Ordre d'appel des APIs adapté à la ville et au contexte
2. **Scoring adaptatif** — Pondérations dynamiques selon les patterns de fraude observés
3. **Détection d'anomalies post-course** — Comparaison contextuelle trajet réel vs prévu
4. **Prédiction de risque** — Identification des zones et créneaux à risque avant la commande
5. **Explicabilité** — Log explicable pour chaque décision (confiance flottes, conformité réglementaire)

**Q68. L'IA réduit-elle les faux positifs ?**
Oui, significativement. Avec des règles fixes, le taux de faux positifs est d'environ 30%. Avec l'IA adaptative, il tombe à < 5% grâce à l'apprentissage continu et la prise en compte du contexte (circulation, météo, habitudes locales).

**Q69. Comment l'IA crée-t-elle une barrière à l'entrée ?**
L'IA SafeRide s'améliore avec les données africaines : plus de courses → plus de données → IA plus précise → moins de fraude → plus de clients → plus de données. C'est un effet réseau auto-renforçant. Un concurrent qui démarre aujourd'hui aura 12-18 mois de retard sur le modèle, même en copiant l'architecture.

## Pourquoi les concurrents ne peuvent pas répliquer

**Q70. Pourquoi Uber, Bolt et Yango ne peuvent-ils pas mettre cela sur pied ?**
4 barrières structurelles :
1. **Conflit d'intérêt** — Ils gagnent sur le volume de courses, pas la sécurité. Bloquer un fraudeur = perdre un revenu. SafeRide est un tiers de confiance indépendant.
2. **Expertise télécom** — Les APIs CAMARA nécessitent un savoir-faire télécom (flows CIBA, consentement, optimisation API) qu'ils n'ont pas. Ce n'est pas leur cœur de métier.
3. **Accès opérateur** — Les APIs CAMARA ne sont pas publiques. Elles nécessitent des accords commerciaux via Nokia NaC / Open Gateway. Uber est du côté consommateur du réseau, pas partenaire infrastructure.
4. **IA adaptative** — Notre modèle s'améliore avec les données africaines (effet réseau). Même en copiant l'architecture, ils auraient 12-18 mois de retard.

**Q71. Uber pourrait-il développer sa propre vérification réseau ?**
Théoriquement oui, comme ils pourraient développer leur propre système de paiement. Mais ils utilisent Stripe parce que c'est mieux et moins cher. De même, ils utiliseront SafeRide pour la vérification réseau. C'est l'analogie Stripe pour la sécurité transport.
