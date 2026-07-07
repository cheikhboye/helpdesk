import pytest
from services.validation import (
    valider_nom,
    valider_email,
    valider_mot_de_passe,
    valider_inscription,
)


# ── valider_nom ───────────────────────────────────────────

class TestValiderNom:
    def test_nom_valide(self):
        assert valider_nom("Dupont", "Nom") is None

    def test_prenom_valide_avec_accent(self):
        assert valider_nom("Éléonore", "Prénom") is None

    def test_nom_avec_trait_dunion(self):
        assert valider_nom("Jean-Pierre", "Nom") is None

    def test_nom_vide(self):
        assert valider_nom("", "Nom") is not None

    def test_nom_espaces_seulement(self):
        assert valider_nom("   ", "Nom") is not None

    def test_nom_trop_court(self):
        assert valider_nom("A", "Nom") is not None

    def test_nom_avec_chiffre(self):
        assert valider_nom("Dupont2", "Nom") is not None

    def test_nom_avec_caractere_special(self):
        assert valider_nom("Dup@nt", "Nom") is not None

    def test_message_contient_libelle(self):
        msg = valider_nom("", "Prénom")
        assert "Prénom" in msg


# ── valider_email ─────────────────────────────────────────

class TestValiderEmail:
    def test_email_valide(self):
        assert valider_email("jean.dupont@example.com") is None

    def test_email_valide_sous_domaine(self):
        assert valider_email("user@mail.entreprise.fr") is None

    def test_email_vide(self):
        assert valider_email("") is not None

    def test_email_sans_arobase(self):
        assert valider_email("jeandupont.com") is not None

    def test_email_sans_domaine(self):
        assert valider_email("jean@") is not None

    def test_email_sans_extension(self):
        assert valider_email("jean@domaine") is not None

    def test_email_espaces(self):
        assert valider_email("   ") is not None


# ── valider_mot_de_passe ──────────────────────────────────

class TestValiderMotDePasse:
    def test_mdp_valide(self):
        assert valider_mot_de_passe("secret1") is None

    def test_mdp_vide(self):
        assert valider_mot_de_passe("") is not None

    def test_mdp_trop_court(self):
        assert valider_mot_de_passe("ab1") is not None

    def test_mdp_sans_chiffre(self):
        assert valider_mot_de_passe("abcdef") is not None

    def test_mdp_sans_lettre(self):
        assert valider_mot_de_passe("123456") is not None

    def test_confirmation_correcte(self):
        assert valider_mot_de_passe("secret1", "secret1") is None

    def test_confirmation_incorrecte(self):
        assert valider_mot_de_passe("secret1", "secret2") is not None

    def test_sans_confirmation(self):
        assert valider_mot_de_passe("secret1", None) is None


# ── valider_inscription ───────────────────────────────────

class TestValiderInscription:
    def test_inscription_valide(self):
        assert valider_inscription("Dupont", "Jean", "jean@example.com",
                                   "secret1", "secret1") is None

    def test_nom_invalide_bloque(self):
        assert valider_inscription("", "Jean", "jean@example.com",
                                   "secret1", "secret1") is not None

    def test_email_invalide_bloque(self):
        assert valider_inscription("Dupont", "Jean", "pas-un-email",
                                   "secret1", "secret1") is not None

    def test_mdp_invalide_bloque(self):
        assert valider_inscription("Dupont", "Jean", "jean@example.com",
                                   "abc", "abc") is not None

    def test_confirmation_incorrecte_bloque(self):
        assert valider_inscription("Dupont", "Jean", "jean@example.com",
                                   "secret1", "secret2") is not None
