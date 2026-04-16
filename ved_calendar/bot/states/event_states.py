from aiogram.fsm.state import StatesGroup, State


class EventSubmission(StatesGroup):
    """Состояния для подачи мероприятия пользователем"""
    title = State()  # Название
    start_date = State()  # Дата начала
    end_date = State()  # Дата окончания
    start_time = State()  # Время начала
    end_time = State()  # Время окончания
    format = State()  # Формат (онлайн/офлайн/смешанный)
    event_type = State()  # Тип мероприятия
    city = State()  # Город
    country = State()  # Страна
    venue = State()  # Место проведения
    description = State()  # Описание
    registration_url = State()  # Ссылка на регистрацию
    source_url = State()  # Ссылка на источник
    source_name = State()  # Название источника
    contact_person = State()  # Контактное лицо
    contact_phone = State()  # Телефон
    contact_email = State()  # Email
    organizer = State()  # Организатор
    confirm = State()  # Подтверждение


class EventEdit(StatesGroup):
    """Состояния для редактирования мероприятия администратором"""
    field_select = State()  # Выбор поля для редактирования
    new_value = State()  # Новое значение
    confirm = State()  # Подтверждение


class FilterState(StatesGroup):
    """Состояния для фильтров"""
    city = State()  # Фильтр по городу
    format = State()  # Фильтр по формату
    type = State()  # Фильтр по типу
    date_start = State()  # Дата начала периода
    date_end = State()  # Дата конца периода
    search = State()  # Поиск по названию
