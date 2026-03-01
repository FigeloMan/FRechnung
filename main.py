"""
FRechnung — Hauptanwendung v4.2  (Flask + pywebview)

Sicherheit:
  - Flask lauscht NUR auf 127.0.0.1 (kein Netzwerkzugriff möglich)
  - Zufälliger Port bei jedem Start (kein fixer, vorhersehbarer Port)
  - Firewall-Hinweis: Windows-Firewall blockiert 127.0.0.1 ohnehin extern
  - Kein Debug-Modus, kein Reloader
  - pywebview öffnet natives Fenster — kein Browser nötig oder involviert
"""

import threading
import sys
import os
import time
import base64
import socket
import tempfile
import subprocess
import secrets
import webview


# ──────────────────────────────────────────────
# Ressourcen-Pfad (PyInstaller-kompatibel)
# ──────────────────────────────────────────────
def resource_path(relative_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


sys.path.insert(0, resource_path("."))

import server as server_module          # ← Modul-Referenz für APP_PORT
from server import app as flask_app


# ──────────────────────────────────────────────
# Zufälligen freien Port finden
# ──────────────────────────────────────────────
def find_free_port() -> int:
    """Betriebssystem einen freien Port zuweisen lassen."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


# ──────────────────────────────────────────────
# Geheimes Token gegen CSRF/lokale Angriffe
# ──────────────────────────────────────────────
SECRET_TOKEN = secrets.token_urlsafe(32)


# ──────────────────────────────────────────────
# Temp-Dateien für PDF-Vorschau verwalten
# ──────────────────────────────────────────────
_preview_temps: list[str] = []


def _cleanup_temps() -> None:
    for p in _preview_temps[:]:
        try:
            os.unlink(p)
            _preview_temps.remove(p)
        except Exception:
            pass


# ──────────────────────────────────────────────
# pywebview JS-API
# ──────────────────────────────────────────────
class Api:
    """window.pywebview.api.* — native Dialoge & PDF-Viewer."""

    def save_pdf_dialog(
        self, pdf_base64: str, default_filename: str = "Rechnung.pdf"
    ) -> dict:
        """Öffnet nativen Windows-Speichern-Dialog."""
        windows = webview.windows
        if not windows:
            return {"ok": False, "error": "Kein Fenster gefunden."}

        result = windows[0].create_file_dialog(
            webview.SAVE_DIALOG,
            directory=os.path.expanduser("~/Documents"),
            save_filename=default_filename,
            file_types=("PDF (*.pdf)",),
        )
        if not result:
            return {"ok": False, "cancelled": True}

        path = result if isinstance(result, str) else result[0]
        if not path.lower().endswith(".pdf"):
            path += ".pdf"

        try:
            with open(path, "wb") as f:
                f.write(base64.b64decode(pdf_base64))
            return {"ok": True, "path": path}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def preview_pdf(self, pdf_base64: str, filename: str = "Vorschau.pdf") -> dict:
        """
        Schreibt PDF in Temp-Datei und öffnet mit dem Standard-PDF-Viewer
        des Systems (Adobe, Edge, Foxit, …).
        """
        try:
            _cleanup_temps()

            tmp = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf",
                prefix="FRechnung_Vorschau_",
                dir=tempfile.gettempdir(),
            )
            tmp.write(base64.b64decode(pdf_base64))
            tmp.close()
            _preview_temps.append(tmp.name)

            if sys.platform == "win32":
                os.startfile(tmp.name)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", tmp.name])
            else:
                subprocess.Popen(["xdg-open", tmp.name])

            return {"ok": True, "path": tmp.name}
        except Exception as e:
            return {"ok": False, "error": str(e)}


# ──────────────────────────────────────────────
# Flask-Server (NUR localhost, zufälliger Port)
# ──────────────────────────────────────────────
def start_flask(port: int) -> None:
    flask_app.run(
        host="127.0.0.1",   # NIEMALS "0.0.0.0" — nur lokal erreichbar
        port=port,
        debug=False,
        use_reloader=False,
        threaded=True,
    )


def wait_for_flask(port: int, timeout: int = 15) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except OSError:
            time.sleep(0.15)
    return False


# ──────────────────────────────────────────────
# Einstiegspunkt
# ──────────────────────────────────────────────
def main() -> None:
    port = find_free_port()

    # Port ins server-Modul schreiben BEVOR Flask startet.
    # Die Index-Route ersetzt __APP_PORT__ im HTML → Frontend
    # kennt immer den richtigen Port, egal welcher zufällig gewählt wurde.
    server_module.APP_PORT = port

    t = threading.Thread(target=start_flask, args=(port,), daemon=True)
    t.start()

    if not wait_for_flask(port):
        sys.exit("❌ Flask-Server konnte nicht gestartet werden.")

    api = Api()

    webview.create_window(
        title="FRechnung",
        url=f"http://127.0.0.1:{port}/",
        width=1140,
        height=880,
        min_size=(920, 680),
        resizable=True,
        text_select=False,
        js_api=api,
    )

    # debug=False → kein DevTools-Menü, kein Browser-Öffnen
    webview.start(debug=False)


if __name__ == "__main__":
    main()
