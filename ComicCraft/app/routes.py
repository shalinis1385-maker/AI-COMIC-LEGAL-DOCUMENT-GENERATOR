from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.schemas import ComicResponse, PromptRequest
from app.services.exporters import save_pdf
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout

router = APIRouter()
settings = get_settings()
templates = Jinja2Templates(directory=str(settings.templates_dir))


def run_pipeline(request: PromptRequest):
    outline = generate_outline(request)
    story = generate_story(request, outline)
    image_paths = [
        generate_image(panel.image_prompt, panel.panel_number)
        for panel in story
    ]
    layout = build_comic_layout(story, image_paths)
    pdf_path = save_pdf(layout)
    pdf_url = f"/static/exports/{pdf_path.name}"
    return layout, pdf_url


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request},
    )


@router.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        prompt_request = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )
        layout, pdf_url = run_pipeline(prompt_request)
        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "request": request,
                "layout": layout,
                "pdf_url": pdf_url,
                "mode": settings.ai_mode,
            },
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"request": request, "error": str(exc)},
            status_code=500,
        )


@router.post("/generate-comic/json", response_model=ComicResponse)
async def generate_json(payload: PromptRequest):
    try:
        layout, pdf_url = run_pipeline(payload)
        return ComicResponse(
            success=True,
            panels=layout,
            pdf_url=pdf_url,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/test-image")
async def test_image(prompt: str = "A brave fox in an enchanted forest, comic book style"):
    try:
        path = generate_image(prompt, 0)
        return {"success": True, "image_url": f"/static/panels/{Path(path).name}"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request, pdf: str | None = None):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={"request": request, "pdf_url": pdf},
    )


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "ai_mode": settings.ai_mode,
        "gemini_configured": bool(settings.gemini_api_key),
        "huggingface_configured": bool(settings.hf_token),
    }
