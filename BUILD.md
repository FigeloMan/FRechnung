# FRechnung — Build-Anleitung

## Projektstruktur nach der Migration

```
FRechnung/
├── main.py                  ← NEU: ersetzt alten CTk-main.py
├── server.py                ← NEU: Flask REST-API
├── invoice_master.spec      ← NEU: PyInstaller-Konfiguration
├── requirements.txt         ← NEU: Abhängigkeiten
├── frontend/
│   └── index.html           ← NEU: React-UI (kein Build-Step nötig)
│
├── pdf_generator.py         ← UNVERÄNDERT
├── config_manager.py        ← UNVERÄNDERT
└── pdf_viewer.py            ← UNVERÄNDERT (nicht mehr aktiv verwendet)
```

---

## Schritt 1 — Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

> **Hinweis:** Falls pywebview Probleme macht, zusätzlich installieren:
> ```bash
> pip install pywebview[qt]      # Alternative: Qt-Backend
> pip install pythonnet          # Für Windows-nativen WebView2
> ```

---

## Schritt 2 — Lokal testen

```bash
python main.py
```

Das Fenster öffnet sich direkt. Im Browser ist die App **nicht** direkt
erreichbar, solange `main.py` läuft (pywebview blockiert den Thread).

Zum Debuggen im Browser:
```bash
python server.py    # Flask direkt starten
# → http://127.0.0.1:5757 im Browser öffnen
```

---

## Schritt 3 — .exe bauen

```bash
pyinstaller invoice_master.spec
```

Die fertige `.exe` liegt danach unter:
```
dist/InvoiceMaster.exe
```

> **Erste Starten dauert ~5–10 Sekunden** (PyInstaller entpackt in Temp-Ordner).
> Das ist bei `--onefile` normal.

---

## Gespeicherte Dateien

Alle Daten werden im Benutzerordner gespeichert:
```
C:\Users\<Name>\InvoiceMaster\
├── Rechnungen\          ← Gespeicherte PDFs
├── logo.png             ← Firmenlogo (nach Upload)
└── config.json          ← Firmeneinstellungen (von config_manager)
```

---

## Troubleshooting

| Problem | Lösung |
|---|---|
| Weißes Fenster beim Start | WebView2 Runtime installieren: https://developer.microsoft.com/de-de/microsoft-edge/webview2/ |
| `ModuleNotFoundError: flask_cors` | `pip install flask-cors` |
| .exe startet nicht (Antivirus) | Antivirus-Ausnahme hinzufügen oder `--key` in spec entfernen |
| Logo wird nicht angezeigt | Pfad in config.json prüfen, muss absoluter Pfad sein |
| PDF-Generierung schlägt fehl | Firmenname unter "Dienstleister" eintragen und speichern |
