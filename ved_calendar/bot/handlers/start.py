from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards.main_keyboard import get_main_keyboard
from config import settings


router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    user_name = message.from_user.first_name
    
    welcome_text = (
        f"👋 Привет, {user_name}!\n\n"
        "Добро пожаловать в **ВЭД-календарь** — ваш помощник в мире международных мероприятий!\n\n"
        "Здесь вы найдете:\n"
        "📅 Актуальные выставки, форумы и вебинары\n"
        "🔍 Удобный поиск и фильтры\n"
        "📝 Возможность предложить своё мероприятие\n\n"
        "Выберите раздел в меню ниже:"
    )
    
    await message.answer(
        text=welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = (
        "📚 **Помощь по боту ВЭД-календарь**\n\n"
        "**Основные команды:**\n"
        "/start - Главное меню\n"
        "/help - Эта справка\n\n"
        "**Разделы бота:**\n"
        "📅 **Актуальные события** - ближайшие мероприятия\n"
        "🗓 **Календарь** - просмотр по датам\n"
        "🔍 **Поиск и фильтры** - найти нужное событие\n"
        "📁 **Архив** - прошедшие мероприятия\n"
        "➕ **Предложить мероприятие** - добавить своё событие\n\n"
        "**Как предложить мероприятие:**\n"
        "1. Нажмите «Предложить мероприятие»\n"
        "2. Заполните форму\n"
        "3. Отправьте на модерацию\n"
        "4. После проверки оно появится в календаре\n\n"
        "❓ Есть вопросы? Свяжитесь с поддержкой."
    )
    
    await message.answer(text=help_text, parse_mode="Markdown")


@router.callback_query(lambda c: c.data == "menu_back")
async def menu_back(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    
    user_name = callback.from_user.first_name
    welcome_text = (
        f"👋 Привет, {user_name}!\n\n"
        "Выберите раздел:"
    )
    
    await callback.message.edit_text(
        text=welcome_text,
        reply_markup=get_main_keyboard()
    )
