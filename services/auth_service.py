from models.utilisateur import Utilisateur
from repositories.utilisateur_repository import UtilisateurRepository
from services.validation import valider_inscription
from services.security import hasher_mot_de_passe, verifier_mot_de_passe


class AuthService:
    """Logique métier d'authentification : connexion et inscription."""

    def __init__(self):
        self._repo = UtilisateurRepository()

    """
    Vérifie les identifiants de connexion.

    Règles métier :
        - Les deux champs sont obligatoires
        - L'email doit correspondre à un compte existant
        - Le mot de passe doit correspondre (comparaison en clair)
        - Le compte doit être actif (actif=1)

    Retourne :
        (user_dict, None)   si les identifiants sont valides
        (None, msg_erreur)  sinon
    """
    def se_connecter(self, email: str, mot_de_passe: str) -> tuple[dict | None, str | None]:
        if not email or not mot_de_passe:
            return None, "Veuillez remplir tous les champs."

        user = self._repo.find_by_email(email.strip())

        if not user:
            return None, "Aucun compte trouvé avec cet email."
        if not verifier_mot_de_passe(mot_de_passe, user["mot_de_passe"]):
            return None, "Mot de passe incorrect."
        if not user["actif"]:
            return None, "Ce compte est désactivé."

        return user, None

    """
    Crée un nouveau compte utilisateur avec le rôle « employé ».

    Règles métier :
        - Tous les champs sont obligatoires
        - Le nom et le prénom ne contiennent que des lettres (2 à 50 car.)
        - L'email doit avoir un format valide
        - Le mot de passe : minimum 6 caractères, une lettre et un chiffre
        - Les deux mots de passe doivent correspondre
        - L'email doit être unique en base

    Retourne :
        (True,  message_succès) si le compte est créé
        (False, message_erreur) si une règle n'est pas respectée
    """
    def s_inscrire(self, nom: str, prenom: str, email: str,
                   mot_de_passe: str, confirmation: str) -> tuple[bool, str]:
        erreur = valider_inscription(nom, prenom, email, mot_de_passe, confirmation)
        if erreur:
            return False, erreur
        if self._repo.find_by_email(email.strip()):
            return False, "Cet email est déjà utilisé."

        self._repo.save(Utilisateur(
            nom=nom.strip(), prenom=prenom.strip(),
            email=email.strip(), mot_de_passe=hasher_mot_de_passe(mot_de_passe), role="employe",
        ))
        return True, "Compte créé avec succès !"
