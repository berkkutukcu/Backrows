from io import BytesIO

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from PIL import Image, UnidentifiedImageError

from ..config import ANNOUNCEMENT_SIZE, ANNOUNCEMENT_SLOTS, ANNOUNCEMENTS_DIR, TEMPLATES_DIR
from ..dependencies import require_admin
from ..repository import (
    create_fuar,
    create_user,
    delete_user,
    get_user_by_email,
    list_etkinlikler,
    list_fuarlar,
    list_users,
    approve_etkinlik,
)
from ..security import hash_password
from ..validators import (
    ad_soyad_gecerli,
    eposta_gecerli,
    sifre_gecerli,
    tarih_gecerli,
    telefon_gecerli,
)

router = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("")
async def dashboard(request: Request, user=Depends(require_admin)):
    return templates.TemplateResponse(
        request, "admin/dashboard.html", {"user": user}
    )


@router.get("/users")
async def users_page(request: Request, hata: str | None = None, mesaj: str | None = None):
    return templates.TemplateResponse(
        request,
        "admin/users.html",
        {"users": list_users(), "hata": hata, "mesaj": mesaj},
    )


@router.post("/users")
async def users_create(
    request: Request,
    ad: str = Form(...),
    soyad: str = Form(...),
    telefon: str = Form(...),
    eposta: str = Form(...),
    sifre: str = Form(...),
    rol: str = Form(...),
):
    hata = _validate_new_user(ad, soyad, telefon, eposta, sifre, rol)
    if hata:
        return templates.TemplateResponse(
            request,
            "admin/users.html",
            {"users": list_users(), "hata": hata, "mesaj": None},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    normalized = eposta.strip().lower()
    if get_user_by_email(normalized):
        return templates.TemplateResponse(
            request,
            "admin/users.html",
            {
                "users": list_users(),
                "hata": "Bu e-posta zaten kayıtlı.",
                "mesaj": None,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    create_user(
        ad=ad.strip(),
        soyad=soyad.strip(),
        telefon=telefon.strip(),
        eposta=normalized,
        sifre_hash=hash_password(sifre),
        rol=rol,
    )
    return RedirectResponse("/admin/users", status_code=303)


def _validate_new_user(
    ad: str, soyad: str, telefon: str, eposta: str, sifre: str, rol: str
) -> str | None:
    if rol not in ("admin", "katilimci", "ziyaretci"):
        return "Geçersiz rol."
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
    return None


@router.post("/users/{user_id}/delete")
async def users_delete(user_id: int, request: Request):
    current_admin_id = request.session.get("user_id")
    if user_id == current_admin_id:
        return RedirectResponse(
            "/admin/users?hata=Kendi+hesab%C4%B1n%C4%B1z%C4%B1+silemezsiniz",
            status_code=303,
        )
    delete_user(user_id)
    return RedirectResponse("/admin/users", status_code=303)


@router.get("/fairs")
async def fairs_page(request: Request, hata: str | None = None):
    return templates.TemplateResponse(
        request, "admin/fairs.html", {"fuarlar": list_fuarlar(), "hata": hata}
    )


@router.post("/fairs")
async def fairs_create(
    request: Request, ad: str = Form(...), tarih: str = Form(...)
):
    if not ad.strip():
        return templates.TemplateResponse(
            request,
            "admin/fairs.html",
            {"fuarlar": list_fuarlar(), "hata": "Fuar adı boş olamaz."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if not tarih_gecerli(tarih.strip()):
        return templates.TemplateResponse(
            request,
            "admin/fairs.html",
            {
                "fuarlar": list_fuarlar(),
                "hata": "Tarih GG/AA/YYYY formatında ve 2024 veya sonrası olmalıdır.",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    create_fuar(ad.strip(), tarih.strip())
    return RedirectResponse("/admin/fairs", status_code=303)


@router.get("/events")
async def events_page(request: Request):
    bekleyen = list_etkinlikler(status="bekliyor")
    onayli = list_etkinlikler(status="onayli")
    return templates.TemplateResponse(
        request,
        "admin/events_approval.html",
        {"bekleyen": bekleyen, "onayli": onayli},
    )


@router.post("/events/{etkinlik_id}/approve")
async def events_approve(etkinlik_id: int):
    approve_etkinlik(etkinlik_id)
    return RedirectResponse("/admin/events", status_code=303)


@router.get("/announcements")
async def announcements_page(request: Request, hata: str | None = None, mesaj: str | None = None):
    slots = []
    for i in range(1, ANNOUNCEMENT_SLOTS + 1):
        p = ANNOUNCEMENTS_DIR / f"DuyuruFoto{i}.png"
        slots.append({"index": i, "exists": p.exists()})
    return templates.TemplateResponse(
        request,
        "admin/announcements.html",
        {"slots": slots, "hata": hata, "mesaj": mesaj},
    )


@router.post("/announcements/{slot}")
async def announcements_upload(slot: int, dosya: UploadFile = File(...)):
    if slot < 1 or slot > ANNOUNCEMENT_SLOTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Geçersiz slot."
        )
    raw = await dosya.read()
    try:
        img = Image.open(BytesIO(raw))
        img.verify()
        img = Image.open(BytesIO(raw))
    except UnidentifiedImageError:
        return RedirectResponse(
            "/admin/announcements?hata=Ge%C3%A7ersiz+g%C3%B6rsel+dosyas%C4%B1",
            status_code=303,
        )
    if img.format != "PNG":
        return RedirectResponse(
            "/admin/announcements?hata=Dosya+PNG+olmal%C4%B1",
            status_code=303,
        )
    if img.size != ANNOUNCEMENT_SIZE:
        return RedirectResponse(
            "/admin/announcements?hata=G%C3%B6rsel+400x400+olmal%C4%B1",
            status_code=303,
        )
    out = ANNOUNCEMENTS_DIR / f"DuyuruFoto{slot}.png"
    out.write_bytes(raw)
    return RedirectResponse("/admin/announcements?mesaj=Y%C3%BCklendi", status_code=303)


@router.get("/qr")
async def admin_qr(request: Request, user=Depends(require_admin)):
    return templates.TemplateResponse(
        request, "admin/qr.html", {"token": user["qr_token"]}
    )
