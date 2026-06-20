from app.services.prompt_service import PromptService

def test_builds_anime_prompt():
    service = PromptService()
    prompt = service.build_prompt(
        traits={"expression": "smiling", "hair_color": "black"},
        universe="anime",
    )
    assert "anime" in prompt.lower()
    assert "smiling" in prompt.lower() or "smile" in prompt.lower()

def test_prompt_includes_quality_suffix():
    service = PromptService()
    prompt = service.build_prompt(traits={}, universe="medieval")
    assert "high quality" in prompt.lower() or "detailed" in prompt.lower()

def test_extract_style_tags_includes_universe():
    service = PromptService()
    tags = service.extract_style_tags(
        traits={"expression": "smiling", "hair_color": "black"},
        universe="anime",
    )
    assert "anime" in tags
    assert "smiling" in tags
    assert "black_hair" in tags
