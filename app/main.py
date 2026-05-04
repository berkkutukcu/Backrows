from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .config import ANNOUNCEMENTS_DIR, SECRET_KEY, STATIC_DIR
from .db import init_db
from .routers import admin, auth, katilimci
from .seed import seed_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_if_empty()
    yield


app = FastAPI(title="BackRows Web", lifespan=lifespan)  # noqa
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount(
    "/uploads/announcements",
    StaticFiles(directory=str(ANNOUNCEMENTS_DIR)),
    name="announcements",
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(katilimci.router)
