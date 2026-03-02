# FRechnung
## **Offizielle Webseite: [frechnung.de](https://frechnung.de)**
> Rechnungserstellung mit ZUGFeRD 2.2 / Factur-X Basic — EN 16931 konform

---

## Übersicht

**FRechnung** ist eine Desktop-Anwendung zur einfachen und professionellen Erstellung von Rechnungen als PDF. Die generierten PDFs enthalten eingebettetes maschinenlesbares XML nach dem **ZUGFeRD 2.2 / Factur-X Basic**-Standard, vollständig konform zur europäischen Norm **EN 16931**.

### Highlights
   Offiziele Seite frechnung.de
- Elegante PDF-Rechnungen in **22 wählbaren Design-Themen**
- **EN 16931 konformes XML** eingebettet (ZUGFeRD 2.2 / Factur-X Basic)
- **B2C-, B2B- und B2G-Modus** — je nach Rechnungsart werden die passenden Pflicht- und Optionalfelder eingeblendet
- Integrierter **PDF-Viewer** mit Zoom, Seitennavigation und Scrollen
- Persistente Einstellungen für Firmendaten und Bankverbindung
- Firmenlogo im PDF oben links
- SEPA-konforme IBAN/BIC im XML

---

## Installation

### Voraussetzungen

- Python 3.10 oder neuer

### Abhängigkeiten installieren

```bash
pip install flask flask-cors pywebview pyinstaller reportlab Pillow cryptography keyring
```

### Schriftarten (optional, empfohlen)

Für Unicode-Unterstützung (€-Zeichen, Umlaute) die Dateien in das Anwendungsverzeichnis legen:

```
DejaVuSans.ttf
DejaVuSans-Bold.ttf
```

Download: [dejavu-fonts.github.io](https://dejavu-fonts.github.io/)

Ohne diese Dateien verwendet die Anwendung automatisch Helvetica als Fallback.

---

## Projektstruktur

```
invoice-master/
├── main.py              # Hauptanwendung (GUI)
├── pdf_generator.py     # PDF-Erzeugung + ZUGFeRD-XML-Generator
├── config_manager.py    # Einstellungsverwaltung (JSON)
├── DejaVuSans.ttf       # (optional) Unicode-Schrift
├── DejaVuSans-Bold.ttf  # (optional) Unicode-Schrift Bold
└── README.md
```

---

## Starten

```bash
python main.py
```

---

## Bedienungsanleitung

### Rechnungsart wählen

Oben in der Anwendung kann zwischen drei Rechnungsarten gewählt werden:

| Modus | Zielgruppe | Besonderheiten |
|-------|-----------|----------------|
| **B2C** | Privatpersonen | Minimalfelder, keine USt-ID des Kunden |
| **B2B** | Unternehmen | Kundennummer und Kunden-USt-ID einblendbar |
| **B2G** | Behörden / öffentliche Auftraggeber | Leitweg-ID (Pflicht), Vertragsnummer, Kostenstelle |

### Rechnung erstellen

1. **Rechnungsart wählen** (B2C / B2B / B2G)
2. **Tab „Rechnungsdaten" öffnen**
3. **Kundendaten ausfüllen**
   - Kundenname (Pflichtfeld)
   - Anschrift (Straße in Zeile 1, PLZ und Ort in Zeile 2 — wichtig für korrektes XML)
   - Objekt / Bauvorhaben, Ausführung (optional)
   - Leistungszeitraum als Freitext (z. B. „01.01.2026 – 31.01.2026")
4. **Modusabhängige Felder ausfüllen**
   - *B2B:* Kundennummer, USt-ID des Kunden (optional)
   - *B2G:* siehe Abschnitt [B2G — E-Rechnung an öffentliche Auftraggeber](#b2g--e-rechnung-an-öffentliche-auftraggeber)
5. **Rechnungsinformationen ausfüllen**
   - Rechnungsnummer (Pflichtfeld)
   - Rechnungsdatum und Lieferdatum (Standard: heute)
   - Umsatzsteuersatz (Standard: 19 %)
   - Rabatt in % (Standard: 0)
   - Zahlungsziel in Tagen (Standard: 14) → Fälligkeitsdatum wird automatisch berechnet
   - Bestellnummer / Käuferreferenz (optional)
   - Zahlungshinweis / Schlusstext (vorausgefüllt, anpassbar)
   - Interne Bemerkungen (erscheinen klein am Seitenende)
6. **Artikel hinzufügen**
   - Bezeichnung, Menge, Einheit und Netto-Einzelpreis eingeben
   - „+ Hinzufügen" klicken
   - Positionen erscheinen in der Liste; einzelne Zeilen oder alle Positionen können entfernt werden
7. **Design-Thema wählen** (Dropdown)
8. **„Berechnen"** → Brutto- und Nettobetrag werden angezeigt
9. **„PDF generieren"** → Vorschau öffnen oder Speichern

### B2G — E-Rechnung an öffentliche Auftraggeber

Bei Auswahl des Modus **B2G** werden zusätzliche Pflicht- und Optionalfelder eingeblendet, die für die Einreichung von E-Rechnungen an Behörden und öffentliche Auftraggeber (gemäß E-Rechnungsgesetz / EU-Richtlinie 2014/55/EU) benötigt werden:

| Feld | Pflicht | Beschreibung |
|------|---------|-------------|
| **Leitweg-ID** | ✅ Pflicht | Eindeutige Routing-Kennung des Empfängers, z. B. `991-1234567890-06`. Wird vom Auftraggeber mitgeteilt und im XML als `BuyerReference` eingetragen. |
| **Vertragsnummer / Auftragsnummer** | Optional | Referenz auf den zugrundeliegenden Vertrag oder die Bestellnummer der Behörde, z. B. `VTR-2025-001`. |
| **Kostenstelle / Haushaltsstelle** | Optional | Interne Haushaltszuordnung des Auftraggebers, z. B. `4200-001`. |

> **Hinweis zur Leitweg-ID:** Die Leitweg-ID ist bei B2G-Rechnungen nach EN 16931 im Feld `BuyerReference` (BT-10) Pflicht. Ohne gültige Leitweg-ID kann die Rechnung vom Empfängerportal (z. B. OZG-RE, E-Rechnung Bund, PEPPOL) abgewiesen werden.

### Vorschau nutzen

- Button **„🔍 Vorschau"** öffnet den PDF im Standard-Programm des Systems
- Navigation, Zoom und Scrollen hängen vom gewählten PDF-Viewer ab

### Firmeneinstellungen speichern

1. **Tab „Dienstleister-Einstellungen" öffnen**
2. Alle Felder ausfüllen:
   - Firmenname, Inhaber, Ansprechpartner, Kontaktdaten
   - Anschrift (Straße in Zeile 1, PLZ Ort in Zeile 2)
   - Steuernummer oder USt-IdNr. (z. B. `DE123456789`)
   - Gläubiger-ID für SEPA-Lastschrift (optional)
   - Bankname, IBAN, BIC
3. Optional: Firmenlogo als PNG/JPG auswählen
4. **„Einstellungen speichern"** → Daten werden dauerhaft gespeichert

---

## Design-Themen

| Theme | Beschreibung |
|-------|-------------|
| **Klassisch Blau** | Farbiger Kopf · alternierende Zeilen · klassisch |
| **Modern Minimal** | Nur Linien · keine Füllung · viel Weißraum |
| **Bold Dunkel** | Schwarzes Band · Goldakzent · voller Totalbalken |
| **Elegant Grün** | Linker 3mm-Balken je Zeile · Zebra-Muster |
| **Corporate Grau** | Außenrahmen · gestrichelte Trennlinien · sachlich |
| **Sunset Orange** | Warmton · breite Beschreibung · Akzenttrennlinien |
| **Premium Navy** | Navy-Band · Gold-Linie · durchgehender Links-Balken |
| **Bauunternehmen** | Doppelband-Kopf · Nummernbadge · Orange |

---

## ZUGFeRD / Factur-X XML (EN 16931)

Die generierten PDFs enthalten eine eingebettete Datei `factur-x.xml` gemäß:

- **Profil:** Factur-X Basic / ZUGFeRD 2.2 Basic
- **Norm:** EN 16931 (europäische E-Rechnungsnorm)
- **Zahlungsart:** TypeCode `58` = SEPA-Überweisung (korrekt nach EN 16931)
- **Pflichtfelder enthalten:**
  - Rechnungsnummer, Datum, Lieferdatum
  - Vollständige Verkäufer- und Käuferdaten inkl. Adresse und USt-Registrierung
  - Positionsdetails mit Menge, Einheitscode, Einzelpreis, Nettosumme
  - Steueraufschlüsselung (Basis, Satz, Betrag) auf Positions- und Kopfebene
  - Monetäre Gesamtsummation: Netto, Steuer, Brutto, Fälligkeitsbetrag
  - Zahlungsbedingungen mit berechnetem Fälligkeitsdatum
  - IBAN und BIC im Zahlungsmittelblock
- **B2B-Felder:** Bestellnummer (`BuyerOrderReferencedDocument`), Käuferreferenz, Kunden-USt-ID
- **B2G-Felder:** Leitweg-ID als `BuyerReference` (BT-10, Pflicht), Vertragsnummer, Kostenstelle

> Zur Validierung des XML kann [Mustang Project Validator](https://www.mustangproject.org/) oder [Factur-X Validator](https://factur-x.io/) verwendet werden.

---

## B2C vs. B2B vs. B2G

| Feld | B2C | B2B | B2G |
|------|:---:|:---:|:---:|
| Kundenname | Pflicht | Pflicht | Pflicht |
| Anschrift | Optional | Empfohlen | Empfohlen |
| Kundennummer | — | Optional | Optional |
| Kunden-USt-ID | — | Optional | Optional |
| Bestellnummer | — | Optional | Optional |
| Käuferreferenz | — | Optional | Optional |
| **Leitweg-ID** | — | — | **Pflicht** |
| Vertragsnummer | — | — | Optional |
| Kostenstelle | — | — | Optional |

---

## Bekannte Einschränkungen

- Mehrzeilige Artikelbeschreibungen werden aktuell einzeilig abgeschnitten (geplant für v5)
- Nur Steuerland DE (für andere Länder ist Anpassung im XML-Generator nötig)
- Währung ist fest auf EUR gesetzt

---

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe `LICENSE` für Details.




