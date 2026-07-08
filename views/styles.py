import tkinter as tk
from tkinter import ttk, messagebox

from models.ticket import (DISPLAY_CATEGORIES, DISPLAY_PRIORITES,
                           LABEL_CATEGORIE, LABEL_PRIORITE)


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


def deconnecter(view: tk.Toplevel) -> None:
    """Ferme la fenêtre d'espace et réaffiche la fenêtre de connexion."""
    view.destroy()
    view.parent.deiconify()


def create_header(parent: tk.Widget, hdr_color: str, titre: str, on_deconnecter) -> None:
    """Bandeau d'en-tête avec titre et bouton de déconnexion, commun aux espaces."""
    hdr = tk.Frame(parent, bg=hdr_color, height=56)
    hdr.pack(fill="x")
    tk.Label(hdr, text=titre, font=F_HEADER, bg=hdr_color,
             fg="white").pack(side="left", padx=16, pady=14)
    create_button(hdr, "Déconnexion", on_deconnecter,
                  bg=BTN_DANGER, font=F_SMALL_BOLD, pady=6
                  ).pack(side="right", padx=16, pady=10)


def create_search_bar(parent: tk.Widget, hdr_color: str, on_search) -> tk.Entry:
    """Champ de recherche avec bouton « Rechercher », commun aux espaces."""
    entry = tk.Entry(parent, font=F_BODY, relief="flat", bg=BG_CARD,
                     fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                     highlightthickness=1, highlightbackground="#cbd5e1",
                     highlightcolor=hdr_color, width=26)
    entry.pack(side="left", padx=(16, 4), ipady=4)
    entry.bind("<Return>", lambda _: on_search())
    create_button(parent, "🔍 Rechercher", on_search,
                  bg=BTN_PRIMARY, font=F_BODY, pady=4
                  ).pack(side="left", padx=2)
    return entry


def create_treeview(parent: tk.Widget, columns: tuple, widths: dict,
                    height: int = 15, padx: int = 8, pady: int = 6) -> ttk.Treeview:
    """Treeview avec colonnes, scrollbar et tags de statut, commun aux listes."""
    frame = tk.Frame(parent, bg=BG_APP)
    frame.pack(fill="both", expand=True, padx=padx, pady=pady)

    tree = ttk.Treeview(frame, columns=columns, show="headings", height=height)
    for col in columns:
        tree.heading(col, text=col)
        width, anchor = widths.get(col, (100, "w"))
        tree.column(col, width=width, anchor=anchor)

    scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    configure_treeview_tags(tree)
    return tree


def champ_texte(parent: tk.Widget, libelle: str, valeur: str = "",
                hdr_color: str = TEXT_PRIMARY) -> tk.Entry:
    """Crée un champ de saisie texte avec son libellé et retourne l'Entry."""
    tk.Label(parent, text=libelle, bg=BG_APP, font=F_LABEL_BOLD,
             fg=TEXT_PRIMARY).pack(anchor="w", pady=(8, 2))
    entry = tk.Entry(parent, font=F_ENTRY, relief="flat", bg=BG_CARD,
                     fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                     highlightthickness=1, highlightbackground="#cbd5e1",
                     highlightcolor=hdr_color)
    entry.pack(fill="x", ipady=5)
    if valeur:
        entry.insert(0, valeur)
    return entry


def champ_mdp(parent: tk.Widget, libelle: str) -> tk.Entry:
    """Crée un champ mot de passe masqué avec toggle 👁 et retourne l'Entry."""
    tk.Label(parent, text=libelle, bg=BG_APP, font=F_LABEL_BOLD,
             fg=TEXT_PRIMARY).pack(anchor="w", pady=(8, 2))
    wrapper = tk.Frame(parent, bg=BG_CARD,
                       highlightthickness=1, highlightbackground="#cbd5e1")
    wrapper.pack(fill="x")
    entry = tk.Entry(wrapper, font=F_ENTRY, relief="flat", bg=BG_CARD,
                     fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                     highlightthickness=0, show="*")
    entry.pack(side="left", fill="x", expand=True, ipady=5)

    def _toggle():
        entry.configure(show="" if entry.cget("show") else "*")
        eye.configure(text="🙈" if not entry.cget("show") else "👁")

    eye = tk.Label(wrapper, text="👁", bg=BG_CARD, fg=TEXT_PRIMARY,
                   font=F_BODY, cursor="hand2", padx=8)
    eye.pack(side="right")
    eye.bind("<Button-1>", lambda _: _toggle())
    return entry


def champ_description(parent: tk.Widget, valeur: str = "") -> tk.Text:
    """Crée un champ de description multi-ligne avec son libellé et retourne le Text."""
    tk.Label(parent, text="Description", bg=BG_APP, font=F_LABEL_BOLD,
             fg=TEXT_PRIMARY).pack(anchor="w", pady=(8, 2))
    text = tk.Text(parent, height=4, font=F_BODY, relief="flat",
                   bg=BG_CARD, fg=TEXT_PRIMARY,
                   insertbackground=TEXT_PRIMARY,
                   highlightthickness=1, highlightbackground="#cbd5e1")
    text.pack(fill="x")
    if valeur:
        text.insert("1.0", valeur)
    return text


def champ_categorie_priorite(parent: tk.Widget, ticket: dict = None) -> tuple:
    """
    Ligne Catégorie / Priorité, pré-remplie si `ticket` est fourni (édition).
    Retourne (cat_var, prio_var).
    """
    row = tk.Frame(parent, bg=BG_APP)
    row.pack(fill="x", pady=(12, 0))
    tk.Label(row, text="Catégorie", bg=BG_APP, font=F_LABEL_BOLD,
             fg=TEXT_PRIMARY).pack(side="left")
    cat_def = LABEL_CATEGORIE.get(ticket["categorie"]) if ticket else DISPLAY_CATEGORIES[0]
    cat_menu, cat_var = create_dropdown(row, DISPLAY_CATEGORIES, default=cat_def, width=16)
    cat_menu.pack(side="left", padx=(6, 20))
    tk.Label(row, text="Priorité", bg=BG_APP, font=F_LABEL_BOLD,
             fg=TEXT_PRIMARY).pack(side="left")
    prio_def = LABEL_PRIORITE.get(ticket["priorite"]) if ticket else "Normale"
    prio_menu, prio_var = create_dropdown(row, DISPLAY_PRIORITES, default=prio_def, width=12)
    prio_menu.pack(side="left", padx=6)
    return cat_var, prio_var


def afficher_description(parent: tk.Widget, description: str) -> None:
    """Affiche le libellé et le contenu (lecture seule) de la description d'un ticket."""
    tk.Label(parent, text="Description :", font=F_LABEL_BOLD,
             bg=BG_APP, fg=TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(10, 2))
    tk.Label(parent, text=description or "(aucune)", bg=BG_CARD,
             fg=TEXT_PRIMARY, font=F_BODY, wraplength=580, justify="left",
             padx=8, pady=6).pack(fill="x", padx=16)


def create_info_cards(parent: tk.Widget, items: list, bg_color: str) -> None:
    """Rangée de mini-cartes d'information (ex : Statut / Priorité / Catégorie)."""
    info = tk.Frame(parent, bg=bg_color, padx=12, pady=10)
    info.pack(fill="x", padx=16)
    for k, v in items:
        col = tk.Frame(info, bg=bg_color)
        col.pack(side="left", padx=16)
        tk.Label(col, text=k, font=F_SMALL, bg=bg_color, fg=TEXT_SECONDARY).pack()
        tk.Label(col, text=v, font=F_LABEL_BOLD, bg=bg_color, fg=TEXT_PRIMARY).pack()


def create_comment_input(parent: tk.Widget, hdr_color: str, btn_color: str, on_send) -> tk.Entry:
    """Champ de saisie + bouton d'envoi pour ajouter un commentaire à un ticket."""
    add = tk.Frame(parent, bg=BG_APP)
    add.pack(fill="x", padx=16, pady=8)
    entry = tk.Entry(add, font=F_BODY, relief="flat", bg=BG_CARD,
                     fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                     highlightthickness=1, highlightbackground="#cbd5e1",
                     highlightcolor=hdr_color)
    entry.pack(side="left", fill="x", expand=True, ipady=6)
    add_placeholder(entry, "Écrivez votre commentaire ici…")
    create_button(add, "Envoyer", on_send,
                  bg=btn_color, font=F_SMALL_BOLD, padx=10, pady=6
                  ).pack(side="left", padx=(8, 0))
    return entry


def envoyer_commentaire(ctrl, entry: tk.Entry, ticket_id: int, user_id: int,
                        on_success, fenetre: tk.Toplevel) -> None:
    """Envoie le contenu de `entry` comme commentaire, ou affiche l'erreur."""
    contenu = "" if getattr(entry, "placeholder_actif", True) else entry.get()
    ok, msg = ctrl.ajouter_commentaire(contenu, ticket_id, user_id)
    if ok:
        entry.delete(0, "end")
        entry.configure(fg=TEXT_PRIMARY)
        entry.placeholder_actif = False
        on_success()
    else:
        messagebox.showwarning("Attention", msg, parent=fenetre)


def appliquer_resultat(fenetre: tk.Toplevel, lbl_msg: tk.Label,
                       callback, ok: bool, msg: str) -> None:
    if ok:
        messagebox.showinfo("Succès", msg, parent=fenetre)
        callback()
        fenetre.destroy()
    else:
        lbl_msg.config(text=msg)


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
