"""
Styled PDF export for generated lecture notes.
"""

from html import escape
from pathlib import Path
import re
import tempfile

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def build_notes_pdf(notes: str, lecture_text: str = "", language: str = None) -> bytes:
    """Build a polished PDF from markdown-like notes and return its bytes."""
    font_name = _register_font()
    styles = _styles(font_name)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        output_path = Path(temp_file.name)

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=1.4 * cm,
        bottomMargin=1.4 * cm,
        title="Lecture Notes",
    )

    story = [
        Paragraph("Lecture Notes", styles["Title"]),
        Paragraph(language or "Generated study material", styles["Subtitle"]),
        Spacer(1, 0.35 * cm),
    ]

    stats = [
        ["Words", str(len((lecture_text or notes).split()))],
        ["Sections", str(sum(1 for line in notes.splitlines() if line.strip().startswith("#")))],
    ]
    story.append(Table(stats, colWidths=[4 * cm, 10 * cm], style=_summary_table_style()))
    story.append(Spacer(1, 0.35 * cm))

    for block in _parse_notes(notes):
        kind = block["kind"]
        text = block["text"]
        if kind == "h1":
            story.append(Paragraph(_inline(text), styles["Heading1"]))
        elif kind == "h2":
            story.append(Paragraph(_inline(text), styles["Heading2"]))
        elif kind == "h3":
            story.append(Paragraph(_inline(text), styles["Heading3"]))
        elif kind == "bullet":
            story.append(Paragraph(f"• {_inline(text)}", styles["Bullet"]))
        elif kind == "blank":
            story.append(Spacer(1, 0.12 * cm))
        else:
            story.append(Paragraph(_inline(text), styles["Body"]))

    document.build(story, onFirstPage=_footer, onLaterPages=_footer)
    data = output_path.read_bytes()
    output_path.unlink(missing_ok=True)
    return data


def _register_font() -> str:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            try:
                pdfmetrics.registerFont(TTFont("LectureFont", candidate))
                return "LectureFont"
            except Exception:
                continue
    return "Helvetica"


def _styles(font_name: str) -> dict:
    base = getSampleStyleSheet()
    return {
        "Title": ParagraphStyle(
            "LectureTitle",
            parent=base["Title"],
            fontName=font_name,
            fontSize=24,
            leading=30,
            textColor=colors.HexColor("#163B2D"),
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "Subtitle": ParagraphStyle(
            "LectureSubtitle",
            parent=base["BodyText"],
            fontName=font_name,
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#53605A"),
            alignment=TA_CENTER,
        ),
        "Heading1": ParagraphStyle(
            "LectureHeading1",
            parent=base["Heading1"],
            fontName=font_name,
            fontSize=18,
            leading=23,
            textColor=colors.HexColor("#163B2D"),
            spaceBefore=14,
            spaceAfter=8,
        ),
        "Heading2": ParagraphStyle(
            "LectureHeading2",
            parent=base["Heading2"],
            fontName=font_name,
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#275A45"),
            spaceBefore=10,
            spaceAfter=6,
        ),
        "Heading3": ParagraphStyle(
            "LectureHeading3",
            parent=base["Heading3"],
            fontName=font_name,
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#32413A"),
            spaceBefore=8,
            spaceAfter=4,
        ),
        "Body": ParagraphStyle(
            "LectureBody",
            parent=base["BodyText"],
            fontName=font_name,
            fontSize=10.5,
            leading=15,
            textColor=colors.HexColor("#1F2723"),
            spaceAfter=5,
        ),
        "Bullet": ParagraphStyle(
            "LectureBullet",
            parent=base["BodyText"],
            fontName=font_name,
            fontSize=10.2,
            leading=14,
            leftIndent=0.45 * cm,
            firstLineIndent=-0.2 * cm,
            textColor=colors.HexColor("#1F2723"),
            spaceAfter=4,
        ),
    }


def _summary_table_style() -> TableStyle:
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EEF5F1")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#163B2D")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#BFD7CA")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D8E7DF")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ])


def _parse_notes(notes: str) -> list:
    blocks = []
    for line in notes.splitlines():
        stripped = line.strip()
        if not stripped:
            blocks.append({"kind": "blank", "text": ""})
        elif stripped.startswith("### "):
            blocks.append({"kind": "h3", "text": stripped[4:]})
        elif stripped.startswith("## "):
            blocks.append({"kind": "h2", "text": stripped[3:]})
        elif stripped.startswith("# "):
            blocks.append({"kind": "h1", "text": stripped[2:]})
        elif stripped.startswith(("- ", "* ")):
            blocks.append({"kind": "bullet", "text": stripped[2:]})
        else:
            blocks.append({"kind": "body", "text": stripped})
    return blocks


def _inline(text: str) -> str:
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    text = re.sub(r"`(.+?)`", r"<font backColor='#EEF5F1'>\1</font>", text)
    text = re.sub(r"([A-Za-z0-9)\]])\^([A-Za-z0-9+\-]+)", r"\1<super>\2</super>", text)
    return text


def _footer(canvas, document):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#BFD7CA"))
    canvas.line(document.leftMargin, 1.05 * cm, A4[0] - document.rightMargin, 1.05 * cm)
    canvas.setFillColor(colors.HexColor("#53605A"))
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(A4[0] / 2, 0.65 * cm, f"Page {document.page}")
    canvas.restoreState()
