# Helpdesk — Application de gestion de tickets

Application de bureau développée en **Python / Tkinter** dans le cadre d'un projet de programmation. Elle permet à une entreprise de gérer ses demandes d'assistance interne (tickets) selon trois rôles : **Employé**, **Agent** et **Administrateur**.

---

## Sommaire

1. [Aperçu](#aperçu)
2. [Prérequis](#prérequis)
3. [Installation](#installation)
4. [Lancement](#lancement)
5. [Compte administrateur par défaut](#compte-administrateur-par-défaut)
6. [Fonctionnalités](#fonctionnalités)
7. [Architecture du projet](#architecture-du-projet)
8. [Structure des fichiers](#structure-des-fichiers)
9. [Schéma de la base de données](#schéma-de-la-base-de-données)
10. [Règles de validation](#règles-de-validation)
11. [Palette de couleurs et thème](#palette-de-couleurs-et-thème)
12. [Stack technique](#stack-technique)

---

## Aperçu

L'application Helpdesk centralise la gestion des demandes d'assistance au sein d'une organisation. Chaque utilisateur se connecte avec son compte et accède à une interface adaptée à son rôle :

| Rôle | Couleur d'en-tête | Accès |
|------|-------------------|-------|
| Employé | Bleu | Créer et suivre ses propres tickets |
| Agent | Ambre | Traiter, assigner et commenter tous les tickets |
| Admin | Violet | Gérer tickets, utilisateurs et consulter les statistiques |

---

## Prérequis

- **Python 3.12** ou supérieur
- **Tkinter** avec support natif (inclus dans Python standard sur Windows/Linux)
- Sur **macOS** : installer le binding Tk séparément via Homebrew

```bash
# macOS uniquement
brew install python-tk@3.12
```

Aucune dépendance externe (pip) n'est requise — le projet utilise uniquement la bibliothèque standard Python.

---

## Installation

```bash
# 1. Cloner ou décompresser le projet
cd helpdesk

# 2. (Optionnel) Créer un environnement virtuel
python3.12 -m venv .venv
source .venv/bin/activate   # macOS / Linux
.venv\Scripts\activate      # Windows
```

La base de données SQLite (`helpdesk.db`) est créée automatiquement au premier lancement dans le répertoire du projet.

---

## Lancement

```bash
python main.py
```

ou avec un interpréteur spécifique :

```bash
/usr/local/bin/python3.12 main.py
```

---

## Compte administrateur par défaut

Lors du tout premier lancement, un compte admin est créé automatiquement si la base est vide :

| Champ | Valeur |
|-------|--------|
| Email | `admin@helpdesk.com` |
| Mot de passe | `admin123` |
| Rôle | `admin` |

> **Important :** Changez ce mot de passe dès la première connexion via la gestion des utilisateurs.

---

## Fonctionnalités

### Authentification (`LoginView`)

- Connexion avec email et mot de passe
- Inscription libre (rôle **employé** attribué automatiquement)
- Affichage/masquage du mot de passe (bouton 👁)
- Redirection automatique vers l'interface correspondant au rôle
- Messages d'erreur inline (aucune boîte de dialogue parasite)

---

### Espace Employé (`EmployeView`)

- **Créer un ticket** : titre (obligatoire), description, catégorie, priorité
- **Voir ses tickets** avec filtrage par statut
- **Modifier un ticket** ouvert (titre, description, catégorie, priorité)
- **Supprimer un ticket** ouvert
- **Consulter le détail** d'un ticket (double-clic) : description complète, historique des commentaires
- **Ajouter un commentaire** sur ses propres tickets
- **Recherche plein texte** sur le titre et la description

**Statuts de ticket disponibles :**

| Statut | Couleur |
|--------|---------|
| `ouvert` | Bleu |
| `en_cours` | Orange |
| `en_attente` | Violet |
| `resolu` | Vert |
| `ferme` | Gris |

---

### Espace Agent (`AgentView`)

- **Voir tous les tickets** avec filtrage par statut
- **Double-cliquer** pour ouvrir la fenêtre de gestion d'un ticket
- **Changer le statut** d'un ticket (avec blocage si statut inchangé)
- **Assigner un ticket** à un agent ou admin
- **Ajouter des commentaires** sur les tickets traités
- Coloration automatique des lignes du tableau selon le statut

---

### Espace Admin (`AdminView`)

Trois onglets :

#### Tableau de bord
- Cartes de statistiques par statut (nombre de tickets ouverts, en cours, résolus…)
- Nombre total d'utilisateurs enregistrés

#### Tous les tickets
- Liste complète avec filtre par statut
- Suppression définitive d'un ticket sélectionné

#### Utilisateurs
- Liste complète des utilisateurs
- **Créer un utilisateur** : formulaire complet (nom, prénom, email, mot de passe avec confirmation, rôle)
- **Changer le rôle** : promouvoir en Agent, promouvoir en Admin, rétrograder en Employé
- Protection : l'admin ne peut pas modifier son propre rôle

---

## Architecture du projet

Le projet suit une architecture en **4 couches** inspirée du pattern MVC enrichi d'une couche Repository :

```
Views  ──►  Controllers  ──►  Services  ──►  Repositories  ──►  Database
 (UI)      (orchestration)  (métier)      (SQL / CRUD)        (SQLite)
```

### Couche Modèles (`models/`)

Dataclasses Python pures, sans logique. Contiennent aussi les constantes métier.

| Fichier | Contenu |
|---------|---------|
| `utilisateur.py` | Dataclass `Utilisateur` + constante `ROLES` |
| `ticket.py` | Dataclass `Ticket` + `STATUTS`, `PRIORITES`, `CATEGORIES`, `COULEURS_STATUT`, `COULEURS_PRIO` |
| `commentaire.py` | Dataclass `Commentaire` |

### Couche Repositories (`repositories/`)

Toutes les requêtes SQL. Aucune logique métier.

| Fichier | Responsabilité |
|---------|----------------|
| `utilisateur_repository.py` | CRUD utilisateurs (save, find_by_id, find_by_email, find_all, count, update_profil, update_role, desactiver) |
| `ticket_repository.py` | CRUD tickets avec JOINs employé/agent, recherche plein texte, statistiques |
| `commentaire_repository.py` | save, find_by_ticket (avec JOIN auteur), delete |

### Couche Services (`services/`)

Logique métier et validations. Orchestre les repositories.

| Fichier | Responsabilité |
|---------|----------------|
| `auth_service.py` | Connexion (vérification email + mot de passe + compte actif), inscription |
| `ticket_service.py` | Gestion complète des tickets, commentaires et utilisateurs (admin) |
| `validation.py` | Fonctions de validation réutilisables : nom, email, mot de passe, inscription |

### Couche Controllers (`controllers/`)

Fins orchestrateurs, délèguent tout au service. Documentés en style Swagger/JavaDoc au-dessus de chaque méthode.

| Fichier | Consommé par |
|---------|--------------|
| `auth_controller.py` | `LoginView` |
| `ticket_controller.py` | `EmployeView`, `AgentView`, `AdminView` |

### Couche Views (`views/`)

Interfaces Tkinter. Aucune logique métier.

| Fichier | Description |
|---------|-------------|
| `login_view.py` | Fenêtre de connexion / inscription |
| `employe_view.py` | Interface employé (liste + détail ticket) |
| `agent_view.py` | Interface agent (liste + gestion ticket) |
| `admin_view.py` | Interface admin (tableau de bord + tickets + utilisateurs) |
| `styles.py` | Constantes de couleurs, polices, helpers UI (`create_button`, `create_dropdown`, `add_placeholder`) |

### Base de données (`database.py`)

Classe `Database` en **Singleton** — une seule connexion SQLite partagée dans toute l'application.

---

## Structure des fichiers

```
helpdesk/
│
├── main.py                          # Point d'entrée
├── database.py                      # Singleton SQLite
├── helpdesk.db                      # Base générée automatiquement
│
├── models/
│   ├── utilisateur.py               # Dataclass Utilisateur + ROLES
│   ├── ticket.py                    # Dataclass Ticket + constantes
│   └── commentaire.py               # Dataclass Commentaire
│
├── repositories/
│   ├── utilisateur_repository.py    # SQL utilisateurs
│   ├── ticket_repository.py         # SQL tickets
│   └── commentaire_repository.py    # SQL commentaires
│
├── services/
│   ├── auth_service.py              # Authentification
│   ├── ticket_service.py            # Logique métier tickets / users
│   └── validation.py                # Règles de validation
│
├── controllers/
│   ├── auth_controller.py           # Endpoints auth
│   └── ticket_controller.py         # Endpoints tickets / users / agents
│
└── views/
    ├── styles.py                    # Palette, polices, helpers UI
    ├── login_view.py                # Écran de connexion
    ├── employe_view.py              # Vue employé
    ├── agent_view.py                # Vue agent
    └── admin_view.py                # Vue administrateur
```

---

## Schéma de la base de données

```sql
utilisateurs
────────────
id              INTEGER PRIMARY KEY AUTOINCREMENT
nom             TEXT    NOT NULL
prenom          TEXT    NOT NULL
email           TEXT    NOT NULL UNIQUE
mot_de_passe    TEXT    NOT NULL
role            TEXT    NOT NULL DEFAULT 'employe'   -- employe | agent | admin
date_creation   DATETIME DEFAULT CURRENT_TIMESTAMP
actif           INTEGER DEFAULT 1

tickets
───────
id                  INTEGER PRIMARY KEY AUTOINCREMENT
titre               TEXT    NOT NULL
description         TEXT
categorie           TEXT    NOT NULL                  -- informatique | materiel | logiciel | reseau | administratif
priorite            TEXT    NOT NULL DEFAULT 'normale' -- basse | normale | haute | urgente
statut              TEXT    NOT NULL DEFAULT 'ouvert'  -- ouvert | en_cours | en_attente | resolu | ferme
date_creation       DATETIME DEFAULT CURRENT_TIMESTAMP
date_modification   DATETIME
employe_id          INTEGER  REFERENCES utilisateurs(id) ON DELETE SET NULL
agent_id            INTEGER  REFERENCES utilisateurs(id) ON DELETE SET NULL

commentaires
────────────
id              INTEGER PRIMARY KEY AUTOINCREMENT
contenu         TEXT    NOT NULL
date_creation   DATETIME DEFAULT CURRENT_TIMESTAMP
ticket_id       INTEGER NOT NULL  REFERENCES tickets(id) ON DELETE CASCADE
auteur_id       INTEGER           REFERENCES utilisateurs(id) ON DELETE SET NULL
```

---

## Règles de validation

Définies dans `services/validation.py` et appliquées dans les services.

| Champ | Règle |
|-------|-------|
| Nom / Prénom | Lettres uniquement (accents inclus), 2 à 50 caractères |
| Email | Format `nom@domaine.ext` via regex |
| Mot de passe | Minimum 6 caractères, au moins une lettre et un chiffre |
| Confirmation | Doit correspondre exactement au mot de passe |
| Titre ticket | Non vide après suppression des espaces |
| Commentaire | Non vide après suppression des espaces |
| Rôle | Valeur parmi `["employe", "agent", "admin"]` |
| Email unique | Vérifié en base avant tout enregistrement |

---

## Palette de couleurs et thème

Le fichier `views/styles.py` centralise toutes les constantes visuelles.

### Couleurs principales

| Constante | Valeur | Usage |
|-----------|--------|-------|
| `BG_APP` | `#f0f4f8` | Fond général de l'application |
| `BG_CARD` | `#ffffff` | Cartes, champs de saisie |
| `BG_TOOLBAR` | `#e2e8f0` | Barres d'outils, en-têtes Treeview |
| `HDR_EMPLOYE` | `#1e40af` | Bandeau employé |
| `HDR_AGENT` | `#b45309` | Bandeau agent |
| `HDR_ADMIN` | `#6b21a8` | Bandeau admin |
| `BTN_PRIMARY` | `#1e40af` | Boutons principaux |
| `BTN_SUCCESS` | `#15803d` | Boutons de confirmation / création |
| `BTN_DANGER` | `#dc2626` | Boutons de suppression |

### Coloration des tickets par statut (Treeview)

| Statut | Fond | Texte |
|--------|------|-------|
| `ouvert` | `#dbeafe` | `#1e40af` |
| `en_cours` | `#fef3c7` | `#92400e` |
| `en_attente` | `#ede9fe` | `#5b21b6` |
| `resolu` | `#d1fae5` | `#065f46` |
| `ferme` | `#f1f5f9` | `#475569` |

### Compatibilité macOS

Sur macOS, `tk.Button` ignore la couleur de fond et `ttk.Combobox` en readonly masque le texte. Deux helpers résolvent ces limitations :

- **`create_button()`** — implémente un bouton via `Frame + Label` (couleur respectée)
- **`create_dropdown()`** — utilise `tk.OptionMenu` à la place de `ttk.Combobox`

---

## Stack technique

| Technologie | Rôle |
|-------------|------|
| Python 3.12 | Langage principal |
| Tkinter | Interface graphique de bureau |
| ttk (Tkinter themed widgets) | Notebook, Treeview, Scrollbar |
| SQLite 3 | Base de données embarquée |
| `dataclasses` | Modèles de données |
| `re` (module standard) | Validation par expressions régulières |
| `os` (module standard) | Résolution du chemin de la base de données |

---

## Auteurs

Projet réalisé dans le cadre du cours de **Programmation en Python** par CHEIKH BOYE et SOKHNA AWA GADIAGA
