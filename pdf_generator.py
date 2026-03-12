"""
PDF Generator — ZUGFeRD 2.3.3 / Factur-X Basic (EN 16931)  v17.1

21 Designs:
  Klassisch Blau  · Modern Minimal  · Bold Dunkel    · Elegant Grün
  Corporate Grau  · Sunset Orange   · Premium Navy   · Bauunternehmen
  Rounded Card    · Soft Pastel     · Dark Neon       · Rose Gold
  Slate Clean     · Typewriter      · Arctic Frost   · Forest Zen
  Midnight Purple · Warm Linen      · Tech Blueprint · Sakura
  Carbon          · Swiss Precision

v17.1: Helvetica-Fallback mit EUR statt € (kein Unicode-Crash mehr)
"""

import os, sys, io
import xml.etree.ElementTree as ET
from datetime import datetime
from fpdf import FPDF
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    DictionaryObject, NameObject, DecodedStreamObject, BooleanObject,
    ArrayObject, ByteStringObject, NumberObject,
)


def resource_path(p):
    try:    base = sys._MEIPASS
    except: base = os.path.abspath(".")
    return os.path.join(base, p)


PAGE_L   = 15
PAGE_R   = 195
PAGE_W   = 180
LOGO_Y   = 10
LOGO_H   = 22
LOGO_GAP = 6
ADDR_Y   = 52
TABLE_Y  = 110

ZUGFERD_GUIDELINE = "urn:cen.eu:en16931:2017#compliant#urn:zugferd.de:2p0:basic"


THEMES = {
    "Klassisch Blau": {
        "layout": "classic",
        "PRIMARY":    (34,  54,  80),  "ACCENT":     (51, 122, 183),
        "TEXT_MAIN":  (22,  22,  22),  "TEXT_LIGHT": (120, 120, 120),
        "BG_SOFT":    (232, 242, 252), "BG_ALT":     (255, 255, 255),
        "HDR_TEXT":   (255, 255, 255), "TOTAL_BG":   (34,  54,  80),
        "TOTAL_TXT":  (255, 255, 255),
    },
    "Modern Minimal": {
        "layout": "minimal",
        "PRIMARY":    (22,  22,  22),  "ACCENT":     (88,  88,  88),
        "TEXT_MAIN":  (22,  22,  22),  "TEXT_LIGHT": (155, 155, 155),
        "BG_SOFT":    (248, 248, 248), "BG_ALT":     (255, 255, 255),
        "HDR_TEXT":   (22,  22,  22),  "TOTAL_BG":   (232, 232, 232),
        "TOTAL_TXT":  (22,  22,  22),
    },
    "Bold Dunkel": {
        "layout": "bold",
        "PRIMARY":    (18,  18,  18),  "ACCENT":     (228, 172,  28),
        "TEXT_MAIN":  (18,  18,  18),  "TEXT_LIGHT": (128, 128, 128),
        "BG_SOFT":    (242, 242, 242), "BG_ALT":     (228, 228, 228),
        "HDR_TEXT":   (228, 172,  28), "TOTAL_BG":   (18,  18,  18),
        "TOTAL_TXT":  (228, 172,  28),
    },
    "Elegant Grün": {
        "layout": "elegant",
        "PRIMARY":    (26,  90,  30),  "ACCENT":     (74, 172,  78),
        "TEXT_MAIN":  (18,  18,  18),  "TEXT_LIGHT": (100, 118,  98),
        "BG_SOFT":    (228, 242, 230), "BG_ALT":     (255, 255, 255),
        "HDR_TEXT":   (255, 255, 255), "TOTAL_BG":   (26,  90,  30),
        "TOTAL_TXT":  (255, 255, 255),
    },
    "Corporate Grau": {
        "layout": "corporate",
        "PRIMARY":    (58,  58,  58),  "ACCENT":     (148, 148, 148),
        "TEXT_MAIN":  (28,  28,  28),  "TEXT_LIGHT": (138, 138, 138),
        "BG_SOFT":    (244, 244, 244), "BG_ALT":     (255, 255, 255),
        "HDR_TEXT":   (255, 255, 255), "TOTAL_BG":   (58,  58,  58),
        "TOTAL_TXT":  (255, 255, 255),
    },
    "Sunset Orange": {
        "layout": "sunset",
        "PRIMARY":    (178,  68,  18), "ACCENT":     (228, 128,  48),
        "TEXT_MAIN":  (28,  18,   8),  "TEXT_LIGHT": (158, 118,  88),
        "BG_SOFT":    (255, 242, 232), "BG_ALT":     (255, 255, 255),
        "HDR_TEXT":   (255, 255, 255), "TOTAL_BG":   (178,  68,  18),
        "TOTAL_TXT":  (255, 255, 255),
    },
    "Premium Navy": {
        "layout": "premium",
        "PRIMARY":    (12,  22,  48),  "ACCENT":     (178, 152,  98),
        "TEXT_MAIN":  (18,  18,  18),  "TEXT_LIGHT": (138, 138, 138),
        "BG_SOFT":    (238, 236, 230), "BG_ALT":     (255, 255, 255),
        "HDR_TEXT":   (255, 255, 255), "TOTAL_BG":   (12,  22,  48),
        "TOTAL_TXT":  (178, 152,  98),
    },
    "Bauunternehmen": {
        "layout": "bau",
        "PRIMARY":    (198,  78,   0), "ACCENT":     (238, 138,  18),
        "TEXT_MAIN":  (18,  18,  18),  "TEXT_LIGHT": (128,  98,  68),
        "BG_SOFT":    (255, 246, 236), "BG_ALT":     (255, 255, 255),
        "HDR_TEXT":   (255, 255, 255), "TOTAL_BG":   (198,  78,   0),
        "TOTAL_TXT":  (255, 255, 255),
    },
    "Rounded Card": {
        "layout": "rounded",
        "PRIMARY":    (45,  85, 195),  "ACCENT":     (100, 149, 237),
        "TEXT_MAIN":  (25,  25,  45),  "TEXT_LIGHT": (130, 140, 165),
        "BG_SOFT":    (240, 244, 255), "BG_ALT":     (255, 255, 255),
        "HDR_TEXT":   (255, 255, 255), "TOTAL_BG":   (45,  85, 195),
        "TOTAL_TXT":  (255, 255, 255),
    },
    "Soft Pastel": {
        "layout": "pastel",
        "PRIMARY":    (180,  90, 160), "ACCENT":     (220, 150, 200),
        "TEXT_MAIN":  (60,   40,  60), "TEXT_LIGHT": (180, 150, 170),
        "BG_SOFT":    (255, 240, 252), "BG_ALT":     (255, 255, 255),
        "HDR_TEXT":   (255, 255, 255), "TOTAL_BG":   (180,  90, 160),
        "TOTAL_TXT":  (255, 255, 255),
    },
    "Dark Neon": {
        "layout": "neon",
        "PRIMARY":    (18,  18,  30),  "ACCENT":     (0,  220, 180),
        "TEXT_MAIN":  (230, 235, 245), "TEXT_LIGHT": (120, 140, 160),
        "BG_SOFT":    (28,  32,  50),  "BG_ALT":     (22,  24,  38),
        "HDR_TEXT":   (0,  220, 180),  "TOTAL_BG":   (0,  180, 148),
        "TOTAL_TXT":  (18,  18,  30),
    },
    "Rose Gold": {
        "layout": "rosegold",
        "PRIMARY":    (162,  88,  88), "ACCENT":     (212, 168, 140),
        "TEXT_MAIN":  (48,   28,  28), "TEXT_LIGHT": (168, 128, 118),
        "BG_SOFT":    (252, 242, 238), "BG_ALT":     (255, 255, 255),
        "HDR_TEXT":   (255, 255, 255), "TOTAL_BG":   (162,  88,  88),
        "TOTAL_TXT":  (255, 248, 244),
    },
    "Slate Clean": {
        "layout": "slate",
        "PRIMARY":    (42,  58,  78),  "ACCENT":     (78, 168, 188),
        "TEXT_MAIN":  (28,  38,  48),  "TEXT_LIGHT": (118, 138, 158),
        "BG_SOFT":    (236, 242, 248), "BG_ALT":     (255, 255, 255),
        "HDR_TEXT":   (255, 255, 255), "TOTAL_BG":   (42,  58,  78),
        "TOTAL_TXT":  (255, 255, 255),
    },
    "Typewriter": {
        "layout": "type",
        "PRIMARY":    (38,  28,  18),  "ACCENT":     (148,  98,  48),
        "TEXT_MAIN":  (28,  18,   8),  "TEXT_LIGHT": (148, 128, 108),
        "BG_SOFT":    (248, 244, 234), "BG_ALT":     (255, 252, 245),
        "HDR_TEXT":   (255, 252, 245), "TOTAL_BG":   (38,  28,  18),
        "TOTAL_TXT":  (248, 244, 234),
    },
    "Arctic Frost": {
        "layout": "arctic",
        "PRIMARY":    (15,  95, 155),  "ACCENT":     (100, 200, 240),
        "TEXT_MAIN":  (20,  35,  50),  "TEXT_LIGHT": (110, 150, 175),
        "BG_SOFT":    (230, 248, 255), "BG_ALT":     (255, 255, 255),
        "HDR_TEXT":   (255, 255, 255), "TOTAL_BG":   (15,  95, 155),
        "TOTAL_TXT":  (255, 255, 255),
    },
    "Forest Zen": {
        "layout": "zen",
        "PRIMARY":    (38,  72,  48),  "ACCENT":     (130, 190, 100),
        "TEXT_MAIN":  (28,  42,  28),  "TEXT_LIGHT": (110, 140, 100),
        "BG_SOFT":    (238, 248, 235), "BG_ALT":     (255, 255, 255),
        "HDR_TEXT":   (255, 255, 255), "TOTAL_BG":   (38,  72,  48),
        "TOTAL_TXT":  (220, 255, 200),
    },
    "Midnight Purple": {
        "layout": "midnight",
        "PRIMARY":    (42,  18,  82),  "ACCENT":     (168,  98, 230),
        "TEXT_MAIN":  (245, 240, 255), "TEXT_LIGHT": (160, 140, 190),
        "BG_SOFT":    (55,  28, 100),  "BG_ALT":     (48,  22,  88),
        "HDR_TEXT":   (255, 255, 255), "TOTAL_BG":   (168,  98, 230),
        "TOTAL_TXT":  (255, 255, 255),
    },
    "Warm Linen": {
        "layout": "linen",
        "PRIMARY":    (108,  80,  52), "ACCENT":     (188, 148,  88),
        "TEXT_MAIN":  (58,   40,  22), "TEXT_LIGHT": (158, 130,  98),
        "BG_SOFT":    (252, 246, 236), "BG_ALT":     (255, 252, 245),
        "HDR_TEXT":   (255, 248, 235), "TOTAL_BG":   (108,  80,  52),
        "TOTAL_TXT":  (255, 248, 235),
    },
    "Tech Blueprint": {
        "layout": "blueprint",
        "PRIMARY":    (8,   40,  88),  "ACCENT":     (30, 130, 200),
        "TEXT_MAIN":  (200, 220, 245), "TEXT_LIGHT": (100, 150, 190),
        "BG_SOFT":    (12,  48, 100),  "BG_ALT":     (10,  40,  85),
        "HDR_TEXT":   (30, 200, 255),  "TOTAL_BG":   (30, 130, 200),
        "TOTAL_TXT":  (255, 255, 255),
    },
    "Sakura": {
        "layout": "sakura",
        "PRIMARY":    (195,  80, 110), "ACCENT":     (255, 168, 185),
        "TEXT_MAIN":  (60,   25,  35), "TEXT_LIGHT": (175, 125, 135),
        "BG_SOFT":    (255, 240, 244), "BG_ALT":     (255, 255, 255),
        "HDR_TEXT":   (255, 255, 255), "TOTAL_BG":   (195,  80, 110),
        "TOTAL_TXT":  (255, 240, 244),
    },
    "Carbon": {
        "layout": "carbon",
        "PRIMARY":    (28,  28,  28),  "ACCENT":     (220,  50,  50),
        "TEXT_MAIN":  (235, 235, 235), "TEXT_LIGHT": (140, 140, 140),
        "BG_SOFT":    (42,  42,  42),  "BG_ALT":     (35,  35,  35),
        "HDR_TEXT":   (255, 255, 255), "TOTAL_BG":   (220,  50,  50),
        "TOTAL_TXT":  (255, 255, 255),
    },
    "Swiss Precision": {
        "layout": "swiss",
        "PRIMARY":    (200,  10,  10), "ACCENT":     (200,  10,  10),
        "TEXT_MAIN":  (15,   15,  15), "TEXT_LIGHT": (130, 130, 130),
        "BG_SOFT":    (248, 248, 248), "BG_ALT":     (255, 255, 255),
        "HDR_TEXT":   (255, 255, 255), "TOTAL_BG":   (200,  10,  10),
        "TOTAL_TXT":  (255, 255, 255),
    },
}

THEME_NAMES = list(THEMES.keys())


def _lines(*pairs):
    return [
        f"{label}: {str(val).strip()}"
        for label, val in pairs
        if val is not None and str(val).strip() not in ("", "None")
    ]


def _build_xmp(invoice_number: str, invoice_date: str) -> bytes:
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
    xmp = (
        '<?xpacket begin="\xef\xbb\xbf" id="W5M0MpCehiHzreSzNTczkc9d"?>\n'
        '<x:xmpmeta xmlns:x="adobe:ns:meta/">\n'
        '  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">\n'
        '    <rdf:Description rdf:about=""\n'
        '        xmlns:pdfaid="http://www.aiim.org/pdfa/ns/id/">\n'
        '      <pdfaid:part>3</pdfaid:part>\n'
        '      <pdfaid:conformance>B</pdfaid:conformance>\n'
        '    </rdf:Description>\n'
        '    <rdf:Description rdf:about=""\n'
        '        xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
        '      <dc:format>application/pdf</dc:format>\n'
        '      <dc:title><rdf:Alt><rdf:li xml:lang="x-default">'
        f'ZUGFeRD Rechnung {invoice_number}'
        '</rdf:li></rdf:Alt></dc:title>\n'
        '    </rdf:Description>\n'
        '    <rdf:Description rdf:about=""\n'
        '        xmlns:xmp="http://ns.adobe.com/xap/1.0/">\n'
        f'      <xmp:CreatorTool>FRechnung v1.2.0</xmp:CreatorTool>\n'
        f'      <xmp:CreateDate>{now}</xmp:CreateDate>\n'
        f'      <xmp:ModifyDate>{now}</xmp:ModifyDate>\n'
        '    </rdf:Description>\n'
        '    <rdf:Description rdf:about=""\n'
        '        xmlns:fx="urn:factur-x:pdfa:CrossIndustryDocument:invoice:1p0#">\n'
        '      <fx:DocumentType>INVOICE</fx:DocumentType>\n'
        '      <fx:DocumentFileName>factur-x.xml</fx:DocumentFileName>\n'
        '      <fx:Version>2.3</fx:Version>\n'
        '      <fx:ConformanceLevel>BASIC</fx:ConformanceLevel>\n'
        '    </rdf:Description>\n'
        '    <rdf:Description rdf:about=""\n'
        '        xmlns:pdfaExtension="http://www.aiim.org/pdfa/ns/extension/"\n'
        '        xmlns:pdfaSchema="http://www.aiim.org/pdfa/ns/schema#"\n'
        '        xmlns:pdfaProperty="http://www.aiim.org/pdfa/ns/property#">\n'
        '      <pdfaExtension:schemas><rdf:Bag><rdf:li rdf:parseType="Resource">\n'
        '        <pdfaSchema:schema>Factur-X PDFA Extension Schema</pdfaSchema:schema>\n'
        '        <pdfaSchema:namespaceURI>urn:factur-x:pdfa:CrossIndustryDocument:invoice:1p0#</pdfaSchema:namespaceURI>\n'
        '        <pdfaSchema:prefix>fx</pdfaSchema:prefix>\n'
        '        <pdfaSchema:property><rdf:Seq>\n'
        '          <rdf:li rdf:parseType="Resource"><pdfaProperty:name>DocumentType</pdfaProperty:name>'
        '<pdfaProperty:valueType>Text</pdfaProperty:valueType>'
        '<pdfaProperty:category>external</pdfaProperty:category>'
        '<pdfaProperty:description>The document type</pdfaProperty:description></rdf:li>\n'
        '          <rdf:li rdf:parseType="Resource"><pdfaProperty:name>DocumentFileName</pdfaProperty:name>'
        '<pdfaProperty:valueType>Text</pdfaProperty:valueType>'
        '<pdfaProperty:category>external</pdfaProperty:category>'
        '<pdfaProperty:description>The XML file name</pdfaProperty:description></rdf:li>\n'
        '          <rdf:li rdf:parseType="Resource"><pdfaProperty:name>Version</pdfaProperty:name>'
        '<pdfaProperty:valueType>Text</pdfaProperty:valueType>'
        '<pdfaProperty:category>external</pdfaProperty:category>'
        '<pdfaProperty:description>The ZUGFeRD version</pdfaProperty:description></rdf:li>\n'
        '          <rdf:li rdf:parseType="Resource"><pdfaProperty:name>ConformanceLevel</pdfaProperty:name>'
        '<pdfaProperty:valueType>Text</pdfaProperty:valueType>'
        '<pdfaProperty:category>external</pdfaProperty:category>'
        '<pdfaProperty:description>The ZUGFeRD conformance level</pdfaProperty:description></rdf:li>\n'
        '        </rdf:Seq></pdfaSchema:property>\n'
        '      </rdf:li></rdf:Bag></pdfaExtension:schemas>\n'
        '    </rdf:Description>\n'
        '  </rdf:RDF>\n'
        '</x:xmpmeta>\n'
        '<?xpacket end="w"?>'
    )
    return xmp.encode("utf-8")


class PDFGenerator(FPDF):

    def __init__(self, theme_name="Klassisch Blau"):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_auto_page_break(auto=True, margin=42)
        # Fonts zuerst laden — cur wird dabei gesetzt
        self._setup_fonts()
        # Spaltenheader abhängig von cur (€ oder EUR)
        self._H = ["POS", "BESCHREIBUNG", "MENGE",
                   f"EINZEL {self.cur}", f"SUMME {self.cur}"]
        self.logo_path          = ""
        self.invoice_number     = "---"
        self.invoice_date       = "---"
        self._footer_contact    = []
        self._footer_bank       = []
        self._footer_tax        = []
        self._logo_w            = 0.0
        self._apply_theme(theme_name)

    def _apply_theme(self, name):
        t = THEMES.get(name, THEMES["Klassisch Blau"])
        for k in ("layout","PRIMARY","ACCENT","TEXT_MAIN","TEXT_LIGHT",
                  "BG_SOFT","BG_ALT","HDR_TEXT","TOTAL_BG","TOTAL_TXT"):
            setattr(self, k, t[k])

    def _setup_fonts(self):
        """
        Versucht DejaVu Unicode-Fonts zu laden.
        Gelingt es nicht, wird auf Helvetica zurückgefallen —
        in diesem Fall wird self.cur = 'EUR' gesetzt statt '€',
        damit kein Unicode-Crash entsteht.
        """
        r = resource_path("DejaVuSans.ttf")
        b = resource_path("DejaVuSans-Bold.ttf")
        if os.path.exists(r) and os.path.exists(b):
            # Veraltete .pkl-Cache-Dateien löschen
            for ttf in [r, b]:
                pkl = ttf.replace(".ttf", ".pkl")
                if os.path.exists(pkl):
                    try: os.remove(pkl)
                    except: pass
            try:
                self.add_font("DejaVu", "",  r, uni=True)
                self.add_font("DejaVu", "B", b, uni=True)
                self.fn  = "DejaVu"
                self.cur = "\u20ac"   # € — Unicode verfügbar
                return
            except Exception as e:
                print(f"[FRechnung] Font-Ladefehler: {e} — Fallback auf Helvetica")
        else:
            print(f"[FRechnung] DejaVu-Fonts nicht gefunden in: {r} — Fallback auf Helvetica")
        # Helvetica-Fallback: kein Unicode → EUR statt €
        self.fn  = "Helvetica"
        self.cur = "EUR"

    def _safe(self, text: str) -> str:
        """
        Bereinigt Text für Helvetica-Fallback:
        Ersetzt bekannte Unicode-Zeichen durch Latin-1-kompatible Alternativen.
        Bei DejaVu wird der Text unverändert zurückgegeben.
        """
        if self.fn != "Helvetica":
            return text
        replacements = {
            "\u20ac": "EUR",   # €
            "\u2212": "-",     # −
            "\u00b7": "·",     # · (Mittelpunkt — Latin-1 safe)
            "\u2013": "-",     # –
            "\u2014": "--",    # —
            "\u201c": '"',     # "
            "\u201d": '"',     # "
            "\u2018": "'",     # '
            "\u2019": "'",     # '
        }
        for uni, asc in replacements.items():
            text = text.replace(uni, asc)
        # Alles was noch nicht Latin-1 ist, ersetzen
        return text.encode("latin-1", errors="replace").decode("latin-1")

    # ── Zeichenhilfen ─────────────────────────────────────────────────────────
    def _rounded_rect(self, x, y, w, h, r, style=""):
        r = min(r, w / 2, h / 2)
        k = 0.5523
        self.move_to(x + r, y)
        self.line_to(x + w - r, y)
        self._bezier(x + w - r, y, x + w - r + k*r, y, x + w, y + r - k*r, x + w, y + r)
        self.line_to(x + w, y + h - r)
        self._bezier(x + w, y + h - r, x + w, y + h - r + k*r, x + w - r + k*r, y + h, x + w - r, y + h)
        self.line_to(x + r, y + h)
        self._bezier(x + r, y + h, x + r - k*r, y + h, x, y + h - r + k*r, x, y + h - r)
        self.line_to(x, y + r)
        self._bezier(x, y + r, x, y + r - k*r, x + r - k*r, y, x + r, y)
        op = {"F": "f", "FD": "b", "DF": "b", "": "s"}.get(style.upper(), "s")
        self._out(op)

    def _bezier(self, x1, y1, x2, y2, x3, y3, x4, y4):
        self._out(f"{x1*self.k:.2f} {(self.h - y1)*self.k:.2f} "
                  f"{x2*self.k:.2f} {(self.h - y2)*self.k:.2f} "
                  f"{x3*self.k:.2f} {(self.h - y3)*self.k:.2f} "
                  f"{x4*self.k:.2f} {(self.h - y4)*self.k:.2f} c")

    def move_to(self, x, y):
        self._out(f"{x*self.k:.2f} {(self.h - y)*self.k:.2f} m")

    def line_to(self, x, y):
        self._out(f"{x*self.k:.2f} {(self.h - y)*self.k:.2f} l")

    def _shadow_rect(self, x, y, w, h, r=2, shadow=1.2):
        self.set_fill_color(200, 205, 215)
        self._rounded_rect(x + shadow, y + shadow, w, h, r, "F")

    def _pill_badge(self, x, y, text, bg, fg, font_size=7.5):
        self.set_font(self.fn, "B", font_size)
        tw = self.get_string_width(text)
        pw = tw + 6; ph = 5.5; r = ph / 2
        self.set_fill_color(*bg)
        self._rounded_rect(x, y, pw, ph, r, "F")
        self.set_text_color(*fg)
        self.set_xy(x, y + 0.5)
        self.cell(pw, ph - 0.5, text, 0, 0, "C")
        return pw

    # ── PAGE HEADER ───────────────────────────────────────────────────────────
    def header(self):
        if self.logo_path and os.path.exists(self.logo_path):
            try: self.image(self.logo_path, PAGE_L, LOGO_Y, h=LOGO_H)
            except: pass
        lx = self._logo_right()
        {
            "minimal":    self._hdr_minimal,
            "bold":       self._hdr_bold,
            "premium":    self._hdr_premium,
            "bau":        self._hdr_bau,
            "rounded":    self._hdr_rounded,
            "pastel":     self._hdr_pastel,
            "neon":       self._hdr_neon,
            "rosegold":   self._hdr_rosegold,
            "slate":      self._hdr_slate,
            "type":       self._hdr_type,
            "arctic":     self._hdr_arctic,
            "zen":        self._hdr_zen,
            "midnight":   self._hdr_midnight,
            "linen":      self._hdr_linen,
            "blueprint":  self._hdr_blueprint,
            "sakura":     self._hdr_sakura,
            "carbon":     self._hdr_carbon,
            "swiss":      self._hdr_swiss,
        }.get(self.layout, self._hdr_default)(lx)

    def _measure_logo(self):
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                from PIL import Image as PILImg
                with PILImg.open(self.logo_path) as im:
                    w_px, h_px = im.size
                self._logo_w = LOGO_H * (w_px / h_px)
            except Exception:
                self._logo_w = LOGO_H
        else:
            self._logo_w = 0.0

    def _logo_right(self):
        return PAGE_L + self._logo_w + LOGO_GAP if self._logo_w > 0 else PAGE_L

    def _hdr_default(self, lx):
        avail = PAGE_R - lx
        self.set_font(self.fn, "B", 25); self.set_text_color(*self.PRIMARY)
        self.set_xy(lx, LOGO_Y); self.cell(avail, 11, "RECHNUNG", 0, 1, "R")
        line_y = LOGO_Y + 12
        self.set_draw_color(*self.ACCENT); self.set_line_width(0.55)
        self.line(lx, line_y, PAGE_R, line_y)
        self.set_font(self.fn, "", 8.5); self.set_text_color(*self.TEXT_LIGHT)
        self.set_xy(lx, line_y + 2); self.cell(avail, 5, f"Nr: {self.invoice_number}", 0, 1, "R")
        self.set_xy(lx, line_y + 7); self.cell(avail, 5, f"Datum: {self.invoice_date}", 0, 1, "R")

    def _hdr_minimal(self, lx):
        avail = PAGE_R - lx
        self.set_font(self.fn, "B", 27); self.set_text_color(*self.PRIMARY)
        self.set_xy(lx, LOGO_Y); self.cell(avail, 12, "RECHNUNG", 0, 1, "R")
        line_y = LOGO_Y + 13
        self.set_draw_color(*self.PRIMARY); self.set_line_width(0.9)
        self.line(lx, line_y, PAGE_R, line_y)
        self.set_font(self.fn, "", 8); self.set_text_color(*self.TEXT_LIGHT)
        self.set_xy(lx, line_y + 2)
        self.cell(avail / 2, 5, f"Nr. {self.invoice_number}", 0, 0, "L")
        self.cell(avail / 2, 5, f"Datum: {self.invoice_date}", 0, 1, "R")

    def _hdr_bold(self, lx):
        bw = PAGE_R - lx + 15
        self.set_fill_color(*self.PRIMARY); self.rect(lx, 0, bw, 28, "F")
        self.set_font(self.fn, "B", 17); self.set_text_color(*self.HDR_TEXT)
        self.set_xy(lx + 5, 6); self.cell(PAGE_R - lx - 5, 10, "RECHNUNG", 0, 0, "L")
        self.set_font(self.fn, "", 8)
        self.set_xy(PAGE_R - 80, 8); self.cell(80, 5, f"Nr: {self.invoice_number}", 0, 1, "R")
        self.set_xy(PAGE_R - 80, 14); self.cell(80, 5, f"Datum: {self.invoice_date}", 0, 1, "R")

    def _hdr_premium(self, lx):
        bw = PAGE_R - lx + 15
        self.set_fill_color(*self.PRIMARY); self.rect(lx, 0, bw, 30, "F")
        self.set_draw_color(*self.ACCENT); self.set_line_width(1.0)
        self.line(lx, 30, PAGE_R, 30)
        self.set_font(self.fn, "B", 17); self.set_text_color(*self.ACCENT)
        self.set_xy(lx + 5, 7); self.cell(PAGE_R - lx - 5, 10, "RECHNUNG", 0, 0, "L")
        self.set_font(self.fn, "", 8); self.set_text_color(*self.HDR_TEXT)
        self.set_xy(PAGE_R - 80, 9); self.cell(80, 5, f"Nr: {self.invoice_number}", 0, 1, "R")
        self.set_xy(PAGE_R - 80, 15); self.cell(80, 5, f"Datum: {self.invoice_date}", 0, 1, "R")

    def _hdr_bau(self, lx):
        bw = PAGE_R - lx + 15
        self.set_fill_color(*self.PRIMARY); self.rect(lx, 0, bw, 24, "F")
        self.set_fill_color(*self.ACCENT);  self.rect(lx, 24, bw, 4, "F")
        self.set_font(self.fn, "B", 19); self.set_text_color(*self.HDR_TEXT)
        self.set_xy(lx + 5, 5); self.cell(PAGE_R - lx - 5, 12, "RECHNUNG", 0, 0, "L")
        self.set_font(self.fn, "", 8)
        self.set_xy(PAGE_R - 78, 7);  self.cell(78, 5, f"Nr: {self.invoice_number}", 0, 1, "R")
        self.set_xy(PAGE_R - 78, 13); self.cell(78, 5, f"Datum: {self.invoice_date}", 0, 1, "R")

    def _hdr_rounded(self, lx):
        bw = PAGE_R - lx; bh = 26
        self.set_fill_color(210, 218, 240)
        self._rounded_rect(lx + 1.5, 8 + 1.5, bw, bh, 5, "F")
        self.set_fill_color(*self.PRIMARY)
        self._rounded_rect(lx, 8, bw, bh, 5, "F")
        self.set_font(self.fn, "B", 18); self.set_text_color(*self.HDR_TEXT)
        self.set_xy(lx + 6, 12); self.cell(bw - 12, 9, "RECHNUNG", 0, 0, "L")
        self.set_font(self.fn, "", 7.5); self.set_text_color(200, 215, 255)
        self.set_xy(lx + 6, 21)
        self.cell((bw-12)/2, 5, f"Nr: {self.invoice_number}", 0, 0, "L")
        self.cell((bw-12)/2, 5, f"Datum: {self.invoice_date}", 0, 0, "R")

    def _hdr_pastel(self, lx):
        avail = PAGE_R - lx
        self.set_fill_color(250, 230, 248)
        self.rect(0, 0, 210, 32, "F")
        self.set_fill_color(*self.ACCENT)
        self.ellipse(5, 2, 12, 12, "F")
        self.set_fill_color(*self.PRIMARY)
        self.ellipse(8, 5, 6, 6, "F")
        self.set_font(self.fn, "B", 22); self.set_text_color(*self.PRIMARY)
        self.set_xy(lx, 9); self.cell(avail, 10, "RECHNUNG", 0, 0, "R")
        self._pill_badge(PAGE_R - 88, 22, f"Nr: {self.invoice_number}", self.PRIMARY, (255,255,255), 7)
        self._pill_badge(PAGE_R - 50, 22, self.invoice_date, self.ACCENT, (255,255,255), 7)

    def _hdr_neon(self, lx):
        self.set_fill_color(*self.PRIMARY); self.rect(0, 0, 210, 32, "F")
        self.set_draw_color(*self.ACCENT); self.set_line_width(1.8)
        self.line(0, 0, 210, 0)
        self.set_line_width(0.8)
        self.line(lx, 31, PAGE_R, 31)
        self.set_font(self.fn, "B", 20); self.set_text_color(*self.ACCENT)
        avail = PAGE_R - lx
        self.set_xy(lx, 10); self.cell(avail, 10, "RECHNUNG", 0, 0, "R")
        self.set_font(self.fn, "", 7.5); self.set_text_color(*self.TEXT_LIGHT)
        self.set_xy(lx, 22)
        self.cell(avail/2, 5, f"Nr: {self.invoice_number}", 0, 0, "L")
        self.cell(avail/2, 5, f"Datum: {self.invoice_date}", 0, 0, "R")

    def _hdr_rosegold(self, lx):
        avail = PAGE_R - lx
        steps = 20
        for i in range(steps):
            t = i / steps
            r = int(self.PRIMARY[0] + (self.ACCENT[0] - self.PRIMARY[0]) * t)
            g = int(self.PRIMARY[1] + (self.ACCENT[1] - self.PRIMARY[1]) * t)
            b = int(self.PRIMARY[2] + (self.ACCENT[2] - self.PRIMARY[2]) * t)
            self.set_fill_color(r, g, b)
            self.rect(lx + i * (avail / steps), 0, avail / steps + 0.5, 30, "F")
        self.set_font(self.fn, "B", 19); self.set_text_color(255, 248, 244)
        self.set_xy(lx + 5, 8); self.cell(avail - 10, 10, "RECHNUNG", 0, 0, "L")
        self.set_draw_color(255, 220, 180); self.set_line_width(0.6)
        self.line(lx + 5, 20, PAGE_R - 5, 20)
        self.set_font(self.fn, "", 7.5); self.set_text_color(255, 235, 220)
        self.set_xy(lx + 5, 22)
        self.cell((avail-10)/2, 5, f"Nr: {self.invoice_number}", 0, 0, "L")
        self.cell((avail-10)/2, 5, f"Datum: {self.invoice_date}", 0, 0, "R")

    def _hdr_slate(self, lx):
        self.set_fill_color(*self.ACCENT); self.rect(0, 0, 5, 40, "F")
        avail = PAGE_R - lx
        self.set_font(self.fn, "B", 24); self.set_text_color(*self.PRIMARY)
        self.set_xy(lx, LOGO_Y); self.cell(avail, 11, "RECHNUNG", 0, 1, "R")
        self.set_draw_color(*self.ACCENT); self.set_line_width(0.4)
        self.line(lx, LOGO_Y + 12, PAGE_R, LOGO_Y + 12)
        self.set_font(self.fn, "", 8); self.set_text_color(*self.TEXT_LIGHT)
        self.set_xy(lx, LOGO_Y + 14)
        self.cell(avail/2, 5, f"Nr: {self.invoice_number}", 0, 0, "L")
        self.cell(avail/2, 5, f"Datum: {self.invoice_date}", 0, 0, "R")

    def _hdr_type(self, lx):
        avail = PAGE_R - lx
        self.set_draw_color(*self.PRIMARY); self.set_line_width(1.2)
        self.rect(lx, 7, avail, 22)
        self.set_line_width(0.4)
        self.rect(lx + 1.5, 8.5, avail - 3, 19)
        self.set_font(self.fn, "B", 20); self.set_text_color(*self.PRIMARY)
        self.set_xy(lx, 10); self.cell(avail, 10, "RECHNUNG", 0, 0, "C")
        self.set_draw_color(*self.ACCENT); self.set_line_width(0.3)
        self.line(lx + 8, 21, lx + avail - 8, 21)
        self.set_font(self.fn, "", 7.5); self.set_text_color(*self.TEXT_LIGHT)
        self.set_xy(lx, 22)
        self.cell(avail/2, 5, f"Nr: {self.invoice_number}", 0, 0, "C")
        self.set_xy(lx, 22)
        self.cell(avail - 4, 5, f"Datum: {self.invoice_date}", 0, 0, "R")

    def _hdr_arctic(self, lx):
        avail = PAGE_R - lx
        self.set_fill_color(*self.PRIMARY)
        self.rect(lx, 0, avail + 15, 30, "F")
        for i, alpha in [(0, 60), (6, 100), (12, 140)]:
            r = int(self.ACCENT[0] * alpha // 255 + self.PRIMARY[0] * (255 - alpha) // 255)
            g = int(self.ACCENT[1] * alpha // 255 + self.PRIMARY[1] * (255 - alpha) // 255)
            b = int(self.ACCENT[2] * alpha // 255 + self.PRIMARY[2] * (255 - alpha) // 255)
            self.set_fill_color(r, g, b)
            self.set_draw_color(r, g, b)
            self.move_to(PAGE_R - 30 + i, 0)
            self.line_to(PAGE_R + 15, 0)
            self.line_to(PAGE_R + 15, 30 - i * 2)
            self._out("f")
        self.set_font(self.fn, "B", 19); self.set_text_color(255, 255, 255)
        self.set_xy(lx + 6, 7); self.cell(avail - 40, 10, "RECHNUNG", 0, 0, "L")
        self.set_draw_color(*self.ACCENT); self.set_line_width(1.2)
        self.line(lx, 30, PAGE_R, 30)
        self.set_font(self.fn, "", 7.5); self.set_text_color(200, 235, 255)
        self.set_xy(lx + 6, 21)
        self.cell(avail / 2, 5, f"Nr: {self.invoice_number}", 0, 0, "L")
        self.cell(avail / 2, 5, f"Datum: {self.invoice_date}", 0, 0, "R")

    def _hdr_zen(self, lx):
        avail = PAGE_R - lx
        self.set_draw_color(*self.PRIMARY); self.set_line_width(2.5)
        self.line(0, 0, 210, 0)
        self.set_line_width(0.4)
        for xi in [5, 8, 10.5]:
            self.set_draw_color(*self.ACCENT)
            self.line(xi, 2, xi, 34)
        self.set_font(self.fn, "B", 22); self.set_text_color(*self.PRIMARY)
        self.set_xy(lx, LOGO_Y + 2); self.cell(avail, 11, "RECHNUNG", 0, 1, "R")
        self.set_draw_color(*self.ACCENT); self.set_line_width(0.6)
        self.line(lx, LOGO_Y + 14, PAGE_R, LOGO_Y + 14)
        self.set_fill_color(*self.ACCENT)
        self.ellipse(lx - 0.5, LOGO_Y + 12, 4, 4, "F")
        self.set_font(self.fn, "", 8); self.set_text_color(*self.TEXT_LIGHT)
        self.set_xy(lx + 6, LOGO_Y + 16)
        self.cell(avail / 2, 5, f"Nr: {self.invoice_number}", 0, 0, "L")
        self.cell(avail / 2 - 6, 5, f"Datum: {self.invoice_date}", 0, 0, "R")

    def _hdr_midnight(self, lx):
        self.set_fill_color(*self.PRIMARY); self.rect(0, 0, 210, 33, "F")
        avail = PAGE_R - lx
        self.set_draw_color(*self.ACCENT)
        for w in [2.5, 1.2, 0.5]:
            self.set_line_width(w)
            self.line(lx, 32, PAGE_R, 32)
        self.set_font(self.fn, "B", 20); self.set_text_color(*self.ACCENT)
        self.set_xy(lx, 8); self.cell(avail, 11, "RECHNUNG", 0, 0, "R")
        self.set_font(self.fn, "", 7.5); self.set_text_color(*self.TEXT_LIGHT)
        self.set_xy(lx, 22)
        self.cell(avail / 2, 5, f"Nr: {self.invoice_number}", 0, 0, "L")
        self.cell(avail / 2, 5, f"Datum: {self.invoice_date}", 0, 0, "R")

    def _hdr_linen(self, lx):
        avail = PAGE_R - lx
        for i in range(0, 32, 4):
            shade = 248 - (i % 8)
            self.set_fill_color(shade, shade - 4, shade - 10)
            self.rect(0, i, 210, 4, "F")
        self.set_fill_color(*self.ACCENT); self.rect(PAGE_L, 6, 1.5, 22, "F")
        self.set_font(self.fn, "B", 21); self.set_text_color(*self.PRIMARY)
        self.set_xy(lx + 6, 9); self.cell(avail - 6, 11, "RECHNUNG", 0, 0, "L")
        self.set_draw_color(*self.ACCENT); self.set_line_width(0.8)
        self.line(lx + 6, 22, PAGE_R, 22)
        self.set_draw_color(*self.PRIMARY); self.set_line_width(0.2)
        self.line(lx + 6, 23.5, PAGE_R, 23.5)
        self.set_font(self.fn, "", 8); self.set_text_color(*self.TEXT_LIGHT)
        self.set_xy(lx + 6, 25)
        self.cell(avail / 2, 5, f"Nr: {self.invoice_number}", 0, 0, "L")
        self.cell(avail / 2 - 6, 5, f"Datum: {self.invoice_date}", 0, 0, "R")

    def _hdr_blueprint(self, lx):
        avail = PAGE_R - lx
        self.set_fill_color(*self.PRIMARY); self.rect(0, 0, 210, 34, "F")
        self.set_draw_color(20, 70, 130); self.set_line_width(0.15)
        for xi in range(0, 215, 8):
            self.line(xi, 0, xi, 34)
        for yi in range(0, 36, 8):
            self.line(0, yi, 210, yi)
        self.set_draw_color(*self.ACCENT); self.set_line_width(0.5)
        for cx, cy in [(PAGE_L, 4), (PAGE_R, 4), (PAGE_L, 30), (PAGE_R, 30)]:
            self.line(cx - 3, cy, cx + 3, cy)
            self.line(cx, cy - 3, cx, cy + 3)
        self.set_font(self.fn, "B", 16); self.set_text_color(*self.HDR_TEXT)
        self.set_xy(lx, 8); self.cell(avail, 10, "RECHNUNG", 0, 0, "R")
        self.set_draw_color(*self.ACCENT); self.set_line_width(0.8)
        self.line(lx, 21, PAGE_R, 21)
        self.set_font(self.fn, "", 7); self.set_text_color(*self.TEXT_LIGHT)
        self.set_xy(lx, 23)
        self.cell(avail / 2, 5, f"// NR: {self.invoice_number}", 0, 0, "L")
        self.cell(avail / 2, 5, f"DATE: {self.invoice_date} //", 0, 0, "R")

    def _hdr_sakura(self, lx):
        avail = PAGE_R - lx
        self.set_fill_color(255, 240, 244); self.rect(0, 0, 210, 34, "F")
        blossoms = [(18, 8, 5), (25, 15, 3.5), (14, 22, 4), (35, 6, 3),
                    (PAGE_R - 10, 6, 4), (PAGE_R - 18, 18, 3), (PAGE_R - 5, 25, 2.5)]
        for bx, by, br in blossoms:
            self.set_fill_color(*self.ACCENT)
            self.ellipse(bx, by, br * 2, br * 2, "F")
            self.set_fill_color(255, 210, 220)
            self.ellipse(bx + br * 0.3, by + br * 0.3, br, br, "F")
        self.set_draw_color(*self.PRIMARY); self.set_line_width(1.5)
        self.line(lx, 31, PAGE_R, 31)
        self.set_draw_color(*self.ACCENT); self.set_line_width(0.4)
        self.line(lx, 32.5, PAGE_R, 32.5)
        self.set_font(self.fn, "B", 20); self.set_text_color(*self.PRIMARY)
        self.set_xy(lx, 10); self.cell(avail, 11, "RECHNUNG", 0, 0, "R")
        self.set_font(self.fn, "", 7.5); self.set_text_color(*self.TEXT_LIGHT)
        self.set_xy(lx, 23)
        self.cell(avail / 2, 5, f"Nr: {self.invoice_number}", 0, 0, "L")
        self.cell(avail / 2, 5, f"Datum: {self.invoice_date}", 0, 0, "R")

    def _hdr_carbon(self, lx):
        avail = PAGE_R - lx
        self.set_fill_color(28, 28, 28); self.rect(0, 0, 210, 32, "F")
        self.set_draw_color(42, 42, 42); self.set_line_width(0.3)
        for i in range(-5, 215, 6):
            self.line(i, 0, i + 32, 32)
        for i in range(-5, 215, 6):
            self.line(i + 32, 0, i, 32)
        self.set_fill_color(*self.ACCENT); self.rect(0, 29, 210, 3, "F")
        self.set_font(self.fn, "B", 18); self.set_text_color(255, 255, 255)
        self.set_xy(lx, 8); self.cell(avail, 11, "RECHNUNG", 0, 0, "R")
        self.set_font(self.fn, "", 7.5); self.set_text_color(180, 180, 180)
        self.set_xy(lx, 20)
        self.cell(avail / 2, 5, f"Nr: {self.invoice_number}", 0, 0, "L")
        self.cell(avail / 2, 5, f"Datum: {self.invoice_date}", 0, 0, "R")

    def _hdr_swiss(self, lx):
        avail = PAGE_R - lx
        self.set_fill_color(*self.PRIMARY); self.rect(0, 0, 210, 3.5, "F")
        self.set_font(self.fn, "B", 28); self.set_text_color(*self.PRIMARY)
        self.set_xy(lx, LOGO_Y); self.cell(avail, 14, "RECHNUNG", 0, 1, "R")
        self.set_draw_color(15, 15, 15); self.set_line_width(1.8)
        self.line(lx, LOGO_Y + 15, PAGE_R, LOGO_Y + 15)
        self.set_font(self.fn, "", 8); self.set_text_color(*self.TEXT_LIGHT)
        self.set_xy(lx, LOGO_Y + 17)
        self.cell(avail, 5, f"Nr: {self.invoice_number}   |   Datum: {self.invoice_date}", 0, 0, "R")

    # ── PAGE FOOTER ───────────────────────────────────────────────────────────
    def footer(self):
        self.set_y(-40)
        self.set_draw_color(200, 200, 200); self.set_line_width(0.3)
        self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y()); self.ln(4)
        y = self.get_y()
        self.set_font(self.fn, "", 7.2); self.set_text_color(*self.TEXT_LIGHT)
        if self._footer_contact:
            self.set_xy(PAGE_L, y)
            self.set_font(self.fn, "B", 7.2); self.cell(58, 3.8, "KONTAKT", 0, 1)
            self.set_font(self.fn, "", 7.2)
            for line in self._footer_contact:
                self.set_x(PAGE_L); self.cell(58, 3.8, self._safe(line), 0, 1)
        if self._footer_bank:
            self.set_xy(76, y)
            self.set_font(self.fn, "B", 7.2); self.cell(58, 3.8, "BANK", 0, 1)
            self.set_font(self.fn, "", 7.2)
            for line in self._footer_bank:
                self.set_x(76); self.cell(58, 3.8, self._safe(line), 0, 1)
        if self._footer_tax:
            self.set_xy(136, y)
            self.set_font(self.fn, "B", 7.2); self.cell(59, 3.8, "STEUER", 0, 1, "R")
            self.set_font(self.fn, "", 7.2)
            for line in self._footer_tax:
                self.set_x(136); self.cell(59, 3.8, self._safe(line), 0, 1, "R")
        self.set_xy(PAGE_L, -10)
        self.cell(0, 5, f"Seite {self.page_no()} von {{nb}}", 0, 0, "C")

    # ── Adressblock ───────────────────────────────────────────────────────────
    def _add_address(self, sender, receiver):
        self.set_xy(PAGE_L, ADDR_Y)
        self.set_font(self.fn, "", 7); self.set_text_color(*self.TEXT_LIGHT)
        al = sender.get('address', '').replace('\n', ' - ')
        self.cell(0, 4, self._safe(f"{sender.get('company_name','')} - {al}"), 0, 1)
        self.ln(1); self.set_x(PAGE_L)
        self.set_font(self.fn, "B", 10.5); self.set_text_color(*self.TEXT_MAIN)
        self.multi_cell(90, 5.8,
            self._safe(f"{receiver.get('customer_name','')}\n{receiver.get('customer_address','')}"), 0, "L")
        for label, val in [
            ("Bauvorhaben",       receiver.get('Object')),
            ("Ausfuehrung",       receiver.get('aus')),
            ("Leistungszeitraum", receiver.get('leistungszeitraum')),
        ]:
            if val and str(val).strip():
                self.ln(2); self.set_x(PAGE_L)
                self.set_font(self.fn, "B", 9); self.set_text_color(*self.PRIMARY)
                self.cell(0, 5, self._safe(f"{label}: {val}"), 0, 1)
        if receiver.get('leitweg_id'):
            self.ln(3); self.set_x(PAGE_L)
            self.set_font(self.fn, "B", 9); self.set_text_color(*self.ACCENT)
            self.cell(0, 5, self._safe(f"Leitweg-ID (E-Rechnung): {receiver['leitweg_id']}"), 0, 1)
        if receiver.get('contract_ref') and str(receiver['contract_ref']).strip():
            self.ln(1); self.set_x(PAGE_L)
            self.set_font(self.fn, "", 8.5); self.set_text_color(*self.TEXT_LIGHT)
            self.cell(0, 5, self._safe(f"Vertragsnummer: {receiver['contract_ref']}"), 0, 1)
        if receiver.get('cost_center') and str(receiver['cost_center']).strip():
            self.set_x(PAGE_L)
            self.set_font(self.fn, "", 8.5); self.set_text_color(*self.TEXT_LIGHT)
            self.cell(0, 5, self._safe(f"Kostenstelle: {receiver['cost_center']}"), 0, 1)

    # ── Tabellen-Dispatch ─────────────────────────────────────────────────────
    _C_STD = [11, 87, 24, 28, 30]
    _C_SUN = [11, 95, 20, 26, 28]
    _A     = ["C", "L", "R", "R", "R"]

    def _add_table(self, items, inv):
        self.set_y(TABLE_Y)
        {
            "classic":    self._tbl_classic,
            "minimal":    self._tbl_minimal,
            "bold":       self._tbl_bold,
            "elegant":    self._tbl_elegant,
            "corporate":  self._tbl_corporate,
            "sunset":     self._tbl_sunset,
            "premium":    self._tbl_premium,
            "bau":        self._tbl_bau,
            "rounded":    self._tbl_rounded,
            "pastel":     self._tbl_pastel,
            "neon":       self._tbl_neon,
            "rosegold":   self._tbl_rosegold,
            "slate":      self._tbl_slate,
            "type":       self._tbl_type,
            "arctic":     self._tbl_arctic,
            "zen":        self._tbl_zen,
            "midnight":   self._tbl_midnight,
            "linen":      self._tbl_linen,
            "blueprint":  self._tbl_blueprint,
            "sakura":     self._tbl_sakura,
            "carbon":     self._tbl_carbon,
            "swiss":      self._tbl_swiss,
        }.get(self.layout, self._tbl_classic)(items, inv)

    # ── Hilfs-Methoden ────────────────────────────────────────────────────────
    def _hdr_row(self, C, h):
        self.set_fill_color(*self.PRIMARY); self.set_text_color(*self.HDR_TEXT)
        self.set_font(self.fn, "B", 8.5); self.set_x(PAGE_L)
        for j, h2 in enumerate(self._H): self.cell(C[j], h, h2, 0, 0, self._A[j], True)
        self.ln(h)

    def _vals(self, idx, item):
        u = item.get("unit", "")
        return [str(idx),
                self._safe(str(item.get("product_name", ""))),
                f"{item.get('quantity', 0):.2f} {u}".strip(),
                f"{item.get('unit_price', 0):.2f}",
                f"{item.get('total_price', 0):.2f}"]

    def _totals_right(self, inv):
        rows = [(self._safe("Nettobetrag:"),           f"{inv['subtotal']:.2f} {self.cur}"),
                (self._safe(f"MwSt. {inv['tax_rate']} %:"), f"{inv['tax_amount']:.2f} {self.cur}")]
        if inv.get('discount_amount', 0):
            rows.append((self._safe(f"Rabatt {inv.get('discount_percent', 0):.1f} %:"),
                         f"-{inv['discount_amount']:.2f} {self.cur}"))
        self.set_font(self.fn, "", 9.5); self.set_text_color(*self.TEXT_MAIN)
        for lbl, val in rows:
            self.set_x(120); self.cell(45, 7, lbl, 0, 0, "R"); self.cell(30, 7, val, 0, 1, "R")
        self.ln(1); self.set_x(120)
        self.set_fill_color(*self.TOTAL_BG); self.set_text_color(*self.TOTAL_TXT)
        self.set_font(self.fn, "B", 11)
        self.cell(75, 12, f"  GESAMT: {inv['total']:.2f} {self.cur}  ", 0, 1, "R", True)

    def _totals_rounded(self, inv):
        rows = [(self._safe("Nettobetrag:"),           f"{inv['subtotal']:.2f} {self.cur}"),
                (self._safe(f"MwSt. {inv['tax_rate']} %:"), f"{inv['tax_amount']:.2f} {self.cur}")]
        if inv.get('discount_amount', 0):
            rows.append((self._safe("Rabatt:"), f"-{inv['discount_amount']:.2f} {self.cur}"))
        self.set_font(self.fn, "", 9.5); self.set_text_color(*self.TEXT_MAIN)
        for lbl, val in rows:
            self.set_x(120); self.cell(45, 7, lbl, 0, 0, "R"); self.cell(30, 7, val, 0, 1, "R")
        self.ln(1)
        self._shadow_rect(120, self.get_y(), 75, 12, 3)
        self.set_fill_color(*self.TOTAL_BG)
        self._rounded_rect(120, self.get_y(), 75, 12, 3, "F")
        self.set_font(self.fn, "B", 11); self.set_text_color(*self.TOTAL_TXT)
        self.set_xy(120, self.get_y())
        self.cell(75, 12, f"  GESAMT: {inv['total']:.2f} {self.cur}  ", 0, 1, "R")

    def _totals_fullwidth(self, inv):
        rows = [(self._safe("Nettobetrag:"),           f"{inv['subtotal']:.2f} {self.cur}"),
                (self._safe(f"MwSt. {inv['tax_rate']} %:"), f"{inv['tax_amount']:.2f} {self.cur}")]
        if inv.get('discount_amount', 0):
            rows.append((self._safe(f"Rabatt {inv.get('discount_percent', 0):.1f} %:"),
                         f"-{inv['discount_amount']:.2f} {self.cur}"))
        self.set_font(self.fn, "", 9.5); self.set_text_color(*self.TEXT_MAIN)
        for lbl, val in rows:
            self.set_x(120); self.cell(45, 7, lbl, 0, 0, "R"); self.cell(30, 7, val, 0, 1, "R")
        self.ln(2); self.set_x(PAGE_L)
        self.set_fill_color(*self.TOTAL_BG); self.set_text_color(*self.TOTAL_TXT)
        self.set_font(self.fn, "B", 13)
        self.cell(PAGE_W, 13, f"GESAMTBETRAG:   {inv['total']:.2f} {self.cur}", 0, 1, "R", True)

    # ── Tabellen ──────────────────────────────────────────────────────────────
    def _tbl_classic(self, items, inv):
        C = self._C_STD; self._hdr_row(C, 9)
        self.set_font(self.fn, "", 8.5)
        for i, item in enumerate(items, 1):
            self.set_fill_color(*(self.BG_SOFT if i % 2 else self.BG_ALT))
            self.set_text_color(*self.TEXT_MAIN); self.set_x(PAGE_L)
            for j, v in enumerate(self._vals(i, item)):
                self.cell(C[j], 8, v, 0, 0, self._A[j], True)
            self.ln(8)
        self.ln(4)
        self.set_draw_color(*self.ACCENT); self.set_line_width(0.4)
        self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y()); self.ln(4)
        self._totals_right(inv)

    def _tbl_minimal(self, items, inv):
        C = self._C_STD
        self.set_draw_color(*self.PRIMARY); self.set_line_width(0.85)
        self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y()); self.ln(2)
        self.set_font(self.fn, "B", 8); self.set_text_color(85, 85, 85); self.set_x(PAGE_L)
        for j, h in enumerate(self._H): self.cell(C[j], 7, h, 0, 0, self._A[j])
        self.ln(7)
        self.set_draw_color(178, 178, 178); self.set_line_width(0.3)
        self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y()); self.ln(1)
        self.set_font(self.fn, "", 9); self.set_text_color(*self.TEXT_MAIN)
        for i, item in enumerate(items, 1):
            self.set_x(PAGE_L)
            for j, v in enumerate(self._vals(i, item)): self.cell(C[j], 9, v, 0, 0, self._A[j])
            self.ln(9)
            self.set_draw_color(222, 222, 222); self.set_line_width(0.15)
            self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y())
        self.ln(5)
        self.set_draw_color(*self.PRIMARY); self.set_line_width(0.7)
        self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y()); self.ln(4)
        self._totals_right(inv)

    def _tbl_bold(self, items, inv):
        C = self._C_STD; self._hdr_row(C, 11); self.set_font(self.fn, "", 9)
        for i, item in enumerate(items, 1):
            self.set_fill_color(*(self.BG_SOFT if i % 2 else self.BG_ALT))
            self.set_text_color(*self.TEXT_MAIN); self.set_x(PAGE_L)
            for j, v in enumerate(self._vals(i, item)): self.cell(C[j], 9, v, 0, 0, self._A[j], True)
            self.ln(9)
        self.ln(3)
        self.set_draw_color(*self.ACCENT); self.set_line_width(1.3)
        self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y()); self.ln(4)
        self._totals_fullwidth(inv)

    def _tbl_elegant(self, items, inv):
        C = self._C_STD; self._hdr_row(C, 9); self.set_font(self.fn, "", 9)
        for i, item in enumerate(items, 1):
            y0 = self.get_y(); bg = self.BG_SOFT if i % 2 else self.BG_ALT
            if i % 2 == 1:
                self.set_fill_color(*self.ACCENT); self.rect(PAGE_L, y0, 3, 8, "F")
            self.set_fill_color(*bg); self.set_text_color(*self.TEXT_MAIN); self.set_x(PAGE_L)
            for j, v in enumerate(self._vals(i, item)): self.cell(C[j], 8, v, 0, 0, self._A[j], True)
            self.ln(8)
        self.ln(4)
        self.set_draw_color(*self.ACCENT); self.set_line_width(0.6)
        self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y()); self.ln(4)
        self._totals_right(inv)

    def _tbl_corporate(self, items, inv):
        C = self._C_STD; top = self.get_y(); self._hdr_row(C, 9)
        self.set_font(self.fn, "", 8.5)
        for i, item in enumerate(items, 1):
            self.set_fill_color(*(self.BG_SOFT if i % 2 else self.BG_ALT))
            self.set_text_color(*self.TEXT_MAIN); self.set_x(PAGE_L)
            for j, v in enumerate(self._vals(i, item)): self.cell(C[j], 8, v, 0, 0, self._A[j], True)
            self.ln(8)
            self.set_draw_color(192, 192, 192); self.set_line_width(0.14)
            self._out("[1.5 1.5] 0 d")
            self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y())
            self._out("[] 0 d")
        bot = self.get_y()
        self.set_draw_color(*self.PRIMARY); self.set_line_width(0.55)
        self.rect(PAGE_L, top, PAGE_W, bot - top); self.ln(5); self._totals_right(inv)

    def _tbl_sunset(self, items, inv):
        C = self._C_SUN; self._hdr_row(C, 9); self.set_font(self.fn, "", 8.5)
        for i, item in enumerate(items, 1):
            self.set_fill_color(*(self.BG_SOFT if i % 2 else self.BG_ALT))
            self.set_text_color(*self.TEXT_MAIN); self.set_x(PAGE_L)
            for j, v in enumerate(self._vals(i, item)): self.cell(C[j], 8, v, 0, 0, self._A[j], True)
            self.ln(8)
            self.set_draw_color(*self.ACCENT); self.set_line_width(0.28)
            self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y())
        self.ln(4)
        self.set_draw_color(*self.PRIMARY); self.set_line_width(0.5)
        self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y()); self.ln(4)
        self._totals_right(inv)

    def _tbl_premium(self, items, inv):
        C = self._C_STD; top = self.get_y(); self._hdr_row(C, 10)
        self.set_font(self.fn, "", 8.5)
        for i, item in enumerate(items, 1):
            self.set_fill_color(*(self.BG_SOFT if i % 2 == 0 else self.BG_ALT))
            self.set_text_color(*self.TEXT_MAIN); self.set_x(PAGE_L)
            for j, v in enumerate(self._vals(i, item)): self.cell(C[j], 8, v, 0, 0, self._A[j], True)
            self.ln(8)
        bot = self.get_y()
        self.set_fill_color(*self.ACCENT); self.rect(PAGE_L, top, 2.8, bot - top, "F")
        self.ln(4)
        self.set_draw_color(*self.ACCENT); self.set_line_width(0.8)
        self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y()); self.ln(4)
        self._totals_right(inv)

    def _tbl_bau(self, items, inv):
        C = self._C_STD
        self.set_fill_color(*self.PRIMARY); self.set_text_color(*self.HDR_TEXT)
        self.set_font(self.fn, "B", 9); self.set_x(PAGE_L)
        for j, h in enumerate(self._H): self.cell(C[j], 10, h, 0, 0, self._A[j], True)
        self.ln(10)
        self.set_fill_color(*self.ACCENT); self.set_x(PAGE_L)
        self.cell(PAGE_W, 2.5, "", 0, 1, "L", True)
        self.set_font(self.fn, "", 8.5)
        for i, item in enumerate(items, 1):
            bg = self.BG_SOFT if i % 2 else self.BG_ALT
            self.set_fill_color(*self.PRIMARY); self.set_text_color(255,255,255)
            self.set_x(PAGE_L); self.cell(C[0], 8, str(i), 0, 0, "C", True)
            self.set_fill_color(*bg); self.set_text_color(*self.TEXT_MAIN)
            vals = self._vals(i, item)
            for j in range(1, len(C)): self.cell(C[j], 8, vals[j], 0, 0, self._A[j], True)
            self.ln(8)
        self.ln(5)
        self.set_draw_color(*self.PRIMARY); self.set_line_width(0.5)
        self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y()); self.ln(4)
        self._totals_right(inv)

    def _tbl_rounded(self, items, inv):
        C = self._C_STD
        self._shadow_rect(PAGE_L, self.get_y(), PAGE_W, 10, 3, 1)
        self.set_fill_color(*self.PRIMARY)
        self._rounded_rect(PAGE_L, self.get_y(), PAGE_W, 10, 3, "F")
        self.set_font(self.fn, "B", 8.5); self.set_text_color(*self.HDR_TEXT)
        self.set_x(PAGE_L)
        for j, h in enumerate(self._H): self.cell(C[j], 10, h, 0, 0, self._A[j])
        self.ln(10); self.ln(2)
        self.set_font(self.fn, "", 8.5)
        for i, item in enumerate(items, 1):
            y_row = self.get_y()
            self.set_fill_color(215, 222, 240)
            self._rounded_rect(PAGE_L + 0.8, y_row + 0.8, PAGE_W, 8, 2, "F")
            bg = self.BG_SOFT if i % 2 else self.BG_ALT
            self.set_fill_color(*bg)
            self._rounded_rect(PAGE_L, y_row, PAGE_W, 8, 2, "F")
            self.set_text_color(*self.TEXT_MAIN); self.set_x(PAGE_L)
            for j, v in enumerate(self._vals(i, item)): self.cell(C[j], 8, v, 0, 0, self._A[j])
            self.ln(10)
        self.ln(2)
        self._totals_rounded(inv)

    def _tbl_pastel(self, items, inv):
        C = self._C_STD
        self.set_fill_color(*self.PRIMARY)
        self._rounded_rect(PAGE_L, self.get_y(), PAGE_W, 9, 3, "F")
        self.set_font(self.fn, "B", 8.5); self.set_text_color(*self.HDR_TEXT)
        self.set_x(PAGE_L)
        for j, h in enumerate(self._H): self.cell(C[j], 9, h, 0, 0, self._A[j])
        self.ln(9); self.ln(2)
        self.set_font(self.fn, "", 8.5)
        for i, item in enumerate(items, 1):
            y_row = self.get_y()
            bg = (255, 245, 254) if i % 2 else (255, 255, 255)
            self.set_fill_color(*bg); self.rect(PAGE_L, y_row, PAGE_W, 9, "F")
            self._pill_badge(PAGE_L + 0.5, y_row + 1.8, str(i), self.ACCENT, (255,255,255), 7)
            self.set_text_color(*self.TEXT_MAIN)
            vals = self._vals(i, item)
            self.set_xy(PAGE_L + C[0], y_row)
            for j in range(1, len(C)): self.cell(C[j], 9, vals[j], 0, 0, self._A[j])
            self.ln(11)
        self.ln(2)
        self.set_draw_color(*self.ACCENT); self.set_line_width(0.5)
        self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y()); self.ln(4)
        self._totals_right(inv)

    def _tbl_neon(self, items, inv):
        C = self._C_STD
        self.set_fill_color(*self.PRIMARY); self.rect(PAGE_L, self.get_y(), PAGE_W, 10, "F")
        self.set_draw_color(*self.ACCENT); self.set_line_width(0.8)
        self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y())
        self.set_font(self.fn, "B", 8.5); self.set_text_color(*self.ACCENT)
        self.set_x(PAGE_L)
        for j, h in enumerate(self._H): self.cell(C[j], 10, h, 0, 0, self._A[j])
        self.ln(10)
        self.set_draw_color(*self.ACCENT); self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y())
        self.set_font(self.fn, "", 8.5)
        for i, item in enumerate(items, 1):
            bg = self.BG_SOFT if i % 2 else self.BG_ALT
            self.set_fill_color(*bg); self.set_text_color(*self.TEXT_MAIN)
            self.set_x(PAGE_L)
            for j, v in enumerate(self._vals(i, item)): self.cell(C[j], 9, v, 0, 0, self._A[j], True)
            self.ln(9)
            r, g, b = self.ACCENT
            self.set_draw_color(r//3, g//3, b//3); self.set_line_width(0.2)
            self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y())
        self.ln(4)
        self.set_draw_color(*self.ACCENT); self.set_line_width(0.8)
        self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y()); self.ln(4)
        rows = [(self._safe("Nettobetrag:"),           f"{inv['subtotal']:.2f} {self.cur}"),
                (self._safe(f"MwSt. {inv['tax_rate']} %:"), f"{inv['tax_amount']:.2f} {self.cur}")]
        if inv.get('discount_amount', 0):
            rows.append((self._safe("Rabatt:"), f"-{inv['discount_amount']:.2f} {self.cur}"))
        self.set_font(self.fn, "", 9); self.set_text_color(*self.TEXT_LIGHT)
        for lbl, val in rows:
            self.set_x(120); self.cell(45, 7, lbl, 0, 0, "R"); self.cell(30, 7, val, 0, 1, "R")
        self.ln(1); self.set_x(120)
        self.set_fill_color(*self.TOTAL_BG)
        self._rounded_rect(120, self.get_y(), 75, 12, 3, "F")
        self.set_font(self.fn, "B", 11); self.set_text_color(*self.TOTAL_TXT)
        self.set_xy(120, self.get_y())
        self.cell(75, 12, f"  GESAMT: {inv['total']:.2f} {self.cur}  ", 0, 1, "R")

    def _tbl_rosegold(self, items, inv):
        C = self._C_STD
        steps = 10; w_step = PAGE_W / steps
        for i in range(steps):
            t = i / steps
            r = int(self.PRIMARY[0] + (self.ACCENT[0] - self.PRIMARY[0]) * t)
            g = int(self.PRIMARY[1] + (self.ACCENT[1] - self.PRIMARY[1]) * t)
            b = int(self.PRIMARY[2] + (self.ACCENT[2] - self.PRIMARY[2]) * t)
            self.set_fill_color(r, g, b)
            self.rect(PAGE_L + i * w_step, self.get_y(), w_step + 0.5, 9, "F")
        self.set_font(self.fn, "B", 8.5); self.set_text_color(255, 248, 244)
        self.set_x(PAGE_L)
        for j, h in enumerate(self._H): self.cell(C[j], 9, h, 0, 0, self._A[j])
        self.ln(9)
        self.set_font(self.fn, "", 8.5)
        for i, item in enumerate(items, 1):
            bg = (252, 242, 238) if i % 2 else (255, 255, 255)
            self.set_fill_color(*bg); self.set_text_color(*self.TEXT_MAIN)
            self.set_x(PAGE_L)
            for j, v in enumerate(self._vals(i, item)): self.cell(C[j], 8, v, 0, 0, self._A[j], True)
            self.ln(8)
            self.set_draw_color(212, 168, 140); self.set_line_width(0.2)
            self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y())
        self.ln(4)
        self.set_draw_color(*self.PRIMARY); self.set_line_width(0.6)
        self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y()); self.ln(4)
        self._totals_right(inv)

    def _tbl_slate(self, items, inv):
        C = self._C_STD; top_y = self.get_y()
        self.set_fill_color(*self.PRIMARY)
        self._rounded_rect(PAGE_L, top_y, PAGE_W, 9, 3, "F")
        self.set_font(self.fn, "B", 8.5); self.set_text_color(*self.HDR_TEXT)
        self.set_x(PAGE_L)
        for j, h in enumerate(self._H): self.cell(C[j], 9, h, 0, 0, self._A[j])
        self.ln(9)
        self.set_font(self.fn, "", 8.5)
        for i, item in enumerate(items, 1):
            y_row = self.get_y()
            bg = self.BG_SOFT if i % 2 else self.BG_ALT
            self.set_fill_color(*bg); self.set_text_color(*self.TEXT_MAIN)
            self.set_x(PAGE_L)
            for j, v in enumerate(self._vals(i, item)): self.cell(C[j], 8, v, 0, 0, self._A[j], True)
            self.ln(8)
            self.set_fill_color(*self.ACCENT)
            self.rect(PAGE_L, y_row, 2, 8, "F")
        bot_y = self.get_y()
        self.set_draw_color(*self.PRIMARY); self.set_line_width(0.5)
        self._rounded_rect(PAGE_L, top_y, PAGE_W, bot_y - top_y, 3)
        self.ln(4)
        self.set_draw_color(*self.ACCENT); self.set_line_width(0.5)
        self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y()); self.ln(4)
        self._totals_right(inv)

    def _tbl_type(self, items, inv):
        C = self._C_STD; top_y = self.get_y()
        self.set_fill_color(*self.PRIMARY); self.rect(PAGE_L, top_y, PAGE_W, 9, "F")
        self.set_font(self.fn, "B", 8.5); self.set_text_color(*self.HDR_TEXT)
        self.set_x(PAGE_L)
        for j, h in enumerate(self._H): self.cell(C[j], 9, h, 0, 0, self._A[j])
        self.ln(9)
        self.set_draw_color(*self.PRIMARY); self.set_line_width(0.7)
        self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y())
        self.set_line_width(0.25)
        self.line(PAGE_L, self.get_y() + 1.2, PAGE_R, self.get_y() + 1.2)
        self.ln(3)
        self.set_font(self.fn, "", 8.5)
        for i, item in enumerate(items, 1):
            bg = self.BG_SOFT if i % 2 else self.BG_ALT
            self.set_fill_color(*bg); self.set_text_color(*self.TEXT_MAIN)
            self.set_x(PAGE_L)
            for j, v in enumerate(self._vals(i, item)): self.cell(C[j], 8, v, 0, 0, self._A[j], True)
            self.ln(8)
            self.set_draw_color(*self.TEXT_LIGHT); self.set_line_width(0.15)
            self._out("[2 2] 0 d")
            self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y())
            self._out("[] 0 d")
        bot_y = self.get_y()
        self.set_draw_color(*self.PRIMARY); self.set_line_width(0.7)
        self.line(PAGE_L, bot_y, PAGE_R, bot_y)
        self.set_line_width(0.25)
        self.line(PAGE_L, bot_y + 1.2, PAGE_R, bot_y + 1.2)
        self.ln(6)
        self._totals_right(inv)

    def _tbl_arctic(self, items, inv):
        C = self._C_STD
        self.set_fill_color(*self.PRIMARY)
        self._rounded_rect(PAGE_L, self.get_y(), PAGE_W, 10, 4, "F")
        self.set_font(self.fn, "B", 8.5); self.set_text_color(*self.HDR_TEXT)
        self.set_x(PAGE_L)
        for j, h in enumerate(self._H): self.cell(C[j], 10, h, 0, 0, self._A[j])
        self.ln(12)
        self.set_font(self.fn, "", 8.5)
        for i, item in enumerate(items, 1):
            y_row = self.get_y()
            bg = self.BG_SOFT if i % 2 else self.BG_ALT
            self.set_fill_color(*bg)
            self._rounded_rect(PAGE_L, y_row, PAGE_W, 8.5, 2, "F")
            self.set_draw_color(*self.ACCENT); self.set_line_width(0.25)
            self._rounded_rect(PAGE_L, y_row, PAGE_W, 8.5, 2)
            self.set_text_color(*self.TEXT_MAIN); self.set_x(PAGE_L)
            for j, v in enumerate(self._vals(i, item)): self.cell(C[j], 8.5, v, 0, 0, self._A[j])
            self.ln(11)
        self.ln(2)
        self._totals_rounded(inv)

    def _tbl_zen(self, items, inv):
        C = self._C_STD
        self.set_font(self.fn, "B", 8); self.set_text_color(*self.PRIMARY)
        self.set_x(PAGE_L)
        for j, h in enumerate(self._H): self.cell(C[j], 8, h.upper(), 0, 0, self._A[j])
        self.ln(8)
        self.set_draw_color(*self.ACCENT); self.set_line_width(1.0)
        self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y()); self.ln(3)
        self.set_font(self.fn, "", 9); self.set_text_color(*self.TEXT_MAIN)
        for i, item in enumerate(items, 1):
            self.set_x(PAGE_L)
            self.set_text_color(*self.ACCENT)
            self.cell(C[0], 10, ">>", 0, 0, "C")
            self.set_text_color(*self.TEXT_MAIN)
            vals = self._vals(i, item)
            for j in range(1, len(C)): self.cell(C[j], 10, vals[j], 0, 0, self._A[j])
            self.ln(10)
            self.set_draw_color(180, 210, 170); self.set_line_width(0.2)
            self._out("[3 2] 0 d")
            self.line(PAGE_L + 15, self.get_y(), PAGE_R, self.get_y())
            self._out("[] 0 d")
        self.ln(4)
        self.set_draw_color(*self.PRIMARY); self.set_line_width(1.0)
        self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y()); self.ln(4)
        self._totals_right(inv)

    def _tbl_midnight(self, items, inv):
        C = self._C_STD
        self.set_fill_color(*self.BG_SOFT)
        self._rounded_rect(PAGE_L, self.get_y(), PAGE_W, 10, 4, "F")
        self.set_font(self.fn, "B", 8.5); self.set_text_color(*self.ACCENT)
        self.set_x(PAGE_L)
        for j, h in enumerate(self._H): self.cell(C[j], 10, h, 0, 0, self._A[j])
        self.ln(12)
        self.set_font(self.fn, "", 8.5)
        for i, item in enumerate(items, 1):
            y_row = self.get_y()
            bg = self.BG_SOFT if i % 2 else self.BG_ALT
            self.set_fill_color(*bg); self.rect(PAGE_L, y_row, PAGE_W, 9, "F")
            self.set_fill_color(*self.ACCENT)
            self.ellipse(PAGE_L + 1, y_row + 1.5, 7, 6, "F")
            self.set_font(self.fn, "B", 7); self.set_text_color(*self.BG_ALT)
            self.set_xy(PAGE_L + 1, y_row + 2)
            self.cell(7, 5, str(i), 0, 0, "C")
            self.set_font(self.fn, "", 8.5); self.set_text_color(*self.TEXT_MAIN)
            vals = self._vals(i, item)
            self.set_xy(PAGE_L + C[0], y_row)
            for j in range(1, len(C)): self.cell(C[j], 9, vals[j], 0, 0, self._A[j])
            self.ln(11)
        self.ln(2)
        rows = [(self._safe("Nettobetrag:"),           f"{inv['subtotal']:.2f} {self.cur}"),
                (self._safe(f"MwSt. {inv['tax_rate']} %:"), f"{inv['tax_amount']:.2f} {self.cur}")]
        self.set_font(self.fn, "", 9); self.set_text_color(*self.TEXT_MAIN)
        for lbl, val in rows:
            self.set_x(120); self.cell(45, 7, lbl, 0, 0, "R"); self.cell(30, 7, val, 0, 1, "R")
        self.ln(1)
        self.set_fill_color(*self.TOTAL_BG)
        self._rounded_rect(120, self.get_y(), 75, 12, 6, "F")
        self.set_font(self.fn, "B", 11); self.set_text_color(*self.TOTAL_TXT)
        self.set_xy(120, self.get_y())
        self.cell(75, 12, f"  GESAMT: {inv['total']:.2f} {self.cur}  ", 0, 1, "R")

    def _tbl_linen(self, items, inv):
        C = self._C_STD; top_y = self.get_y()
        self.set_fill_color(*self.PRIMARY); self.rect(PAGE_L, top_y, PAGE_W, 9, "F")
        self.set_font(self.fn, "B", 8.5); self.set_text_color(*self.HDR_TEXT)
        self.set_x(PAGE_L)
        for j, h in enumerate(self._H): self.cell(C[j], 9, h, 0, 0, self._A[j])
        self.ln(9)
        self.set_draw_color(*self.ACCENT); self.set_line_width(0.6)
        self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y())
        self.set_draw_color(220, 190, 150); self.set_line_width(0.2)
        self.line(PAGE_L, self.get_y() + 1.2, PAGE_R, self.get_y() + 1.2)
        self.ln(2)
        self.set_font(self.fn, "", 8.5); row_start = self.get_y()
        for i, item in enumerate(items, 1):
            y_row = self.get_y()
            bg = self.BG_SOFT if i % 2 else self.BG_ALT
            self.set_fill_color(*bg); self.set_text_color(*self.TEXT_MAIN)
            self.set_x(PAGE_L)
            for j, v in enumerate(self._vals(i, item)): self.cell(C[j], 8, v, 0, 0, self._A[j], True)
            self.ln(8)
        row_end = self.get_y()
        self.set_draw_color(200, 170, 130); self.set_line_width(0.2)
        x = PAGE_L
        for j in range(len(C) - 1):
            x += C[j]
            self.line(x, row_start, x, row_end)
        self.set_draw_color(*self.ACCENT); self.set_line_width(0.6)
        self.line(PAGE_L, row_end, PAGE_R, row_end)
        self.ln(5); self._totals_right(inv)

    def _tbl_blueprint(self, items, inv):
        C = self._C_STD; top_y = self.get_y()
        self.set_fill_color(*self.BG_SOFT); self.rect(PAGE_L, top_y, PAGE_W, 10, "F")
        self.set_draw_color(*self.ACCENT); self.set_line_width(0.8)
        self.line(PAGE_L, top_y, PAGE_R, top_y)
        self.line(PAGE_L, top_y + 10, PAGE_R, top_y + 10)
        self.set_font(self.fn, "B", 8.5); self.set_text_color(*self.HDR_TEXT)
        self.set_x(PAGE_L)
        for j, h in enumerate(self._H): self.cell(C[j], 10, h, 0, 0, self._A[j])
        self.ln(10)
        self.set_font(self.fn, "", 8.5)
        for i, item in enumerate(items, 1):
            bg = self.BG_SOFT if i % 2 else self.BG_ALT
            self.set_fill_color(*bg); self.set_text_color(*self.TEXT_MAIN)
            self.set_x(PAGE_L)
            for j, v in enumerate(self._vals(i, item)): self.cell(C[j], 9, v, 0, 0, self._A[j], True)
            self.ln(9)
            self.set_draw_color(*self.ACCENT); self.set_line_width(0.15)
            self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y())
        bot_y = self.get_y()
        self.set_draw_color(*self.ACCENT); self.set_line_width(0.8)
        self.line(PAGE_L, bot_y, PAGE_R, bot_y)
        self.ln(5)
        rows = [(self._safe("Nettobetrag:"),           f"{inv['subtotal']:.2f} {self.cur}"),
                (self._safe(f"MwSt. {inv['tax_rate']} %:"), f"{inv['tax_amount']:.2f} {self.cur}")]
        self.set_font(self.fn, "", 9); self.set_text_color(*self.TEXT_MAIN)
        for lbl, val in rows:
            self.set_x(120); self.cell(45, 7, lbl, 0, 0, "R"); self.cell(30, 7, val, 0, 1, "R")
        self.ln(1)
        self.set_fill_color(*self.TOTAL_BG)
        self._rounded_rect(120, self.get_y(), 75, 12, 3, "F")
        self.set_draw_color(*self.ACCENT); self.set_line_width(0.6)
        self._rounded_rect(120, self.get_y(), 75, 12, 3)
        self.set_font(self.fn, "B", 11); self.set_text_color(*self.TOTAL_TXT)
        self.set_xy(120, self.get_y())
        self.cell(75, 12, f"  GESAMT: {inv['total']:.2f} {self.cur}  ", 0, 1, "R")

    def _tbl_sakura(self, items, inv):
        C = self._C_STD
        self.set_fill_color(*self.PRIMARY)
        self._rounded_rect(PAGE_L, self.get_y(), PAGE_W, 10, 5, "F")
        self.set_font(self.fn, "B", 8.5); self.set_text_color(*self.HDR_TEXT)
        self.set_x(PAGE_L)
        for j, h in enumerate(self._H): self.cell(C[j], 10, h, 0, 0, self._A[j])
        self.ln(13)
        self.set_font(self.fn, "", 8.5)
        for i, item in enumerate(items, 1):
            y_row = self.get_y()
            self.set_fill_color(*(self.BG_SOFT if i % 2 else self.BG_ALT))
            self._rounded_rect(PAGE_L, y_row, PAGE_W, 9, 3, "F")
            self.set_fill_color(*self.ACCENT)
            self.ellipse(PAGE_L + 2, y_row + 3, 3, 3, "F")
            self.set_text_color(*self.TEXT_MAIN); self.set_x(PAGE_L)
            for j, v in enumerate(self._vals(i, item)): self.cell(C[j], 9, v, 0, 0, self._A[j])
            self.ln(12)
        self.ln(2)
        rows = [(self._safe("Nettobetrag:"),           f"{inv['subtotal']:.2f} {self.cur}"),
                (self._safe(f"MwSt. {inv['tax_rate']} %:"), f"{inv['tax_amount']:.2f} {self.cur}")]
        self.set_font(self.fn, "", 9); self.set_text_color(*self.TEXT_MAIN)
        for lbl, val in rows:
            self.set_x(120); self.cell(45, 7, lbl, 0, 0, "R"); self.cell(30, 7, val, 0, 1, "R")
        self.ln(1)
        self.set_fill_color(*self.TOTAL_BG)
        self._rounded_rect(120, self.get_y(), 75, 13, 6, "F")
        self.set_font(self.fn, "B", 11); self.set_text_color(*self.TOTAL_TXT)
        self.set_xy(120, self.get_y())
        self.cell(75, 13, f"  GESAMT: {inv['total']:.2f} {self.cur}  ", 0, 1, "R")

    def _tbl_carbon(self, items, inv):
        C = self._C_STD
        self.set_fill_color(*self.PRIMARY); self.rect(PAGE_L, self.get_y(), PAGE_W, 11, "F")
        self.set_draw_color(*self.ACCENT); self.set_line_width(0.25)
        for xi in range(int(PAGE_L), int(PAGE_R), 4):
            self.line(xi, self.get_y(), xi + 11, self.get_y() + 11)
        self.set_font(self.fn, "B", 8.5); self.set_text_color(*self.HDR_TEXT)
        self.set_x(PAGE_L)
        for j, h in enumerate(self._H): self.cell(C[j], 11, h, 0, 0, self._A[j])
        self.ln(11)
        self.set_fill_color(*self.ACCENT); self.rect(PAGE_L, self.get_y(), PAGE_W, 2, "F")
        self.ln(3)
        self.set_font(self.fn, "", 8.5)
        for i, item in enumerate(items, 1):
            bg = self.BG_SOFT if i % 2 else self.BG_ALT
            self.set_fill_color(*bg); self.set_text_color(*self.TEXT_MAIN)
            self.set_x(PAGE_L)
            for j, v in enumerate(self._vals(i, item)): self.cell(C[j], 9, v, 0, 0, self._A[j], True)
            self.ln(9)
        self.set_fill_color(*self.ACCENT); self.rect(PAGE_L, self.get_y(), PAGE_W, 2, "F")
        self.ln(6)
        rows = [(self._safe("Nettobetrag:"),           f"{inv['subtotal']:.2f} {self.cur}"),
                (self._safe(f"MwSt. {inv['tax_rate']} %:"), f"{inv['tax_amount']:.2f} {self.cur}")]
        self.set_font(self.fn, "", 9); self.set_text_color(*self.TEXT_MAIN)
        for lbl, val in rows:
            self.set_x(120); self.cell(45, 7, lbl, 0, 0, "R"); self.cell(30, 7, val, 0, 1, "R")
        self.ln(2); self.set_x(PAGE_L)
        self.set_fill_color(*self.PRIMARY); self.rect(PAGE_L, self.get_y(), PAGE_W, 13, "F")
        self.set_fill_color(*self.ACCENT); self.rect(PAGE_L, self.get_y(), 3, 13, "F")
        self.set_fill_color(*self.ACCENT); self.rect(PAGE_R - 3, self.get_y(), 3, 13, "F")
        self.set_font(self.fn, "B", 13); self.set_text_color(*self.TOTAL_TXT)
        self.set_x(PAGE_L)
        self.cell(PAGE_W, 13, f"GESAMT:   {inv['total']:.2f} {self.cur}", 0, 1, "R", False)

    def _tbl_swiss(self, items, inv):
        C = self._C_STD; top_y = self.get_y()
        self.set_draw_color(*self.PRIMARY); self.set_line_width(1.5)
        self.line(PAGE_L, top_y, PAGE_R, top_y)
        self.set_font(self.fn, "B", 8.5); self.set_text_color(*self.PRIMARY)
        self.set_x(PAGE_L)
        for j, h in enumerate(self._H): self.cell(C[j], 9, h, 0, 0, self._A[j])
        self.ln(9)
        self.set_line_width(0.5)
        self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y()); self.ln(1)
        self.set_font(self.fn, "", 9); self.set_text_color(*self.TEXT_MAIN)
        for i, item in enumerate(items, 1):
            if i % 2 == 0:
                self.set_fill_color(*self.BG_SOFT)
                self.rect(PAGE_L, self.get_y(), PAGE_W, 9, "F")
            self.set_x(PAGE_L)
            for j, v in enumerate(self._vals(i, item)): self.cell(C[j], 9, v, 0, 0, self._A[j])
            self.ln(9)
        self.set_line_width(1.5); self.set_draw_color(*self.PRIMARY)
        self.line(PAGE_L, self.get_y(), PAGE_R, self.get_y())
        self.ln(6)
        rows = [(self._safe("Nettobetrag"),           f"{inv['subtotal']:.2f} {self.cur}"),
                (self._safe(f"MwSt. {inv['tax_rate']} %"), f"{inv['tax_amount']:.2f} {self.cur}")]
        self.set_font(self.fn, "", 9); self.set_text_color(*self.TEXT_MAIN)
        for lbl, val in rows:
            self.set_x(120); self.cell(45, 7, lbl, 0, 0, "R")
            self.cell(30, 7, val, 0, 1, "R")
        self.set_draw_color(*self.PRIMARY); self.set_line_width(1.2)
        self.line(120, self.get_y(), PAGE_R, self.get_y())
        self.ln(2); self.set_x(120)
        self.set_font(self.fn, "B", 12); self.set_text_color(*self.PRIMARY)
        self.cell(45, 8, "GESAMT", 0, 0, "R")
        self.cell(30, 8, f"{inv['total']:.2f} {self.cur}", 0, 1, "R")
        self.set_draw_color(*self.PRIMARY); self.set_line_width(1.2)
        self.line(120, self.get_y(), PAGE_R, self.get_y())

    # ── Haupt-Einstieg ────────────────────────────────────────────────────────
    def generate_invoice(self, invoice_data, receiver_data, items, sender_data):
        self.invoice_number = invoice_data.get("invoice_number", "---")
        self.invoice_date   = invoice_data.get("invoice_date",   "---")
        self._footer_contact = _lines(
            ("Tel",  sender_data.get("phone",  "")),
            ("Mail", sender_data.get("email",  "")),
        )
        self._footer_bank = _lines(
            ("Bank", sender_data.get("bank",         "")),
            ("IBAN", sender_data.get("bank_account", "")),
            ("BIC",  sender_data.get("bank_bic",     "")),
        )
        self._footer_tax = _lines(
            ("USt-ID",  sender_data.get("tax_id", "")),
            ("Inhaber", sender_data.get("owner",  "")),
        )
        self._measure_logo()
        self.alias_nb_pages()
        self.add_page()
        self._add_address(sender_data, receiver_data)
        self._add_table(items, invoice_data)
        closing = invoice_data.get("payment_terms",
            "Zahlbar sofort nach Erhalt ohne Abzug. Vielen Dank fuer Ihren Auftrag!")
        self.ln(10); self.set_x(PAGE_L)
        self.set_font(self.fn, "", 8.5); self.set_text_color(*self.TEXT_MAIN)
        self.multi_cell(0, 5, self._safe(closing), 0, "L")
        if invoice_data.get("notes") and str(invoice_data["notes"]).strip():
            self.ln(4); self.set_x(PAGE_L)
            self.set_font(self.fn, "", 7.5); self.set_text_color(*self.TEXT_LIGHT)
            self.multi_cell(0, 4.5, self._safe(invoice_data["notes"]), 0, "L")
        raw = self.output(dest='S')
        pdf_raw = raw.encode('latin-1') if isinstance(raw, str) else raw
        xml_data = self._build_xml(invoice_data, receiver_data, items, sender_data)
        return self._embed_xml(pdf_raw, xml_data, invoice_data), xml_data

    # ── EN 16931 / ZUGFeRD 2.3.3 XML ─────────────────────────────────────────
    def _build_xml(self, invoice_data, receiver_data, items, sender_data):
        RSM = "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
        RAM = "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
        UDT = "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100"
        ET.register_namespace('rsm', RSM)
        ET.register_namespace('ram', RAM)
        ET.register_namespace('udt', UDT)

        root = ET.Element(f"{{{RSM}}}CrossIndustryInvoice")

        ctx = ET.SubElement(root, f"{{{RSM}}}ExchangedDocumentContext")
        gp  = ET.SubElement(ctx, f"{{{RAM}}}GuidelineSpecifiedDocumentContextParameter")
        ET.SubElement(gp, f"{{{RAM}}}ID").text = ZUGFERD_GUIDELINE

        hdr = ET.SubElement(root, f"{{{RSM}}}ExchangedDocument")
        ET.SubElement(hdr, f"{{{RAM}}}ID").text       = str(invoice_data.get("invoice_number", ""))
        ET.SubElement(hdr, f"{{{RAM}}}TypeCode").text = "380"
        idt = ET.SubElement(hdr, f"{{{RAM}}}IssueDateTime")
        dt  = datetime.strptime(invoice_data.get("invoice_date"), "%d.%m.%Y")
        ET.SubElement(idt, f"{{{UDT}}}DateTimeString", format="102").text = dt.strftime("%Y%m%d")

        txn = ET.SubElement(root, f"{{{RSM}}}SupplyChainTradeTransaction")

        for i, item in enumerate(items, 1):
            li   = ET.SubElement(txn, f"{{{RAM}}}IncludedSupplyChainTradeLineItem")
            ldoc = ET.SubElement(li,  f"{{{RAM}}}AssociatedDocumentLineDocument")
            ET.SubElement(ldoc, f"{{{RAM}}}LineID").text = str(i)
            prod = ET.SubElement(li,  f"{{{RAM}}}SpecifiedTradeProduct")
            ET.SubElement(prod, f"{{{RAM}}}Name").text = item.get("product_name", "")
            agr_li = ET.SubElement(li, f"{{{RAM}}}SpecifiedLineTradeAgreement")
            price  = ET.SubElement(agr_li, f"{{{RAM}}}NetPriceProductTradePrice")
            ET.SubElement(price, f"{{{RAM}}}ChargeAmount").text = f"{item.get('unit_price', 0):.2f}"
            delv_li = ET.SubElement(li, f"{{{RAM}}}SpecifiedLineTradeDelivery")
            ET.SubElement(
                delv_li, f"{{{RAM}}}BilledQuantity",
                unitCode=item.get("unit_code", "C62")
            ).text = f"{item.get('quantity', 0):.2f}"
            sett_li = ET.SubElement(li, f"{{{RAM}}}SpecifiedLineTradeSettlement")
            ltax    = ET.SubElement(sett_li, f"{{{RAM}}}ApplicableTradeTax")
            tr      = float(invoice_data.get("tax_rate", 19))
            ET.SubElement(ltax, f"{{{RAM}}}TypeCode").text              = "VAT"
            ET.SubElement(ltax, f"{{{RAM}}}CategoryCode").text          = "S" if tr > 0 else "Z"
            ET.SubElement(ltax, f"{{{RAM}}}RateApplicablePercent").text = str(tr)
            mon = ET.SubElement(sett_li, f"{{{RAM}}}SpecifiedTradeSettlementLineMonetarySummation")
            ET.SubElement(mon, f"{{{RAM}}}LineTotalAmount").text = f"{item.get('total_price', 0):.2f}"

        agr = ET.SubElement(txn, f"{{{RAM}}}ApplicableHeaderTradeAgreement")

        leitweg = receiver_data.get("leitweg_id", "").strip()
        br_val  = leitweg or invoice_data.get("buyer_reference", "") or "n/a"
        ET.SubElement(agr, f"{{{RAM}}}BuyerReference").text = br_val

        if invoice_data.get("purchase_order_number"):
            po = ET.SubElement(agr, f"{{{RAM}}}BuyerOrderReferencedDocument")
            ET.SubElement(po, f"{{{RAM}}}IssuerAssignedID").text = invoice_data["purchase_order_number"]

        # ContractReferencedDocument ist im ZUGFeRD Basic-Profil NICHT erlaubt (nur EXTENDED).
        # Vertragsnummer wird daher nur im PDF-Text ausgegeben, nicht im XML.

        seller = ET.SubElement(agr, f"{{{RAM}}}SellerTradeParty")
        # Korrekte Reihenfolge laut EN 16931 XSD:
        # ID → Name → SpecifiedLegalOrganization → DefinedTradeContact → PostalTradeAddress → ...
        tid_raw = sender_data.get("tax_id", "").replace(" ", "").upper()
        ET.SubElement(seller, f"{{{RAM}}}Name").text = sender_data.get("company_name", "")
        legal_org = ET.SubElement(seller, f"{{{RAM}}}SpecifiedLegalOrganization")
        ET.SubElement(legal_org, f"{{{RAM}}}ID", schemeID="0002").text = (
            tid_raw or sender_data.get("company_name", "n/a")
        )

        if any([sender_data.get("contact_person"), sender_data.get("phone"), sender_data.get("email")]):
            sc = ET.SubElement(seller, f"{{{RAM}}}DefinedTradeContact")
            if sender_data.get("contact_person"):
                ET.SubElement(sc, f"{{{RAM}}}PersonName").text = sender_data["contact_person"]
            if sender_data.get("phone"):
                ph = ET.SubElement(sc, f"{{{RAM}}}TelephoneUniversalCommunication")
                ET.SubElement(ph, f"{{{RAM}}}CompleteNumber").text = sender_data["phone"]
            if sender_data.get("email"):
                em = ET.SubElement(sc, f"{{{RAM}}}EmailURIUniversalCommunication")
                ET.SubElement(em, f"{{{RAM}}}URIID").text = sender_data["email"]

        sa    = ET.SubElement(seller, f"{{{RAM}}}PostalTradeAddress")
        parts = sender_data.get("address", "").split("\n")
        if len(parts) >= 2:
            ET.SubElement(sa, f"{{{RAM}}}LineOne").text = parts[0].strip()
            pc = parts[-1].strip().split(" ", 1)
            if len(pc) == 2:
                ET.SubElement(sa, f"{{{RAM}}}PostcodeCode").text = pc[0]
                ET.SubElement(sa, f"{{{RAM}}}CityName").text     = pc[1]
        ET.SubElement(sa, f"{{{RAM}}}CountryID").text = "DE"

        trate_check = float(invoice_data.get("tax_rate", 19))
        if trate_check > 0:
            st = ET.SubElement(seller, f"{{{RAM}}}SpecifiedTaxRegistration")
            if tid_raw:
                scheme = "VA" if tid_raw.startswith("DE") else "FC"
                ET.SubElement(st, f"{{{RAM}}}ID", schemeID=scheme).text = tid_raw
            else:
                ET.SubElement(st, f"{{{RAM}}}ID", schemeID="FC").text = "UNBEKANNT"
        elif tid_raw:
            st = ET.SubElement(seller, f"{{{RAM}}}SpecifiedTaxRegistration")
            scheme = "VA" if tid_raw.startswith("DE") else "FC"
            ET.SubElement(st, f"{{{RAM}}}ID", schemeID=scheme).text = tid_raw

        buyer = ET.SubElement(agr, f"{{{RAM}}}BuyerTradeParty")
        # Korrekte Reihenfolge laut EN 16931 XSD: ID → Name → PostalTradeAddress → ...
        if receiver_data.get("customer_number"):
            ET.SubElement(buyer, f"{{{RAM}}}ID").text = receiver_data["customer_number"]
        ET.SubElement(buyer, f"{{{RAM}}}Name").text = receiver_data.get("customer_name", "")
        ba = ET.SubElement(buyer, f"{{{RAM}}}PostalTradeAddress")
        bp = receiver_data.get("customer_address", "").split("\n")
        if len(bp) >= 2:
            ET.SubElement(ba, f"{{{RAM}}}LineOne").text = bp[0].strip()
            bpc = bp[-1].strip().split(" ", 1)
            if len(bpc) == 2:
                ET.SubElement(ba, f"{{{RAM}}}PostcodeCode").text = bpc[0]
                ET.SubElement(ba, f"{{{RAM}}}CityName").text     = bpc[1]
        ET.SubElement(ba, f"{{{RAM}}}CountryID").text = "DE"
        bvat = receiver_data.get("customer_vat", "").replace(" ", "").upper()
        if bvat:
            bt = ET.SubElement(buyer, f"{{{RAM}}}SpecifiedTaxRegistration")
            ET.SubElement(bt, f"{{{RAM}}}ID", schemeID="VA").text = bvat

        delv  = ET.SubElement(txn, f"{{{RAM}}}ApplicableHeaderTradeDelivery")
        event = ET.SubElement(delv, f"{{{RAM}}}ActualDeliverySupplyChainEvent")
        occ   = ET.SubElement(event, f"{{{RAM}}}OccurrenceDateTime")
        d_str = invoice_data.get("delivery_date") or invoice_data.get("invoice_date")
        d_dt  = datetime.strptime(d_str, "%d.%m.%Y")
        ET.SubElement(occ, f"{{{UDT}}}DateTimeString", format="102").text = d_dt.strftime("%Y%m%d")

        sett = ET.SubElement(txn, f"{{{RAM}}}ApplicableHeaderTradeSettlement")
        if sender_data.get("creditor_reference"):
            ET.SubElement(sett, f"{{{RAM}}}CreditorReferenceID").text = sender_data["creditor_reference"]
        ET.SubElement(sett, f"{{{RAM}}}InvoiceCurrencyCode").text = "EUR"

        iban = sender_data.get("bank_account", "").replace(" ", "")
        if iban:
            pm  = ET.SubElement(sett, f"{{{RAM}}}SpecifiedTradeSettlementPaymentMeans")
            ET.SubElement(pm, f"{{{RAM}}}TypeCode").text = "58"
            acc = ET.SubElement(pm, f"{{{RAM}}}PayeePartyCreditorFinancialAccount")
            ET.SubElement(acc, f"{{{RAM}}}IBANID").text = iban
            if sender_data.get("bank_bic"):
                fi = ET.SubElement(pm, f"{{{RAM}}}PayeeSpecifiedCreditorFinancialInstitution")
                ET.SubElement(fi, f"{{{RAM}}}BICID").text = sender_data["bank_bic"].replace(" ", "")

        htax  = ET.SubElement(sett, f"{{{RAM}}}ApplicableTradeTax")
        trate = float(invoice_data.get("tax_rate", 19))
        ET.SubElement(htax, f"{{{RAM}}}CalculatedAmount").text     = f"{invoice_data.get('tax_amount', 0):.2f}"
        ET.SubElement(htax, f"{{{RAM}}}TypeCode").text              = "VAT"
        ET.SubElement(htax, f"{{{RAM}}}BasisAmount").text           = f"{invoice_data.get('subtotal', 0):.2f}"
        ET.SubElement(htax, f"{{{RAM}}}CategoryCode").text          = "S" if trate > 0 else "Z"
        ET.SubElement(htax, f"{{{RAM}}}RateApplicablePercent").text = str(trate)

        pt = ET.SubElement(sett, f"{{{RAM}}}SpecifiedTradePaymentTerms")
        ET.SubElement(pt, f"{{{RAM}}}Description").text = invoice_data.get(
            "payment_terms", "Zahlbar sofort ohne Abzug.")
        if invoice_data.get("due_date"):
            dd = datetime.strptime(invoice_data["due_date"], "%d.%m.%Y")
            de = ET.SubElement(pt, f"{{{RAM}}}DueDateDateTime")
            ET.SubElement(de, f"{{{UDT}}}DateTimeString", format="102").text = dd.strftime("%Y%m%d")

        subtotal        = float(invoice_data.get('subtotal', 0))
        tax_amount      = float(invoice_data.get('tax_amount', 0))
        total           = float(invoice_data.get('total', 0))
        prepaid         = float(invoice_data.get('prepaid_amount', 0))
        allowance_total = float(invoice_data.get('discount_amount', 0))
        due_payable     = total - prepaid

        summ = ET.SubElement(sett, f"{{{RAM}}}SpecifiedTradeSettlementHeaderMonetarySummation")
        ET.SubElement(summ, f"{{{RAM}}}LineTotalAmount").text      = f"{subtotal:.2f}"
        ET.SubElement(summ, f"{{{RAM}}}ChargeTotalAmount").text    = "0.00"
        ET.SubElement(summ, f"{{{RAM}}}AllowanceTotalAmount").text = f"{allowance_total:.2f}"
        ET.SubElement(summ, f"{{{RAM}}}TaxBasisTotalAmount").text  = f"{subtotal:.2f}"
        ET.SubElement(summ, f"{{{RAM}}}TaxTotalAmount", currencyID="EUR").text = f"{tax_amount:.2f}"
        ET.SubElement(summ, f"{{{RAM}}}GrandTotalAmount").text     = f"{total:.2f}"
        ET.SubElement(summ, f"{{{RAM}}}TotalPrepaidAmount").text   = f"{prepaid:.2f}"
        ET.SubElement(summ, f"{{{RAM}}}DuePayableAmount").text     = f"{due_payable:.2f}"

        return ET.tostring(root, encoding='utf-8', xml_declaration=True)

    # ── PDF/A-3b konforme Einbettung ──────────────────────────────────────────
    def _embed_xml(self, pdf_bytes: bytes, xml_bytes: bytes, invoice_data: dict) -> bytes:
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin-1')

        reader = PdfReader(io.BytesIO(pdf_bytes))
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        writer.add_attachment("factur-x.xml", xml_bytes)

        ef_ref = None
        try:
            catalog  = writer._root_object
            names_ob = catalog.get("/Names")
            if names_ob:
                names_ob = names_ob.get_object()
                ef_ob = names_ob.get("/EmbeddedFiles")
                if ef_ob:
                    ef_ob = ef_ob.get_object()
                    ef_names = ef_ob.get("/Names")
                    if ef_names:
                        ef_names = ef_names.get_object()
                        for k in range(1, len(ef_names), 2):
                            fs_ref = ef_names[k]
                            fs = fs_ref.get_object()
                            if isinstance(fs, DictionaryObject):
                                fs[NameObject("/AFRelationship")] = NameObject("/Alternative")
                                ef_ref = fs_ref
        except Exception:
            pass

        if ef_ref is not None:
            try:
                af_array = ArrayObject([ef_ref])
                writer._root_object[NameObject("/AF")] = af_array
            except Exception:
                pass

        xmp_bytes_data = _build_xmp(
            invoice_data.get("invoice_number", ""),
            invoice_data.get("invoice_date",   "")
        )
        xmp_stream = DecodedStreamObject()
        xmp_stream.set_data(xmp_bytes_data)
        xmp_stream.update({
            NameObject("/Type"):    NameObject("/Metadata"),
            NameObject("/Subtype"): NameObject("/XML"),
        })
        xmp_ref = writer._add_object(xmp_stream)
        writer._root_object[NameObject("/Metadata")] = xmp_ref

        mark_info = DictionaryObject({
            NameObject("/Marked"): BooleanObject(True),
        })
        writer._root_object[NameObject("/MarkInfo")] = mark_info

        icc_stream = DecodedStreamObject()
        icc_stream.set_data(b"")
        icc_stream.update({
            NameObject("/N"): NumberObject(3),
        })
        icc_ref = writer._add_object(icc_stream)

        output_intent = DictionaryObject({
            NameObject("/Type"):             NameObject("/OutputIntent"),
            NameObject("/S"):                NameObject("/GTS_PDFA1"),
            NameObject("/OutputConditionIdentifier"): ByteStringObject(b"sRGB"),
            NameObject("/RegistryName"):     ByteStringObject(b"http://www.color.org"),
            NameObject("/Info"):             ByteStringObject(b"sRGB IEC61966-2.1"),
            NameObject("/DestOutputProfile"): icc_ref,
        })
        oi_ref = writer._add_object(output_intent)
        writer._root_object[NameObject("/OutputIntents")] = ArrayObject([oi_ref])

        viewer_prefs = DictionaryObject({
            NameObject("/DisplayDocTitle"): BooleanObject(True),
        })
        writer._root_object[NameObject("/ViewerPreferences")] = viewer_prefs

        writer.add_metadata({
            '/Title':        f'ZUGFeRD Rechnung {invoice_data.get("invoice_number", "")}',
            '/Creator':      'FRechnung v1.2.0',
            '/Producer':     'FRechnung v1.2.0 / pypdf',
            '/Subject':      'ZUGFeRD 2.3.3 Basic',
            '/CreationDate': datetime.utcnow().strftime("D:%Y%m%d%H%M%S+00'00'"),
            '/ModDate':      datetime.utcnow().strftime("D:%Y%m%d%H%M%S+00'00'"),
        })

        out = io.BytesIO()
        writer.write(out)
        pdf_out = out.getvalue()

        for old in [b'%PDF-1.3', b'%PDF-1.4', b'%PDF-1.5', b'%PDF-1.6']:
            pdf_out = pdf_out.replace(old, b'%PDF-1.7', 1)

        binary_comment = b'\x25\xe2\xe3\xcf\xd3\n'
        pdf_out = pdf_out.replace(b'%PDF-1.7\n', b'%PDF-1.7\n' + binary_comment, 1)

        return pdf_out


# ── Öffentliche API ───────────────────────────────────────────────────────────

def create_invoice_pdf(invoice_data, receiver_data, items, sender_data,
                       logo_path="", theme_name="Klassisch Blau"):
    gen = PDFGenerator(theme_name=theme_name)
    gen.logo_path = logo_path
    return gen.generate_invoice(invoice_data, receiver_data, items, sender_data)