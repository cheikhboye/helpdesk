import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from views.login_view import LoginView
from views.styles import apply_theme

if __name__ == "__main__":
    app = LoginView()
    apply_theme(app)
    app.mainloop()
