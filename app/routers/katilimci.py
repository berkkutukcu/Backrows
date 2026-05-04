from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..config import TEMPLATES_DIR
from ..dependencies import require_katilimci
from ..repository import (
    create_etkinlik_request,
    get_fuar,
    join_fuar,
    list_fuarlar,
    list_user_fuarlar,
    list_etkinlikler,
)
from ..validators import saat_gecerli

router = APIRouter(prefix="/katilimci", dependencies=[Depends(require_katilimci)])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("")
async def dashboard(request: Request, user=Depends(require_katilimci)):
    return templates.TemplateResponse(
        request, "katilimci/dashboard.html", {"user": user}
    )


@router.get("/fairs")
async def fairs_page(
    request: Request,
    user=Depends(require_katilimci),
    mesaj: str | None = None,
    hata: str | None = None,
):
    tum = list_fuarlar()
    benim = list_user_fuarlar(user["id"])
    benim_ids = {f["id"] for f in benim}
    return templates.TemplateResponse(
        request,
        "katilimci/fairs.html",
        {
            "tum": tum,
            "benim": benim,
            "benim_ids": benim_ids,
            "mesaj": mesaj,
            "hata": hata,
        },
    )


@router.post("/fairs/{fuar_id}/join")
async def fair_join(fuar_id: int, user=Depends(require_katilimci)):
    if not get_fuar(fuar_id):
        return RedirectResponse(
            "/katilimci/fairs?hata=Fuar+bulunamad%C4%B1", status_code=303
        )
    ok = join_fuar(user["id"], fuar_id)
    if not ok:
        return RedirectResponse(
            "/katilimci/fairs?hata=Bu+fuara+zaten+kat%C4%B1ld%C4%B1n%C4%B1z",
            status_code=303,
        )
    return RedirectResponse("/katilimci/fairs?mesaj=Kat%C4%B1ld%C4%B1n%C4%B1z", status_code=303)


@router.get("/event-request")
async def event_request_page(
    request: Request,
    user=Depends(require_katilimci),
    mesaj: str | None = None,
    hata: str | None = None,
):
    benim = list_user_fuarlar(user["id"])
    saatler = [f"{h:02d}.00" for h in range(9, 23)]
    istekler = [
        e for e in list_etkinlikler() if e["konusmaci"] == f"{user['ad']} {user['soyad']}"
    ]
    return templates.TemplateResponse(
        request,
        "katilimci/event_request.html",
        {
            "benim": benim,
            "saatler": saatler,
            "istekler": istekler,
            "mesaj": mesaj,
            "hata": hata,
        },
    )


@router.post("/event-request")
async def event_request_submit(
    request: Request,
    fuar_id: int = Form(...),
    saat: str = Form(...),
    user=Depends(require_katilimci),
):
    benim_ids = {f["id"] for f in list_user_fuarlar(user["id"])}
    if fuar_id not in benim_ids:
        return RedirectResponse(
            "/katilimci/event-request?hata=%C3%96nce+bu+fuara+kat%C4%B1lmal%C4%B1s%C4%B1n%C4%B1z",
            status_code=303,
        )
    if not saat_gecerli(saat.strip()):
        return RedirectResponse(
            "/katilimci/event-request?hata=Saat+09.00-22.00+aras%C4%B1nda+HH.MM+format%C4%B1nda+olmal%C4%B1",
            status_code=303,
        )
    konusmaci = f"{user['ad']} {user['soyad']}"
    etkinlik_id = create_etkinlik_request(
        fuar_id=fuar_id,
        saat=saat.strip(),
        konusmaci=konusmaci,
        status="bekliyor",
    )
    if etkinlik_id is None:
        return RedirectResponse(
            "/katilimci/event-request?hata=Bu+saat+dolu",
            status_code=303,
        )
    return RedirectResponse(
        "/katilimci/event-request?mesaj=Talep+olu%C5%9Fturuldu%2C+onay+bekleniyor",
        status_code=303,
    )


@router.get("/qr")
async def katilimci_qr(request: Request, user=Depends(require_katilimci)):
    return templates.TemplateResponse(
        request, "katilimci/qr.html", {"token": user["qr_token"]}
    )
