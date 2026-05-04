from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..config import TEMPLATES_DIR
from ..dependencies import require_ziyaretci
from ..repository import (
    get_fuar,
    join_fuar,
    list_etkinlikler,
    list_fuarlar,
    list_user_fuarlar,
)

router = APIRouter(prefix="/ziyaretci", dependencies=[Depends(require_ziyaretci)])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("")
async def dashboard(request: Request, user=Depends(require_ziyaretci)):
    return templates.TemplateResponse(
        request, "ziyaretci/dashboard.html", {"user": user}
    )


@router.get("/fairs")
async def fairs_page(
    request: Request,
    user=Depends(require_ziyaretci),
    mesaj: str | None = None,
    hata: str | None = None,
):
    tum = list_fuarlar()
    benim = list_user_fuarlar(user["id"])
    benim_ids = {f["id"] for f in benim}
    return templates.TemplateResponse(
        request,
        "ziyaretci/fairs.html",
        {
            "tum": tum,
            "benim": benim,
            "benim_ids": benim_ids,
            "mesaj": mesaj,
            "hata": hata,
        },
    )


@router.post("/fairs/{fuar_id}/join")
async def fair_join(fuar_id: int, user=Depends(require_ziyaretci)):
    if not get_fuar(fuar_id):
        return RedirectResponse(
            "/ziyaretci/fairs?hata=Fuar+bulunamad%C4%B1", status_code=303
        )
    ok = join_fuar(user["id"], fuar_id)
    if not ok:
        return RedirectResponse(
            "/ziyaretci/fairs?hata=Bu+fuara+zaten+kat%C4%B1ld%C4%B1n%C4%B1z",
            status_code=303,
        )
    return RedirectResponse(
        "/ziyaretci/fairs?mesaj=Kat%C4%B1ld%C4%B1n%C4%B1z", status_code=303
    )


@router.get("/events")
async def events_page(
    request: Request,
    user=Depends(require_ziyaretci),
    fuar_id: int | None = None,
):
    benim = list_user_fuarlar(user["id"])
    secili_fuar = None
    etkinlikler = []
    if fuar_id is not None:
        secili_fuar = get_fuar(fuar_id)
        if secili_fuar:
            etkinlikler = [
                e
                for e in list_etkinlikler(status="onayli")
                if e["fuar_id"] == fuar_id
            ]
    return templates.TemplateResponse(
        request,
        "ziyaretci/events.html",
        {
            "benim": benim,
            "secili_fuar": secili_fuar,
            "fuar_id": fuar_id,
            "etkinlikler": etkinlikler,
        },
    )


@router.get("/qr")
async def ziyaretci_qr(request: Request, user=Depends(require_ziyaretci)):
    return templates.TemplateResponse(
        request, "ziyaretci/qr.html", {"token": user["qr_token"]}
    )
