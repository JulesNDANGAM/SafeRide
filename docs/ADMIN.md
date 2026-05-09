# SafeRide — Manuel administrateur

## 1. Connexion

Le back-office est accessible depuis l’onglet **Admin** de l’interface principale.

1. Saisir le token administrateur (`SAFERIDE_ADMIN_TOKEN`).
2. Le token est validé via `GET /admin/login` puis stocké dans `localStorage` (clé `saferide.admin.token`).
3. Cliquer sur **Déconnexion** pour purger le token.

> ⚠️ Le token par défaut `saferide-admin-dev` doit absolument être changé en production via la variable d’environnement `SAFERIDE_ADMIN_TOKEN`.

## 2. Vue d'ensemble (KPIs)

En tête du tableau de bord :

| KPI                | Définition                                                          |
| ------------------ | ------------------------------------------------------------------- |
| Chauffeurs         | Nombre total de chauffeurs enregistrés                              |
| Score moyen        | Moyenne des Network Trust Score (toutes villes)                     |
| Bloqués            | Chauffeurs en statut `blocked` (score < 40)                         |
| Courses            | Total des courses (toutes statuts confondus)                        |
| Abonnés actifs     | Nombre d’abonnements `active`                                       |
| MRR (XAF)          | Somme des prix mensuels des abonnements actifs                      |

## 3. Onglet **Chauffeurs**

- Liste complète avec score, ville, opérateur, véhicule, plaque.
- Boutons :
  - **+ Ajouter un chauffeur** ouvre un formulaire (nom, téléphone, opérateur, ville, véhicule, plaque, GPS, position réseau, statut device, congestion, etc.).
  - **Modifier** ouvre le même formulaire pré-rempli.
  - **Supprimer** retire le chauffeur (confirmation requise).
- Champs sensibles :
  - `device_status` : `healthy` / `unknown` / `suspicious`
  - `sim_swap_recent` : marque le chauffeur comme suspect SIM swap (force score `0` sur cette dimension)
  - `inside_geofence` : si décoché, le moteur Geofencing alerte automatiquement
  - `quality_on_demand_ready` : nécessaire pour autoriser le suivi temps réel

## 4. Onglet **Courses**

Liste des courses observées (toutes villes). Pour chaque course :

- ID + nom du passager
- Ville + chauffeur attribué
- Cycle de monitoring courant
- Tarif (XAF)
- Statut (`in_progress` / `completed`)

## 5. Onglet **Abonnements**

Liste des abonnements Premium chauffeur (Chariow).

| Statut       | Signification                                       |
| ------------ | --------------------------------------------------- |
| `pending`    | L’iframe Chariow est ouverte, paiement en attente   |
| `active`     | Webhook Chariow reçu avec succès                    |
| `cancelled`  | Annulé par admin ou via Chariow                     |
| `expired`    | Échec de paiement, paiement rejeté                  |

Le bouton **Annuler l'abonnement** envoie `POST /admin/subscriptions/{id}/cancel`.

## 6. Bonnes pratiques

- **Ne pas partager** le token admin par e-mail ou messagerie non sécurisée.
- **Roter** régulièrement le token (`SAFERIDE_ADMIN_TOKEN`) et redéployer le backend.
- En cas de fuite, désactiver immédiatement le token et vérifier les logs (`/admin/*`).
- Configurer la **signature HMAC** Chariow dès que possible.
- En production, déployer derrière HTTPS uniquement.

## 7. Réinitialiser les données (MVP en mémoire)

Tant que la base PostgreSQL n’est pas branchée (Phase 1), les données se trouvent en mémoire dans le processus uvicorn. Redémarrer le backend = repartir des données seed (`backend/app/store.py::seed_drivers`).

## 8. Évolutions futures

- Pages dédiées par chauffeur (timeline d’événements de fraude, historique des courses)
- Pages par passager (KYC réseau via Number Verification)
- Rôles fins (`admin` / `ops` / `support` / `finance`)
- Audit log immuable (qui a modifié quoi)
- Export CSV / Parquet pour le data warehouse
