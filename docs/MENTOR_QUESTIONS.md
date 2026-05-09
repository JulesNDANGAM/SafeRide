# SafeRide — Questions à poser à mon mentor du hackathon

> Liste organisée par thème pour ta session de mentorat. Pose celles qui ont
> le plus de levier sur ton projet ; n'essaie pas de toutes les poser. Coche
> celles que tu as déjà couvertes.

## 1. Stratégie produit & cadrage

- [ ] Le **scope MVP** que j'ai choisi (7 APIs CAMARA + Trust Score + Chariow + Admin) est-il aligné avec les attentes du jury, ou est-ce trop large pour un hackathon ?
- [ ] Quelles parties dois-je **mettre le plus en avant** dans la démo de 5 minutes : la formule du score ? le monitoring temps réel ? le back-office ? la roadmap business ?
- [ ] Vaut-il mieux **simplifier le pitch** (1 problème, 1 solution, 1 chiffre) ou **densifier** (montrer la profondeur technique) face au jury Africa Ignite ?
- [ ] Mon **différenciateur principal** doit-il être positionné comme « moteur de confiance » ou comme « plateforme VTC sécurisée » ? Quel angle parle le mieux au jury ?
- [ ] Y a-t-il un **cas d'usage** (passager, chauffeur, opérateur, B2B) que je devrais retirer pour éviter de diluer le message ?

## 2. Critères d'évaluation Africa Ignite

- [ ] Sur les critères publiés (impact, applicabilité NaC, plusieurs APIs, résolution du problème), **lequel pèse réellement le plus** dans la notation finale ?
- [ ] Comment maximiser le score « *Did the team use several different APIs ?* » : faut-il **démontrer 7 APIs** ou en **approfondir 3-4** avec des cas d'usage très concrets ?
- [ ] Y a-t-il des **critères implicites** (qualité de la démo, originalité, faisabilité business) au-delà de ceux affichés ?
- [ ] La **phase Onsite Prototype** (s'il y a finale) impose-t-elle des critères différents (live coding, intégration réelle Nokia NaC, etc.) ?

## 3. Intégration Nokia Network-as-Code

- [ ] Aurai-je accès à des **clés sandbox Nokia NaC** pendant le hackathon, et comment les obtenir rapidement ?
- [ ] Les juges Nokia attendent-ils de voir **un appel API réel** dans la démo ou est-ce qu'un mock fidèle aux signatures CAMARA suffit ?
- [ ] Est-il pertinent d'utiliser le SDK Python `network-as-code` officiel pour la démo, ou rester sur des appels REST simples ?
- [ ] Quelles APIs Nokia NaC sont **les plus impressionnantes pour le jury** au-delà de SIM Swap (qui est un classique) ? *Geofencing live* ? *QoD session démo* ?
- [ ] Pour la **Phase 1 (pilote Douala)**, peut-on obtenir un partenariat formel avec MTN Cameroon et Nokia, et combien de temps cela prend-il ?

## 4. Architecture technique

- [ ] L'architecture **FastAPI + React + in-memory** est-elle suffisante pour le jury, ou dois-je impérativement brancher **PostgreSQL** avant la finale ?
- [ ] Comment **prouver que ça scale** (100 000 utilisateurs visés à 12 mois) sans avoir le temps de faire du load-testing pendant le hackathon ?
- [ ] Pour le **Trust Agent agentique**, vaut-il mieux rester sur l'orchestrateur déterministe actuel ou tenter une intégration LLM (Ollama / Llama 3) en démo ?
- [ ] Comment positionner techniquement **les 3 APIs non-mandatory** (QoD, Congestion, Geofencing) pour qu'elles **n'apparaissent pas comme du bonus** mais comme des piliers du monitoring ?
- [ ] Mon code est-il **suffisamment lisible** pour qu'un juge senior tech puisse le parcourir en 2 min et comprendre la valeur ?

## 5. Modèle économique & business

- [ ] La **commission 8 %** vs 15-25 % Bolt/Uber est-elle crédible, ou trop agressive face aux coûts CAMARA réels ?
- [ ] Le prix **5 000 FCFA / mois Premium** correspond-il vraiment à la *willingness to pay* d'un chauffeur de mototaxi à Douala ?
- [ ] Les opérateurs (MTN, Orange) sont-ils prêts à **partager des revenus** sur les appels CAMARA, et quel ordre de grandeur est réaliste ?
- [ ] Le marché **B2B Trust Score API** (fintech, livraison, santé) est-il réellement adressable avec 1 produit et 1 équipe en Phase 2 ?
- [ ] Quel est le **funding minimal réaliste** pour le pilote Douala : 120 k€ comme estimé, ou plus / moins ?
- [ ] Y a-t-il des **compétiteurs émergents** (européens, indiens, américains) qui font la même chose en Afrique sub-saharienne et que je devrais citer (ou éviter de citer) ?

## 6. Pitch & présentation

- [ ] La **structure de mon PPT** (problème → solution → archi → business → équipe → valeur → APIs → roadmap) est-elle la bonne pour le jury Africa Ignite ?
- [ ] Faut-il **commencer par une statistique choc** (+340 % SIM swap), par la **démo live**, ou par la **vision** ?
- [ ] Sur 5 minutes de pitch, **combien de temps consacrer à la démo live** vs slides ? Y a-t-il un format imposé (Demo Day vs Pitch classique) ?
- [ ] Comment **gérer une question piège** du jury : « Pourquoi pas Bolt + une option SafeRide ? » ou « Et si Nokia NaC n'est pas adopté en Afrique ? »
- [ ] Faut-il que je **prépare un Plan B** au cas où la connexion ne tienne pas pendant la démo live (vidéo enregistrée + screenshots) ?

## 7. Équipe & rôles

- [ ] Faut-il que je **présente une équipe de 3-5 personnes** (même fictives sur certains rôles) ou puis-je pitcher en solo ?
- [ ] Quels **profils manquants** sont rédhibitoires aux yeux des investisseurs (Telco partnership ? Data scientist ? Local ops ?) ?
- [ ] À quel moment faut-il recruter le **partner opérateur** (avant le pitch ? après une LOI ? après le pilote ?) ?
- [ ] Comment **valoriser mon profil** (en tant que dev solo) face à des équipes qui ont déjà 5 cofounders ?

## 8. Sécurité & conformité

- [ ] Quels sont les **risques réglementaires** majeurs en Afrique sub-saharienne (Cameroun, Nigeria, Kenya, Sénégal) sur la collecte de données réseau ?
- [ ] Faut-il un **agrément ART / NCC / ARTP** avant de pouvoir consommer les APIs CAMARA en production ?
- [ ] Comment se positionner sur la **vie privée du passager** sans alourdir le pitch ?
- [ ] La conformité **CDP / NDPR / DPA / DDPR** est-elle un frein ou un avantage compétitif (KYC réseau natif vs KYC papier) ?

## 9. Démo

- [ ] Si je dois **enregistrer une vidéo de démo** de 90 s, quels écrans choisir : passager+map ? simulation d'alerte critique ? admin KPIs ? Premium Chariow ?
- [ ] Faut-il préparer **2 versions de la démo** (live + secours préenregistrée) ?
- [ ] La **navigation FR/EN** doit-elle être démontrée, ou est-ce considéré comme du polish ?
- [ ] Faut-il **scripter la démo au mot près** ou rester en improvisation ?

## 10. Après le hackathon

- [ ] Si je gagne / suis finaliste, **quelles ressources Nokia / GSMA** deviennent accessibles automatiquement ?
- [ ] Comment **transformer le réseau du hackathon** en partenariats opérateurs réels (mailing post-évent ? side meetings ?) ?
- [ ] Faut-il **ouvrir le code sur GitHub** dès la fin du hackathon pour la visibilité, ou rester en privé pour préserver l'IP ?
- [ ] Quelle est la **fenêtre optimale** entre la fin du hackathon et le démarrage du pilote Douala (3 mois ? 6 mois ?) ?
- [ ] Le mentor a-t-il un **contact direct chez Nokia / MTN / Orange** qu'il peut me présenter après le hackathon ?

## 11. Questions plus personnelles / mentorat

- [ ] Quelles sont **les 3 erreurs** que tu vois le plus souvent chez les participants Africa Ignite, que je devrais éviter ?
- [ ] Sur quoi devrais-je **passer le moins de temps** dans les 48 h restantes (et que je risque de sur-investir) ?
- [ ] Tu as vu mon code et ma doc — quelle est la **plus grosse faiblesse** non encore traitée ?
- [ ] Si tu étais à ma place, **quel serait ton plan d'action** pour les 24 h précédant le pitch ?
- [ ] Quel **conseil clé** donnerais-tu à un dev solo qui pitche un projet d'infrastructure mobilité pour la première fois ?

---

## Annexe — Comment utiliser cette liste

1. **Sélectionne 5 à 8 questions** par session (sinon tu manques de temps).
2. **Priorise** selon le moment :
   - **Avant le pitch** : sections 1, 2, 6, 9.
   - **Pendant le développement** : sections 3, 4.
   - **Après une session de feedback** : sections 5, 7, 11.
   - **Après le hackathon** : section 10.
3. Note les **réponses du mentor** directement sous chaque question (en commentaire ou dans un cahier).
4. **Recroise** ses réponses avec le PDF d'idéation et la doc `BUSINESS.md` / `TECHNICAL.md` pour rester cohérent.

> Le mentor n'est ni un juge ni un code reviewer. Sa valeur réside dans
> son réseau, son expérience des pitch et sa connaissance fine des
> attentes du jury. Use ton temps avec lui pour les questions à fort levier.
