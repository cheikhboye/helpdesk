from dataclasses import dataclass
from typing import Optional


STATUTS    = ["ouvert", "en_cours", "en_attente", "resolu", "ferme"]
PRIORITES  = ["basse", "normale", "haute", "urgente"]
CATEGORIES = ["informatique", "materiel", "logiciel", "reseau", "administratif"]

COULEURS_STATUT = {
    "ouvert":     "#3b82f6",
    "en_cours":   "#f59e0b",
    "en_attente": "#8b5cf6",
    "resolu":     "#22c55e",
    "ferme":      "#64748b",
}
COULEURS_PRIO = {
    "basse":   "#22c55e",
    "normale": "#3b82f6",
    "haute":   "#f59e0b",
    "urgente": "#dc2626",
}


@dataclass
class Ticket:
    titre: str = ""
    description: str = ""
    categorie: str = "informatique"
    priorite: str = "normale"
    statut: str = "ouvert"
    employe_id: Optional[int] = None
    agent_id: Optional[int] = None
    id: Optional[int] = None
    date_creation: Optional[str] = None
    date_modification: Optional[str] = None

    def __str__(self) -> str:
        return f"[{self.id}] {self.titre} — {self.statut} ({self.priorite})"
