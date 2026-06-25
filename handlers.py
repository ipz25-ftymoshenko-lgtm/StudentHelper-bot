from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import init_db, add_deadline, get_deadlines, delete_deadline, add_schedule, get_schedule
from ai_module import ask_ai

router = Router()

# FSM States
class AskAI(StatesGroup):
    waiting_for_question = State()

class AddDeadline(StatesGroup):
    waiting_for_subject = State()
    waiting_for_task = State()
    waiting_for_date = State()

class AddSchedule(StatesGroup):
    waiting_for_day = State()
    waiting_for_time = State()
    waiting_for_subject = State()

# --- Main Menu ---
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 Запитати AI", callback_data="ask_ai")],
        [InlineKeyboardButton(text="📅 Розклад", callback_data="schedule"),
         InlineKeyboardButton(text="📌 Дедлайни", callback_data="deadlines")],
        [InlineKeyboardButton(text="ℹ️ Про бота", callback_data="about")]
    ])

def back_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Головне меню", callback_data="main_menu")]
    ])

# --- /start ---
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    init_db()
    await message.answer(
        f"👋 Привіт, <b>{message.from_user.first_name}</b>!\n\n"
        "Я <b>StudentHelper</b> — твій навчальний помічник 🎓\n\n"
        "Я можу:\n"
        "• 🤖 Відповідати на питання з навчання за допомогою AI\n"
        "• 📅 Зберігати твій розклад пар\n"
        "• 📌 Нагадувати про дедлайни\n\n"
        "Обери, що тебе цікавить:",
        reply_markup=main_menu()
    )

@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("📋 Головне меню:", reply_markup=main_menu())

# --- Main menu callback ---
@router.callback_query(F.data == "main_menu")
async def cb_main_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("📋 Головне меню:", reply_markup=main_menu())

# --- About ---
@router.callback_query(F.data == "about")
async def cb_about(call: CallbackQuery):
    await call.message.edit_text(
        "ℹ️ <b>StudentHelper Bot</b>\n\n"
        "Розроблено студентом НУБіП України як навчальний проєкт.\n\n"
        "<b>Функції:</b>\n"
        "• AI-відповіді на навчальні запитання (GPT-4o-mini)\n"
        "• Управління розкладом занять\n"
        "• Відстеження дедлайнів\n\n"
        "<b>Стек:</b> Python, aiogram 3, OpenAI API, SQLite",
        reply_markup=back_button()
    )

# --- ASK AI ---
@router.callback_query(F.data == "ask_ai")
async def cb_ask_ai(call: CallbackQuery, state: FSMContext):
    await state.set_state(AskAI.waiting_for_question)
    await call.message.edit_text(
        "🤖 <b>AI-асистент</b>\n\n"
        "Напиши своє навчальне питання, і я відповім!\n\n"
        "<i>Наприклад: «Поясни що таке рекурсія» або «Як працює сортування бульбашкою?»</i>\n\n"
        "Для виходу напиши /menu",
        reply_markup=None
    )

@router.message(AskAI.waiting_for_question)
async def process_ai_question(message: Message, state: FSMContext):
    await message.answer("⏳ Думаю над відповіддю...")
    answer = await ask_ai(message.text)
    await state.clear()
    await message.answer(f"🤖 <b>Відповідь AI:</b>\n\n{answer}", reply_markup=main_menu())

# --- SCHEDULE ---
@router.callback_query(F.data == "schedule")
async def cb_schedule(call: CallbackQuery):
    rows = get_schedule(call.from_user.id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Додати пару", callback_data="add_schedule")],
        [InlineKeyboardButton(text="⬅️ Головне меню", callback_data="main_menu")]
    ])
    if not rows:
        text = "📅 <b>Розклад</b>\n\nРозклад порожній. Додай свої пари!"
    else:
        text = "📅 <b>Твій розклад:</b>\n\n"
        current_day = None
        for _, day, time, subject in rows:
            if day != current_day:
                text += f"\n📆 <b>{day}</b>\n"
                current_day = day
            text += f"  🕐 {time} — {subject}\n"
    await call.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data == "add_schedule")
async def cb_add_schedule(call: CallbackQuery, state: FSMContext):
    await state.set_state(AddSchedule.waiting_for_day)
    days_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Понеділок", callback_data="day_Понеділок"),
         InlineKeyboardButton(text="Вівторок", callback_data="day_Вівторок")],
        [InlineKeyboardButton(text="Середа", callback_data="day_Середа"),
         InlineKeyboardButton(text="Четвер", callback_data="day_Четвер")],
        [InlineKeyboardButton(text="П'ятниця", callback_data="day_Пятниця")],
        [InlineKeyboardButton(text="⬅️ Скасувати", callback_data="schedule")]
    ])
    await call.message.edit_text("📅 Оберіть день тижня:", reply_markup=days_kb)

@router.callback_query(F.data.startswith("day_"), AddSchedule.waiting_for_day)
async def process_schedule_day(call: CallbackQuery, state: FSMContext):
    day = call.data.replace("day_", "")
    await state.update_data(day=day)
    await state.set_state(AddSchedule.waiting_for_time)
    await call.message.edit_text(
        f"📅 День: <b>{day}</b>\n\n⏰ Напиши час пари (наприклад: <code>08:30</code>):",
        reply_markup=None
    )

@router.message(AddSchedule.waiting_for_time)
async def process_schedule_time(message: Message, state: FSMContext):
    await state.update_data(time=message.text)
    await state.set_state(AddSchedule.waiting_for_subject)
    await message.answer("📚 Напиши назву предмету:")

@router.message(AddSchedule.waiting_for_subject)
async def process_schedule_subject(message: Message, state: FSMContext):
    data = await state.get_data()
    add_schedule(message.from_user.id, data["day"], data["time"], message.text)
    await state.clear()
    await message.answer(
        f"✅ Пару додано!\n\n📆 {data['day']} о {data['time']} — {message.text}",
        reply_markup=main_menu()
    )

# --- DEADLINES ---
@router.callback_query(F.data == "deadlines")
async def cb_deadlines(call: CallbackQuery):
    rows = get_deadlines(call.from_user.id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Додати дедлайн", callback_data="add_deadline")],
        [InlineKeyboardButton(text="⬅️ Головне меню", callback_data="main_menu")]
    ])
    if not rows:
        text = "📌 <b>Дедлайни</b>\n\nСписок дедлайнів порожній. Молодець!"
    else:
        text = "📌 <b>Твої дедлайни:</b>\n\n"
        for i, (did, subject, task, due_date) in enumerate(rows, 1):
            text += f"{i}. 📚 <b>{subject}</b>\n   📝 {task}\n   📅 до {due_date}\n\n"
    await call.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data == "add_deadline")
async def cb_add_deadline(call: CallbackQuery, state: FSMContext):
    await state.set_state(AddDeadline.waiting_for_subject)
    await call.message.edit_text(
        "📌 <b>Новий дедлайн</b>\n\n📚 Напиши назву предмету:",
        reply_markup=None
    )

@router.message(AddDeadline.waiting_for_subject)
async def process_deadline_subject(message: Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await state.set_state(AddDeadline.waiting_for_task)
    await message.answer("📝 Опиши завдання:")

@router.message(AddDeadline.waiting_for_task)
async def process_deadline_task(message: Message, state: FSMContext):
    await state.update_data(task=message.text)
    await state.set_state(AddDeadline.waiting_for_date)
    await message.answer("📅 Вкажи дату дедлайну (наприклад: <code>30.06.2026</code>):")

@router.message(AddDeadline.waiting_for_date)
async def process_deadline_date(message: Message, state: FSMContext):
    data = await state.get_data()
    add_deadline(message.from_user.id, data["subject"], data["task"], message.text)
    await state.clear()
    await message.answer(
        f"✅ Дедлайн додано!\n\n"
        f"📚 {data['subject']}\n"
        f"📝 {data['task']}\n"
        f"📅 до {message.text}",
        reply_markup=main_menu()
    )
