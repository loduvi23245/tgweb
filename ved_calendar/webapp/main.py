from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from config import settings
from database.models import Base
import os

# Создание приложения
app = FastAPI(
    title="ВЭД-календарь",
    description="Веб мини-апп для просмотра мероприятий",
    version="1.0.0"
)

# Настройка шаблонов
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

# Настройка статических файлов
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# База данных
engine = create_async_engine(settings.database_async_url, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    """Зависимость для получения сессии БД"""
    async with AsyncSessionLocal() as session:
        yield session


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Главная страница веб-аппа"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/events", response_class=HTMLResponse)
async def events_page(request: Request):
    """Страница списка событий"""
    return templates.TemplateResponse("events.html", {"request": request})


@app.get("/event/{event_id}", response_class=HTMLResponse)
async def event_detail(request: Request, event_id: int):
    """Страница детали события"""
    return templates.TemplateResponse("event_detail.html", {
        "request": request,
        "event_id": event_id
    })


@app.get("/calendar", response_class=HTMLResponse)
async def calendar_page(request: Request):
    """Страница календаря"""
    return templates.TemplateResponse("calendar.html", {"request": request})


@app.get("/submit", response_class=HTMLResponse)
async def submit_page(request: Request):
    """Страница подачи мероприятия"""
    return templates.TemplateResponse("submit.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "webapp.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))

        reload=settings.DEBUG
    )
