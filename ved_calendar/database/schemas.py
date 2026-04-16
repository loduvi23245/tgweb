from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from database.models import EventStatus, EventFormat, EventType


class EventBase(BaseModel):
    """Базовая схема мероприятия"""
    title: str = Field(..., min_length=1, max_length=500, description="Название мероприятия")
    description: Optional[str] = Field(None, description="Описание мероприятия")
    
    start_date: datetime = Field(..., description="Дата начала")
    end_date: datetime = Field(..., description="Дата окончания")
    start_time: Optional[str] = Field(None, max_length=20, description="Время начала")
    end_time: Optional[str] = Field(None, max_length=20, description="Время окончания")
    
    format: EventFormat = Field(default=EventFormat.OFFLINE, description="Формат мероприятия")
    event_type: EventType = Field(default=EventType.OTHER, description="Тип мероприятия")
    
    city: Optional[str] = Field(None, max_length=200, description="Город")
    country: Optional[str] = Field(None, max_length=200, description="Страна")
    venue: Optional[str] = Field(None, max_length=500, description="Место проведения")
    
    registration_url: Optional[str] = Field(None, max_length=1000, description="Ссылка на регистрацию")
    source_url: Optional[str] = Field(None, max_length=1000, description="Ссылка на источник")
    source_name: Optional[str] = Field(None, max_length=200, description="Название источника")
    
    contact_person: Optional[str] = Field(None, max_length=200, description="Контактное лицо")
    contact_phone: Optional[str] = Field(None, max_length=50, description="Телефон")
    contact_email: Optional[str] = Field(None, max_length=255, description="Email")
    organizer: Optional[str] = Field(None, max_length=300, description="Организатор")
    
    @field_validator('end_date')
    @classmethod
    def check_dates(cls, v, info):
        """Проверка что дата окончания не раньше даты начала"""
        # Эта проверка будет выполнена после валидации всех полей
        return v


class EventCreate(EventBase):
    """Схема для создания мероприятия"""
    status: EventStatus = Field(default=EventStatus.PENDING, description="Статус мероприятия")
    created_by: Optional[int] = None
    submitted_by: Optional[int] = None


class EventUpdate(BaseModel):
    """Схема для обновления мероприятия"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    format: Optional[EventFormat] = None
    event_type: Optional[EventType] = None
    city: Optional[str] = None
    country: Optional[str] = None
    venue: Optional[str] = None
    registration_url: Optional[str] = None
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    organizer: Optional[str] = None
    status: Optional[EventStatus] = None
    is_published: Optional[bool] = None
    moderator_comment: Optional[str] = None
    rejection_reason: Optional[str] = None


class EventResponse(EventBase):
    """Схема ответа с мероприятием"""
    id: int
    status: EventStatus
    is_published: bool
    moderator_comment: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_by: Optional[int] = None
    submitted_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    """Список мероприятий с пагинацией"""
    items: List[EventResponse]
    total: int
    page: int
    per_page: int
    pages: int


class UserCreate(BaseModel):
    """Схема создания пользователя"""
    username: str = Field(..., min_length=3, max_length=100)
    email: Optional[str] = None
    password: str = Field(..., min_length=6)
    telegram_id: Optional[int] = None
    is_admin: bool = False


class UserResponse(BaseModel):
    """Схема ответа с пользователем"""
    id: int
    username: str
    email: Optional[str] = None
    telegram_id: Optional[int] = None
    is_admin: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Схема токена доступа"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Данные токена"""
    username: Optional[str] = None
    user_id: Optional[int] = None


class AdminLogResponse(BaseModel):
    """Схема лога действий администратора"""
    id: int
    admin_id: Optional[int]
    action: str
    entity_type: Optional[str]
    entity_id: Optional[int]
    details: Optional[str]
    ip_address: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class FilterParams(BaseModel):
    """Параметры фильтрации мероприятий"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    format: Optional[EventFormat] = None
    event_type: Optional[EventType] = None
    city: Optional[str] = None
    country: Optional[str] = None
    status: Optional[EventStatus] = None
    search: Optional[str] = None
    page: int = 1
    per_page: int = 20
