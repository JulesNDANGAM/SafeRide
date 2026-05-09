# SafeRide — Références des APIs externes

Toutes les APIs réseau orchestrées par SafeRide sont des **APIs CAMARA** (standardisées par la **Linux Foundation**) consommées via la plateforme **Nokia Network-as-Code (NaC)**. La couche paiement est fournie par **Chariow**.

## 1. CAMARA Project (Linux Foundation)

CAMARA est l’initiative open-source qui standardise les APIs des opérateurs mobiles (GSMA Open Gateway). Tous les opérateurs partenaires (MTN, Orange, Safaricom, Vodacom, Telefónica, Deutsche Telekom, etc.) exposent les mêmes signatures d’API.

- Site officiel : https://camaraproject.org/
- GitHub : https://github.com/camaraproject
- Releases stables : https://camaraproject.org/2025/10/07/camara-the-global-telco-api-alliance-issues-its-latest-meta-release-of-stable-network-apis-advancing-api-interoperability/

## 2. Nokia Network-as-Code (NaC)

Plateforme et SDK officiels qui agrègent les APIs CAMARA de plusieurs opérateurs derrière une interface unifiée.

- Portail développeur : https://networkascode.nokia.io/
- Site corporate : https://www.nokia.com/programmable-networks/network-as-code/
- Exemple Device Swap (basé sur CAMARA) : https://networkascode.nokia.io/_docs/device-swap/device-swap
- SDK Python : `pip install network-as-code`

### Activer le SDK réel dans SafeRide

Dans `backend/.env` :

```env
SAFERIDE_USE_REAL_NAC=true
SAFERIDE_NOKIA_NAC_BASE_URL=https://network-as-code.p-eu.rapidapi.com
SAFERIDE_NOKIA_NAC_API_KEY=<votre clé Nokia NaC>
```

Puis dans `backend/app/services/camara.py`, étendre `CamaraMockService` (ou créer une classe `CamaraNokiaService`) pour appeler le SDK officiel. Exemple minimal :

```python
import network_as_code as nac

client = nac.NetworkAsCodeClient(token=settings.nokia_nac_api_key)
device = client.devices.get("+237670000101")
swap = client.sim_swap.check_sim_swap(device, max_age=72)  # CAMARA Sim Swap
```

## 3. APIs CAMARA orchestrées par SafeRide

> **Source produit Nokia NaC pour les APIs anti-fraude utilisées par SafeRide** :
> https://networkascode.nokia.io/products/digital-identity-and-anti-fraud
>
> Cette page liste exactement les APIs SafeRide consomme : *SIM Swap, Number Verification,
> Device Swap, Location Verification, KYC Match, KYC Age Verification, Call Forwarding Signal*.
> Les APIs `Quality on Demand`, `Congestion Insights` et `Geofencing` sont fournies par les
> produits *Connectivity* et *Network Intelligence* de la même plateforme.

### 3.1 SIM Swap (35 % du score)

- Spec : https://camaraproject.org/sim-swap/
- GitHub : https://github.com/camaraproject/SimSwap
- Catégorie : Identity & Fraud — **MANDATORY**
- Usage SafeRide : détecte si le chauffeur a échangé sa carte SIM dans les 72 dernières heures. Si oui, score `0` sur cette dimension.

### 3.2 Number Verification (20 %)

- GitHub : https://github.com/camaraproject/NumberVerification
- Catégorie : Identity & Fraud — **MANDATORY**
- Usage : valide que le numéro de téléphone est bien associé à l’opérateur déclaré par le chauffeur.

### 3.3 Device Status / Reachability (20 %)

- GitHub : https://github.com/camaraproject/DeviceStatus
- Catégorie : Network Intelligence — **MANDATORY**
- Usage : vérifie que l’appareil est actif, non suspect, non intrusif.

### 3.4 Location Verification (25 %)

- GitHub : https://github.com/camaraproject/DeviceLocation
- Catégorie : Identity & Fraud — **MANDATORY**
- Usage : compare la position GPS déclarée par le chauffeur avec la position réseau réelle (cellule mobile) pour détecter le GPS spoofing.

### 3.5 Quality on Demand (QoD)

- GitHub : https://github.com/camaraproject/QualityOnDemand
- Catégorie : Connectivity — **CORE**
- Usage : ouvre une session de qualité réseau garantie pour le suivi GPS et la communication temps réel.

### 3.6 Congestion Insights

- GitHub : https://github.com/camaraproject/CongestionInsights
- Catégorie : Network Intelligence
- Usage : détecte les zones congestionnées pour anticiper les coupures et recalculer l’itinéraire.

### 3.7 Geofencing Subscriptions

- GitHub : https://github.com/camaraproject/Geofencing
- Catégorie : Network Intelligence
- Usage : déclenche une alerte si le chauffeur quitte le périmètre prévu de la course.

## 4. Mapping (OpenStreetMap + Leaflet)

- Tuiles : https://www.openstreetmap.org/
- Leaflet : https://leafletjs.com/
- React-Leaflet : https://react-leaflet.js.org/

## 5. Chariow (paiement)

Chariow est la plateforme africaine de vente de produits digitaux (https://chariow.com), supportant **Mobile Money** (Orange Money, MTN MoMo, Wave, Moov), **cartes bancaires** et **cryptomonnaies**.

- Site : https://chariow.com/fr
- Documentation : https://help.chariow.com/
- Création de produit : https://help.chariow.com/fr/articles/168-creer-un-cours-sur-chariow
- Liens de paiement personnalisés : https://help.chariow.com/en/articles/274-create-custom-product-links

### 5.1 Configuration côté SafeRide

1. Créer un produit dans le dashboard Chariow (par ex. *SafeRide Premium Driver — 5 000 FCFA / mois*).
2. Récupérer le lien de checkout (avec « accès direct au paiement » activé).
3. Renseigner ce lien dans `backend/.env` :

   ```env
   SAFERIDE_CHARIOW_CHECKOUT_URL=https://chariow.com/<vendeur>/<produit>
   ```

4. Le frontend appelle `POST /subscriptions` qui crée un abonnement `pending` et renvoie l’URL paramétrée. La page est chargée dans une **iframe** (`PremiumView.jsx`).

### 5.2 Webhook Chariow

Configurer dans Chariow l’URL `POST` :

```
https://api.saferide.app/subscriptions/webhook/chariow
```

Payload accepté (laxiste pour s’adapter aux différents events Chariow) :

```json
{
  "event": "payment.succeeded",
  "reference": "abc123",
  "status": "succeeded",
  "amount": 5000,
  "customer_email": "driver@example.com",
  "customer_phone": "+237670000101",
  "metadata": { "subscription_id": "sub-xxxxxxxx" }
}
```

Statuts mappés :

| `status` Chariow            | État SafeRide  |
| --------------------------- | -------------- |
| `succeeded`, `paid`, `active` | `active`     |
| `pending`                   | `pending`      |
| `failed`                    | `expired`      |
| `cancelled`, `refunded`     | `cancelled`    |

> ⚠️ En production, vérifier obligatoirement la **signature HMAC** envoyée par Chariow dans l’en-tête (extension à ajouter dans `subscriptions.handle_chariow_webhook`).

## 6. Synthèse — où est utilisée chaque API

| API                       | Avant la course | Pendant la course | Admin |
| ------------------------- | :-------------: | :---------------: | :---: |
| SIM Swap                  | ✅              |                   | ✅    |
| Number Verification       | ✅              |                   | ✅    |
| Device Status             | ✅              |                   | ✅    |
| Location Verification     | ✅              | ✅                | ✅    |
| Quality on Demand         |                 | ✅                |       |
| Congestion Insights       |                 | ✅                | ✅    |
| Geofencing Subscriptions  |                 | ✅                |       |
| Chariow                   |                 |                   | ✅    |
