import tkinter as tk
from tkinter import messagebox
from controllers.ticket_controller import TicketController
from models.ticket import (DB_PRIORITE, DB_CATEGORIE,
                           LABEL_STATUT, LABEL_CATEGORIE, LABEL_PRIORITE)
from views.styles import (
    BG_APP, BG_CARD, BG_TOOLBAR,
    HDR_EMPLOYE, BTN_PRIMARY, BTN_SUCCESS, BTN_NEUTRAL,
    TEXT_PRIMARY, TEXT_MUTED,
    F_LABEL_BOLD, F_BODY, F_SMALL_BOLD, F_SMALL,
    create_button, create_header, create_search_bar,
    create_treeview, champ_texte, champ_description, champ_categorie_priorite,
    afficher_description, create_info_cards, create_comment_input,
    envoyer_commentaire, render_commentaires, appliquer_resultat, deconnecter,
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
        self.protocol("WM_DELETE_WINDOW", lambda: deconnecter(self))
        self._build_ui()
        self._charger_tickets()

    def _build_ui(self):
        create_header(self, HDR_EMPLOYE,
                      f"🎫 Helpdesk  |  Employé : {self.user['prenom']} {self.user['nom']}",
                      lambda: deconnecter(self))

        # ── Barre d'outils ────────────────────────────────
        toolbar = tk.Frame(self, bg=BG_TOOLBAR, pady=8)
        toolbar.pack(fill="x")
        create_button(toolbar, "＋  Nouveau ticket", self._nouveau_ticket,
                      bg=BTN_SUCCESS, font=F_LABEL_BOLD, pady=4
                      ).pack(side="left", padx=12)
        create_button(toolbar, "↺  Actualiser", self._charger_tickets,
                      bg=BTN_NEUTRAL, font=F_BODY, pady=4
                      ).pack(side="left", padx=4)

        self.e_search = create_search_bar(toolbar, HDR_EMPLOYE, self._rechercher)

        # ── Tableau ───────────────────────────────────────
        widths = {
            "N°": (55, "center"), "Titre": (310, "center"), "Catégorie": (120, "center"),
            "Priorité": (90, "center"), "Statut": (110, "center"), "Date": (140, "center"),
        }
        self.tree = create_treeview(
            self, ("N°", "Titre", "Catégorie", "Priorité", "Statut", "Date"),
            widths, height=18, padx=12, pady=8)
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

        self.e_titre = champ_texte(frame, "Titre *", hdr_color=HDR_EMPLOYE,
                                   valeur=self.ticket["titre"] if self.edition else "")

        self.e_desc = champ_description(
            frame, valeur=self.ticket.get("description", "") if self.edition else "")

        self.cat_var, self.prio_var = champ_categorie_priorite(
            frame, self.ticket if self.edition else None)

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
        appliquer_resultat(self, self.lbl_msg, self.callback, ok, msg)


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

        create_info_cards(self, [
            ("Statut", t["statut"]), ("Priorité", t["priorite"]),
            ("Catégorie", t["categorie"]),
            ("Créé le", str(t["date_creation"])[:16]),
        ], BG_TOOLBAR)

        afficher_description(self, t["description"])

        tk.Label(self, text="Commentaires :", font=F_LABEL_BOLD,
                 bg=BG_APP, fg=TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(12, 2))
        self.frame_comments = tk.Frame(self, bg=BG_CARD, relief="flat", bd=1)
        self.frame_comments.pack(fill="both", expand=True, padx=16)
        self._charger_commentaires()

        self.e_comment = create_comment_input(self, HDR_EMPLOYE, BTN_PRIMARY, self._commenter)

    def _charger_commentaires(self):
        render_commentaires(self.frame_comments, self.ctrl.get_commentaires(self.ticket_id),
                            HDR_EMPLOYE, show_date=True)

    def _commenter(self):
        envoyer_commentaire(self.ctrl, self.e_comment, self.ticket_id,
                            self.user["id"], self._charger_commentaires, self)

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
