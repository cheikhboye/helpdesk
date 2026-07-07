import hashlib


def hasher_mot_de_passe(mot_de_passe: str) -> str:
    """Retourne le hash SHA-256 du mot de passe (bibliothèque standard Python)."""
    return hashlib.sha256(mot_de_passe.encode("utf-8")).hexdigest()


def verifier_mot_de_passe(mot_de_passe_clair: str, hash_stocke: str) -> bool:
    """Vérifie qu'un mot de passe en clair correspond au hash stocké en base."""
    return hasher_mot_de_passe(mot_de_passe_clair) == hash_stocke
