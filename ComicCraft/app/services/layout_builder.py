from pathlib import Path
from app.schemas import PanelStory


def build_comic_layout(
    stories: list[PanelStory], image_paths: list[Path]
) -> list[dict]:
    if len(stories) != len(image_paths):
        raise ValueError("Every story panel must have a matching image.")

    return [
        {
            "panel_number": story.panel_number,
            "title": story.title,
            "image_path": str(image_path),
            "image_url": f"/static/panels/{image_path.name}",
            "scene_description": story.scene_description,
            "caption": story.caption,
            "narration": story.narration,
            "dialogue": story.dialogue,
            "image_prompt": story.image_prompt,
        }
        for story, image_path in zip(stories, image_paths)
    ]
