from database import Database
from models.commentaire import Commentaire


class CommentaireRepository:
    """Accès aux données de la table commentaires (CRUD)."""

    def __init__(self):
        self._db = Database()

    # ── Création ──────────────────────────────────────────

    """Insère un nouveau commentaire associé à un ticket et un auteur."""
    def save(self, c: Commentaire) -> None:
        self._db.executer(
            "INSERT INTO commentaires (contenu, ticket_id, auteur_id) VALUES (?,?,?)",
            (c.contenu, c.ticket_id, c.auteur_id),
        )

    # ── Lecture ───────────────────────────────────────────

    """
    Retourne les commentaires d'un ticket avec les infos auteur (JOIN),
    triés par date de création croissante.
    """
    def find_by_ticket(self, ticket_id: int) -> list[dict]:
        return self._db.fetchall(
            """SELECT c.*, u.nom, u.prenom, u.role
               FROM commentaires c
               LEFT JOIN utilisateurs u ON c.auteur_id = u.id
               WHERE c.ticket_id=?
               ORDER BY c.date_creation ASC""",
            (ticket_id,),
        )

    # ── Suppression ───────────────────────────────────────

    """Supprime un commentaire par son id."""
    def delete(self, commentaire_id: int) -> None:
        self._db.executer(
            "DELETE FROM commentaires WHERE id=?", (commentaire_id,)
        )
