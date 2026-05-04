from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from ..config import EMAIL_CODE_TTL_SECONDS, TEMPLATES_DIR
from ..dependencies import current_user
from ..repository import (
    create_user,
    delete_verification,
    get_user_by_email,
    get_user_by_qr_token,
    get_verification,
    save_verification,
)
from ..security import (
    create_verification_code,
    hash_password,
    verify_password,
)
from ..validators import (
    ad_soyad_gecerli,
    eposta_gecerli,
    sifre_gecerli,
    telefon_gecerli,
)

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


_ROL_DASHBOARD = {
    "admin": "/admin",
    "katilimci": "/katilimci",
    "ziyaretci": "/ziyaretci",
}


def _redirect_for_role(rol: str) -> str:
    return _ROL_DASHBOARD.get(rol, "/")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    user = current_user(request)
    if user:
        return RedirectResponse(_redirect_for_role(user["rol"]), status_code=303)
    return templates.TemplateResponse(request, "login.html", {"hata": None})


@router.post("/login")
async def login(
    request: Request,
    eposta: str = Form(...),
    sifre: str = Form(...),
):
    user = get_user_by_email(eposta.strip().lower())
    if not user or not verify_password(sifre, user["sifre_hash"]):
        return templates.TemplateResponse(
            request,
            "login.html",
            {"hata": "E-posta veya şifre hatalı."},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    request.session["user_id"] = user["id"]
    request.session["rol"] = user["rol"]
    return RedirectResponse(_redirect_for_role(user["rol"]), status_code=303)


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)


@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse(request, "register.html", {"hata": None})


@router.post("/register")
async def register(
    request: Request,
    ad: str = Form(...),
    soyad: str = Form(...),
    telefon: str = Form(...),
    eposta: str = Form(...),
    sifre: str = Form(...),
    sifre_tekrar: str = Form(...),
):
    hata = _validate_register(ad, soyad, telefon, eposta, sifre, sifre_tekrar)
    if hata:
        return templates.TemplateResponse(
            request,
            "register.html",
            {
                "hata": hata,
                "ad": ad,
                "soyad": soyad,
                "telefon": telefon,
                "eposta": eposta,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    normalized = eposta.strip().lower()
    if get_user_by_email(normalized):
        return templates.TemplateResponse(
            request,
            "register.html",
            {
                "hata": "Bu e-posta adresi zaten kayıtlı.",
                "ad": ad,
                "soyad": soyad,
                "telefon": telefon,
                "eposta": eposta,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    kod = create_verification_code()
    expires = datetime.now(timezone.utc) + timedelta(seconds=EMAIL_CODE_TTL_SECONDS)
    save_verification(
        eposta=normalized,
        kod=kod,
        ad=ad.strip(),
        soyad=soyad.strip(),
        telefon=telefon.strip(),
        sifre_hash=hash_password(sifre),
        expires_at=expires.isoformat(),
    )
    return templates.TemplateResponse(
        request,
        "verify_email.html",
        {"eposta": normalized, "kod": kod, "hata": None},
    )


def _validate_register(
    ad: str, soyad: str, telefon: str, eposta: str, sifre: str, sifre_tekrar: str
) -> str | None:
    if not ad_soyad_gecerli(ad.strip()):
        return "Ad en az 2 harf olmalı ve sadece harflerden oluşmalı."
    if not ad_soyad_gecerli(soyad.strip()):
        return "Soyad en az 2 harf olmalı ve sadece harflerden oluşmalı."
    if not telefon_gecerli(telefon.strip()):
        return "Telefon 10 haneli olmalı ve başında 0 olmamalı."
    if not eposta_gecerli(eposta.strip()):
        return "Geçerli bir e-posta adresi giriniz."
    if not sifre_gecerli(sifre):
        return "Şifre en az 8 karakter ve en az bir özel karakter içermelidir."
    if sifre != sifre_tekrar:
        return "Şifreler eşleşmiyor."
    return None


@router.post("/register/verify")
async def verify_email(
    request: Request,
    eposta: str = Form(...),
    kod: str = Form(...),
):
    normalized = eposta.strip().lower()
    record = get_verification(normalized)
    if not record:
        return templates.TemplateResponse(
            request,
            "verify_email.html",
            {"eposta": normalized, "kod": None, "hata": "Doğrulama kaydı bulunamadı."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    expires_at = datetime.fromisoformat(record["expires_at"])
    if expires_at < datetime.now(timezone.utc):
        delete_verification(normalized)
        return templates.TemplateResponse(
            request,
            "verify_email.html",
            {"eposta": normalized, "kod": None, "hata": "Doğrulama kodu süresi doldu."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if kod.strip() != record["kod"]:
        return templates.TemplateResponse(
            request,
            "verify_email.html",
            {"eposta": normalized, "kod": record["kod"], "hata": "Kod hatalı."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    create_user(
        ad=record["ad"],
        soyad=record["soyad"],
        telefon=record["telefon"],
        eposta=record["eposta"],
        sifre_hash=record["sifre_hash"],
        rol="ziyaretci",
    )
    delete_verification(normalized)
    return templates.TemplateResponse(
        request,
        "login.html",
        {
            "hata": None,
            "mesaj": "Kayıt tamamlandı. Giriş yapabilirsiniz.",
        },
    )


@router.get("/qr-login", response_class=HTMLResponse)
async def qr_login_page(request: Request):
    return templates.TemplateResponse(request, "qr_login.html", {})


class QrLoginIn(BaseModel):
    token: str


@router.post("/qr-login")
async def qr_login(request: Request, body: QrLoginIn):
    user = get_user_by_qr_token(body.token.strip())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="QR kodu tanınmadı.",
        )
    request.session["user_id"] = user["id"]
    request.session["rol"] = user["rol"]
    return JSONResponse({"redirect": _redirect_for_role(user["rol"])})
