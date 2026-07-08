from models.ticket import Ticket
from models.commentaire import Commentaire
from models.utilisateur import Utilisateur, ROLES
from repositories.ticket_repository import TicketRepository
from repositories.utilisateur_repository import UtilisateurRepository
from repositories.commentaire_repository import CommentaireRepository
from services.validation import valider_nom, valider_email, valider_mot_de_passe
from services.security import hasher_mot_de_passe


class TicketService:
    """Logique métier pour les tickets, commentaires et utilisateurs."""

    def __init__(self):
        self._tickets  = TicketRepository()
        self._users    = UtilisateurRepository()
        self._comments = CommentaireRepository()

    # ── Tickets ───────────────────────────────────────────

    def creer_ticket(self, titre: str, description: str, categorie: str,
                     priorite: str, employe_id: int) -> tuple[bool, str]:
        """
        Crée un ticket ouvert après validation du titre.

        Règles métier :
            - Le titre ne peut pas être vide

        Retourne :
            (True,  "Ticket créé avec succès !") si valide
            (False, message_erreur)              si le titre est vide
        """
        if not titre.strip():
            return False, "Le titre est obligatoire."
        self._tickets.save(Ticket(
            titre=titre.strip(), description=description.strip(),
            categorie=categorie, priorite=priorite, employe_id=employe_id,
        ))
        return True, "Ticket créé avec succès !"

    def modifier_ticket(self, ticket_id: int, titre: str, description: str,
                        categorie: str, priorite: str) -> tuple[bool, str]:
        """
        Met à jour les champs éditables d'un ticket existant.

        Règles métier :
            - Le titre ne peut pas être vide

        Retourne :
            (True,  "Ticket modifié avec succès !") si valide
            (False, message_erreur)                 si le titre est vide
        """
        if not titre.strip():
            return False, "Le titre est obligatoire."
        self._tickets.update(ticket_id, titre.strip(), description.strip(), categorie, priorite)
        return True, "Ticket modifié avec succès !"

    def changer_statut(self, ticket_id: int, nouveau_statut: str) -> tuple[bool, str]:
        """
        Change le statut d'un ticket et met à jour date_modification.

        Retourne :
            (True, "Statut changé en « … ».")
        """
        self._tickets.update_statut(ticket_id, nouveau_statut)
        return True, f"Statut changé en « {nouveau_statut} »."

    def assigner_ticket(self, ticket_id: int, agent_id: int) -> tuple[bool, str]:
        """
        Assigne un ticket à un agent et passe son statut à « en_cours ».

        Règles métier :
            - Le statut est automatiquement mis à « en_cours » lors de l'assignation

        Retourne :
            (True, "Ticket assigné à Prénom Nom.")
        """
        self._tickets.assign(ticket_id, agent_id)
        agent = self._users.find_by_id(agent_id)
        nom = f"{agent['prenom']} {agent['nom']}" if agent else "agent"
        return True, f"Ticket assigné à {nom}."

    def supprimer_ticket(self, ticket_id: int) -> tuple[bool, str]:
        """
        Supprime définitivement un ticket (les commentaires sont supprimés en CASCADE).

        Retourne :
            (True, "Ticket supprimé.")
        """
        self._tickets.delete(ticket_id)
        return True, "Ticket supprimé."

    # ── Listes ────────────────────────────────────────────

    def get_ticket_by_id(self, ticket_id: int) -> dict | None:
        return self._tickets.find_by_id(ticket_id)

    def get_tous_tickets(self) -> list[dict]:
        return self._tickets.find_all()

    def get_tickets_employe(self, employe_id: int) -> list[dict]:
        return self._tickets.find_by_employe(employe_id)

    def get_tickets_par_statut(self, statut: str) -> list[dict]:
        return self._tickets.find_by_statut(statut)

    def rechercher(self, terme: str) -> list[dict]:
        return self._tickets.search(terme)

    def rechercher_employe(self, terme: str, employe_id: int) -> list[dict]:
        return self._tickets.find_by_employe(employe_id, terme=terme)

    def get_stats(self) -> dict:
        return self._tickets.get_stats()

    # ── Commentaires ──────────────────────────────────────

    def ajouter_commentaire(self, contenu: str, ticket_id: int,
                            auteur_id: int) -> tuple[bool, str]:
        """
        Ajoute un commentaire après validation du contenu.

        Règles métier :
            - Le contenu ne peut pas être vide

        Retourne :
            (True,  "Commentaire ajouté.") si valide
            (False, message_erreur)        si le contenu est vide
        """
        if not contenu.strip():
            return False, "Le commentaire ne peut pas être vide."
        self._comments.save(Commentaire(
            contenu=contenu.strip(), ticket_id=ticket_id, auteur_id=auteur_id,
        ))
        return True, "Commentaire ajouté."

    def get_commentaires(self, ticket_id: int) -> list[dict]:
        return self._comments.find_by_ticket(ticket_id)

    # ── Utilisateurs ──────────────────────────────────────

    def get_agents(self) -> list[dict]:
        return [u for u in self._users.find_all() if u["actif"]]

    def get_user_by_id(self, user_id: int) -> dict | None:
        return self._users.find_by_id(user_id)

    def get_all_users(self) -> list[dict]:
        return self._users.find_all()

    def count_users(self) -> int:
        return self._users.count()

    def update_user_role(self, user_id: int, nouveau_role: str) -> None:
        self._users.update_role(user_id, nouveau_role)

    def modifier_utilisateur(self, user_id: int, nom: str, prenom: str, email: str,
                             mot_de_passe: str = "", confirmation: str = "") -> tuple[bool, str]:
        """
        Met à jour le profil d'un utilisateur existant.

        Règles métier :
            - Nom, prénom et email sont validés
            - L'email doit être unique (hors utilisateur lui-même)
            - Le mot de passe n'est modifié que s'il est renseigné

        Retourne :
            (True,  "Utilisateur modifié avec succès !") si valide
            (False, message_erreur)                      sinon
        """
        erreur = (valider_nom(nom, "Nom")
                  or valider_nom(prenom, "Prénom")
                  or valider_email(email))
        if erreur:
            return False, erreur

        existing = self._users.find_by_email(email.strip())
        if existing and existing["id"] != user_id:
            return False, "Cet email est déjà utilisé par un autre compte."

        self._users.update_profil(user_id, nom.strip(), prenom.strip(), email.strip())

        if mot_de_passe:
            erreur_mdp = valider_mot_de_passe(mot_de_passe, confirmation or None)
            if erreur_mdp:
                return False, erreur_mdp
            self._users.update_mot_de_passe(user_id, hasher_mot_de_passe(mot_de_passe))

        return True, "Utilisateur modifié avec succès !"

    def creer_utilisateur(self, nom: str, prenom: str, email: str,
                          mot_de_passe: str, confirmation: str,
                          role: str) -> tuple[bool, str]:
        """
        Crée un nouvel utilisateur avec le rôle choisi (réservé à l'admin).

        Règles métier :
            - Nom et prénom : lettres uniquement (2 à 50 caractères)
            - Email : format valide et unique en base
            - Mot de passe : minimum 6 caractères, une lettre et un chiffre
            - Confirmation : doit correspondre au mot de passe
            - Rôle : valeur parmi ROLES

        Retourne :
            (True,  "Utilisateur créé avec succès !") si valide
            (False, message_erreur)                   sinon
        """
        erreur = (valider_nom(nom, "Nom")
                  or valider_nom(prenom, "Prénom")
                  or valider_email(email)
                  or valider_mot_de_passe(mot_de_passe, confirmation))
        if erreur:
            return False, erreur
        if role not in ROLES:
            return False, "Rôle invalide."
        if self._users.find_by_email(email.strip()):
            return False, "Cet email est déjà utilisé."
        self._users.save(Utilisateur(
            nom=nom.strip(), prenom=prenom.strip(),
            email=email.strip(), mot_de_passe=hasher_mot_de_passe(mot_de_passe), role=role,
        ))
        return True, "Utilisateur créé avec succès !"
