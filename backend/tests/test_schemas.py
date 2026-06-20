from app.models.schemas import GenerateAlterEgoRequest, AlterEgoResponse, FeedItem

def test_generate_request_requires_fields():
    from pydantic import ValidationError
    import pytest
    with pytest.raises(ValidationError):
        GenerateAlterEgoRequest()

def test_alter_ego_response_has_image_url():
    r = AlterEgoResponse(id="abc", image_url="https://example.com/img.png", universe="anime")
    assert r.image_url == "https://example.com/img.png"
