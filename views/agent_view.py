import tkinter as tk
from tkinter import messagebox
from controllers.ticket_controller import TicketController
from models.ticket import (DISPLAY_STATUTS, DB_STATUT,
                           LABEL_STATUT, LABEL_CATEGORIE, LABEL_PRIORITE)
from views.styles import (
    BG_APP, BG_CARD, BG_TOOLBAR,
    HDR_AGENT, BTN_NEUTRAL, BTN_PRIMARY,
    TEXT_PRIMARY, TEXT_MUTED,
    F_LABEL_BOLD, F_BODY, F_SMALL_BOLD, F_SMALL,
    create_button, create_dropdown, create_header, create_search_bar,
    create_treeview, afficher_description, create_info_cards,
    create_comment_input, envoyer_commentaire, render_commentaires,
    deconnecter,
)


class AgentView(tk.Toplevel):
    def __init__(self, user, parent):
        super().__init__(parent)
        self.user   = user
        self.parent = parent
        self.ctrl   = TicketController()
        self.title(f"Helpdesk — Espace Agent : {user['prenom']} {user['nom']}")
        self.geometry("1050x660")
        self.configure(bg=BG_APP)
        self.protocol("WM_DELETE_WINDOW", lambda: deconnecter(self))
        self._build_ui()
        self._charger_tickets()

    def _build_ui(self):
        create_header(self, HDR_AGENT,
                      f"🎫 Helpdesk  |  Agent : {self.user['prenom']} {self.user['nom']}",
                      lambda: deconnecter(self))

        # ── Filtres ───────────────────────────────────────
        bar = tk.Frame(self, bg=BG_TOOLBAR, pady=8)
        bar.pack(fill="x")
        tk.Label(bar, text="Filtrer :", bg=BG_TOOLBAR,
                 font=F_LABEL_BOLD, fg=TEXT_PRIMARY).pack(side="left", padx=12)

        filtre_menu, self.filtre_var = create_dropdown(
            bar, ["Tous"] + DISPLAY_STATUTS, default="Tous",
            on_change=self._charger_tickets, width=12)
        filtre_menu.pack(side="left", padx=4)

        create_button(bar, "↺  Actualiser", self._charger_tickets,
                      bg=BTN_NEUTRAL, font=F_BODY, pady=4
                      ).pack(side="left", padx=8)

        self.e_search = create_search_bar(bar, HDR_AGENT, self._rechercher)

        # ── Tableau ───────────────────────────────────────
        widths = {
            "N°": (50, "center"), "Titre": (240, "center"), "Catégorie": (110, "center"),
            "Priorité": (80, "center"), "Statut": (100, "center"),
            "Employé": (120, "center"), "Agent": (120, "center"), "Date": (130, "center"),
        }
        self.tree = create_treeview(
            self, ("N°", "Titre", "Catégorie", "Priorité", "Statut", "Employé", "Agent", "Date"),
            widths, height=20, padx=12, pady=8)
        self.tree.bind("<Double-1>", self._gerer_ticket)

        tk.Label(self, text="Double-cliquez sur un ticket pour le gérer",
                 bg=BG_APP, fg=TEXT_MUTED, font=F_SMALL).pack(pady=4)

    def _charger_tickets(self):
        self.e_search.delete(0, "end")
        filtre  = self.filtre_var.get()
        filtre_db = DB_STATUT.get(filtre)
        tickets = (self.ctrl.get_tous_tickets() if filtre_db is None
                   else self.ctrl.get_tickets_par_statut(filtre_db))
        self._afficher_tickets(tickets)

    def _rechercher(self):
        terme = self.e_search.get().strip()
        if not terme:
            self._charger_tickets()
            return
        self._afficher_tickets(self.ctrl.rechercher(terme))

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
                f"{t['emp_prenom']} {t['emp_nom']}" if t.get("emp_nom") else "—",
                f"{t['agt_prenom']} {t['agt_nom']}" if t.get("agt_nom") else "Non assigné",
                str(t["date_creation"])[:16] if t["date_creation"] else ""
            ))

    def _gerer_ticket(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        ticket_id = int(sel[0])
        _GestionTicket(self, ticket_id, self.user, self.ctrl, self._charger_tickets)


class _GestionTicket(tk.Toplevel):
    def __init__(self, parent, ticket_id, user, ctrl, callback):
        super().__init__(parent)
        self.ticket_id = ticket_id
        self.user      = user
        self.ctrl      = ctrl
        self.callback  = callback
        self.title(f"Gérer ticket #{ticket_id}")
        self.geometry("640x600")
        self.configure(bg=BG_APP)
        self._build()

    def _build(self):
        t = self.ctrl.get_ticket_by_id(self.ticket_id)
        if not t:
            return

        tk.Label(self, text=f"Ticket #{t['id']} — {t['titre']}",
                 font=("Helvetica Neue", 13, "bold"), bg=BG_APP,
                 fg=TEXT_PRIMARY, wraplength=600).pack(pady=10, padx=16, anchor="w")

        create_info_cards(self, [
            ("Statut",    LABEL_STATUT.get(t["statut"],      t["statut"])),
            ("Priorité",  LABEL_PRIORITE.get(t["priorite"],  t["priorite"])),
            ("Catégorie", LABEL_CATEGORIE.get(t["categorie"], t["categorie"])),
        ], "#fef3c7")

        afficher_description(self, t["description"])

        # ── Actions ───────────────────────────────────────
        action = tk.Frame(self, bg=BG_TOOLBAR, padx=12, pady=6)
        action.pack(fill="x", padx=16, pady=(8, 0))

        tk.Label(action, text="Changer statut :", bg=BG_TOOLBAR,
                 font=F_LABEL_BOLD, fg=TEXT_PRIMARY).pack(side="left")
        self._statut_initial = t["statut"]
        statut_menu, self.statut_var = create_dropdown(
            action, DISPLAY_STATUTS,
            default=LABEL_STATUT.get(t["statut"], t["statut"]), width=14)
        statut_menu.pack(side="left", padx=6)
        create_button(action, "Appliquer", self._changer_statut,
                      bg=HDR_AGENT, font=F_SMALL_BOLD, padx=8, pady=4
                      ).pack(side="left", padx=6)

        agents = self.ctrl.get_agents()
        if agents:
            assign = tk.Frame(self, bg=BG_TOOLBAR, padx=12, pady=6)
            assign.pack(fill="x", padx=16, pady=(2, 8))
            self.agents_map = {f"{a['prenom']} {a['nom']}": a["id"] for a in agents}
            tk.Label(assign, text="Assigner à :", bg=BG_TOOLBAR,
                     font=F_LABEL_BOLD, fg=TEXT_PRIMARY).pack(side="left")
            agent_menu, self.agent_var = create_dropdown(
                assign, list(self.agents_map.keys()), width=20)
            agent_menu.pack(side="left", padx=6)
            create_button(assign, "Assigner", self._assigner,
                          bg=BTN_PRIMARY, font=F_SMALL_BOLD, padx=8, pady=4
                          ).pack(side="left", padx=4)

        # ── Commentaires ──────────────────────────────────
        tk.Label(self, text="Commentaires :", font=F_LABEL_BOLD,
                 bg=BG_APP, fg=TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(6, 2))
        self.frame_c = tk.Frame(self, bg=BG_CARD)
        self.frame_c.pack(fill="both", expand=True, padx=16)
        self._charger_commentaires()

        self.e_com = create_comment_input(self, HDR_AGENT, HDR_AGENT, self._commenter)

    def _charger_commentaires(self):
        render_commentaires(self.frame_c, self.ctrl.get_commentaires(self.ticket_id),
                            HDR_AGENT, wraplength=560)

    def _changer_statut(self):
        nouveau_display = self.statut_var.get()
        nouveau = DB_STATUT.get(nouveau_display, nouveau_display)
        if nouveau == self._statut_initial:
            messagebox.showinfo("Info", "Le statut est déjà « " + nouveau_display + " ».", parent=self)
            return
        _, msg = self.ctrl.changer_statut(self.ticket_id, nouveau)
        self._statut_initial = nouveau
        messagebox.showinfo("Info", msg, parent=self)
        self.callback()

    def _assigner(self):
        if not hasattr(self, "agents_map"):
            return
        agent_id = self.agents_map.get(self.agent_var.get())
        if not agent_id:
            messagebox.showwarning("Attention", "Sélectionnez un utilisateur.", parent=self)
            return
        _, msg = self.ctrl.assigner_ticket(self.ticket_id, agent_id)
        messagebox.showinfo("Assigné", msg, parent=self)
        self.callback()

    def _commenter(self):
        envoyer_commentaire(self.ctrl, self.e_com, self.ticket_id,
                            self.user["id"], self._charger_commentaires, self)
