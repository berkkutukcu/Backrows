from io import BytesIO

import qrcode
from fastapi import APIRouter, HTTPException, Response, status

from ..repository import get_user_by_qr_token

router = APIRouter()


@router.get("/qr/{token}.png")
async def qr_image(token: str):
    user = get_user_by_qr_token(token.strip())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="QR kodu bulunamadı."
        )
    img = qrcode.make(token)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return Response(
        content=buf.getvalue(),
        media_type="image/png",
        headers={"Cache-Control": "no-store"},
    )
