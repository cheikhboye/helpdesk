import tkinter as tk
from tkinter import ttk, messagebox
from controllers.ticket_controller import TicketController
from models.ticket import STATUTS
from views.styles import (
    BG_APP, BG_CARD, BG_TOOLBAR, BG_COMMENT,
    HDR_AGENT, BTN_DANGER, BTN_NEUTRAL, BTN_PRIMARY,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    F_HEADER, F_LABEL_BOLD, F_BODY, F_SMALL_BOLD, F_SMALL,
    configure_treeview_tags, create_button, create_dropdown, add_placeholder,
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
        self.protocol("WM_DELETE_WINDOW", self._deconnecter)
        self._build_ui()
        self._charger_tickets()

    def _build_ui(self):
        # ── En-tête ───────────────────────────────────────
        hdr = tk.Frame(self, bg=HDR_AGENT, height=56)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"🎫 Helpdesk  |  Agent : {self.user['prenom']} {self.user['nom']}",
                 font=F_HEADER, bg=HDR_AGENT, fg="white").pack(side="left", padx=16, pady=14)
        create_button(hdr, "Déconnexion", self._deconnecter,
                      bg=BTN_DANGER, font=F_SMALL_BOLD, pady=6
                      ).pack(side="right", padx=16, pady=10)

        # ── Filtres ───────────────────────────────────────
        bar = tk.Frame(self, bg=BG_TOOLBAR, pady=8)
        bar.pack(fill="x")
        tk.Label(bar, text="Filtrer :", bg=BG_TOOLBAR,
                 font=F_LABEL_BOLD, fg=TEXT_PRIMARY).pack(side="left", padx=12)

        filtre_menu, self.filtre_var = create_dropdown(
            bar, ["tous"] + STATUTS, default="tous",
            on_change=self._charger_tickets, width=12)
        filtre_menu.pack(side="left", padx=4)

        create_button(bar, "↺  Actualiser", self._charger_tickets,
                      bg=BTN_NEUTRAL, font=F_BODY, pady=4
                      ).pack(side="left", padx=8)

        # ── Tableau ───────────────────────────────────────
        cols = ("ID", "Titre", "Catégorie", "Priorité", "Statut", "Employé", "Agent", "Date")
        frame_t = tk.Frame(self, bg=BG_APP)
        frame_t.pack(fill="both", expand=True, padx=12, pady=8)

        self.tree = ttk.Treeview(frame_t, columns=cols, show="headings", height=20)
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.column("ID",        width=40,  anchor="center")
        self.tree.column("Titre",     width=250)
        self.tree.column("Catégorie", width=110, anchor="center")
        self.tree.column("Priorité",  width=80,  anchor="center")
        self.tree.column("Statut",    width=100, anchor="center")
        self.tree.column("Employé",   width=120, anchor="center")
        self.tree.column("Agent",     width=120, anchor="center")
        self.tree.column("Date",      width=130, anchor="center")

        scroll = ttk.Scrollbar(frame_t, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        configure_treeview_tags(self.tree)
        self.tree.bind("<Double-1>", self._gerer_ticket)

        tk.Label(self, text="Double-cliquez sur un ticket pour le gérer",
                 bg=BG_APP, fg=TEXT_MUTED, font=F_SMALL).pack(pady=4)

    def _charger_tickets(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        filtre  = self.filtre_var.get()
        tickets = (self.ctrl.get_tous_tickets() if filtre == "tous"
                   else self.ctrl.get_tickets_par_statut(filtre))
        for t in tickets:
            self.tree.insert("", "end", tags=(t["statut"],), values=(
                t["id"], t["titre"], t["categorie"], t["priorite"], t["statut"],
                f"{t['emp_prenom']} {t['emp_nom']}" if t.get("emp_nom") else "—",
                f"{t['agt_prenom']} {t['agt_nom']}" if t.get("agt_nom") else "Non assigné",
                str(t["date_creation"])[:16] if t["date_creation"] else ""
            ))

    def _gerer_ticket(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        ticket_id = self.tree.item(sel[0])["values"][0]
        _GestionTicket(self, ticket_id, self.user, self.ctrl, self._charger_tickets)

    def _deconnecter(self):
        self.destroy()
        self.parent.deiconify()


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

        info = tk.Frame(self, bg="#fef3c7", padx=12, pady=10)
        info.pack(fill="x", padx=16)
        for k, v in [("Statut", t["statut"]), ("Priorité", t["priorite"]),
                     ("Catégorie", t["categorie"])]:
            col = tk.Frame(info, bg="#fef3c7")
            col.pack(side="left", padx=16)
            tk.Label(col, text=k, font=F_SMALL, bg="#fef3c7",
                     fg=TEXT_SECONDARY).pack()
            tk.Label(col, text=v, font=F_LABEL_BOLD, bg="#fef3c7",
                     fg=TEXT_PRIMARY).pack()

        tk.Label(self, text="Description :", font=F_LABEL_BOLD,
                 bg=BG_APP, fg=TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(10, 2))
        tk.Label(self, text=t["description"] or "(aucune)", bg=BG_CARD,
                 fg=TEXT_PRIMARY, font=F_BODY, wraplength=580, justify="left",
                 padx=8, pady=6).pack(fill="x", padx=16)

        # ── Actions ───────────────────────────────────────
        action = tk.Frame(self, bg=BG_TOOLBAR, padx=12, pady=8)
        action.pack(fill="x", padx=16, pady=8)

        tk.Label(action, text="Changer statut :", bg=BG_TOOLBAR,
                 font=F_LABEL_BOLD, fg=TEXT_PRIMARY).pack(side="left")
        self._statut_initial = t["statut"]
        statut_menu, self.statut_var = create_dropdown(
            action, STATUTS, default=t["statut"], width=14)
        statut_menu.pack(side="left", padx=6)
        create_button(action, "Appliquer", self._changer_statut,
                      bg=HDR_AGENT, font=F_SMALL_BOLD, padx=8, pady=4
                      ).pack(side="left", padx=6)

        agents = self.ctrl.get_agents()
        if agents:
            tk.Label(action, text="  Assigner à :", bg=BG_TOOLBAR,
                     font=F_LABEL_BOLD, fg=TEXT_PRIMARY).pack(side="left", padx=(12, 0))
            self.agents_map = {f"{a['prenom']} {a['nom']}": a["id"] for a in agents}
            agent_menu, self.agent_var = create_dropdown(
                action, list(self.agents_map.keys()), width=16)
            agent_menu.pack(side="left", padx=6)
            create_button(action, "Assigner", self._assigner,
                          bg=BTN_PRIMARY, font=F_SMALL_BOLD, padx=8, pady=4
                          ).pack(side="left", padx=4)

        # ── Commentaires ──────────────────────────────────
        tk.Label(self, text="Commentaires :", font=F_LABEL_BOLD,
                 bg=BG_APP, fg=TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(6, 2))
        self.frame_c = tk.Frame(self, bg=BG_CARD)
        self.frame_c.pack(fill="both", expand=True, padx=16)
        self._charger_commentaires()

        add = tk.Frame(self, bg=BG_APP)
        add.pack(fill="x", padx=16, pady=8)
        self.e_com = tk.Entry(add, font=F_BODY, relief="flat", bg=BG_CARD,
                              fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY, bd=6,
                              highlightthickness=1, highlightbackground="#cbd5e1",
                              highlightcolor=HDR_AGENT)
        self.e_com.pack(side="left", fill="x", expand=True)
        add_placeholder(self.e_com, "Écrivez votre commentaire ici…")
        create_button(add, "Envoyer", self._commenter,
                      bg=HDR_AGENT, font=F_SMALL_BOLD, padx=10, pady=6
                      ).pack(side="left", padx=(8, 0))

    def _charger_commentaires(self):
        for w in self.frame_c.winfo_children():
            w.destroy()
        comments = self.ctrl.get_commentaires(self.ticket_id)
        if not comments:
            tk.Label(self.frame_c, text="Aucun commentaire.",
                     bg=BG_CARD, fg=TEXT_MUTED, font=F_SMALL).pack(pady=10)
        for c in comments:
            auteur = f"{c.get('prenom','')} {c.get('nom','')}" if c.get("nom") else "Inconnu"
            row = tk.Frame(self.frame_c, bg=BG_COMMENT, pady=5)
            row.pack(fill="x", padx=4, pady=2)
            tk.Label(row, text=f"👤 {auteur}", font=F_SMALL_BOLD,
                     bg=BG_COMMENT, fg=HDR_AGENT).pack(anchor="w", padx=6)
            tk.Label(row, text=c["contenu"], bg=BG_COMMENT, font=F_BODY,
                     fg=TEXT_PRIMARY, wraplength=560,
                     justify="left").pack(anchor="w", padx=6)

    def _changer_statut(self):
        nouveau = self.statut_var.get()
        if nouveau == self._statut_initial:
            messagebox.showinfo("Info", "Le statut est déjà « " + nouveau + " ».", parent=self)
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
            return
        _, msg = self.ctrl.assigner_ticket(self.ticket_id, agent_id)
        messagebox.showinfo("Info", msg, parent=self)
        self.callback()

    def _commenter(self):
        if getattr(self.e_com, "placeholder_actif", True):
            contenu = ""
        else:
            contenu = self.e_com.get()
        ok, msg = self.ctrl.ajouter_commentaire(
            contenu, self.ticket_id, self.user["id"]
        )
        if ok:
            self.e_com.delete(0, "end")
            self.e_com.configure(fg=TEXT_PRIMARY)
            self.e_com.placeholder_actif = False
            self._charger_commentaires()
        else:
            messagebox.showwarning("Attention", msg, parent=self)
