import json
from google import genai
from google.genai import types

from app.config import get_settings
from app.schemas import PanelOutline, PanelStory, PromptRequest


def _demo_story(request: PromptRequest, outline: list[PanelOutline]) -> list[PanelStory]:
    dialogues = [
        f"{request.character_name}: “Something is waiting for me here.”",
        f"{request.character_name}: “This clue must mean something.”",
        f"{request.character_name}: “I can face this.”",
        f"{request.character_name}: “Courage is the first step.”",
        f"{request.character_name}: “This is only the beginning.”",
    ]
    captions = [
        "A quiet moment before the adventure.",
        "A secret changes the direction of the journey.",
        "The hardest moment arrives.",
        "Courage turns the challenge into an opportunity.",
        "The adventure ends, but a new chapter begins.",
    ]
    return [
        PanelStory(
            panel_number=p.panel_number,
            title=p.title,
            scene_description=p.scene_description,
            caption=captions[i],
            narration=f"{p.scene_description} The moment feels {request.tone}, and {request.character_name} moves forward with purpose.",
            dialogue=dialogues[i],
            image_prompt=p.image_prompt,
        )
        for i, p in enumerate(outline)
    ]


def generate_story(
    request: PromptRequest, outline: list[PanelOutline]
) -> list[PanelStory]:
    settings = get_settings()
    if settings.ai_mode.lower() == "demo" or not settings.gemini_api_key:
        return _demo_story(request, outline)

    client = genai.Client(api_key=settings.gemini_api_key)
    outline_json = json.dumps([p.model_dump() for p in outline], ensure_ascii=False)

    prompt = f"""
Expand this comic outline into polished panel-by-panel comic writing.

Original idea: {request.story_prompt}
Character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Art style: {request.art_style}

Outline:
{outline_json}

Return ONLY valid JSON matching:
[
  {{
    "panel_number": 1,
    "title": "same or improved title",
    "scene_description": "short visual scene description",
    "caption": "brief environmental or comic caption",
    "narration": "2-4 sentences of story narration",
    "dialogue": "short dialogue or internal line",
    "image_prompt": "detailed visual prompt preserving character continuity"
  }}
]

Keep the same character, setting, tone, and visual identity across panels.
"""
    response = client.models.generate_content(
        model=settings.gemini_story_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[PanelStory],
            max_output_tokens=5000,
        ),
    )
    data = json.loads(response.text)
    panels = [PanelStory.model_validate(item) for item in data]
    if len(panels) != len(outline):
        raise ValueError("Story generation returned an unexpected panel count.")
    return panels
