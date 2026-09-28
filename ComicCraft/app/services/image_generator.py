from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from huggingface_hub import InferenceClient

from app.config import get_settings
from app.utils.files import safe_filename


def _font(size: int):
    candidates = [
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size=size)
            except OSError:
                pass
    return ImageFont.load_default()


def _demo_image(prompt: str, output_path: Path, panel_number: int) -> Path:
    settings = get_settings()
    image = Image.new("RGB", (settings.image_width, settings.image_height), (245, 238, 218))
    draw = ImageDraw.Draw(image)
    title_font = _font(42)
    body_font = _font(22)
    draw.rectangle((28, 28, settings.image_width - 28, settings.image_height - 28), outline=(30, 30, 30), width=6)
    draw.text((60, 60), f"COMICCRAFT — PANEL {panel_number}", font=title_font, fill=(25, 25, 25))
    wrapped = []
    words = prompt.split()
    line = ""
    for word in words:
        if len(line) + len(word) + 1 > 48:
            wrapped.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    if line:
        wrapped.append(line)
    y = 180
    for line in wrapped[:14]:
        draw.text((60, y), line, font=body_font, fill=(55, 55, 55))
        y += 34
    draw.ellipse((settings.image_width - 240, settings.image_height - 240,
                  settings.image_width - 80, settings.image_height - 80),
                 outline=(40, 40, 40), width=6)
    draw.text((settings.image_width - 220, settings.image_height - 205), "AI", font=title_font, fill=(25, 25, 25))
    image.save(output_path, format="PNG")
    return output_path


def generate_image(image_prompt: str, panel_number: int) -> Path:
    settings = get_settings()
    filename = f"{panel_number:02d}_{safe_filename(image_prompt)}.png"
    output_path = settings.panels_dir / filename

    if settings.ai_mode.lower() == "demo" or not settings.hf_token:
        return _demo_image(image_prompt, output_path, panel_number)

    client = InferenceClient(
        provider=settings.hf_provider,
        api_key=settings.hf_token,
    )
    prompt = (
        f"{image_prompt}. High-quality comic panel illustration, consistent character design, "
        "no text, no speech bubbles, clear focal subject, polished digital art."
    )
    image = client.text_to_image(
        prompt=prompt,
        model=settings.hf_image_model,
    )
    image.save(output_path)
    return output_path
