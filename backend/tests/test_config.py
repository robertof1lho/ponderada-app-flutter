from app.core.config import settings

def test_settings_has_required_fields():
    assert hasattr(settings, "supabase_url")
    assert hasattr(settings, "neo4j_uri")
    assert hasattr(settings, "google_vision_api_key")
    assert hasattr(settings, "replicate_api_token")
