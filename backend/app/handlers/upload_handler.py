import uuid
from fastapi import APIRouter, UploadFile, File, Depends
from app.middleware.auth import verify_jwt_token
from app.core.storage import get_storage_client
from app.core.config import settings

router = APIRouter()


@router.post("/selfie")
async def upload_selfie(
    file: UploadFile = File(...),
    claims: dict = Depends(verify_jwt_token),
):
    contents = await file.read()
    client = get_storage_client()
    path = f"selfies/{claims['sub']}/{uuid.uuid4()}.jpg"
    client.put_object(
        Bucket=settings.minio_bucket,
        Key=path,
        Body=contents,
        ContentType="image/jpeg",
    )
    # Retorna URL pública (acessível pelo browser)
    public_url = f"{settings.public_endpoint}/{settings.minio_bucket}/{path}"
    return {"url": public_url}
