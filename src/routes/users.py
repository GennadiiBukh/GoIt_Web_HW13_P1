import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, File, Depends, APIRouter, HTTPException, status, Request
from sqlalchemy.orm import Session

from src.conf.limiter_config import limiter
from src.database.db import get_db
from src.database.models import User
from src.schemas import UserResponse
from src.conf.config import config
from src.services.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
)


@router.patch("/avatar", response_model=UserResponse)
@limiter.limit("10/minute", key_func=lambda request: request.client.host)
async def update_avatar(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type"
        )

    public_id = f"Web16_BGU/{current_user.email}"
    result = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)

    # Створюємо URL з визначеними параметрами
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=result.get("version")
    )
    current_user.avatar = res_url
    db.commit()
    db.refresh(current_user)

    return current_user
