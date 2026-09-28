# ComicCraft — AI Comic Story Creator

ComicCraft is a FastAPI web application that turns a user's story idea into a five-panel comic:
1. Gemini generates a structured panel outline.
2. Gemini expands the outline into narration, captions, and dialogue.
3. Hugging Face Inference Providers generates an illustration for each panel.
4. FastAPI renders the comic in Jinja2.
5. FPDF2 exports the complete comic as a PDF.

The implementation keeps the architecture from the supplied project document while updating the integrations to current SDKs:
- Google uses the `google-genai` SDK rather than the retired `google-generativeai` package.
- Hugging Face uses `huggingface_hub.InferenceClient` and its Inference Providers for text-to-image.
- The exact models are configurable through `.env`.

## Project structure

```text
ComicCraft/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── routes.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini_flash.py
│   │   ├── gemini_pro.py
│   │   ├── image_generator.py
│   │   ├── layout_builder.py
│   │   └── exporters.py
│   └── utils/
│       ├── __init__.py
│       └── files.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── comic_preview.html
│   └── export_success.html
├── static/
│   ├── css/style.css
│   ├── js/app.js
│   ├── panels/.gitkeep
│   └── exports/.gitkeep
├── tests/
│   ├── test_api.py
│   └── test_services.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 1. VS Code setup

Install:
- Python 3.11 or newer
- VS Code
- Git (optional)

Open the `ComicCraft` folder in VS Code.

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell blocks activation, use Command Prompt:

```bat
.venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

## 2. Configure AI

Open `.env`.

For a real AI run:

```dotenv
AI_MODE=ai
GEMINI_API_KEY=your_key
HF_TOKEN=your_token
```

The Google Gemini API requires an API key. Hugging Face image generation requires a token with appropriate Inference Providers access.

For a no-key local smoke test:

```dotenv
AI_MODE=demo
```

Demo mode creates deterministic placeholder panel art and still exercises the FastAPI, Jinja2, layout, PDF, and API pipeline.

## 3. Run

From the project root:

```bash
uvicorn app.main:app --reload
```

Open:

- Website: http://127.0.0.1:8000
- Swagger/OpenAPI: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

## 4. Test

Run:

```bash
pytest -q
```

The tests use demo mode, so they do not consume API credits.

## 5. API example

POST JSON to `/generate-comic/json`:

```json
{
  "story_prompt": "A brave fox explores an enchanted forest.",
  "character_name": "Lumi",
  "setting": "enchanted forest",
  "tone": "dramatic",
  "art_style": "comic book"
}
```

Example with curl:

```bash
curl -X POST http://127.0.0.1:8000/generate-comic/json \
  -H "Content-Type: application/json" \
  -d "{\"story_prompt\":\"A brave fox explores an enchanted forest.\",\"character_name\":\"Lumi\",\"setting\":\"enchanted forest\",\"tone\":\"dramatic\",\"art_style\":\"comic book\"}"
```

## 6. Notes about the supplied project document

The supplied document describes Gemini 1.5 Flash/Pro and `runwayml/stable-diffusion-v1-5`. Those are retained as the conceptual architecture, but the code makes model names configurable because model availability and SDKs change over time. The current Google GenAI SDK is used in this implementation.

The app intentionally keeps outline generation and story generation as separate service functions (`gemini_flash.py` and `gemini_pro.py`) so the architecture remains easy to explain in a project presentation, even when both functions use the same modern Gemini model by default.

## 7. Common fixes

### `ModuleNotFoundError`
Make sure the virtual environment is activated and run:

```bash
pip install -r requirements.txt
```

### `GEMINI_API_KEY is missing`
Set `AI_MODE=demo` for local testing, or put your real key in `.env`.

### Hugging Face image generation fails
Check `HF_TOKEN`, the selected model, and the provider availability. You can temporarily use `AI_MODE=demo` to verify the rest of the application.

### PDF cannot be generated
Confirm that `fpdf2` and Pillow installed correctly:

```bash
pip install --upgrade fpdf2 Pillow
```
