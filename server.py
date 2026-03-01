"""
FRechnung — Flask REST-API
Verbindet das React-Frontend mit pdf_generator & config_manager.
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import base64
import os
import sys
import io

from config_manager import ConfigManager
from pdf_generator import create_invoice_pdf, THEME_NAMES

# ── Ressourcenpfad (PyInstaller-kompatibel) ───────────────────────────────────
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)

FRONTEND_DIR = resource_path("frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

config_manager = ConfigManager()

# Wird von main.py gesetzt, bevor der Server startet
APP_PORT: int = 5757


# ── Frontend ──────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    """
    Liest index.html und ersetzt den Platzhalter __APP_PORT__ mit dem
    tatsächlichen Port. So kennt das Frontend immer die richtige API-URL,
    auch wenn main.py einen zufälligen Port gewählt hat.
    """
    html_path = os.path.join(FRONTEND_DIR, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    html = html.replace("__APP_PORT__", str(APP_PORT))
    return html, 200, {"Content-Type": "text/html; charset=utf-8"}

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(FRONTEND_DIR, "favicon.ico", mimetype="image/x-icon")


# ── Config: Dienstleister laden ───────────────────────────────────────────────
@app.route("/api/provider", methods=["GET"])
def get_provider():
    return jsonify(config_manager.get_service_provider())


# ── Config: Dienstleister speichern ──────────────────────────────────────────
@app.route("/api/provider", methods=["POST"])
def save_provider():
    data = request.get_json()
    try:
        config_manager.set_service_provider(data)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ── Logo: Pfad setzen ─────────────────────────────────────────────────────────
@app.route("/api/provider/logo", methods=["POST"])
def set_logo():
    data = request.get_json()
    path = data.get("path", "")
    try:
        config_manager.set_logo_path(path)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ── Logo: Datei hochladen (base64) ────────────────────────────────────────────
@app.route("/api/provider/logo/upload", methods=["POST"])
def upload_logo():
    data = request.get_json()
    b64  = data.get("data", "")
    name = data.get("name", "logo.png")
    try:
        save_dir = os.path.join(os.path.expanduser("~"), "FRechnung")
        os.makedirs(save_dir, exist_ok=True)
        path = os.path.join(save_dir, name)
        with open(path, "wb") as f:
            f.write(base64.b64decode(b64))
        config_manager.set_logo_path(path)
        return jsonify({"ok": True, "path": path})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ── Themes laden ──────────────────────────────────────────────────────────────
@app.route("/api/themes", methods=["GET"])
def get_themes():
    return jsonify(THEME_NAMES)


# ── PDF generieren ────────────────────────────────────────────────────────────
@app.route("/api/generate-pdf", methods=["POST"])
def generate_pdf():
    payload = request.get_json()

    inv_data  = payload.get("invoice",  {})
    recv_data = payload.get("receiver", {})
    items     = payload.get("items",    [])
    company   = payload.get("company",  config_manager.get_service_provider())
    theme     = payload.get("theme",    THEME_NAMES[0])
    logo      = company.get("logo_path", "")

    if not items:
        return jsonify({"ok": False, "error": "Keine Artikel übergeben."}), 400
    if not company.get("company_name"):
        return jsonify({"ok": False, "error": "Firmenname fehlt in den Einstellungen."}), 400

    try:
        result    = create_invoice_pdf(
            inv_data, recv_data, items, company,
            logo_path=logo if logo and os.path.exists(logo) else "",
            theme_name=theme,
        )
        pdf_bytes = result[0] if isinstance(result, tuple) else result
        b64       = base64.b64encode(pdf_bytes).decode("utf-8")
        return jsonify({"ok": True, "pdf_base64": b64})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ── PDF speichern ─────────────────────────────────────────────────────────────
@app.route("/api/save-pdf", methods=["POST"])
def save_pdf():
    payload   = request.get_json()
    b64       = payload.get("pdf_base64", "")
    filename  = payload.get("filename", "Rechnung.pdf")
    save_dir  = os.path.join(os.path.expanduser("~"), "FRechnung", "Rechnungen")
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, filename)
    try:
        with open(path, "wb") as f:
            f.write(base64.b64decode(b64))
        return jsonify({"ok": True, "path": path})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5757, debug=True)
