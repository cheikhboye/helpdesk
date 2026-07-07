import pytest
from unittest.mock import MagicMock, patch
from services.ticket_service import TicketService


def _make_service(tickets=None, users=None, comments=None):
    """Instancie TicketService en remplaçant les vrais repositories par des mocks."""
    mock_tickets  = tickets  or MagicMock()
    mock_users    = users    or MagicMock()
    mock_comments = comments or MagicMock()

    with patch("services.ticket_service.TicketRepository",       return_value=mock_tickets), \
         patch("services.ticket_service.UtilisateurRepository",  return_value=mock_users), \
         patch("services.ticket_service.CommentaireRepository",  return_value=mock_comments):
        service = TicketService()

    return service, mock_tickets, mock_users, mock_comments


# ── creer_ticket ──────────────────────────────────────────

class TestCreerTicket:
    def test_ticket_cree_avec_succes(self):
        service, repo, *_ = _make_service()

        ok, msg = service.creer_ticket("Bug login", "Détail", "informatique",
                                       "haute", employe_id=1)

        assert ok is True
        repo.save.assert_called_once()

    def test_titre_vide_refuse(self):
        service, repo, *_ = _make_service()

        ok, msg = service.creer_ticket("   ", "Détail", "informatique",
                                       "haute", employe_id=1)

        assert ok is False
        repo.save.assert_not_called()

    def test_titre_espaces_refuse(self):
        service, repo, *_ = _make_service()

        ok, msg = service.creer_ticket("  ", "", "informatique", "normale", employe_id=2)

        assert ok is False


# ── modifier_ticket ───────────────────────────────────────

class TestModifierTicket:
    def test_modification_reussie(self):
        service, repo, *_ = _make_service()

        ok, msg = service.modifier_ticket(1, "Nouveau titre", "Desc",
                                          "logiciel", "basse")

        assert ok is True
        repo.update.assert_called_once()

    def test_titre_vide_refuse(self):
        service, repo, *_ = _make_service()

        ok, msg = service.modifier_ticket(1, "", "Desc", "logiciel", "basse")

        assert ok is False
        repo.update.assert_not_called()


# ── ajouter_commentaire ───────────────────────────────────

class TestAjouterCommentaire:
    def test_commentaire_ajoute(self):
        service, _, _, repo_com = _make_service()

        ok, msg = service.ajouter_commentaire("Super commentaire", ticket_id=1,
                                              auteur_id=2)

        assert ok is True
        repo_com.save.assert_called_once()

    def test_commentaire_vide_refuse(self):
        service, _, _, repo_com = _make_service()

        ok, msg = service.ajouter_commentaire("   ", ticket_id=1, auteur_id=2)

        assert ok is False
        repo_com.save.assert_not_called()


# ── creer_utilisateur ─────────────────────────────────────

class TestCreerUtilisateur:
    def test_creation_reussie(self):
        mock_users = MagicMock()
        mock_users.find_by_email.return_value = None
        service, _, _, _ = _make_service(users=mock_users)

        ok, msg = service.creer_utilisateur("Dupont", "Jean", "jean@example.com",
                                            "secret1", "secret1", "agent")

        assert ok is True
        mock_users.save.assert_called_once()

    def test_email_deja_utilise(self):
        mock_users = MagicMock()
        mock_users.find_by_email.return_value = {"id": 99, "email": "jean@example.com"}
        service, _, _, _ = _make_service(users=mock_users)

        ok, msg = service.creer_utilisateur("Dupont", "Jean", "jean@example.com",
                                            "secret1", "secret1", "agent")

        assert ok is False
        mock_users.save.assert_not_called()

    def test_role_invalide(self):
        mock_users = MagicMock()
        mock_users.find_by_email.return_value = None
        service, _, _, _ = _make_service(users=mock_users)

        ok, msg = service.creer_utilisateur("Dupont", "Jean", "jean@example.com",
                                            "secret1", "secret1", "superadmin")

        assert ok is False

    def test_confirmation_incorrecte(self):
        mock_users = MagicMock()
        mock_users.find_by_email.return_value = None
        service, _, _, _ = _make_service(users=mock_users)

        ok, msg = service.creer_utilisateur("Dupont", "Jean", "jean@example.com",
                                            "secret1", "autrechose", "employe")

        assert ok is False
        mock_users.save.assert_not_called()


# ── modifier_utilisateur ──────────────────────────────────

class TestModifierUtilisateur:
    def test_modification_reussie(self):
        mock_users = MagicMock()
        mock_users.find_by_email.return_value = None
        service, _, _, _ = _make_service(users=mock_users)

        ok, msg = service.modifier_utilisateur(1, "Martin", "Paul",
                                               "paul@example.com")

        assert ok is True
        mock_users.update_profil.assert_called_once()

    def test_email_pris_par_autre(self):
        mock_users = MagicMock()
        mock_users.find_by_email.return_value = {"id": 99, "email": "paul@example.com"}
        service, _, _, _ = _make_service(users=mock_users)

        ok, msg = service.modifier_utilisateur(1, "Martin", "Paul",
                                               "paul@example.com")

        assert ok is False
        mock_users.update_profil.assert_not_called()

    def test_email_identique_autorise(self):
        """L'utilisateur garde son propre email — pas de conflit."""
        mock_users = MagicMock()
        mock_users.find_by_email.return_value = {"id": 1, "email": "paul@example.com"}
        service, _, _, _ = _make_service(users=mock_users)

        ok, msg = service.modifier_utilisateur(1, "Martin", "Paul",
                                               "paul@example.com")

        assert ok is True

    def test_mdp_vide_non_modifie(self):
        mock_users = MagicMock()
        mock_users.find_by_email.return_value = None
        service, _, _, _ = _make_service(users=mock_users)

        service.modifier_utilisateur(1, "Martin", "Paul",
                                     "paul@example.com", mot_de_passe="")

        mock_users.update_mot_de_passe.assert_not_called()

    def test_nouveau_mdp_valide_mis_a_jour(self):
        mock_users = MagicMock()
        mock_users.find_by_email.return_value = None
        service, _, _, _ = _make_service(users=mock_users)

        ok, msg = service.modifier_utilisateur(1, "Martin", "Paul",
                                               "paul@example.com",
                                               mot_de_passe="nouveau1",
                                               confirmation="nouveau1")

        assert ok is True
        mock_users.update_mot_de_passe.assert_called_once()

    def test_nouveau_mdp_invalide_refuse(self):
        mock_users = MagicMock()
        mock_users.find_by_email.return_value = None
        service, _, _, _ = _make_service(users=mock_users)

        ok, msg = service.modifier_utilisateur(1, "Martin", "Paul",
                                               "paul@example.com",
                                               mot_de_passe="abc",
                                               confirmation="abc")

        assert ok is False
        mock_users.update_mot_de_passe.assert_not_called()
