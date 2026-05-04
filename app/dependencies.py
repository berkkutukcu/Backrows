from typing import Optional

from fastapi import HTTPException, Request, status

from .repository import get_user_by_id


def current_user(request: Request):
    user_id: Optional[int] = request.session.get("user_id")
    if not user_id:
        return None
    return get_user_by_id(user_id)


def require_role(*roles: str):
    def _dep(request: Request):
        user = current_user(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Giriş yapmalısınız.",
            )
        if user["rol"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu sayfaya erişim yetkiniz yok.",
            )
        return user

    return _dep


require_admin = require_role("admin")
require_katilimci = require_role("katilimci")
require_ziyaretci = require_role("ziyaretci")
