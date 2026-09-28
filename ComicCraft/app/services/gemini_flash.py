import json
from google import genai
from google.genai import types

from app.config import get_settings
from app.schemas import PanelOutline, PromptRequest


def _demo_outline(request: PromptRequest) -> list[PanelOutline]:
    return [
        PanelOutline(
            panel_number=1,
            title="The Beginning",
            scene_description=f"{request.character_name} arrives at the {request.setting}, sensing that an unusual adventure is about to begin.",
            image_prompt=f"{request.character_name} at the entrance of a {request.setting}, cinematic establishing shot, {request.art_style}, {request.tone}, expressive character, clean composition",
        ),
        PanelOutline(
            panel_number=2,
            title="A Strange Discovery",
            scene_description=f"{request.character_name} discovers a mysterious clue hidden in the {request.setting}.",
            image_prompt=f"{request.character_name} discovering a mysterious glowing clue in a {request.setting}, {request.art_style}, {request.tone}, dramatic lighting, comic panel composition",
        ),
        PanelOutline(
            panel_number=3,
            title="The Challenge",
            scene_description=f"A sudden obstacle forces {request.character_name} to make a brave decision.",
            image_prompt=f"{request.character_name} facing a challenging obstacle in the {request.setting}, dynamic action pose, {request.art_style}, {request.tone}, vivid comic illustration",
        ),
        PanelOutline(
            panel_number=4,
            title="The Turning Point",
            scene_description=f"{request.character_name} uses courage and creativity to overcome the obstacle.",
            image_prompt=f"{request.character_name} overcoming the challenge in the {request.setting}, heroic moment, {request.art_style}, {request.tone}, energetic comic-book framing",
        ),
        PanelOutline(
            panel_number=5,
            title="A New Beginning",
            scene_description=f"{request.character_name} looks toward the future, carrying the lesson learned from the adventure.",
            image_prompt=f"{request.character_name} standing triumphantly in the {request.setting}, hopeful ending, {request.art_style}, {request.tone}, beautiful final comic panel",
        ),
    ]


def generate_outline(request: PromptRequest) -> list[PanelOutline]:
    settings = get_settings()
    if settings.ai_mode.lower() == "demo" or not settings.gemini_api_key:
        return _demo_outline(request)

    client = genai.Client(api_key=settings.gemini_api_key)
    prompt = f"""
Create a coherent {settings.panel_count}-panel comic outline.

User story idea: {request.story_prompt}
Main character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Art style: {request.art_style}

Return ONLY valid JSON matching this schema:
[
  {{
    "panel_number": 1,
    "title": "short title",
    "scene_description": "1-2 sentence visual scene description",
    "image_prompt": "detailed prompt for an image model"
  }}
]

Rules:
- Exactly {settings.panel_count} panels.
- Keep the same main character across all panels.
- Make the story have a clear beginning, development, challenge, and ending.
- Do not put dialogue in image_prompt.
- Make each image prompt visually specific.
"""
    response = client.models.generate_content(
        model=settings.gemini_outline_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[PanelOutline],
            max_output_tokens=3000,
        ),
    )
    data = json.loads(response.text)
    panels = [PanelOutline.model_validate(item) for item in data]
    if len(panels) != settings.panel_count:
        raise ValueError(f"Gemini returned {len(panels)} panels; expected {settings.panel_count}.")
    return panels
