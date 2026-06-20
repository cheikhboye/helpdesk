import tkinter as tk
from tkinter import ttk, messagebox
from controllers.ticket_controller import TicketController
from models.ticket import STATUTS, COULEURS_STATUT
from models.utilisateur import ROLES
from views.styles import (
    BG_APP, BG_CARD, BG_TOOLBAR,
    HDR_ADMIN, BTN_DANGER, BTN_NEUTRAL, BTN_DARK, BTN_SUCCESS, BTN_PRIMARY,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    F_HEADER, F_LABEL_BOLD, F_BODY, F_ENTRY, F_SMALL_BOLD, F_SMALL, F_LARGE_NUM,
    configure_treeview_tags, create_button, create_dropdown,
)


class AdminView(tk.Toplevel):
    def __init__(self, user, parent):
        super().__init__(parent)
        self.user   = user
        self.parent = parent
        self.ctrl   = TicketController()
        self.title("Helpdesk — Administration")
        self.geometry("1100x700")
        self.configure(bg=BG_APP)
        self.protocol("WM_DELETE_WINDOW", self._deconnecter)
        self._build_ui()

    def _build_ui(self):
        hdr = tk.Frame(self, bg=HDR_ADMIN, height=56)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"🎫 Helpdesk  |  Admin : {self.user['prenom']} {self.user['nom']}",
                 font=F_HEADER, bg=HDR_ADMIN, fg="white").pack(side="left", padx=16, pady=14)
        create_button(hdr, "Déconnexion", self._deconnecter,
                      bg=BTN_DANGER, font=F_SMALL_BOLD, pady=6
                      ).pack(side="right", padx=16, pady=10)

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        tab_stats   = tk.Frame(nb, bg=BG_APP)
        tab_tickets = tk.Frame(nb, bg=BG_APP)
        tab_users   = tk.Frame(nb, bg=BG_APP)

        nb.add(tab_stats,   text="  📊 Tableau de bord  ")
        nb.add(tab_tickets, text="  🎫 Tous les tickets  ")
        nb.add(tab_users,   text="  👥 Utilisateurs  ")

        self._build_stats(tab_stats)
        self._build_tickets(tab_tickets)
        self._build_users(tab_users)

    # ── Tableau de bord ───────────────────────────────────
    def _build_stats(self, parent):
        tk.Label(parent, text="Tableau de bord",
                 font=("Helvetica Neue", 15, "bold"),
                 bg=BG_APP, fg=TEXT_PRIMARY).pack(pady=16)

        stats    = self.ctrl.get_stats()
        couleurs = {**COULEURS_STATUT, "total": "#1e293b"}

        cards = tk.Frame(parent, bg=BG_APP)
        cards.pack(pady=10)
        for key, val in stats.items():
            bg   = couleurs.get(key, "#334155")
            card = tk.Frame(cards, bg=bg, width=150, height=110, padx=10, pady=10)
            card.pack(side="left", padx=10)
            card.pack_propagate(False)
            tk.Label(card, text=str(val), font=F_LARGE_NUM, bg=bg, fg="white").pack()
            tk.Label(card, text=key.replace("_", " ").upper(),
                     font=F_SMALL_BOLD, bg=bg, fg="white").pack()

        nb_users = self.ctrl.count_users()
        tk.Label(parent, text=f"👥  {nb_users} utilisateurs enregistrés",
                 font=("Helvetica Neue", 12), bg=BG_APP,
                 fg=TEXT_SECONDARY).pack(pady=20)

    # ── Tickets ───────────────────────────────────────────
    def _build_tickets(self, parent):
        bar = tk.Frame(parent, bg=BG_TOOLBAR, pady=8)
        bar.pack(fill="x")
        tk.Label(bar, text="Filtrer :", bg=BG_TOOLBAR,
                 font=F_LABEL_BOLD, fg=TEXT_PRIMARY).pack(side="left", padx=10)
        filtre_menu, self.filtre_var = create_dropdown(
            bar, ["tous"] + STATUTS, default="tous",
            on_change=self._charger_tickets, width=12)
        filtre_menu.pack(side="left", padx=4)
        create_button(bar, "↺  Actualiser", self._charger_tickets,
                      bg=BTN_NEUTRAL, font=F_BODY, pady=4
                      ).pack(side="left", padx=8)

        cols = ("ID", "Titre", "Statut", "Priorité", "Employé", "Agent", "Date")

        create_button(parent, "🗑  Supprimer ticket sélectionné",
                      self._supprimer_ticket,
                      bg=BTN_DANGER, pady=8
                      ).pack(side="bottom", pady=6, ipadx=10)

        frame_t = tk.Frame(parent, bg=BG_APP)
        frame_t.pack(fill="both", expand=True, padx=8, pady=6)

        self.tree_t = ttk.Treeview(frame_t, columns=cols, show="headings", height=15)
        for col in cols:
            self.tree_t.heading(col, text=col)
        self.tree_t.column("ID",       width=40,  anchor="center")
        self.tree_t.column("Titre",    width=280)
        self.tree_t.column("Statut",   width=100, anchor="center")
        self.tree_t.column("Priorité", width=80,  anchor="center")
        self.tree_t.column("Employé",  width=130, anchor="center")
        self.tree_t.column("Agent",    width=130, anchor="center")
        self.tree_t.column("Date",     width=130, anchor="center")

        sc = ttk.Scrollbar(frame_t, orient="vertical", command=self.tree_t.yview)
        self.tree_t.configure(yscrollcommand=sc.set)
        self.tree_t.pack(side="left", fill="both", expand=True)
        sc.pack(side="right", fill="y")

        configure_treeview_tags(self.tree_t)

        self._charger_tickets()

    def _charger_tickets(self):
        for row in self.tree_t.get_children():
            self.tree_t.delete(row)
        filtre  = self.filtre_var.get()
        tickets = (self.ctrl.get_tous_tickets() if filtre == "tous"
                   else self.ctrl.get_tickets_par_statut(filtre))
        for t in tickets:
            self.tree_t.insert("", "end", iid=str(t["id"]), tags=(t["statut"],), values=(
                t["id"], t["titre"], t["statut"], t["priorite"],
                f"{t['emp_prenom']} {t['emp_nom']}" if t.get("emp_nom") else "—",
                f"{t['agt_prenom']} {t['agt_nom']}" if t.get("agt_nom") else "Non assigné",
                str(t["date_creation"])[:16] if t["date_creation"] else ""
            ))

    def _supprimer_ticket(self):
        sel = self.tree_t.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez un ticket.", parent=self)
            return
        if messagebox.askyesno("Confirmation", "Supprimer ce ticket ?", parent=self):
            self.ctrl.supprimer_ticket(int(sel[0]))
            self._charger_tickets()

    # ── Utilisateurs ──────────────────────────────────────
    def _build_users(self, parent):
        cols = ("ID", "Nom", "Prénom", "Email", "Rôle", "Actif", "Créé le")

        # Barre de boutons ancrée en bas (packée avant le tableau extensible)
        btn_frame = tk.Frame(parent, bg=BG_APP)
        btn_frame.pack(side="bottom", fill="x", pady=8)

        create_button(btn_frame, "＋  Créer un utilisateur", self._creer_utilisateur,
                      bg=BTN_SUCCESS, font=F_LABEL_BOLD, pady=5
                      ).pack(side="left", padx=6)

        for label, color, role in [
            ("Promouvoir en Agent", "#b45309", "agent"),
            ("Promouvoir en Admin", HDR_ADMIN,  "admin"),
            ("Rétrograder Employé", BTN_NEUTRAL, "employe"),
        ]:
            create_button(btn_frame, label, lambda r=role: self._changer_role(r),
                          bg=color, pady=5).pack(side="left", padx=6)

        create_button(btn_frame, "↺  Actualiser", self._charger_users,
                      bg=BTN_DARK, font=F_BODY, pady=5
                      ).pack(side="left", padx=6)

        frame_u = tk.Frame(parent, bg=BG_APP)
        frame_u.pack(fill="both", expand=True, padx=8, pady=8)

        self.tree_u = ttk.Treeview(frame_u, columns=cols, show="headings", height=15)
        for col in cols:
            self.tree_u.heading(col, text=col)
        self.tree_u.column("ID",      width=40,  anchor="center")
        self.tree_u.column("Nom",     width=140)
        self.tree_u.column("Prénom",  width=140)
        self.tree_u.column("Email",   width=230)
        self.tree_u.column("Rôle",    width=90,  anchor="center")
        self.tree_u.column("Actif",   width=60,  anchor="center")
        self.tree_u.column("Créé le", width=130, anchor="center")

        sc = ttk.Scrollbar(frame_u, orient="vertical", command=self.tree_u.yview)
        self.tree_u.configure(yscrollcommand=sc.set)
        self.tree_u.pack(side="left", fill="both", expand=True)
        sc.pack(side="right", fill="y")

        self._charger_users()

    def _charger_users(self):
        for row in self.tree_u.get_children():
            self.tree_u.delete(row)
        for u in self.ctrl.get_all_users():
            self.tree_u.insert("", "end", iid=str(u["id"]), values=(
                u["id"], u["nom"], u["prenom"], u["email"],
                u["role"], "Oui" if u["actif"] else "Non",
                str(u["date_creation"])[:16] if u["date_creation"] else ""
            ))

    def _changer_role(self, nouveau_role):
        sel = self.tree_u.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez un utilisateur.", parent=self)
            return
        if int(sel[0]) == self.user["id"]:
            messagebox.showwarning(
                "Action interdite",
                "Vous ne pouvez pas modifier votre propre rôle.",
                parent=self,
            )
            return
        self.ctrl.update_user_role(int(sel[0]), nouveau_role)
        self._charger_users()
        messagebox.showinfo("Info", f"Rôle changé en « {nouveau_role} ».", parent=self)

    def _creer_utilisateur(self):
        _FormulaireUtilisateur(self, self.ctrl, self._charger_users)

    def _deconnecter(self):
        self.destroy()
        self.parent.deiconify()


class _FormulaireUtilisateur(tk.Toplevel):
    """Formulaire de création d'un utilisateur (employé / agent / admin)."""

    def __init__(self, parent, ctrl, callback):
        super().__init__(parent)
        self.ctrl     = ctrl
        self.callback = callback
        self.title("Créer un utilisateur")
        self.geometry("440x530")
        self.configure(bg=BG_APP)
        self.resizable(False, False)
        self._build()

    def _build(self):
        tk.Label(self, text="Nouvel utilisateur", font=("Helvetica Neue", 14, "bold"),
                 bg=BG_APP, fg=TEXT_PRIMARY).pack(pady=14)

        frame = tk.Frame(self, bg=BG_APP, padx=24)
        frame.pack(fill="both", expand=True)

        self.e_nom     = self._champ(frame, "Nom *")
        self.e_prenom  = self._champ(frame, "Prénom *")
        self.e_email   = self._champ(frame, "Email *")
        self.e_mdp     = self._champ(frame, "Mot de passe *", password=True)
        self.e_confirm = self._champ(frame, "Confirmer le mot de passe *", password=True)

        tk.Label(frame, text="Rôle", bg=BG_APP, font=F_LABEL_BOLD,
                 fg=TEXT_PRIMARY).pack(anchor="w", pady=(10, 2))
        role_menu, self.role_var = create_dropdown(frame, ROLES,
                                                    default="agent", width=16)
        role_menu.pack(anchor="w")

        self.lbl_msg = tk.Label(frame, text="", fg="#dc2626", bg=BG_APP, font=F_SMALL,
                                wraplength=380, justify="left")
        self.lbl_msg.pack(pady=8)

        create_button(frame, "Créer l'utilisateur", self._soumettre,
                      bg=BTN_PRIMARY, pady=8).pack(fill="x")

    def _champ(self, parent, libelle, *, password=False):
        tk.Label(parent, text=libelle, bg=BG_APP, font=F_LABEL_BOLD,
                 fg=TEXT_PRIMARY).pack(anchor="w", pady=(8, 2))

        if not password:
            entry = tk.Entry(parent, font=F_ENTRY, relief="flat", bg=BG_CARD,
                             fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                             highlightthickness=1, highlightbackground="#cbd5e1",
                             highlightcolor=HDR_ADMIN)
            entry.pack(fill="x", ipady=5)
            return entry

        # Champ mot de passe avec toggle afficher/masquer
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

    def _soumettre(self):
        ok, msg = self.ctrl.creer_utilisateur(
            self.e_nom.get(), self.e_prenom.get(), self.e_email.get(),
            self.e_mdp.get(), self.e_confirm.get(), self.role_var.get()
        )
        if ok:
            messagebox.showinfo("Succès", msg, parent=self)
            self.callback()
            self.destroy()
        else:
            self.lbl_msg.config(text=msg)
