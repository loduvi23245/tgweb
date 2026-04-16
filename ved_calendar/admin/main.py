from fastapi import FastAPI, Request, Depends, HTTPException, status, Form, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from pydantic import BaseModel
from config import settings
from database.models import Base, User, Event, EventStatus, AdminLog
from database.crud import EventCRUD, UserCRUD, AdminLogCRUD
import os

# Создание приложения
app = FastAPI(
    title="Админ-панель ВЭД-календарь",
    description="Панель администратора для управления мероприятиями",
    version="1.0.0"
)

# Настройка шаблонов
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

# Настройка статических файлов
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Безопасность
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admin/token")

# База данных
engine = create_async_engine(settings.database_async_url, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    """Зависимость для получения сессии БД"""
    async with AsyncSessionLocal() as session:
        yield session


def verify_password(plain_password, hashed_password):
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db: AsyncSession):
    """Аутентификация пользователя"""
    # Это синхронная функция, нужно будет сделать асинхронную версию
    pass


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Создание токена доступа"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/admin/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Страница входа"""
    return templates.TemplateResponse("admin_login.html", {"request": request})


@app.post("/admin/token")
async def login_for_access_token(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Получение токена доступа"""
    user = await UserCRUD.get_user_by_username(db, username)
    
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_admin or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь не активен или не имеет прав администратора"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    # Логирование входа
    await AdminLogCRUD.create_log(
        db=db,
        admin_id=user.id,
        action="login",
        details=f"Вход в систему"
    )
    
    response = RedirectResponse(url="/admin/dashboard", status_code=302)
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=1800)
    return response


@app.get("/admin/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    """Панель управления"""
    # Получение статистики
    pending_count = len(await EventCRUD.get_pending_events(db))
    
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "pending_count": pending_count
    })


@app.get("/admin/events", response_class=HTMLResponse)
async def events_list(request: Request, db: AsyncSession = Depends(get_db)):
    """Список всех мероприятий"""
    events, total = await EventCRUD.get_events(db, page=1, per_page=50)
    
    return templates.TemplateResponse("admin_events.html", {
        "request": request,
        "events": events,
        "total": total
    })


@app.get("/admin/pending", response_class=HTMLResponse)
async def pending_events(request: Request, db: AsyncSession = Depends(get_db)):
    """Мероприятия на модерации"""
    events = await EventCRUD.get_pending_events(db)
    
    return templates.TemplateResponse("admin_pending.html", {
        "request": request,
        "events": events
    })


@app.get("/admin/event/{event_id}", response_class=HTMLResponse)
async def event_detail(request: Request, event_id: int, db: AsyncSession = Depends(get_db)):
    """Детали мероприятия"""
    event = await EventCRUD.get_event(db, event_id)
    
    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
    
    return templates.TemplateResponse("admin_event_detail.html", {
        "request": request,
        "event": event
    })


@app.post("/admin/event/{event_id}/approve")
async def approve_event(
    request: Request,
    event_id: int,
    moderator_comment: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Одобрить мероприятие"""
    event = await EventCRUD.get_event(db, event_id)
    
    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
    
    await EventCRUD.approve_event(db, event, moderator_comment)
    
    # Логирование
    # TODO: Получить ID администратора из токена
    await AdminLogCRUD.create_log(
        db=db,
        admin_id=1,
        action="approve_event",
        entity_type="event",
        entity_id=event_id,
        details=f"Одобрено: {event.title}"
    )
    
    return RedirectResponse(url="/admin/pending", status_code=302)


@app.post("/admin/event/{event_id}/reject")
async def reject_event(
    request: Request,
    event_id: int,
    rejection_reason: str = Form(...),
    moderator_comment: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Отклонить мероприятие"""
    event = await EventCRUD.get_event(db, event_id)
    
    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
    
    await EventCRUD.reject_event(db, event, rejection_reason, moderator_comment)
    
    # Логирование
    await AdminLogCRUD.create_log(
        db=db,
        admin_id=1,
        action="reject_event",
        entity_type="event",
        entity_id=event_id,
        details=f"Отклонено: {event.title}. Причина: {rejection_reason}"
    )
    
    return RedirectResponse(url="/admin/pending", status_code=302)


@app.get("/admin/logs", response_class=HTMLResponse)
async def logs_list(request: Request, db: AsyncSession = Depends(get_db)):
    """Лог действий администратора"""
    logs, total = await AdminLogCRUD.get_logs(db, page=1, per_page=100)
    
    return templates.TemplateResponse("admin_logs.html", {
        "request": request,
        "logs": logs,
        "total": total
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "admin.main:app",
        host=settings.ADMIN_HOST,
        port=settings.ADMIN_PORT,
        reload=settings.DEBUG
    )
