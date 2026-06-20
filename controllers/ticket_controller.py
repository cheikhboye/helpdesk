from services.ticket_service import TicketService


class TicketController:
    """
    Endpoints de gestion des tickets, commentaires et utilisateurs.
    Consommé par : EmployeView · AgentView · AdminView
    """

    def __init__(self):
        self._service = TicketService()

    # ──────────────────────────────────────────────────────
    # TICKETS
    # ──────────────────────────────────────────────────────

    """
    Crée un nouveau ticket ouvert associé à un employé.

    Paramètres :
        titre       -- intitulé du ticket (obligatoire)
        description -- détail du problème
        categorie   -- valeur parmi CATEGORIES (models/ticket.py)
        priorite    -- valeur parmi PRIORITES  (models/ticket.py)
        employe_id  -- id de l'employé déclarant

    Retourne :
        (True,  "Ticket créé avec succès !") en cas de succès
        (False, message_erreur)              si le titre est vide
    """
    def creer_ticket(self, titre: str, description: str, categorie: str,
                     priorite: str, employe_id: int) -> tuple[bool, str]:
        return self._service.creer_ticket(titre, description, categorie, priorite, employe_id)

    """
    Met à jour les champs éditables d'un ticket existant.

    Paramètres :
        ticket_id   -- identifiant du ticket à modifier
        titre       -- nouveau titre (obligatoire)
        description -- nouvelle description
        categorie   -- nouvelle catégorie
        priorite    -- nouvelle priorité

    Retourne :
        (True,  "Ticket modifié avec succès !") en cas de succès
        (False, message_erreur)                 si le titre est vide
    """
    def modifier_ticket(self, ticket_id: int, titre: str, description: str,
                        categorie: str, priorite: str) -> tuple[bool, str]:
        return self._service.modifier_ticket(ticket_id, titre, description, categorie, priorite)

    """
    Change le statut d'un ticket (ex. ouvert → en_cours).

    Paramètres :
        ticket_id      -- identifiant du ticket
        nouveau_statut -- valeur parmi STATUTS (models/ticket.py)

    Retourne :
        (True, "Statut changé en « … ».")
    """
    def changer_statut(self, ticket_id: int, nouveau_statut: str) -> tuple[bool, str]:
        return self._service.changer_statut(ticket_id, nouveau_statut)

    """
    Assigne un ticket à un agent et passe son statut à « en_cours ».

    Paramètres :
        ticket_id -- identifiant du ticket
        agent_id  -- identifiant de l'agent ou admin destinataire

    Retourne :
        (True, "Ticket assigné à Prénom Nom.")
    """
    def assigner_ticket(self, ticket_id: int, agent_id: int) -> tuple[bool, str]:
        return self._service.assigner_ticket(ticket_id, agent_id)

    """
    Supprime définitivement un ticket et ses commentaires (CASCADE).

    Paramètres :
        ticket_id -- identifiant du ticket à supprimer

    Retourne :
        (True, "Ticket supprimé.")
    """
    def supprimer_ticket(self, ticket_id: int) -> tuple[bool, str]:
        return self._service.supprimer_ticket(ticket_id)

    # ──────────────────────────────────────────────────────
    # LECTURE / LISTES
    # ──────────────────────────────────────────────────────

    """
    Retourne un ticket par son identifiant.

    Paramètres :
        ticket_id -- identifiant du ticket recherché

    Retourne :
        dict avec les colonnes de la table tickets, ou None si introuvable
    """
    def get_ticket_by_id(self, ticket_id: int) -> dict | None:
        return self._service.get_ticket_by_id(ticket_id)

    """
    Retourne tous les tickets avec les noms employé/agent (JOIN).

    Retourne :
        Liste de dicts incluant emp_nom, emp_prenom, agt_nom, agt_prenom,
        triée par date de création décroissante
    """
    def get_tous_tickets(self) -> list[dict]:
        return self._service.get_tous_tickets()

    """
    Retourne les tickets créés par un employé donné.

    Paramètres :
        employe_id -- identifiant de l'employé

    Retourne :
        Liste de dicts triée par date de création décroissante
    """
    def get_tickets_employe(self, employe_id: int) -> list[dict]:
        return self._service.get_tickets_employe(employe_id)

    """
    Filtre les tickets par statut avec les noms employé/agent (JOIN).

    Paramètres :
        statut -- valeur parmi STATUTS (models/ticket.py)

    Retourne :
        Liste de dicts incluant emp_nom, emp_prenom, agt_nom, agt_prenom
    """
    def get_tickets_par_statut(self, statut: str) -> list[dict]:
        return self._service.get_tickets_par_statut(statut)

    """
    Recherche plein-texte sur le titre et la description des tickets.

    Paramètres :
        terme -- chaîne de recherche (insensible à la casse via LIKE)

    Retourne :
        Liste de dicts correspondants
    """
    def rechercher(self, terme: str) -> list[dict]:
        return self._service.rechercher(terme)

    """
    Retourne le nombre de tickets par statut et le total général.

    Retourne :
        {"ouvert": n, "en_cours": n, "en_attente": n,
         "resolu": n, "ferme": n, "total": n}
    """
    def get_stats(self) -> dict:
        return self._service.get_stats()

    # ──────────────────────────────────────────────────────
    # COMMENTAIRES
    # ──────────────────────────────────────────────────────

    """
    Ajoute un commentaire à un ticket.

    Paramètres :
        contenu   -- texte du commentaire (obligatoire, non vide)
        ticket_id -- identifiant du ticket concerné
        auteur_id -- identifiant de l'utilisateur qui commente

    Retourne :
        (True,  "Commentaire ajouté.") en cas de succès
        (False, message_erreur)        si le contenu est vide
    """
    def ajouter_commentaire(self, contenu: str, ticket_id: int,
                            auteur_id: int) -> tuple[bool, str]:
        return self._service.ajouter_commentaire(contenu, ticket_id, auteur_id)

    """
    Retourne les commentaires d'un ticket avec les infos auteur (JOIN).

    Paramètres :
        ticket_id -- identifiant du ticket

    Retourne :
        Liste de dicts incluant nom, prenom, role de l'auteur,
        triée par date de création croissante
    """
    def get_commentaires(self, ticket_id: int) -> list[dict]:
        return self._service.get_commentaires(ticket_id)

    # ──────────────────────────────────────────────────────
    # UTILISATEURS (réservé à AdminView)
    # ──────────────────────────────────────────────────────

    """
    Retourne les utilisateurs ayant le rôle agent ou admin.

    Retourne :
        Liste de dicts utilisateurs éligibles à l'assignation de tickets
    """
    def get_agents(self) -> list[dict]:
        return self._service.get_agents()

    """
    Retourne tous les utilisateurs enregistrés, triés par nom.

    Retourne :
        Liste complète de dicts utilisateurs
    """
    def get_all_users(self) -> list[dict]:
        return self._service.get_all_users()

    """
    Retourne le nombre total d'utilisateurs enregistrés.

    Retourne :
        Entier — nombre de lignes dans la table utilisateurs
    """
    def count_users(self) -> int:
        return self._service.count_users()

    """
    Change le rôle d'un utilisateur (employe / agent / admin).

    Paramètres :
        user_id      -- identifiant de l'utilisateur à modifier
        nouveau_role -- "employe", "agent" ou "admin"

    Retourne :
        None
    """
    def update_user_role(self, user_id: int, nouveau_role: str) -> None:
        return self._service.update_user_role(user_id, nouveau_role)

    """
    Crée un nouvel utilisateur avec le rôle choisi (réservé à l'admin).

    Paramètres :
        nom, prenom  -- identité de l'utilisateur
        email        -- doit être unique et au format valide
        mot_de_passe -- minimum 6 caractères, une lettre et un chiffre
        role         -- "employe", "agent" ou "admin"

    Retourne :
        (True,  "Utilisateur créé avec succès !") en cas de succès
        (False, message_erreur)                   si validation échoue
    """
    def creer_utilisateur(self, nom: str, prenom: str, email: str,
                          mot_de_passe: str, confirmation: str,
                          role: str) -> tuple[bool, str]:
        return self._service.creer_utilisateur(
            nom, prenom, email, mot_de_passe, confirmation, role
        )
