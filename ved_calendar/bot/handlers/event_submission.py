from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime
from database.crud import EventCRUD
from database.schemas import EventCreate
from database.models import EventFormat, EventType
from keyboards.main_keyboard import (
    get_main_keyboard,
    get_format_filter_keyboard,
    get_type_filter_keyboard,
    get_moderation_keyboard
)
from states.event_states import EventSubmission
from config import settings


router = Router()


@router.callback_query(lambda c: c.data == "submit_event")
async def start_submit_event(callback: CallbackQuery, state: FSMContext):
    """Начало процесса подачи мероприятия"""
    await state.clear()
    
    text = (
        "📝 **Подача мероприятия**\n\n"
        "Давайте заполним информацию о вашем мероприятии.\n\n"
        "Отправьте **название мероприятия** первым сообщением:"
    )
    
    await callback.message.edit_text(text=text, parse_mode="Markdown")
    await state.set_state(EventSubmission.title)


@router.message(EventSubmission.title)
async def process_title(message: Message, state: FSMContext):
    """Обработка названия мероприятия"""
    if len(message.text) < 5:
        await message.answer("❌ Название слишком короткое. Минимум 5 символов.\n\nВведите название ещё раз:")
        return
    
    await state.update_data(title=message.text)
    
    await message.answer(
        "✅ Название принято!\n\n"
        "Теперь отправьте **дату начала** в формате ДД.ММ.ГГГГ (например, 15.09.2025):"
    )
    await state.set_state(EventSubmission.start_date)


@router.message(EventSubmission.start_date)
async def process_start_date(message: Message, state: FSMContext):
    """Обработка даты начала"""
    try:
        start_date = datetime.strptime(message.text.strip(), "%d.%m.%Y")
        
        if start_date.date() < datetime.now().date():
            await message.answer("⚠️ Дата начала не может быть в прошлом.\n\nВведите корректную дату:")
            return
        
        await state.update_data(start_date=start_date.isoformat())
        
        await message.answer(
            "✅ Дата начала принята!\n\n"
            "Теперь отправьте **дату окончания** в формате ДД.ММ.ГГГГ:"
        )
        await state.set_state(EventSubmission.end_date)
    except ValueError:
        await message.answer("❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ.\n\nВведите дату ещё раз:")


@router.message(EventSubmission.end_date)
async def process_end_date(message: Message, state: FSMContext):
    """Обработка даты окончания"""
    try:
        end_date = datetime.strptime(message.text.strip(), "%d.%m.%Y")
        data = await state.get_data()
        start_date = datetime.fromisoformat(data["start_date"])
        
        if end_date.date() < start_date.date():
            await message.answer("⚠️ Дата окончания не может быть раньше даты начала.\n\nВведите корректную дату:")
            return
        
        await state.update_data(end_date=end_date.isoformat())
        
        await message.answer(
            "✅ Дата окончания принята!\n\n"
            "Теперь отправьте **время начала** в формате ЧЧ:ММ (например, 10:00):\n"
            "(или напишите «пропустить», если время не указано)"
        )
        await state.set_state(EventSubmission.start_time)


@router.message(EventSubmission.start_time)
async def process_start_time(message: Message, state: FSMContext):
    """Обработка времени начала"""
    if message.text.lower() in ["пропустить", "-"]:
        await state.update_data(start_time=None)
    else:
        try:
            datetime.strptime(message.text.strip(), "%H:%M")
            await state.update_data(start_time=message.text.strip())
        except ValueError:
            await message.answer("❌ Неверный формат времени. Используйте ЧЧ:ММ.\n\nВведите время ещё раз:")
            return
    
    await message.answer(
        "✅ Время начала принято!\n\n"
        "Теперь отправьте **время окончания** в формате ЧЧ:ММ:\n"
        "(или напишите «пропустить», если время не указано)"
    )
    await state.set_state(EventSubmission.end_time)


@router.message(EventSubmission.end_time)
async def process_end_time(message: Message, state: FSMContext):
    """Обработка времени окончания"""
    if message.text.lower() in ["пропустить", "-"]:
        await state.update_data(end_time=None)
    else:
        try:
            datetime.strptime(message.text.strip(), "%H:%M")
            await state.update_data(end_time=message.text.strip())
        except ValueError:
            await message.answer("❌ Неверный формат времени. Используйте ЧЧ:ММ.\n\nВведите время ещё раз:")
            return
    
    await message.answer(
        "✅ Время окончания принято!\n\n"
        "Выберите **формат мероприятия**:",
        reply_markup=get_format_filter_keyboard()
    )
    await state.set_state(EventSubmission.format)


@router.callback_query(EventSubmission.format)
async def process_format(callback: CallbackQuery, state: FSMContext):
    """Обработка формата мероприятия"""
    format_map = {
        "filter_format_online": EventFormat.ONLINE,
        "filter_format_offline": EventFormat.OFFLINE,
        "filter_format_hybrid": EventFormat.HYBRID
    }
    
    selected_format = format_map.get(callback.data)
    if not selected_format:
        return
    
    await state.update_data(format=selected_format.value)
    
    await callback.message.edit_text(
        text=f"✅ Формат: **{selected_format.value}**\n\nВыберите **тип мероприятия**:",
        parse_mode="Markdown",
        reply_markup=get_type_filter_keyboard()
    )
    await state.set_state(EventSubmission.event_type)


@router.callback_query(EventSubmission.event_type)
async def process_event_type(callback: CallbackQuery, state: FSMContext):
    """Обработка типа мероприятия"""
    type_map = {
        "filter_type_exhibition": EventType.EXHIBITION,
        "filter_type_forum": EventType.FORUM,
        "filter_type_webinar": EventType.WEBINAR,
        "filter_type_seminar": EventType.SEMINAR,
        "filter_type_conference": EventType.CONFERENCE,
        "filter_type_b2b": EventType.B2B,
        "filter_type_b2g": EventType.B2G,
        "filter_type_other": EventType.OTHER
    }
    
    selected_type = type_map.get(callback.data)
    if not selected_type:
        return
    
    await state.update_data(event_type=selected_type.value)
    
    await callback.message.edit_text(
        text=f"✅ Тип: **{selected_type.value}**\n\nТеперь отправьте **город** проведения:"
    )
    await state.set_state(EventSubmission.city)


@router.message(EventSubmission.city)
async def process_city(message: Message, state: FSMContext):
    """Обработка города"""
    await state.update_data(city=message.text.strip())
    
    await message.answer(
        "✅ Город принят!\n\n"
        "Теперь отправьте **страну**:"
    )
    await state.set_state(EventSubmission.country)


@router.message(EventSubmission.country)
async def process_country(message: Message, state: FSMContext):
    """Обработка страны"""
    await state.update_data(country=message.text.strip())
    
    await message.answer(
        "✅ Страна принята!\n\n"
        "Отправьте **место проведения** (название площадки, адрес):\n"
        "(или напишите «пропустить» для онлайн-мероприятий)"
    )
    await state.set_state(EventSubmission.venue)


@router.message(EventSubmission.venue)
async def process_venue(message: Message, state: FSMContext):
    """Обработка места проведения"""
    venue = message.text.strip()
    if venue.lower() in ["пропустить", "-"]:
        venue = None
    
    await state.update_data(venue=venue)
    
    await message.answer(
        "✅ Место проведения принято!\n\n"
        "Теперь отправьте **описание мероприятия**:\n"
        "(можно использовать несколько сообщений, закончите словом «готово»)"
    )
    await state.set_state(EventSubmission.description)


@router.message(EventSubmission.description)
async def process_description(message: Message, state: FSMContext):
    """Обработка описания"""
    current_desc = await state.get_value("description")
    
    if message.text.lower() == "готово":
        if not current_desc:
            await message.answer("❌ Описание не может быть пустым.\n\nВведите описание:")
            return
        
        await state.update_data(description=current_desc)
        
        await message.answer(
            "✅ Описание принято!\n\n"
            "Отправьте **ссылку на регистрацию**:\n"
            "(или напишите «пропустить», если ссылки нет)"
        )
        await state.set_state(EventSubmission.registration_url)
    else:
        # Добавляем текст к описанию
        if current_desc:
            new_desc = current_desc + "\n" + message.text
        else:
            new_desc = message.text
        await state.update_data(description=new_desc)
        await message.answer("Продолжайте вводить описание или напишите «готово» для завершения.")


@router.message(EventSubmission.registration_url)
async def process_registration_url(message: Message, state: FSMContext):
    """Обработка ссылки на регистрацию"""
    url = message.text.strip()
    if url.lower() in ["пропустить", "-"]:
        url = None
    
    await state.update_data(registration_url=url)
    
    await message.answer(
        "✅ Ссылка на регистрацию принята!\n\n"
        "Отправьте **ссылку на источник** информации:\n"
        "(или напишите «пропустить»)"
    )
    await state.set_state(EventSubmission.source_url)


@router.message(EventSubmission.source_url)
async def process_source_url(message: Message, state: FSMContext):
    """Обработка ссылки на источник"""
    url = message.text.strip()
    if url.lower() in ["пропустить", "-"]:
        url = None
    
    await state.update_data(source_url=url)
    
    await message.answer(
        "✅ Ссылка на источник принята!\n\n"
        "Отправьте **название источника**:\n"
        "(или напишите «пропустить»)"
    )
    await state.set_state(EventSubmission.source_name)


@router.message(EventSubmission.source_name)
async def process_source_name(message: Message, state: FSMContext):
    """Обработка названия источника"""
    name = message.text.strip()
    if name.lower() in ["пропустить", "-"]:
        name = None
    
    await state.update_data(source_name=name)
    
    await message.answer(
        "✅ Источник принят!\n\n"
        "Отправьте **контактное лицо**:\n"
        "(или напишите «пропустить»)"
    )
    await state.set_state(EventSubmission.contact_person)


@router.message(EventSubmission.contact_person)
async def process_contact_person(message: Message, state: FSMContext):
    """Обработка контактного лица"""
    contact = message.text.strip()
    if contact.lower() in ["пропустить", "-"]:
        contact = None
    
    await state.update_data(contact_person=contact)
    
    await message.answer(
        "✅ Контактное лицо принято!\n\n"
        "Отправьте **телефон для связи**:\n"
        "(или напишите «пропустить»)"
    )
    await state.set_state(EventSubmission.contact_phone)


@router.message(EventSubmission.contact_phone)
async def process_contact_phone(message: Message, state: FSMContext):
    """Обработка телефона"""
    phone = message.text.strip()
    if phone.lower() in ["пропустить", "-"]:
        phone = None
    
    await state.update_data(contact_phone=phone)
    
    await message.answer(
        "✅ Телефон принят!\n\n"
        "Отправьте **email для связи**:\n"
        "(или напишите «пропустить»)"
    )
    await state.set_state(EventSubmission.contact_email)


@router.message(EventSubmission.contact_email)
async def process_contact_email(message: Message, state: FSMContext):
    """Обработка email"""
    email = message.text.strip()
    if email.lower() in ["пропустить", "-"]:
        email = None
    elif "@" not in email:
        await message.answer("❌ Неверный формат email.\n\nВведите корректный email:")
        return
    
    await state.update_data(contact_email=email)
    
    await message.answer(
        "✅ Email принят!\n\n"
        "Отправьте **название организатора**:\n"
        "(или напишите «пропустить»)"
    )
    await state.set_state(EventSubmission.organizer)


@router.message(EventSubmission.organizer)
async def process_organizer(message: Message, state: FSMContext):
    """Обработка организатора"""
    organizer = message.text.strip()
    if organizer.lower() in ["пропустить", "-"]:
        organizer = None
    
    await state.update_data(organizer=organizer)
    
    # Показываем сводку для подтверждения
    data = await state.get_data()
    
    summary = (
        "📋 **Проверьте данные перед отправкой:**\n\n"
        f"📌 Название: {data['title']}\n"
        f"📅 Даты: {data['start_date'][:10]} - {data['end_date'][:10]}\n"
        f"⏰ Время: {data.get('start_time', 'не указано')} - {data.get('end_time', 'не указано')}\n"
        f"🌐 Формат: {data['format']}\n"
        f"📊 Тип: {data['event_type']}\n"
        f"📍 Место: {data['city']}, {data['country']}\n"
        f"🏢 Площадка: {data.get('venue', 'не указано')}\n"
        f"👤 Организатор: {data.get('organizer', 'не указано')}\n\n"
        "Если всё верно, напишите **«подтвердить»** для отправки на модерацию.\n"
        "Или **«изменить»**, чтобы начать заново."
    )
    
    await message.answer(text=summary, parse_mode="Markdown")
    await state.set_state(EventSubmission.confirm)


@router.message(EventSubmission.confirm)
async def process_confirm(message: Message, state: FSMContext):
    """Подтверждение и отправка мероприятия"""
    if message.text.lower() not in ["подтвердить", "да", "ok"]:
        if message.text.lower() in ["изменить", "нет", "отмена"]:
            await state.clear()
            await message.answer(
                "❌ Заявка отменена.\n\n"
                "Вы можете начать подачу мероприятия заново, выбрав «Предложить мероприятие».",
                reply_markup=get_main_keyboard()
            )
            return
        else:
            await message.answer("Напишите «подтвердить» для отправки или «изменить» для отмены:")
            return
    
    # Получаем данные из состояния
    data = await state.get_data()
    
    # Создаём объект мероприятия
    event_data = EventCreate(
        title=data['title'],
        description=data.get('description'),
        start_date=datetime.fromisoformat(data['start_date']),
        end_date=datetime.fromisoformat(data['end_date']),
        start_time=data.get('start_time'),
        end_time=data.get('end_time'),
        format=EventFormat(data['format']),
        event_type=EventType(data['event_type']),
        city=data['city'],
        country=data['country'],
        venue=data.get('venue'),
        registration_url=data.get('registration_url'),
        source_url=data.get('source_url'),
        source_name=data.get('source_name'),
        contact_person=data.get('contact_person'),
        contact_phone=data.get('contact_phone'),
        contact_email=data.get('contact_email'),
        organizer=data.get('organizer'),
        submitted_by=message.from_user.id
    )
    
    # TODO: Сохранение в БД через EventCRUD
    # async with AsyncSessionLocal() as session:
    #     event = await EventCRUD.create_event(session, event_data)
    #     await AdminLogCRUD.create_log(...)
    
    await state.clear()
    
    await message.answer(
        "✅ **Ваша заявка принята!**\n\n"
        "Мероприятие отправлено на модерацию.\n"
        "После проверки администратором оно появится в календаре.\n\n"
        "Спасибо за ваше предложение! 🙏",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )
    
    # TODO: Отправить уведомление администраторам
