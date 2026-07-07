import pytest
from unittest.mock import MagicMock, patch
from services.auth_service import AuthService


def _make_service(mock_repo):
    """Instancie AuthService en remplaçant le vrai repository par un mock."""
    with patch("services.auth_service.UtilisateurRepository", return_value=mock_repo):
        return AuthService()


def _utilisateur_actif(**kwargs):
    base = {
        "id": 1, "nom": "Dupont", "prenom": "Jean",
        "email": "jean@example.com", "mot_de_passe": "secret1",
        "role": "employe", "actif": 1,
    }
    base.update(kwargs)
    return base


# ── se_connecter ──────────────────────────────────────────

class TestSeConnecter:
    def test_connexion_reussie(self):
        repo = MagicMock()
        repo.find_by_email.return_value = _utilisateur_actif()
        service = _make_service(repo)

        user, err = service.se_connecter("jean@example.com", "secret1")

        assert err is None
        assert user["email"] == "jean@example.com"

    def test_email_inconnu(self):
        repo = MagicMock()
        repo.find_by_email.return_value = None
        service = _make_service(repo)

        user, err = service.se_connecter("inconnu@example.com", "secret1")

        assert user is None
        assert err is not None

    def test_mauvais_mot_de_passe(self):
        repo = MagicMock()
        repo.find_by_email.return_value = _utilisateur_actif()
        service = _make_service(repo)

        user, err = service.se_connecter("jean@example.com", "mauvais")

        assert user is None
        assert err is not None

    def test_compte_inactif(self):
        repo = MagicMock()
        repo.find_by_email.return_value = _utilisateur_actif(actif=0)
        service = _make_service(repo)

        user, err = service.se_connecter("jean@example.com", "secret1")

        assert user is None
        assert err is not None

    def test_champs_vides(self):
        repo = MagicMock()
        service = _make_service(repo)

        user, err = service.se_connecter("", "")

        assert user is None
        assert err is not None


# ── s_inscrire ────────────────────────────────────────────

class TestSInscrire:
    def test_inscription_reussie(self):
        repo = MagicMock()
        repo.find_by_email.return_value = None
        service = _make_service(repo)

        ok, msg = service.s_inscrire("Dupont", "Jean", "jean@example.com",
                                     "secret1", "secret1")

        assert ok is True
        repo.save.assert_called_once()

    def test_email_deja_utilise(self):
        repo = MagicMock()
        repo.find_by_email.return_value = _utilisateur_actif()
        service = _make_service(repo)

        ok, msg = service.s_inscrire("Dupont", "Jean", "jean@example.com",
                                     "secret1", "secret1")

        assert ok is False
        repo.save.assert_not_called()

    def test_nom_invalide(self):
        repo = MagicMock()
        service = _make_service(repo)

        ok, msg = service.s_inscrire("", "Jean", "jean@example.com",
                                     "secret1", "secret1")

        assert ok is False
        repo.save.assert_not_called()

    def test_email_invalide(self):
        repo = MagicMock()
        service = _make_service(repo)

        ok, msg = service.s_inscrire("Dupont", "Jean", "pas-un-email",
                                     "secret1", "secret1")

        assert ok is False

    def test_confirmation_incorrecte(self):
        repo = MagicMock()
        repo.find_by_email.return_value = None
        service = _make_service(repo)

        ok, msg = service.s_inscrire("Dupont", "Jean", "jean@example.com",
                                     "secret1", "autrechose")

        assert ok is False
        repo.save.assert_not_called()

    def test_role_employe_force(self):
        repo = MagicMock()
        repo.find_by_email.return_value = None
        service = _make_service(repo)

        service.s_inscrire("Dupont", "Jean", "jean@example.com",
                           "secret1", "secret1")

        utilisateur_sauve = repo.save.call_args[0][0]
        assert utilisateur_sauve.role == "employe"
