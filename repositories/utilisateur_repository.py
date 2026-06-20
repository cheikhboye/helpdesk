from database import Database
from models.utilisateur import Utilisateur


class UtilisateurRepository:
    """Accès aux données de la table utilisateurs (CRUD)."""

    def __init__(self):
        self._db = Database()

    # ── Création ──────────────────────────────────────────

    """Insère un nouvel utilisateur en base."""
    def save(self, u: Utilisateur) -> None:
        self._db.executer(
            "INSERT INTO utilisateurs (nom, prenom, email, mot_de_passe, role) VALUES (?,?,?,?,?)",
            (u.nom, u.prenom, u.email, u.mot_de_passe, u.role),
        )

    # ── Lecture ───────────────────────────────────────────

    """Retourne un utilisateur par son id, ou None s'il n'existe pas."""
    def find_by_id(self, user_id: int) -> dict | None:
        return self._db.fetchone(
            "SELECT * FROM utilisateurs WHERE id=?", (user_id,)
        )

    """Retourne un utilisateur par son email, ou None s'il n'existe pas."""
    def find_by_email(self, email: str) -> dict | None:
        return self._db.fetchone(
            "SELECT * FROM utilisateurs WHERE email=?", (email,)
        )

    """Retourne tous les utilisateurs triés par nom."""
    def find_all(self) -> list[dict]:
        return self._db.fetchall("SELECT * FROM utilisateurs ORDER BY nom")

    """Retourne le nombre total d'utilisateurs enregistrés."""
    def count(self) -> int:
        row = self._db.fetchone("SELECT COUNT(*) AS total FROM utilisateurs")
        return row["total"] if row else 0

    # ── Modification ──────────────────────────────────────

    """Met à jour le nom, prénom et email d'un utilisateur."""
    def update_profil(self, user_id: int, nom: str, prenom: str, email: str) -> None:
        self._db.executer(
            "UPDATE utilisateurs SET nom=?, prenom=?, email=? WHERE id=?",
            (nom, prenom, email, user_id),
        )

    """Met à jour le mot de passe d'un utilisateur."""
    def update_mot_de_passe(self, user_id: int, nouveau_mdp: str) -> None:
        self._db.executer(
            "UPDATE utilisateurs SET mot_de_passe=? WHERE id=?",
            (nouveau_mdp, user_id),
        )

    """Change le rôle d'un utilisateur (employe / agent / admin)."""
    def update_role(self, user_id: int, nouveau_role: str) -> None:
        self._db.executer(
            "UPDATE utilisateurs SET role=? WHERE id=?",
            (nouveau_role, user_id),
        )

    """Désactive un compte sans le supprimer (soft delete)."""
    def desactiver(self, user_id: int) -> None:
        self._db.executer(
            "UPDATE utilisateurs SET actif=0 WHERE id=?", (user_id,)
        )
