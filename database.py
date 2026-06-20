import sqlite3
import os


class Database:
    """Singleton — une seule instance de connexion SQLite partagée dans tout le projet."""
    _instance: "Database | None" = None

    def __new__(cls) -> "Database":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            db_path = os.path.join(os.path.dirname(__file__), "helpdesk.db")
            cls._instance.connexion = sqlite3.connect(db_path, check_same_thread=False)
            cls._instance.connexion.row_factory = sqlite3.Row
            cls._instance.connexion.execute("PRAGMA foreign_keys = ON")
            cls._instance._creer_tables()
        return cls._instance

    def _creer_tables(self) -> None:
        cursor = self.connexion.cursor()

        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS utilisateurs (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                nom             TEXT    NOT NULL,
                prenom          TEXT    NOT NULL,
                email           TEXT    NOT NULL UNIQUE,
                mot_de_passe    TEXT    NOT NULL,
                role            TEXT    NOT NULL DEFAULT 'employe',
                date_creation   DATETIME DEFAULT CURRENT_TIMESTAMP,
                actif           INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS tickets (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                titre               TEXT    NOT NULL,
                description         TEXT,
                categorie           TEXT    NOT NULL,
                priorite            TEXT    NOT NULL DEFAULT 'normale',
                statut              TEXT    NOT NULL DEFAULT 'ouvert',
                date_creation       DATETIME DEFAULT CURRENT_TIMESTAMP,
                date_modification   DATETIME,
                employe_id          INTEGER,
                agent_id            INTEGER,
                FOREIGN KEY (employe_id) REFERENCES utilisateurs(id) ON DELETE SET NULL,
                FOREIGN KEY (agent_id)   REFERENCES utilisateurs(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS commentaires (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                contenu         TEXT    NOT NULL,
                date_creation   DATETIME DEFAULT CURRENT_TIMESTAMP,
                ticket_id       INTEGER NOT NULL,
                auteur_id       INTEGER,
                FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
                FOREIGN KEY (auteur_id) REFERENCES utilisateurs(id) ON DELETE SET NULL
            );
        """)
        self.connexion.commit()

        # Créer un admin par défaut si aucun utilisateur n'existe
        cursor.execute("SELECT COUNT(*) FROM utilisateurs")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO utilisateurs (nom, prenom, email, mot_de_passe, role)
                VALUES ('Admin', 'Système', 'admin@helpdesk.com', 'admin123', 'admin')
            """)
            self.connexion.commit()

    def executer(self, requete: str, params: tuple = ()) -> None:
        """Exécute une requête d'écriture (INSERT / UPDATE / DELETE) et commit."""
        cursor = self.connexion.cursor()
        cursor.execute(requete, params)
        self.connexion.commit()

    def fetchall(self, requete: str, params: tuple = ()) -> list[dict]:
        """Exécute une requête SELECT et retourne toutes les lignes sous forme de dicts."""
        cursor = self.connexion.cursor()
        cursor.execute(requete, params)
        return [dict(row) for row in cursor.fetchall()]

    def fetchone(self, requete: str, params: tuple = ()) -> dict | None:
        """Exécute une requête SELECT et retourne la première ligne, ou None."""
        cursor = self.connexion.cursor()
        cursor.execute(requete, params)
        row = cursor.fetchone()
        return dict(row) if row else None
