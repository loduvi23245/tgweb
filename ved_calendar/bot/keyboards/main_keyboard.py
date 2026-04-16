from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Главное меню бота"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📅 Актуальные события", callback_data="events_current")
    builder.button(text="🗓 Календарь", callback_data="calendar")
    builder.button(text="🔍 Поиск и фильтры", callback_data="search_filters")
    builder.button(text="📁 Архив", callback_data="archive")
    builder.button(text="➕ Предложить мероприятие", callback_data="submit_event")
    builder.button(text="❓ Помощь", callback_data="help")
    
    # Настройка сетки кнопок (2 кнопки в ряд)
    builder.adjust(1, 1, 1, 1, 1, 1)
    
    return builder.as_markup()


def get_events_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для просмотра событий"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📋 Список", callback_data="events_list")
    builder.button(text="📆 Календарь", callback_data="calendar_view")
    builder.button(text="🔙 Назад в меню", callback_data="menu_back")
    
    builder.adjust(2, 1)
    return builder.as_markup()


def get_event_detail_keyboard(event_id: int, webapp_url: str = None) -> InlineKeyboardMarkup:
    """Клавиатура для карточки события"""
    builder = InlineKeyboardBuilder()
    
    if webapp_url:
        builder.button(text="🌐 Открыть в веб-приложении", url=webapp_url)
    
    builder.button(text="📥 Добавить в календарь", callback_data=f"event_ics_{event_id}")
    builder.button(text="🔙 Назад к списку", callback_data="events_list_back")
    
    builder.adjust(1, 1)
    return builder.as_markup()


def get_calendar_keyboard(year: int, month: int) -> InlineKeyboardMarkup:
    """Клавиатура календаря на месяц"""
    from datetime import datetime
    import calendar
    
    builder = InlineKeyboardBuilder()
    
    # Название месяца и года
    month_name = calendar.month_name[month]
    builder.button(text=f"📅 {month_name} {year}", callback_data="calendar_title")
    
    # Дни недели
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    for day in days:
        builder.button(text=day, callback_data="calendar_day_header")
    
    # Дни месяца
    cal = calendar.monthcalendar(year, month)
    for week in cal:
        for day in week:
            if day == 0:
                builder.button(text=" ", callback_data="calendar_empty")
            else:
                builder.button(text=str(day), callback_data=f"calendar_day_{year}_{month}_{day}")
    
    # Навигация по месяцам
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    builder.button(text="◀️ Пред. месяц", callback_data=f"calendar_{prev_year}_{prev_month}")
    builder.button(text="🔙 Назад", callback_data="menu_back")
    builder.button(text="След. месяц ▶️", callback_data=f"calendar_{next_year}_{next_month}")
    
    builder.adjust(7)  # 7 дней в неделю
    builder.adjust(3, 3, 3)  # Дни
    builder.adjust(3)  # Навигация
    
    return builder.as_markup()


def get_filters_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура фильтров"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📍 По городу", callback_data="filter_city")
    builder.button(text="🌐 По формату", callback_data="filter_format")
    builder.button(text="📊 По типу", callback_data="filter_type")
    builder.button(text="📅 По дате", callback_data="filter_date")
    builder.button(text="🔍 Поиск по названию", callback_data="filter_search")
    builder.button(text="✅ Применить фильтры", callback_data="filters_apply")
    builder.button(text="🗑 Сбросить фильтры", callback_data="filters_reset")
    builder.button(text="🔙 Назад", callback_data="menu_back")
    
    builder.adjust(2, 2, 2, 2)
    return builder.as_markup()


def get_format_filter_keyboard() -> InlineKeyboardMarkup:
    """Фильтр по формату мероприятия"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="🌐 Онлайн", callback_data="filter_format_online")
    builder.button(text="🏢 Офлайн", callback_data="filter_format_offline")
    builder.button(text="🔄 Смешанный", callback_data="filter_format_hybrid")
    builder.button(text="🔙 Назад", callback_data="search_filters")
    
    builder.adjust(1)
    return builder.as_markup()


def get_type_filter_keyboard() -> InlineKeyboardMarkup:
    """Фильтр по типу мероприятия"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="🎪 Выставка", callback_data="filter_type_exhibition")
    builder.button(text="💼 Форум", callback_data="filter_type_forum")
    builder.button(text="💻 Вебинар", callback_data="filter_type_webinar")
    builder.button(text="📚 Семинар", callback_data="filter_type_seminar")
    builder.button(text="🎤 Конференция", callback_data="filter_type_conference")
    builder.button(text="🤝 B2B встреча", callback_data="filter_type_b2b")
    builder.button(text="🏛 B2G встреча", callback_data="filter_type_b2g")
    builder.button(text="📁 Другое", callback_data="filter_type_other")
    builder.button(text="🔙 Назад", callback_data="search_filters")
    
    builder.adjust(1)
    return builder.as_markup()


def get_moderation_keyboard(event_id: int) -> InlineKeyboardMarkup:
    """Клавиатура модерации для администратора"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="✅ Одобрить", callback_data=f"mod_approve_{event_id}")
    builder.button(text="❌ Отклонить", callback_data=f"mod_reject_{event_id}")
    builder.button(text="✏️ Редактировать", callback_data=f"mod_edit_{event_id}")
    builder.button(text="📝 Комментарий", callback_data=f"mod_comment_{event_id}")
    builder.button(text="🔙 Назад", callback_data="admin_pending")
    
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def get_pagination_keyboard(page: int, total_pages: int, callback_prefix: str = "page") -> InlineKeyboardMarkup:
    """Клавиатура пагинации"""
    builder = InlineKeyboardBuilder()
    
    if total_pages > 1:
        if page > 1:
            builder.button(text="◀️ Назад", callback_data=f"{callback_prefix}_{page-1}")
        
        builder.button(text=f"📄 Стр. {page}/{total_pages}", callback_data="page_info")
        
        if page < total_pages:
            builder.button(text="Вперед ▶️", callback_data=f"{callback_prefix}_{page+1}")
        
        builder.adjust(3)
    
    return builder.as_markup()


def get_archive_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура архива"""
    from datetime import datetime
    
    builder = InlineKeyboardBuilder()
    current_year = datetime.now().year
    
    # Годы для фильтрации (последние 5 лет)
    for year in range(current_year, current_year - 5, -1):
        builder.button(text=f"📁 {year}", callback_data=f"archive_year_{year}")
    
    builder.button(text="🔙 Назад", callback_data="menu_back")
    builder.adjust(1)
    
    return builder.as_markup()
