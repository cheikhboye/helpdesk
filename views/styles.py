import tkinter as tk
from tkinter import ttk


# ── Palette ───────────────────────────────────────────────
BG_APP     = "#f0f4f8"
BG_CARD    = "#ffffff"
BG_TOOLBAR = "#e2e8f0"
BG_COMMENT = "#f8fafc"

TEXT_PRIMARY   = "#1e293b"
TEXT_SECONDARY = "#64748b"
TEXT_MUTED     = "#94a3b8"

# En-têtes par rôle
HDR_EMPLOYE = "#1e40af"
HDR_AGENT   = "#b45309"
HDR_ADMIN   = "#6b21a8"

# Boutons
BTN_PRIMARY = "#1e40af"
BTN_SUCCESS = "#15803d"
BTN_DANGER  = "#dc2626"
BTN_NEUTRAL = "#475569"
BTN_DARK    = "#334155"

# ── Polices ───────────────────────────────────────────────
F_TITLE      = ("Helvetica Neue", 22, "bold")
F_HEADER     = ("Helvetica Neue", 13, "bold")
F_LABEL_BOLD = ("Helvetica Neue", 10, "bold")
F_BODY       = ("Helvetica Neue", 10)
F_ENTRY      = ("Helvetica Neue", 11)
F_SMALL_BOLD = ("Helvetica Neue", 9, "bold")
F_SMALL      = ("Helvetica Neue", 9)
F_LARGE_NUM  = ("Helvetica Neue", 28, "bold")

# ── Tags Treeview par statut ──────────────────────────────
STATUT_TAGS = {
    "ouvert":     ("#dbeafe", "#1e40af"),
    "en_cours":   ("#fef3c7", "#92400e"),
    "en_attente": ("#ede9fe", "#5b21b6"),
    "resolu":     ("#d1fae5", "#065f46"),
    "ferme":      ("#f1f5f9", "#475569"),
}


def create_dropdown(parent: tk.Widget, options: list, default: str = None,
                   on_change=None, width: int = 14) -> tuple:
    """
    Menu déroulant macOS-compatible via tk.OptionMenu.
    ttk.Combobox en readonly ignore les couleurs sur macOS — OptionMenu les respecte.
    Retourne (widget, StringVar).
    """
    var = tk.StringVar(value=default if default is not None else options[0])
    menu = tk.OptionMenu(parent, var, *options)
    menu.configure(
        bg=BG_CARD, fg=TEXT_PRIMARY, font=F_BODY,
        relief="flat", bd=0,
        highlightthickness=1, highlightbackground="#cbd5e1",
        activebackground=BG_TOOLBAR, activeforeground=TEXT_PRIMARY,
        width=width,
    )
    menu["menu"].configure(
        bg=BG_CARD, fg=TEXT_PRIMARY, font=F_BODY,
        activebackground=TEXT_PRIMARY, activeforeground="white",
        relief="flat", bd=0,
    )
    if on_change:
        var.trace_add("write", lambda *_: on_change())
    return menu, var


def create_button(parent: tk.Widget, text: str, command,
                  bg: str, fg: str = "white", font=None,
                  padx: int = 12, pady: int = 5) -> tk.Frame:
    """
    Bouton coloré compatible macOS.
    tk.Button ignore bg sur macOS avec relief=flat — on utilise Frame+Label.
    """
    if font is None:
        font = F_LABEL_BOLD
    frame = tk.Frame(parent, bg=bg, cursor="hand2",
                     highlightthickness=0, bd=0)
    label = tk.Label(frame, text=text, bg=bg, fg=fg, font=font,
                     cursor="hand2", padx=padx, pady=pady,
                     anchor="center")
    label.pack(fill="both", expand=True)
    frame.bind("<Button-1>", lambda e: command())
    label.bind("<Button-1>", lambda e: command())
    return frame


def add_placeholder(entry: tk.Entry, texte: str,
                    couleur_normale: str = TEXT_PRIMARY,
                    couleur_indice: str = TEXT_MUTED) -> None:
    """
    Ajoute un texte d'indication (placeholder) à un champ Entry.
    L'indice disparaît au focus et réapparaît si le champ est laissé vide.
    """
    def _afficher_indice():
        entry.delete(0, "end")
        entry.insert(0, texte)
        entry.configure(fg=couleur_indice)
        entry.placeholder_actif = True

    def _on_focus_in(_):
        if getattr(entry, "placeholder_actif", False):
            entry.delete(0, "end")
            entry.configure(fg=couleur_normale)
            entry.placeholder_actif = False

    def _on_focus_out(_):
        if not entry.get():
            _afficher_indice()

    _afficher_indice()
    entry.bind("<FocusIn>", _on_focus_in)
    entry.bind("<FocusOut>", _on_focus_out)


def render_commentaires(frame: tk.Frame, comments: list, accent_color: str,
                        wraplength: int = 540, show_date: bool = False) -> None:
    for w in frame.winfo_children():
        w.destroy()
    if not comments:
        tk.Label(frame, text="Aucun commentaire.",
                 bg=BG_CARD, fg=TEXT_MUTED, font=F_SMALL).pack(pady=10)
        return
    for c in comments:
        auteur = f"{c.get('prenom','')} {c.get('nom','')}" if c.get("nom") else "Inconnu"
        row = tk.Frame(frame, bg=BG_COMMENT, pady=6)
        row.pack(fill="x", padx=6, pady=2)
        tk.Label(row, text=f"👤 {auteur}", font=F_SMALL_BOLD,
                 bg=BG_COMMENT, fg=accent_color).pack(anchor="w", padx=6)
        tk.Label(row, text=c["contenu"], bg=BG_COMMENT, font=F_BODY,
                 fg=TEXT_PRIMARY, wraplength=wraplength,
                 justify="left").pack(anchor="w", padx=6)
        if show_date:
            tk.Label(row, text=str(c["date_creation"])[:16], bg=BG_COMMENT,
                     fg=TEXT_MUTED, font=F_SMALL).pack(anchor="e", padx=6)


def configure_treeview_tags(tree: ttk.Treeview) -> None:
    """Applique les couleurs de statut sur les tags du Treeview."""
    for statut, (bg, fg) in STATUT_TAGS.items():
        tree.tag_configure(statut, background=bg, foreground=fg)


def apply_theme(root: tk.Misc) -> None:
    """Configure le thème ttk global de l'application."""
    style = ttk.Style(root)
    style.theme_use("clam")

    # ── Notebook ──────────────────────────────────────────
    style.configure("TNotebook", background=BG_APP, borderwidth=0)
    style.configure("TNotebook.Tab",
                    background=BG_TOOLBAR, foreground=TEXT_SECONDARY,
                    padding=[14, 7], font=F_BODY)
    style.map("TNotebook.Tab",
              background=[("selected", BG_CARD)],
              foreground=[("selected", TEXT_PRIMARY)])

    # ── Treeview ──────────────────────────────────────────
    style.configure("Treeview",
                    background=BG_CARD, foreground=TEXT_PRIMARY,
                    rowheight=30, fieldbackground=BG_CARD,
                    borderwidth=0, font=F_BODY)
    style.configure("Treeview.Heading",
                    background=BG_TOOLBAR, foreground=TEXT_PRIMARY,
                    font=F_LABEL_BOLD, relief="flat", padding=[8, 6])
    style.map("Treeview",
              background=[("selected", "#dbeafe")],
              foreground=[("selected", "#1e40af")])

    # ── Scrollbar ─────────────────────────────────────────
    style.configure("TScrollbar",
                    background=BG_TOOLBAR, troughcolor=BG_APP,
                    borderwidth=0, relief="flat")

    # ── Combobox ──────────────────────────────────────────
    style.configure("TCombobox",
                    fieldbackground=BG_CARD, background=BG_CARD,
                    foreground=TEXT_PRIMARY,
                    selectforeground=TEXT_PRIMARY,
                    selectbackground=BG_TOOLBAR,
                    padding=[6, 4], font=F_BODY)
    style.map("TCombobox",
              fieldbackground=[("readonly", BG_CARD)],
              foreground=[("readonly", TEXT_PRIMARY)],
              selectbackground=[("readonly", BG_TOOLBAR)],
              selectforeground=[("readonly", TEXT_PRIMARY)])

    # Force la couleur du texte dans le champ et la liste déroulante sur macOS
    root.option_add("*TCombobox*Listbox.foreground",        TEXT_PRIMARY)
    root.option_add("*TCombobox*Listbox.background",        BG_CARD)
    root.option_add("*TCombobox*Listbox.selectForeground",  "white")
    root.option_add("*TCombobox*Listbox.selectBackground",  TEXT_PRIMARY)
    root.option_add("*TCombobox*Listbox.font",              F_BODY)
