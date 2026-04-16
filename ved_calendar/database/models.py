from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from config import settings


Base = declarative_base()


class EventStatus(str, PyEnum):
    """Статусы мероприятия"""
    DRAFT = "draft"  # Черновик
    PENDING = "pending"  # На модерации
    PUBLISHED = "published"  # Опубликовано
    REJECTED = "rejected"  # Отклонено
    ARCHIVED = "archived"  # Архив


class EventFormat(str, PyEnum):
    """Формат мероприятия"""
    ONLINE = "online"  # Онлайн
    OFFLINE = "offline"  # Офлайн
    HYBRID = "hybrid"  # Смешанный


class EventType(str, PyEnum):
    """Тип мероприятия"""
    EXHIBITION = "exhibition"  # Выставка
    FORUM = "forum"  # Форум
    WEBINAR = "webinar"  # Вебинар
    SEMINAR = "seminar"  # Семинар
    CONFERENCE = "conference"  # Конференция
    B2B = "b2b"  # B2B встреча
    B2G = "b2g"  # B2G встреча
    OTHER = "other"  # Другое


class User(Base):
    """Пользователь (администратор)"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=True)  # Telegram ID пользователя
    username = Column(String(100), unique=True, nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    events_created = relationship("Event", back_populates="creator", foreign_keys="Event.created_by")
    events_submitted = relationship("Event", back_populates="submitter", foreign_keys="Event.submitted_by")


class Event(Base):
    """Мероприятие"""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Основная информация
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # Даты и время
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    start_time = Column(String(20), nullable=True)  # Время начала (строка для гибкости)
    end_time = Column(String(20), nullable=True)  # Время окончания
    
    # Формат и тип
    format = Column(Enum(EventFormat), default=EventFormat.OFFLINE)
    event_type = Column(Enum(EventType), default=EventType.OTHER)
    
    # Местоположение
    city = Column(String(200), nullable=True)
    country = Column(String(200), nullable=True)
    venue = Column(String(500), nullable=True)  # Место проведения
    
    # Ссылки
    registration_url = Column(String(1000), nullable=True)
    source_url = Column(String(1000), nullable=True)
    source_name = Column(String(200), nullable=True)
    
    # Контакты
    contact_person = Column(String(200), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    contact_email = Column(String(255), nullable=True)
    organizer = Column(String(300), nullable=True)
    
    # Статус и модерация
    status = Column(Enum(EventStatus), default=EventStatus.PENDING)
    is_published = Column(Boolean, default=False)
    
    # Модерация
    moderator_comment = Column(Text, nullable=True)  # Комментарий администратора
    rejection_reason = Column(Text, nullable=True)  # Причина отклонения
    
    # Пользователи
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    archived_at = Column(DateTime, nullable=True)
    
    # Связи
    creator = relationship("User", back_populates="events_created", foreign_keys=[created_by])
    submitter = relationship("User", back_populates="events_submitted", foreign_keys=[submitted_by])
    
    def __repr__(self):
        return f"<Event(id={self.id}, title='{self.title}', status='{self.status}')>"


class AdminLog(Base):
    """Лог действий администратора"""
    __tablename__ = "admin_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)  # Действие
    entity_type = Column(String(50), nullable=True)  # Тип сущности (event, user)
    entity_id = Column(Integer, nullable=True)  # ID сущности
    details = Column(Text, nullable=True)  # Детали действия
    ip_address = Column(String(45), nullable=True)  # IP адрес
    created_at = Column(DateTime, default=datetime.utcnow)
    
    admin = relationship("User")


async def init_db():
    """Инициализация базы данных"""
    engine = create_async_engine(settings.database_async_url, echo=settings.DEBUG)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Создание администратора по умолчанию
    async with async_sessionmaker(engine, class_=AsyncSession)() as session:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Проверка наличия администратора
        result = await session.execute(
            Base.select(User).where(User.username == settings.ADMIN_USERNAME)
        )
        admin = result.scalar_one_or_none()
        
        if not admin:
            admin = User(
                username=settings.ADMIN_USERNAME,
                password_hash=pwd_context.hash(settings.ADMIN_PASSWORD),
                is_admin=True,
                is_active=True
            )
            session.add(admin)
            await session.commit()
            print(f"Администратор '{settings.ADMIN_USERNAME}' создан успешно!")
        else:
            print("Администратор уже существует.")
    
    await engine.dispose()
    print("База данных инициализирована успешно!")


# Для синхронных операций (например, в скриптах)
def get_sync_engine():
    """Получить синхронный движок для миграций"""
    from sqlalchemy import create_engine
    url = settings.DATABASE_URL.replace("sqlite+aiosqlite", "sqlite").replace("postgresql+psycopg2", "postgresql").replace("postgresql+asyncpg", "postgresql")
    return create_engine(url, echo=settings.DEBUG)
