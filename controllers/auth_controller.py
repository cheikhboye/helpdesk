from services.auth_service import AuthService


class AuthController:
    """
    Endpoints d'authentification.
    Consommé par : LoginView
    """

    def __init__(self):
        self._service = AuthService()

    """
    Vérifie les identifiants et retourne l'utilisateur connecté.

    Paramètres :
        email        -- adresse email saisie
        mot_de_passe -- mot de passe en clair

    Retourne :
        (user_dict, None)   si la connexion réussit
        (None, msg_erreur)  si les identifiants sont invalides ou le compte inactif
    """
    def se_connecter(self, email: str, mot_de_passe: str) -> tuple[dict | None, str | None]:
        return self._service.se_connecter(email, mot_de_passe)

    """
    Crée un nouveau compte avec le rôle « employé ».

    Paramètres :
        nom, prenom  -- identité de l'utilisateur
        email        -- doit être unique en base
        mot_de_passe -- minimum 4 caractères
        confirmation -- doit correspondre à mot_de_passe

    Retourne :
        (True,  message_succès) si le compte est créé
        (False, message_erreur) si validation échoue ou email déjà utilisé
    """
    def s_inscrire(self, nom: str, prenom: str, email: str,
                   mot_de_passe: str, confirmation: str) -> tuple[bool, str]:
        return self._service.s_inscrire(nom, prenom, email, mot_de_passe, confirmation)

    """
    Invalide la session en cours (réservé aux extensions futures).

    Retourne :
        None
    """
    def se_deconnecter(self) -> None:
        pass
