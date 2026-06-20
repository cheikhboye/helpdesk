from dataclasses import dataclass
from typing import Optional


@dataclass
class Commentaire:
    contenu: str = ""
    ticket_id: Optional[int] = None
    auteur_id: Optional[int] = None
    id: Optional[int] = None
    date_creation: Optional[str] = None

    def __str__(self) -> str:
        return f"Commentaire #{self.id} — ticket {self.ticket_id}"
