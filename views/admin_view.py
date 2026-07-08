import tkinter as tk
from tkinter import ttk, messagebox
from controllers.ticket_controller import TicketController
from models.ticket import (COULEURS_STATUT, DISPLAY_STATUTS,
                           DB_STATUT, DB_PRIORITE, DB_CATEGORIE,
                           LABEL_STATUT, LABEL_PRIORITE)
from models.utilisateur import ROLES
from views.styles import (
    BG_APP, BG_TOOLBAR,
    HDR_ADMIN, BTN_DANGER, BTN_NEUTRAL, BTN_DARK, BTN_SUCCESS, BTN_PRIMARY,
    TEXT_PRIMARY, TEXT_SECONDARY,
    F_LABEL_BOLD, F_BODY, F_SMALL_BOLD, F_SMALL, F_LARGE_NUM,
    create_button, create_dropdown, create_header, create_search_bar,
    create_treeview, champ_texte, champ_mdp, champ_description,
    champ_categorie_priorite, appliquer_resultat, deconnecter,
)


# ── Vue principale ────────────────────────────────────────

class AdminView(tk.Toplevel):
    def __init__(self, user, parent):
        super().__init__(parent)
        self.user   = user
        self.parent = parent
        self.ctrl   = TicketController()
        self.title("Helpdesk — Administration")
        self.geometry("1100x700")
        self.configure(bg=BG_APP)
        self.protocol("WM_DELETE_WINDOW", lambda: deconnecter(self))
        self._build_ui()

    def _build_ui(self):
        create_header(self, HDR_ADMIN,
                      f"🎫 Helpdesk  |  Admin : {self.user['prenom']} {self.user['nom']}",
                      lambda: deconnecter(self))

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
            bar, ["Tous"] + DISPLAY_STATUTS, default="Tous",
            on_change=self._charger_tickets, width=12)
        filtre_menu.pack(side="left", padx=4)
        create_button(bar, "↺  Actualiser", self._charger_tickets,
                      bg=BTN_NEUTRAL, font=F_BODY, pady=4
                      ).pack(side="left", padx=8)
        create_button(bar, "＋  Créer un ticket", self._creer_ticket,
                      bg=BTN_SUCCESS, font=F_LABEL_BOLD, pady=4
                      ).pack(side="left", padx=8)

        self.e_search_t = create_search_bar(bar, HDR_ADMIN, self._rechercher_tickets)

        btn_bar = tk.Frame(parent, bg=BG_APP)
        btn_bar.pack(side="bottom", fill="x", pady=6)
        create_button(btn_bar, "✎  Modifier le ticket sélectionné",
                      self._modifier_ticket_admin,
                      bg=BTN_PRIMARY, pady=8
                      ).pack(side="left", padx=6, ipadx=10)
        create_button(btn_bar, "🗑  Supprimer ticket sélectionné",
                      self._supprimer_ticket,
                      bg=BTN_DANGER, pady=8
                      ).pack(side="left", padx=6, ipadx=10)

        widths = {
            "N°": (50, "center"), "Titre": (270, "center"), "Statut": (100, "center"),
            "Priorité": (80, "center"), "Employé": (130, "center"),
            "Agent": (130, "center"), "Date": (130, "center"),
        }
        self.tree_t = create_treeview(
            parent, ("N°", "Titre", "Statut", "Priorité", "Employé", "Agent", "Date"),
            widths, height=15)
        self._charger_tickets()

    def _charger_tickets(self):
        self.e_search_t.delete(0, "end")
        filtre    = self.filtre_var.get()
        filtre_db = DB_STATUT.get(filtre)
        tickets   = (self.ctrl.get_tous_tickets() if filtre_db is None
                     else self.ctrl.get_tickets_par_statut(filtre_db))
        self._afficher_tickets(tickets)

    def _rechercher_tickets(self):
        terme = self.e_search_t.get().strip()
        if not terme:
            self._charger_tickets()
            return
        self._afficher_tickets(self.ctrl.rechercher(terme))

    def _afficher_tickets(self, tickets):
        for row in self.tree_t.get_children():
            self.tree_t.delete(row)
        for t in tickets:
            self.tree_t.insert("", "end", iid=str(t["id"]), tags=(t["statut"],), values=(
                f"N°{t['id']}",
                t["titre"],
                LABEL_STATUT.get(t["statut"],      t["statut"]),
                LABEL_PRIORITE.get(t["priorite"],  t["priorite"]),
                f"{t['emp_prenom']} {t['emp_nom']}" if t.get("emp_nom") else "—",
                f"{t['agt_prenom']} {t['agt_nom']}" if t.get("agt_nom") else "Non assigné",
                str(t["date_creation"])[:16] if t["date_creation"] else ""
            ))

    def _creer_ticket(self):
        _FormulaireTicketAdmin(self, self.user["id"], self.ctrl, self._charger_tickets)

    def _modifier_ticket_admin(self):
        sel = self.tree_t.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez un ticket.", parent=self)
            return
        ticket = self.ctrl.get_ticket_by_id(int(sel[0]))
        if not ticket:
            return
        _FormulaireTicketAdmin(self, self.user["id"], self.ctrl,
                               self._charger_tickets, ticket=ticket)

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
        btn_frame = tk.Frame(parent, bg=BG_APP)
        btn_frame.pack(side="bottom", fill="x", pady=8)

        create_button(btn_frame, "＋  Créer un utilisateur", self._creer_utilisateur,
                      bg=BTN_SUCCESS, font=F_LABEL_BOLD, pady=5
                      ).pack(side="left", padx=6)

        create_button(btn_frame, "✏  Modifier", self._modifier_utilisateur,
                      bg=BTN_PRIMARY, font=F_LABEL_BOLD, pady=5
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

        widths = {
            "Nom": (170, "w"), "Prénom": (140, "w"), "Email": (230, "w"),
            "Rôle": (90, "center"), "Actif": (60, "center"), "Créé le": (130, "center"),
        }
        self.tree_u = create_treeview(
            parent, ("Nom", "Prénom", "Email", "Rôle", "Actif", "Créé le"),
            widths, height=15, pady=8)
        self._charger_users()

    def _charger_users(self):
        for row in self.tree_u.get_children():
            self.tree_u.delete(row)
        for u in self.ctrl.get_all_users():
            self.tree_u.insert("", "end", iid=str(u["id"]), values=(
                u["nom"], u["prenom"], u["email"],
                u["role"], "Oui" if u["actif"] else "Non",
                str(u["date_creation"])[:16] if u["date_creation"] else ""
            ))

    def _changer_role(self, nouveau_role):
        sel = self.tree_u.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez un utilisateur.", parent=self)
            return
        cible = self.ctrl.get_user_by_id(int(sel[0]))
        if not cible:
            return
        if cible["role"] == "admin":
            messagebox.showwarning(
                "Action interdite",
                "Impossible de modifier le rôle d'un administrateur.",
                parent=self,
            )
            return
        self.ctrl.update_user_role(int(sel[0]), nouveau_role)
        self._charger_users()
        messagebox.showinfo("Info", f"Rôle changé en « {nouveau_role} ».", parent=self)

    def _creer_utilisateur(self):
        _FormulaireUtilisateur(self, self.ctrl, self._charger_users)

    def _modifier_utilisateur(self):
        sel = self.tree_u.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez un utilisateur.", parent=self)
            return
        user = self.ctrl.get_user_by_id(int(sel[0]))
        if not user:
            return
        _FormulaireModificationUtilisateur(self, self.ctrl, user, self._charger_users)


# ── Formulaire de création ────────────────────────────────

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

        self.e_nom     = champ_texte(frame, "Nom *",    hdr_color=HDR_ADMIN)
        self.e_prenom  = champ_texte(frame, "Prénom *", hdr_color=HDR_ADMIN)
        self.e_email   = champ_texte(frame, "Email *",  hdr_color=HDR_ADMIN)
        self.e_mdp     = champ_mdp(frame, "Mot de passe *")
        self.e_confirm = champ_mdp(frame, "Confirmer le mot de passe *")

        tk.Label(frame, text="Rôle", bg=BG_APP, font=F_LABEL_BOLD,
                 fg=TEXT_PRIMARY).pack(anchor="w", pady=(10, 2))
        role_menu, self.role_var = create_dropdown(frame, ROLES, default="agent", width=16)
        role_menu.pack(anchor="w")

        self.lbl_msg = tk.Label(frame, text="", fg="#dc2626", bg=BG_APP, font=F_SMALL,
                                wraplength=380, justify="left")
        self.lbl_msg.pack(pady=8)

        create_button(frame, "Créer l'utilisateur", self._soumettre,
                      bg=BTN_PRIMARY, pady=8).pack(fill="x")

    def _soumettre(self):
        ok, msg = self.ctrl.creer_utilisateur(
            self.e_nom.get(), self.e_prenom.get(), self.e_email.get(),
            self.e_mdp.get(), self.e_confirm.get(), self.role_var.get()
        )
        appliquer_resultat(self, self.lbl_msg, self.callback, ok, msg)


# ── Formulaire ticket (admin) ─────────────────────────────

class _FormulaireTicketAdmin(tk.Toplevel):
    """Formulaire de création / modification de ticket pour l'administrateur."""

    def __init__(self, parent, admin_id, ctrl, callback, ticket=None):
        super().__init__(parent)
        self.admin_id = admin_id
        self.ctrl     = ctrl
        self.callback = callback
        self.ticket   = ticket
        self.edition  = ticket is not None
        self.title("Modifier le ticket" if self.edition else "Nouveau ticket")
        self.geometry("500x430")
        self.configure(bg=BG_APP)
        self.resizable(False, False)
        self._build()

    def _build(self):
        titre_label = "Modifier le ticket" if self.edition else "Nouveau ticket"
        tk.Label(self, text=titre_label, font=("Helvetica Neue", 14, "bold"),
                 bg=BG_APP, fg=TEXT_PRIMARY).pack(pady=14)

        frame = tk.Frame(self, bg=BG_APP, padx=24)
        frame.pack(fill="both", expand=True)

        self.e_titre = champ_texte(frame, "Titre *", hdr_color=HDR_ADMIN,
                                   valeur=self.ticket["titre"] if self.edition else "")

        self.e_desc = champ_description(
            frame, valeur=self.ticket.get("description", "") if self.edition else "")

        self.cat_var, self.prio_var = champ_categorie_priorite(
            frame, self.ticket if self.edition else None)

        self.lbl_msg = tk.Label(frame, text="", fg="#dc2626", bg=BG_APP, font=F_SMALL)
        self.lbl_msg.pack(pady=6)

        btn_text = "Enregistrer les modifications" if self.edition else "Créer le ticket"
        create_button(frame, btn_text, self._soumettre,
                      bg=BTN_PRIMARY, pady=8).pack(fill="x")

    def _soumettre(self):
        titre = self.e_titre.get()
        desc  = self.e_desc.get("1.0", "end-1c")
        cat  = DB_CATEGORIE.get(self.cat_var.get(),  self.cat_var.get())
        prio = DB_PRIORITE.get(self.prio_var.get(), self.prio_var.get())
        if self.edition:
            ok, msg = self.ctrl.modifier_ticket(
                self.ticket["id"], titre, desc, cat, prio
            )
        else:
            ok, msg = self.ctrl.creer_ticket(
                titre, desc, cat, prio, self.admin_id
            )
        appliquer_resultat(self, self.lbl_msg, self.callback, ok, msg)


# ── Formulaire de modification ────────────────────────────

class _FormulaireModificationUtilisateur(tk.Toplevel):
    """Formulaire de modification des informations d'un utilisateur existant."""

    def __init__(self, parent, ctrl, user: dict, callback):
        super().__init__(parent)
        self.ctrl     = ctrl
        self.user     = user
        self.callback = callback
        self.title(f"Modifier — {user['prenom']} {user['nom']}")
        self.geometry("440x560")
        self.configure(bg=BG_APP)
        self.resizable(False, False)
        self._build()

    def _build(self):
        tk.Label(self, text="Modifier l'utilisateur", font=("Helvetica Neue", 14, "bold"),
                 bg=BG_APP, fg=TEXT_PRIMARY).pack(pady=14)

        frame = tk.Frame(self, bg=BG_APP, padx=24)
        frame.pack(fill="both", expand=True)

        self.e_nom     = champ_texte(frame, "Nom *",    valeur=self.user["nom"],    hdr_color=HDR_ADMIN)
        self.e_prenom  = champ_texte(frame, "Prénom *", valeur=self.user["prenom"], hdr_color=HDR_ADMIN)
        self.e_email   = champ_texte(frame, "Email *",  valeur=self.user["email"],  hdr_color=HDR_ADMIN)

        tk.Label(frame, text="Nouveau mot de passe  (laisser vide pour ne pas changer)",
                 bg=BG_APP, font=F_SMALL, fg=TEXT_SECONDARY).pack(anchor="w", pady=(12, 2))
        self.e_mdp     = champ_mdp(frame, "Nouveau mot de passe")
        self.e_confirm = champ_mdp(frame, "Confirmer le mot de passe")

        self.lbl_msg = tk.Label(frame, text="", fg="#dc2626", bg=BG_APP, font=F_SMALL,
                                wraplength=380, justify="left")
        self.lbl_msg.pack(pady=8)

        create_button(frame, "Enregistrer les modifications", self._soumettre,
                      bg=BTN_PRIMARY, pady=8).pack(fill="x")

    def _soumettre(self):
        ok, msg = self.ctrl.modifier_utilisateur(
            self.user["id"],
            self.e_nom.get(), self.e_prenom.get(), self.e_email.get(),
            self.e_mdp.get(), self.e_confirm.get(),
        )
        appliquer_resultat(self, self.lbl_msg, self.callback, ok, msg)
