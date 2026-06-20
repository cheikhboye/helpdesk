from database import Database
from models.ticket import Ticket, STATUTS


_JOIN_USERS = """
    SELECT t.*,
           e.nom     AS emp_nom,    e.prenom AS emp_prenom,
           a.nom     AS agt_nom,    a.prenom AS agt_prenom
    FROM   tickets t
    LEFT JOIN utilisateurs e ON t.employe_id = e.id
    LEFT JOIN utilisateurs a ON t.agent_id   = a.id
"""


class TicketRepository:
    """Accès aux données de la table tickets (CRUD)."""

    def __init__(self):
        self._db = Database()

    # ── Création ──────────────────────────────────────────

    """Insère un nouveau ticket en base avec le statut « ouvert » par défaut."""
    def save(self, t: Ticket) -> None:
        self._db.executer(
            """INSERT INTO tickets (titre, description, categorie, priorite, employe_id)
               VALUES (?,?,?,?,?)""",
            (t.titre, t.description, t.categorie, t.priorite, t.employe_id),
        )

    # ── Lecture ───────────────────────────────────────────

    """Retourne un ticket par son id, ou None s'il n'existe pas."""
    def find_by_id(self, ticket_id: int) -> dict | None:
        return self._db.fetchone(
            "SELECT * FROM tickets WHERE id=?", (ticket_id,)
        )

    """Retourne tous les tickets avec les noms employé/agent (JOIN), triés par date décroissante."""
    def find_all(self) -> list[dict]:
        return self._db.fetchall(_JOIN_USERS + "ORDER BY t.date_creation DESC")

    """Retourne les tickets d'un employé donné, triés par date décroissante."""
    def find_by_employe(self, employe_id: int) -> list[dict]:
        return self._db.fetchall(
            "SELECT * FROM tickets WHERE employe_id=? ORDER BY date_creation DESC",
            (employe_id,),
        )

    """Retourne les tickets filtrés par statut avec les noms employé/agent (JOIN)."""
    def find_by_statut(self, statut: str) -> list[dict]:
        return self._db.fetchall(
            _JOIN_USERS + "WHERE t.statut=? ORDER BY t.date_creation DESC",
            (statut,),
        )

    """Recherche plein-texte sur le titre et la description (LIKE)."""
    def search(self, terme: str) -> list[dict]:
        like = f"%{terme}%"
        return self._db.fetchall(
            "SELECT * FROM tickets WHERE titre LIKE ? OR description LIKE ?",
            (like, like),
        )

    """Retourne le nombre de tickets par statut et le total général en une seule requête."""
    def get_stats(self) -> dict:
        rows = self._db.fetchall(
            "SELECT statut, COUNT(*) AS total FROM tickets GROUP BY statut"
        )
        stats = {s: 0 for s in STATUTS}
        for row in rows:
            stats[row["statut"]] = row["total"]
        stats["total"] = sum(stats[s] for s in STATUTS)
        return stats

    # ── Modification ──────────────────────────────────────

    """Met à jour les champs éditables d'un ticket et horodate la modification."""
    def update(self, ticket_id: int, titre: str, description: str,
               categorie: str, priorite: str) -> None:
        self._db.executer(
            """UPDATE tickets
               SET titre=?, description=?, categorie=?,
                   priorite=?, date_modification=datetime('now')
               WHERE id=?""",
            (titre, description, categorie, priorite, ticket_id),
        )

    """Change le statut d'un ticket et horodate la modification."""
    def update_statut(self, ticket_id: int, nouveau_statut: str) -> None:
        self._db.executer(
            "UPDATE tickets SET statut=?, date_modification=datetime('now') WHERE id=?",
            (nouveau_statut, ticket_id),
        )

    """Assigne un agent au ticket, passe le statut à « en_cours » et horodate."""
    def assign(self, ticket_id: int, agent_id: int) -> None:
        self._db.executer(
            """UPDATE tickets
               SET agent_id=?, statut='en_cours', date_modification=datetime('now')
               WHERE id=?""",
            (agent_id, ticket_id),
        )

    # ── Suppression ───────────────────────────────────────

    """Supprime un ticket (les commentaires associés sont supprimés en CASCADE)."""
    def delete(self, ticket_id: int) -> None:
        self._db.executer("DELETE FROM tickets WHERE id=?", (ticket_id,))
