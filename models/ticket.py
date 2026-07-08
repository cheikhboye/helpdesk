from dataclasses import dataclass
from typing import Optional


# ── Source de vérité unique par domaine ───────────────────
# Clé = valeur BD, Valeur = libellé affiché
_STATUTS_MAP = {
    "ouvert":     "Ouvert",
    "en_cours":   "En cours",
    "en_attente": "En attente",
    "resolu":     "Résolu",
    "ferme":      "Fermé",
}
_PRIORITES_MAP = {
    "basse":   "Basse",
    "normale": "Normale",
    "haute":   "Haute",
    "urgente": "Urgente",
}
_CATEGORIES_MAP = {
    "informatique":  "Informatique",
    "materiel":      "Matériel",
    "logiciel":      "Logiciel",
    "reseau":        "Réseau",
    "administratif": "Administratif",
}

# Listes de valeurs BD (pour requêtes / logique)
STATUTS    = list(_STATUTS_MAP)
PRIORITES  = list(_PRIORITES_MAP)
CATEGORIES = list(_CATEGORIES_MAP)

# Listes de libellés affichés (pour dropdowns)
DISPLAY_STATUTS    = list(_STATUTS_MAP.values())
DISPLAY_PRIORITES  = list(_PRIORITES_MAP.values())
DISPLAY_CATEGORIES = list(_CATEGORIES_MAP.values())

# BD → libellé (pour affichage dans les tableaux)
LABEL_STATUT    = dict(_STATUTS_MAP)
LABEL_PRIORITE  = dict(_PRIORITES_MAP)
LABEL_CATEGORIE = dict(_CATEGORIES_MAP)

# Libellé → BD (pour soumettre les formulaires)
DB_STATUT    = {v: k for k, v in _STATUTS_MAP.items()}
DB_PRIORITE  = {v: k for k, v in _PRIORITES_MAP.items()}
DB_CATEGORIE = {v: k for k, v in _CATEGORIES_MAP.items()}

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
