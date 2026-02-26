<div align="center">

# ☀️ OptiVolt

### L'Uberisation de la Maintenance Solaire au Maroc

<br/>

<img src="https://img.shields.io/badge/Status-Production_Ready-2ea44f?style=for-the-badge" alt="Status"/>
<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
<img src="https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL"/>
<img src="https://img.shields.io/badge/CLI-Rich-af52de?style=for-the-badge" alt="Rich"/>
<img src="https://img.shields.io/badge/Architecture-3--Tiers-ff6f00?style=for-the-badge" alt="3-Tiers"/>

<br/>
<br/>

> *« L'optimisation intelligente de votre énergie solaire. »*

**Opti** *(Optimisation)* — Rendement, durabilité, efficacité maximale.  
**Volt** *(Énergie)* — Puissance et technologie électrique.

<br/>

---

<br/>

<table>
<tr>
<td width="50%">

### 🔴 Le Problème

</td>
<td width="50%">

### 🟢 Notre Solution

</td>
</tr>
<tr>
<td>

📉 Perte de rendement jusqu'à **30%** sans entretien  
🔍 Difficulté à trouver des pros qualifiés  
📋 Zéro outils numériques pour les prestataires

</td>
<td>

🏪 Marketplace transparente (tarifs, avis, services)  
📅 Prise de RDV intelligente sur créneaux libres  
🏗️ ERP intégré (Catalogue, Planning, Rapports)

</td>
</tr>
</table>

<br/>

---

</div>

<br/>

## 💼 Modèle Économique — SaaS B2B

Des revenus **récurrents et prévisibles** via abonnements mensuels pour les prestataires :

<div align="center">

| | 🥉 Basic | 🥈 Pro | 🥇 Premium |
|:---|:---:|:---:|:---:|
| **Prix** | **299 DH**/mois | **599 DH**/mois | **999 DH**/mois |
| Visibilité Marketplace | ✅ Standard | ✅ Prioritaire | ✅ Prioritaire |
| Limite Catalogue | 5 services | 15 services | ♾️ Illimité |
| Vue Planning | ❌ | ✅ | ✅ |
| Support Prioritaire | ❌ | ✅ | ✅ |
| Dashboard Analytics | ❌ | ❌ | ✅ |

</div>

<br/>

---

<br/>

## ✨ Fonctionnalités

<details>
<summary><h3>👤 Espace Client — Propriétaires Solaires</h3></summary>

<br/>

| Fonctionnalité | Description |
|:---|:---|
| 🔎 **Parcours d'achat fluide** | Recherche par catégorie : Nettoyage, Diagnostic, Remplacement |
| 🃏 **Transparence totale** | Cartes entreprises avec prix, horaires et produits inclus |
| 📅 **Réservation intelligente** | Sélection de créneaux disponibles — zéro conflit d'agenda |
| ⭐ **Garantie qualité** | Notation & avis uniquement après vérification de fin de service |

</details>

<details>
<summary><h3>🏢 Espace Entreprise — Prestataires Certifiés</h3></summary>

<br/>

| Fonctionnalité | Description |
|:---|:---|
| 📦 **Gestion de Catalogue** | Tarification dynamique, personnalisation des offres et unités |
| ✅ **Traitement des Demandes** | Acceptation rapide avec assignation de superviseur, ou refus |
| 🗓️ **Planning Automatisé** | Vision claire des interventions à venir *(Pro/Premium)* |
| 📝 **Preuve de Travail** | Rapports d'intervention détaillés avec état avant/après |

</details>

<details>
<summary><h3>🛡️ Espace Administrateur — Plateforme</h3></summary>

<br/>

| Fonctionnalité | Description |
|:---|:---|
| 📊 **Dashboard Global** | KPIs en temps réel : CA global, revenus abonnements |
| 🚫 **Modération** | Bannissement d'utilisateurs, vérification des entreprises |
| ⚙️ **Gestion Métier** | Ajout dynamique de nouvelles catégories de services |

</details>

<br/>

---

<br/>

## 🏗️ Architecture & Design

<div align="center">

```
┌─────────────────────────────────────────────────────────────┐
│                    🖥️  PRÉSENTATION                         │
│                  CLI Interactive (Rich)                      │
│              Tableaux · Panels · Prompts                    │
├─────────────────────────────────────────────────────────────┤
│                  ⚙️  LOGIQUE MÉTIER                         │
│                    Services Layer                           │
│        Auth · Réservation · Pricing · Abonnements          │
├─────────────────────────────────────────────────────────────┤
│                  💾  ACCÈS AUX DONNÉES                      │
│                     DAO Pattern                             │
│              Isolation totale des requêtes SQL              │
├─────────────────────────────────────────────────────────────┤
│                  🗄️  MySQL Database                         │
└─────────────────────────────────────────────────────────────┘
```

</div>

<br/>

### 🧩 Design Patterns (POO)

| Pattern | Utilisation | Bénéfice |
|:---|:---|:---|
| 🔒 **Singleton** | Connexion DB & Logger | Instance unique garantie |
| 🏭 **Factory Method** | Création de profils (Client / Entreprise / Admin) | Extensibilité sans modification |
| 🎯 **Strategy + OCP** | Moteur de prix par zone géo (Rabat, Casa…) | Règles interchangeables |
| 🗃️ **DAO** | Couche d'accès aux données | Isolation SQL totale |

<br/>

---

<br/>

## 📅 Roadmap Agile — Méthodologie Scrum

```
Sprint 1 ██████████░░░░░░░░░░░░░░░░░░░░  Fondations
         UML · Schéma DB · Singleton

Sprint 2 ░░░░░░░░░░██████████░░░░░░░░░░  MVP Core
         Auth · Factory · Catalogue

Sprint 3 ░░░░░░░░░░░░░░░░░░░░██████████  Business Logic
         Réservations · Pricing · Abonnements

Sprint 4 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  Polish & Admin
         Dashboard KPI · Notations · Rapports · Recette
```

<br/>

---

<br/>

## 🚀 Installation & Lancement

### Pré-requis

> **Python 3.10+** · **MySQL 8.0+** · **pip**

<br/>

### 1️⃣ Clone & Setup

```bash
git clone https://github.com/your-username/OptiVolt.git
cd OptiVolt

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2️⃣ Configuration

Créez / vérifiez votre fichier `.env` avec vos accès MySQL :

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=optivolt
```

### 3️⃣ Initialisation de la Base *(une seule fois)*

```bash
# Création des tables
python3 -m utils.db_init

# Injection des données de test
python3 -m utils.seed_data
```

### 4️⃣ Lancement 🎉

```bash
python3 main.py
```

<br/>

### 🔑 Comptes par défaut

| Rôle | Email | Mot de passe |
|:---|:---|:---|
| 🛡️ Admin | `admin@optivolt.ma` | `admin123` |
| 👤 Clients *(seed)* | *(générés)* | `1234` |
| 🏢 Entreprises *(seed)* | *(générés)* | `1234` |

<br/>

---

<br/>

<div align="center">

### 🛠️ Construit avec

<br/>

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
<img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL"/>
<img src="https://img.shields.io/badge/Rich_CLI-af52de?style=for-the-badge&logo=terminal&logoColor=white" alt="Rich"/>
<img src="https://img.shields.io/badge/dotenv-ECD53F?style=for-the-badge&logo=.env&logoColor=black" alt="dotenv"/>

<br/>
<br/>

---

<sub>Fait avec ❤️ pour le marché solaire marocain</sub>

</div>
