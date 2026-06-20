from dataclasses import dataclass
from typing import Optional


ROLES = ["employe", "agent", "admin"]


@dataclass
class Utilisateur:
    nom: str = ""
    prenom: str = ""
    email: str = ""
    mot_de_passe: str = ""
    role: str = "employe"
    id: Optional[int] = None
    date_creation: Optional[str] = None
    actif: int = 1

    def __str__(self) -> str:
        return f"{self.prenom} {self.nom} ({self.role})"
