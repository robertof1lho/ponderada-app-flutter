from app.core.config import settings


def test_settings_has_required_fields():
    assert hasattr(settings, "mysql_url")
    assert hasattr(settings, "minio_endpoint")
    assert hasattr(settings, "jwt_secret")
    assert hasattr(settings, "hf_api_token")
