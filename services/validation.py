import re


EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
NOM_REGEX = re.compile(r"^[A-Za-zÀ-ÿ' -]{2,50}$")
LONGUEUR_MDP_MIN = 6


def valider_nom(valeur: str, libelle: str) -> str | None:
    """Retourne un message d'erreur ou None si le nom/prénom est valide."""
    valeur = (valeur or "").strip()
    if not valeur:
        return f"Le champ « {libelle} » est obligatoire."
    if not NOM_REGEX.match(valeur):
        return (f"Le champ « {libelle} » doit contenir uniquement des lettres "
                "(2 à 50 caractères).")
    return None


def valider_email(email: str) -> str | None:
    """Retourne un message d'erreur ou None si l'email est valide."""
    email = (email or "").strip()
    if not email:
        return "L'email est obligatoire."
    if not EMAIL_REGEX.match(email):
        return "Le format de l'email est invalide (ex. nom@domaine.com)."
    return None


def valider_mot_de_passe(mot_de_passe: str, confirmation: str | None = None) -> str | None:
    """Retourne un message d'erreur ou None si le mot de passe est valide."""
    if not mot_de_passe:
        return "Le mot de passe est obligatoire."
    if len(mot_de_passe) < LONGUEUR_MDP_MIN:
        return f"Le mot de passe doit contenir au moins {LONGUEUR_MDP_MIN} caractères."
    if not re.search(r"[A-Za-z]", mot_de_passe) or not re.search(r"\d", mot_de_passe):
        return "Le mot de passe doit contenir au moins une lettre et un chiffre."
    if confirmation is not None and mot_de_passe != confirmation:
        return "Les mots de passe ne correspondent pas."
    return None


def valider_inscription(nom: str, prenom: str, email: str,
                        mot_de_passe: str, confirmation: str) -> str | None:
    """
    Valide l'ensemble des champs d'inscription.

    Retourne le premier message d'erreur rencontré, ou None si tout est valide.
    """
    return (valider_nom(nom, "Nom")
            or valider_nom(prenom, "Prénom")
            or valider_email(email)
            or valider_mot_de_passe(mot_de_passe, confirmation))
