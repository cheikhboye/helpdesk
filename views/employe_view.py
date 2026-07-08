import tkinter as tk
from tkinter import ttk, messagebox
from controllers.ticket_controller import TicketController
from models.ticket import (DISPLAY_PRIORITES, DISPLAY_CATEGORIES,
                           DB_PRIORITE, DB_CATEGORIE,
                           LABEL_STATUT, LABEL_CATEGORIE, LABEL_PRIORITE)
from views.styles import (
    BG_APP, BG_CARD, BG_TOOLBAR, BG_COMMENT,
    HDR_EMPLOYE, BTN_PRIMARY, BTN_SUCCESS, BTN_NEUTRAL, BTN_DANGER,
    TEXT_PRIMARY, TEXT_MUTED,
    F_HEADER, F_LABEL_BOLD, F_BODY, F_ENTRY, F_SMALL_BOLD, F_SMALL,
    configure_treeview_tags, create_button, create_dropdown, add_placeholder,
    render_commentaires,
)


class EmployeView(tk.Toplevel):
    def __init__(self, user, parent):
        super().__init__(parent)
        self.user   = user
        self.parent = parent
        self.ctrl   = TicketController()
        self.title(f"Helpdesk — Espace Employé : {user['prenom']} {user['nom']}")
        self.geometry("950x640")
        self.configure(bg=BG_APP)
        self.protocol("WM_DELETE_WINDOW", self._deconnecter)
        self._build_ui()
        self._charger_tickets()

    def _build_ui(self):
        # ── En-tête ───────────────────────────────────────
        hdr = tk.Frame(self, bg=HDR_EMPLOYE, height=56)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"🎫 Helpdesk  |  Employé : {self.user['prenom']} {self.user['nom']}",
                 font=F_HEADER, bg=HDR_EMPLOYE, fg="white").pack(side="left", padx=16, pady=14)
        create_button(hdr, "Déconnexion", self._deconnecter,
                      bg=BTN_DANGER, font=F_SMALL_BOLD, pady=6
                      ).pack(side="right", padx=16, pady=10)

        # ── Barre d'outils ────────────────────────────────
        toolbar = tk.Frame(self, bg=BG_TOOLBAR, pady=8)
        toolbar.pack(fill="x")
        create_button(toolbar, "＋  Nouveau ticket", self._nouveau_ticket,
                      bg=BTN_SUCCESS, font=F_LABEL_BOLD, pady=4
                      ).pack(side="left", padx=12)
        create_button(toolbar, "↺  Actualiser", self._charger_tickets,
                      bg=BTN_NEUTRAL, font=F_BODY, pady=4
                      ).pack(side="left", padx=4)

        self.e_search = tk.Entry(toolbar, font=F_BODY, relief="flat", bg=BG_CARD,
                                 fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                 highlightthickness=1, highlightbackground="#cbd5e1",
                                 highlightcolor=HDR_EMPLOYE, width=26)
        self.e_search.pack(side="left", padx=(16, 4), ipady=4)
        self.e_search.bind("<Return>", lambda _: self._rechercher())
        create_button(toolbar, "🔍 Rechercher", self._rechercher,
                      bg=BTN_PRIMARY, font=F_BODY, pady=4
                      ).pack(side="left", padx=2)

        # ── Tableau ───────────────────────────────────────
        cols = ("N°", "Titre", "Catégorie", "Priorité", "Statut", "Date")
        frame_table = tk.Frame(self, bg=BG_APP)
        frame_table.pack(fill="both", expand=True, padx=12, pady=8)

        self.tree = ttk.Treeview(frame_table, columns=cols, show="headings", height=18)
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.column("N°",        width=55,  anchor="center")
        self.tree.column("Titre",     width=310, anchor="center")
        self.tree.column("Catégorie", width=120, anchor="center")
        self.tree.column("Priorité",  width=90,  anchor="center")
        self.tree.column("Statut",    width=110, anchor="center")
        self.tree.column("Date",      width=140, anchor="center")

        scroll = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        configure_treeview_tags(self.tree)
        self.tree.bind("<Double-1>", self._voir_ticket)

        tk.Label(self, text="Double-cliquez sur un ticket pour voir les détails",
                 bg=BG_APP, fg=TEXT_MUTED, font=F_SMALL).pack(pady=4)

    def _charger_tickets(self):
        self.e_search.delete(0, "end")
        self._afficher_tickets(self.ctrl.get_tickets_employe(self.user["id"]))

    def _rechercher(self):
        terme = self.e_search.get().strip()
        if not terme:
            self._charger_tickets()
            return
        self._afficher_tickets(self.ctrl.rechercher_employe(terme, self.user["id"]))

    def _afficher_tickets(self, tickets):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for t in tickets:
            self.tree.insert("", "end", iid=str(t["id"]), tags=(t["statut"],), values=(
                f"N°{t['id']}",
                t["titre"],
                LABEL_CATEGORIE.get(t["categorie"], t["categorie"]),
                LABEL_PRIORITE.get(t["priorite"],  t["priorite"]),
                LABEL_STATUT.get(t["statut"],       t["statut"]),
                t["date_creation"][:16] if t["date_creation"] else ""
            ))

    def _nouveau_ticket(self):
        _FormulaireTicket(self, self.user["id"], self.ctrl, self._charger_tickets)

    def _voir_ticket(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        ticket_id = int(sel[0])
        _DetailTicket(self, ticket_id, self.user, self.ctrl, self._charger_tickets)

    def _deconnecter(self):
        self.destroy()
        self.parent.deiconify()


class _FormulaireTicket(tk.Toplevel):
    def __init__(self, parent, employe_id, ctrl, callback, ticket=None):
        super().__init__(parent)
        self.employe_id = employe_id
        self.ctrl       = ctrl
        self.callback   = callback
        self.ticket     = ticket
        self.edition    = ticket is not None
        self.title("Modifier le ticket" if self.edition else "Nouveau ticket")
        self.geometry("500x430")
        self.configure(bg=BG_APP)
        self.resizable(False, False)
        self._build()

    def _build(self):
        titre = "Modifier le ticket" if self.edition else "Nouveau ticket"
        tk.Label(self, text=titre, font=("Helvetica Neue", 14, "bold"),
                 bg=BG_APP, fg=TEXT_PRIMARY).pack(pady=14)

        frame = tk.Frame(self, bg=BG_APP, padx=24)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Titre *", bg=BG_APP, font=F_LABEL_BOLD,
                 fg=TEXT_PRIMARY).pack(anchor="w", pady=(8, 2))
        self.e_titre = tk.Entry(frame, font=F_ENTRY, relief="flat", bg=BG_CARD,
                                fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                highlightthickness=1, highlightbackground="#cbd5e1",
                                highlightcolor=HDR_EMPLOYE)
        self.e_titre.pack(fill="x", ipady=6)

        tk.Label(frame, text="Description", bg=BG_APP, font=F_LABEL_BOLD,
                 fg=TEXT_PRIMARY).pack(anchor="w", pady=(8, 2))
        self.e_desc = tk.Text(frame, height=4, font=F_BODY, relief="flat",
                              bg=BG_CARD, fg=TEXT_PRIMARY,
                              insertbackground=TEXT_PRIMARY,
                              highlightthickness=1,
                              highlightbackground="#cbd5e1")
        self.e_desc.pack(fill="x")

        row = tk.Frame(frame, bg=BG_APP)
        row.pack(fill="x", pady=(12, 0))
        tk.Label(row, text="Catégorie", bg=BG_APP, font=F_LABEL_BOLD,
                 fg=TEXT_PRIMARY).pack(side="left")
        cat_def = LABEL_CATEGORIE.get(self.ticket["categorie"]) if self.edition else DISPLAY_CATEGORIES[0]
        cat_menu, self.cat_var = create_dropdown(row, DISPLAY_CATEGORIES,
                                                  default=cat_def, width=16)
        cat_menu.pack(side="left", padx=(6, 20))
        tk.Label(row, text="Priorité", bg=BG_APP, font=F_LABEL_BOLD,
                 fg=TEXT_PRIMARY).pack(side="left")
        prio_def = LABEL_PRIORITE.get(self.ticket["priorite"]) if self.edition else "Normale"
        prio_menu, self.prio_var = create_dropdown(row, DISPLAY_PRIORITES,
                                                    default=prio_def, width=12)
        prio_menu.pack(side="left", padx=6)

        if self.edition:
            self.e_titre.insert(0, self.ticket["titre"])
            self.e_desc.insert("1.0", self.ticket["description"] or "")

        self.lbl_msg = tk.Label(frame, text="", fg="#dc2626", bg=BG_APP, font=F_SMALL)
        self.lbl_msg.pack(pady=6)

        btn_text = "Enregistrer les modifications" if self.edition else "Soumettre le ticket"
        create_button(frame, btn_text, self._soumettre,
                      bg=BTN_PRIMARY, pady=8).pack(fill="x")

    def _soumettre(self):
        cat  = DB_CATEGORIE.get(self.cat_var.get(),  self.cat_var.get())
        prio = DB_PRIORITE.get(self.prio_var.get(), self.prio_var.get())
        if self.edition:
            ok, msg = self.ctrl.modifier_ticket(
                self.ticket["id"], self.e_titre.get(),
                self.e_desc.get("1.0", "end-1c"), cat, prio
            )
        else:
            ok, msg = self.ctrl.creer_ticket(
                self.e_titre.get(), self.e_desc.get("1.0", "end-1c"),
                cat, prio, self.employe_id
            )
        if ok:
            messagebox.showinfo("Succès", msg, parent=self)
            self.callback()
            self.destroy()
        else:
            self.lbl_msg.config(text=msg)


class _DetailTicket(tk.Toplevel):
    def __init__(self, parent, ticket_id, user, ctrl, callback):
        super().__init__(parent)
        self.ticket_id = ticket_id
        self.user      = user
        self.ctrl      = ctrl
        self.callback  = callback
        self.title(f"Ticket #{ticket_id}")
        self.geometry("620x540")
        self.configure(bg=BG_APP)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self._build()

    def _build(self):
        t = self.ctrl.get_ticket_by_id(self.ticket_id)
        if not t:
            tk.Label(self, text="Ticket introuvable", font=F_BODY, bg=BG_APP).pack()
            return

        header = tk.Frame(self, bg=BG_APP)
        header.pack(fill="x", pady=12, padx=16)
        tk.Label(header, text=f"Ticket #{t['id']} — {t['titre']}",
                 font=("Helvetica Neue", 13, "bold"), bg=BG_APP, fg=TEXT_PRIMARY,
                 wraplength=460, justify="left").pack(side="left", anchor="w")
        create_button(header, "✎  Modifier", self._modifier,
                      bg=BTN_NEUTRAL, font=F_SMALL_BOLD, padx=10, pady=6
                      ).pack(side="right")

        info = tk.Frame(self, bg=BG_TOOLBAR, padx=12, pady=10)
        info.pack(fill="x", padx=16)
        for k, v in [("Statut", t["statut"]), ("Priorité", t["priorite"]),
                     ("Catégorie", t["categorie"]),
                     ("Créé le", str(t["date_creation"])[:16])]:
            col = tk.Frame(info, bg=BG_TOOLBAR)
            col.pack(side="left", padx=16)
            tk.Label(col, text=k, font=F_SMALL, bg=BG_TOOLBAR, fg="#64748b").pack()
            tk.Label(col, text=v, font=F_LABEL_BOLD, bg=BG_TOOLBAR,
                     fg=TEXT_PRIMARY).pack()

        tk.Label(self, text="Description :", font=F_LABEL_BOLD,
                 bg=BG_APP, fg=TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(10, 2))
        tk.Label(self, text=t["description"] or "(aucune)", bg=BG_CARD,
                 fg=TEXT_PRIMARY, font=F_BODY, wraplength=580, justify="left",
                 padx=8, pady=6).pack(fill="x", padx=16)

        tk.Label(self, text="Commentaires :", font=F_LABEL_BOLD,
                 bg=BG_APP, fg=TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(12, 2))
        self.frame_comments = tk.Frame(self, bg=BG_CARD, relief="flat", bd=1)
        self.frame_comments.pack(fill="both", expand=True, padx=16)
        self._charger_commentaires()

        add = tk.Frame(self, bg=BG_APP)
        add.pack(fill="x", padx=16, pady=8)
        self.e_comment = tk.Entry(add, font=F_BODY, relief="flat", bg=BG_CARD,
                                  fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                  highlightthickness=1, highlightbackground="#cbd5e1",
                                  highlightcolor=HDR_EMPLOYE)
        self.e_comment.pack(side="left", fill="x", expand=True, ipady=6)
        add_placeholder(self.e_comment, "Écrivez votre commentaire ici…")
        create_button(add, "Envoyer", self._commenter,
                      bg=BTN_PRIMARY, font=F_SMALL_BOLD, padx=10, pady=6
                      ).pack(side="left", padx=(8, 0))

    def _charger_commentaires(self):
        render_commentaires(self.frame_comments, self.ctrl.get_commentaires(self.ticket_id),
                            HDR_EMPLOYE, show_date=True)

    def _commenter(self):
        # Défaut True : si placeholder_actif n'est pas défini, traiter comme actif
        # pour éviter d'enregistrer le texte d'indication comme vrai commentaire.
        if getattr(self.e_comment, "placeholder_actif", True):
            contenu = ""
        else:
            contenu = self.e_comment.get()
        ok, msg = self.ctrl.ajouter_commentaire(
            contenu, self.ticket_id, self.user["id"]
        )
        if ok:
            self.e_comment.delete(0, "end")
            self.e_comment.configure(fg=TEXT_PRIMARY)
            self.e_comment.placeholder_actif = False
            self._charger_commentaires()
        else:
            messagebox.showwarning("Attention", msg, parent=self)

    def _modifier(self):
        ticket = self.ctrl.get_ticket_by_id(self.ticket_id)
        _FormulaireTicket(self, self.user["id"], self.ctrl,
                          self._apres_modification, ticket=ticket)

    def _apres_modification(self):
        self.callback()
        for w in self.winfo_children():
            w.destroy()
        ticket = self.ctrl.get_ticket_by_id(self.ticket_id)
        if not ticket:
            messagebox.showwarning(
                "Ticket introuvable",
                "Ce ticket a été supprimé.",
                parent=self,
            )
            self.destroy()
            return
        self._build()
