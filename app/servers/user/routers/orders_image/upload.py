from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.dependencies import get_session
from app.database.models.user import User
from app.servers.user.dependencies import CurrentUser
from app.servers.user.services.order_image.add import add_order_image
from app.services.storage import StorageService

router = APIRouter()


@router.post("/{order_id}/{position}", status_code=status.HTTP_201_CREATED,)
async def add_order_photo(
    order_id: int,
    user: CurrentUser,
    request: Request,
    position: str,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    storage = request.app.state.photo_storage
    
    await add_order_image(
        session=session,
        storage=storage,
        user=user,
        order_id=order_id,
        position=position,
        upload_file=file,
    )

    return