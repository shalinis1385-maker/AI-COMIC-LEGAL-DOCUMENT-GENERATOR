from datetime import datetime
from pathlib import Path

from fpdf import FPDF

from app.config import get_settings


def _safe_text(text: str) -> str:
    return text.replace("“", '"').replace("”", '"').replace("’", "'").replace("–", "-").replace("—", "-")


def save_pdf(layout: list[dict]) -> Path:
    settings = get_settings()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = settings.exports_dir / f"comiccraft_{timestamp}.pdf"

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=14)

    for index, panel in enumerate(layout):
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.multi_cell(0, 10, _safe_text(f"Panel {panel['panel_number']}: {panel['title']}"))
        pdf.ln(3)

        image_path = Path(panel["image_path"])
        if image_path.exists():
            page_width = 182
            pdf.image(str(image_path), x=14, y=36, w=page_width)
            pdf.set_y(142)

        pdf.set_font("Helvetica", "I", 10)
        pdf.multi_cell(0, 6, _safe_text(panel["scene_description"]))
        pdf.ln(2)

        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 7, _safe_text("Caption"))
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, _safe_text(panel["caption"]))
        pdf.ln(1)

        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 7, _safe_text("Narration"))
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, _safe_text(panel["narration"]))
        pdf.ln(1)

        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 7, _safe_text("Dialogue"))
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, _safe_text(panel["dialogue"]))

    pdf.output(str(output))
    return output
