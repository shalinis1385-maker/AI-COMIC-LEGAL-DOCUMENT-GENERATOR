import os
os.environ["AI_MODE"] = "demo"

from app.schemas import PromptRequest
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout
from app.services.exporters import save_pdf


def test_full_demo_pipeline():
    request = PromptRequest(
        story_prompt="A brave fox explores an enchanted forest.",
        character_name="Lumi",
        setting="enchanted forest",
        tone="funny",
        art_style="comic book",
    )
    outline = generate_outline(request)
    story = generate_story(request, outline)
    images = [generate_image(p.image_prompt, p.panel_number) for p in story]
    layout = build_comic_layout(story, images)
    pdf = save_pdf(layout)

    assert len(outline) == 5
    assert len(story) == 5
    assert len(images) == 5
    assert pdf.exists()
    assert pdf.stat().st_size > 0
