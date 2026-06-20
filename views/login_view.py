import tkinter as tk
from tkinter import ttk, messagebox
from controllers.auth_controller import AuthController
from views.styles import (
    BG_APP, BG_CARD, HDR_EMPLOYE, BTN_PRIMARY, BTN_SUCCESS,
    TEXT_PRIMARY, TEXT_MUTED,
    F_TITLE, F_LABEL_BOLD, F_ENTRY, F_SMALL, F_BODY,
    create_button,
)


class LoginView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Helpdesk — Connexion")
        self.geometry("480x720")
        self.resizable(False, False)
        self.configure(bg=BG_APP)
        self.auth = AuthController()
        self._build_ui()
        self.eval('tk::PlaceWindow . center')

    def _build_ui(self):
        header = tk.Frame(self, bg=HDR_EMPLOYE, height=90)
        header.pack(fill="x")
        tk.Label(header, text="🎫 Helpdesk", font=F_TITLE,
                 bg=HDR_EMPLOYE, fg="white").pack(pady=20)

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=30, pady=20)

        self.tab_login = tk.Frame(self.nb, bg=BG_APP)
        self.nb.add(self.tab_login, text="  Se connecter  ")

        tab_register = tk.Frame(self.nb, bg=BG_APP)
        self.nb.add(tab_register, text="  Créer un compte  ")

        self._build_login_tab(self.tab_login)
        self._build_register_tab(tab_register)

    # ── Helpers ───────────────────────────────────────────
    def _lbl(self, parent, text):
        tk.Label(parent, text=text, bg=BG_APP,
                 font=F_LABEL_BOLD, fg=TEXT_PRIMARY).pack(anchor="w", pady=(10, 2))

    def _entry(self, parent, show=None):
        """Champ de saisie simple avec padding interne et bordure."""
        e = tk.Entry(parent, font=F_ENTRY, relief="flat",
                     bg=BG_CARD, fg="#111827", bd=6,
                     insertbackground=TEXT_PRIMARY,
                     highlightthickness=1, highlightbackground="#cbd5e1",
                     highlightcolor=HDR_EMPLOYE, show=show)
        e.pack(fill="x")
        return e

    def _password_entry(self, parent):
        """Champ mot de passe avec bouton afficher/masquer."""
        wrapper = tk.Frame(parent, bg=BG_CARD,
                           highlightthickness=1, highlightbackground="#cbd5e1")
        wrapper.pack(fill="x")

        entry = tk.Entry(wrapper, font=F_ENTRY, relief="flat",
                         bg=BG_CARD, fg="#111827", bd=6,
                         insertbackground=TEXT_PRIMARY,
                         highlightthickness=0, show="*")
        entry.pack(side="left", fill="x", expand=True)

        visible = tk.BooleanVar(value=False)

        def _toggle():
            visible.set(not visible.get())
            entry.configure(show="" if visible.get() else "*")
            eye_lbl.configure(text="🙈" if visible.get() else "👁")

        eye_lbl = tk.Label(wrapper, text="👁", bg=BG_CARD, fg=TEXT_PRIMARY,
                           font=F_BODY, cursor="hand2", padx=8)
        eye_lbl.pack(side="right")
        eye_lbl.bind("<Button-1>", lambda _: _toggle())

        return entry

    # ── Onglet connexion ──────────────────────────────────
    def _build_login_tab(self, parent):
        frame = tk.Frame(parent, bg=BG_APP)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self._lbl(frame, "Email")
        self.e_email = self._entry(frame)
        self.e_email.insert(0, "admin@helpdesk.com")

        self._lbl(frame, "Mot de passe")
        self.e_mdp = self._password_entry(frame)
        self.e_mdp.insert(0, "admin123")

        self.lbl_erreur = tk.Label(frame, text="", fg="#dc2626",
                                   bg=BG_APP, font=F_SMALL)
        self.lbl_erreur.pack(pady=(8, 0))

        create_button(frame, "Se connecter", self._connecter,
                      bg=BTN_PRIMARY, padx=0, pady=10).pack(fill="x", pady=(10, 0))

        tk.Label(frame, text="Compte admin par défaut :\nadmin@helpdesk.com / admin123",
                 bg=BG_APP, fg=TEXT_MUTED, font=F_SMALL).pack(pady=(12, 0))

    # ── Onglet inscription ────────────────────────────────
    def _build_register_tab(self, parent):
        frame = tk.Frame(parent, bg=BG_APP)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self._lbl(frame, "Nom")
        self.r_nom = self._entry(frame)

        self._lbl(frame, "Prénom")
        self.r_prenom = self._entry(frame)

        self._lbl(frame, "Email")
        self.r_email = self._entry(frame)

        self._lbl(frame, "Mot de passe")
        self.r_mdp = self._password_entry(frame)

        self._lbl(frame, "Confirmer le mot de passe")
        self.r_confirm = self._password_entry(frame)

        self.lbl_reg_msg = tk.Label(frame, text="", fg="#dc2626",
                                    bg=BG_APP, font=F_SMALL)
        self.lbl_reg_msg.pack(pady=(6, 0))

        create_button(frame, "Créer mon compte", self._inscrire,
                      bg=BTN_SUCCESS, padx=0, pady=10).pack(fill="x", pady=(8, 0))

    # ── Actions ───────────────────────────────────────────
    def _connecter(self):
        self.lbl_erreur.config(text="")
        user, err = self.auth.se_connecter(self.e_email.get(), self.e_mdp.get())
        if err:
            self.lbl_erreur.config(text=err)
            return
        self._ouvrir_espace(user)

    def _inscrire(self):
        email = self.r_email.get()
        ok, msg = self.auth.s_inscrire(
            self.r_nom.get(), self.r_prenom.get(), email,
            self.r_mdp.get(), self.r_confirm.get()
        )
        if not ok:
            self.lbl_reg_msg.config(text=msg, fg="#dc2626")
            return
        self._reset_register_form()
        self._pre_remplir_login(email)

    def _pre_remplir_login(self, email: str) -> None:
        """Bascule vers l'onglet connexion en pré-remplissant l'email du compte créé."""
        self.e_email.delete(0, "end")
        self.e_email.insert(0, email)
        self.e_mdp.delete(0, "end")
        self.lbl_erreur.config(text="Compte créé ! Connectez-vous.", fg="#15803d")
        self.nb.select(self.tab_login)

    def _reset_register_form(self):
        for champ in (self.r_nom, self.r_prenom, self.r_email):
            champ.delete(0, "end")
        self.r_mdp.delete(0, "end")
        self.r_confirm.delete(0, "end")
        self.lbl_reg_msg.config(text="")

    def _ouvrir_espace(self, user):
        self.withdraw()
        role = user["role"]
        if role == "employe":
            from views.employe_view import EmployeView
            EmployeView(user, self)
        elif role == "agent":
            from views.agent_view import AgentView
            AgentView(user, self)
        elif role == "admin":
            from views.admin_view import AdminView
            AdminView(user, self)
