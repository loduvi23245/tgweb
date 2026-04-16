from datetime import datetime
from icalendar import Calendar, Event as IcalEvent
from io import BytesIO


def create_ics_file(event) -> bytes:
    """Создание ICS файла для мероприятия"""
    cal = Calendar()
    
    # Основная информация календаря
    cal.add('prodid', '-//ВЭД-календарь//VED Calendar//RU')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    
    # Создание события
    ical_event = IcalEvent()
    
    # Обязательные поля
    ical_event.add('summary', event.title)
    ical_event.add('dtstart', event.start_date)
    ical_event.add('dtend', event.end_date)
    ical_event.add('dtstamp', datetime.utcnow())
    
    # Уникальный идентификатор
    ical_event.add('uid', f"event-{event.id}@ved-calendar.ru")
    
    # Описание
    if event.description:
        ical_event.add('description', event.description)
    
    # Местоположение
    location_parts = []
    if event.venue:
        location_parts.append(event.venue)
    if event.city:
        location_parts.append(event.city)
    if event.country:
        location_parts.append(event.country)
    
    if location_parts:
        ical_event.add('location', ', '.join(location_parts))
    
    # Организатор
    if event.organizer:
        ical_event.add('organizer', event.organizer)
    
    # URL регистрации
    if event.registration_url:
        ical_event.add('url', event.registration_url)
    
    # Категория (тип мероприятия)
    if event.event_type:
        ical_event.add('categories', [event.event_type.value])
    
    # Статус
    ical_event.add('status', 'CONFIRMED' if event.is_published else 'TENTATIVE')
    
    # Добавление события в календарь
    cal.add_component(ical_event)
    
    # Сериализация в байты
    return cal.to_ical()


def generate_ics_filename(event) -> str:
    """Генерация имени файла для ICS"""
    # Очистка названия от специальных символов
    safe_title = "".join(c for c in event.title if c.isalnum() or c in ' -_').strip()
    safe_title = safe_title.replace(' ', '_')[:50]
    
    # Форматирование даты
    date_str = event.start_date.strftime('%Y%m%d')
    
    return f"{date_str}_{safe_title}.ics"
