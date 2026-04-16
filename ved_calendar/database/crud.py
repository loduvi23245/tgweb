from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from database.models import Event, User, AdminLog, EventStatus, EventFormat, EventType
from database.schemas import EventCreate, EventUpdate, FilterParams
from config import settings


class EventCRUD:
    """CRUD операции для мероприятий"""
    
    @staticmethod
    async def get_event(db: AsyncSession, event_id: int) -> Optional[Event]:
        """Получить мероприятие по ID"""
        result = await db.execute(
            select(Event).where(Event.id == event_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_events(
        db: AsyncSession,
        filters: Optional[FilterParams] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Event], int]:
        """Получить список мероприятий с фильтрацией и пагинацией"""
        query = select(Event)
        
        # Применение фильтров
        if filters:
            conditions = []
            
            if filters.start_date:
                conditions.append(Event.end_date >= filters.start_date)
            
            if filters.end_date:
                conditions.append(Event.start_date <= filters.end_date)
            
            if filters.format:
                conditions.append(Event.format == filters.format)
            
            if filters.event_type:
                conditions.append(Event.event_type == filters.event_type)
            
            if filters.city:
                conditions.append(Event.city.ilike(f"%{filters.city}%"))
            
            if filters.country:
                conditions.append(Event.country.ilike(f"%{filters.country}%"))
            
            if filters.status:
                conditions.append(Event.status == filters.status)
            
            if filters.search:
                conditions.append(
                    or_(
                        Event.title.ilike(f"%{filters.search}%"),
                        Event.description.ilike(f"%{filters.search}%"),
                        Event.organizer.ilike(f"%{filters.search}%")
                    )
                )
            
            if conditions:
                query = query.where(and_(*conditions))
        
        # Получение общего количества
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Пагинация
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        
        # Выполнение запроса
        result = await db.execute(query)
        events = result.scalars().all()
        
        return events, total
    
    @staticmethod
    async def get_published_events(
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Event], int]:
        """Получить опубликованные мероприятия"""
        filters = FilterParams(
            start_date=start_date,
            end_date=end_date,
            status=EventStatus.PUBLISHED,
            page=page,
            per_page=per_page
        )
        return await EventCRUD.get_events(db, filters, page, per_page)
    
    @staticmethod
    async def get_pending_events(db: AsyncSession) -> List[Event]:
        """Получить мероприятия на модерации"""
        result = await db.execute(
            select(Event)
            .where(Event.status == EventStatus.PENDING)
            .order_by(Event.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def create_event(db: AsyncSession, event_data: EventCreate) -> Event:
        """Создать новое мероприятие"""
        event = Event(**event_data.model_dump())
        
        if event_data.status == EventStatus.PUBLISHED:
            event.is_published = True
            event.published_at = datetime.utcnow()
        
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return event
    
    @staticmethod
    async def update_event(db: AsyncSession, event: Event, update_data: EventUpdate) -> Event:
        """Обновить мероприятие"""
        update_dict = update_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            if value is not None:
                setattr(event, field, value)
        
        # Обновление статуса публикации
        if hasattr(update_data, 'status') and update_data.status:
            if update_data.status == EventStatus.PUBLISHED:
                event.is_published = True
                event.published_at = datetime.utcnow()
            elif update_data.status in [EventStatus.DRAFT, EventStatus.REJECTED, EventStatus.ARCHIVED]:
                event.is_published = False
                if update_data.status == EventStatus.ARCHIVED:
                    event.archived_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(event)
        return event
    
    @staticmethod
    async def delete_event(db: AsyncSession, event: Event) -> bool:
        """Удалить мероприятие"""
        await db.delete(event)
        await db.commit()
        return True
    
    @staticmethod
    async def approve_event(db: AsyncSession, event: Event, moderator_comment: Optional[str] = None) -> Event:
        """Одобрить мероприятие"""
        event.status = EventStatus.PUBLISHED
        event.is_published = True
        event.published_at = datetime.utcnow()
        if moderator_comment:
            event.moderator_comment = moderator_comment
        
        await db.commit()
        await db.refresh(event)
        return event
    
    @staticmethod
    async def reject_event(db: AsyncSession, event: Event, reason: str, moderator_comment: Optional[str] = None) -> Event:
        """Отклонить мероприятие"""
        event.status = EventStatus.REJECTED
        event.rejection_reason = reason
        if moderator_comment:
            event.moderator_comment = moderator_comment
        
        await db.commit()
        await db.refresh(event)
        return event
    
    @staticmethod
    async def archive_event(db: AsyncSession, event: Event) -> Event:
        """Архивировать мероприятие"""
        event.status = EventStatus.ARCHIVED
        event.archived_at = datetime.utcnow()
        event.is_published = False
        
        await db.commit()
        await db.refresh(event)
        return event
    
    @staticmethod
    async def get_events_by_date(db: AsyncSession, date: datetime) -> List[Event]:
        """Получить мероприятия за конкретную дату"""
        result = await db.execute(
            select(Event)
            .where(
                and_(
                    Event.status == EventStatus.PUBLISHED,
                    Event.start_date <= date,
                    Event.end_date >= date
                )
            )
            .order_by(Event.start_date)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_archived_events(
        db: AsyncSession,
        year: Optional[int] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Event], int]:
        """Получить архивные мероприятия"""
        query = select(Event).where(Event.status == EventStatus.ARCHIVED)
        
        if year:
            query = query.where(func.extract('year', Event.end_date) == year)
        
        query = query.order_by(Event.end_date.desc())
        
        # Общее количество
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Пагинация
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        
        result = await db.execute(query)
        events = result.scalars().all()
        
        return events, total


class UserCRUD:
    """CRUD операции для пользователей"""
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Получить пользователя по имени"""
        result = await db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int) -> Optional[User]:
        """Получить пользователя по Telegram ID"""
        result = await db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user(
        db: AsyncSession,
        username: str,
        password_hash: str,
        email: Optional[str] = None,
        telegram_id: Optional[int] = None,
        is_admin: bool = False
    ) -> User:
        """Создать пользователя"""
        user = User(
            username=username,
            password_hash=password_hash,
            email=email,
            telegram_id=telegram_id,
            is_admin=is_admin,
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def update_user(db: AsyncSession, user: User, **kwargs) -> User:
        """Обновить пользователя"""
        for field, value in kwargs.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        return user


class AdminLogCRUD:
    """CRUD операции для логов администратора"""
    
    @staticmethod
    async def create_log(
        db: AsyncSession,
        admin_id: int,
        action: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        details: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> AdminLog:
        """Создать запись лога"""
        log = AdminLog(
            admin_id=admin_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log
    
    @staticmethod
    async def get_logs(
        db: AsyncSession,
        admin_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 50
    ) -> Tuple[List[AdminLog], int]:
        """Получить логи"""
        query = select(AdminLog)
        
        if admin_id:
            query = query.where(AdminLog.admin_id == admin_id)
        
        query = query.order_by(AdminLog.created_at.desc())
        
        # Общее количество
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Пагинация
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        
        result = await db.execute(query)
        logs = result.scalars().all()
        
        return logs, total
