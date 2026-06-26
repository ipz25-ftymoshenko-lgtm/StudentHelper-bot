from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import (
    init_db,
    add_deadline, get_deadlines, delete_deadline,
    add_schedule, get_schedule, delete_schedule,
    add_grade, get_grades, delete_grade, get_subjects_with_grades,
    add_note, get_note_subjects, get_notes_by_subject, delete_note,
)
from ai_module import ask_ai

router = Router()

# ── FSM States ────────────────────────────────────────────────────────────────
class AskAI(StatesGroup):
    waiting_for_question = State()

class QuizAI(StatesGroup):
    waiting_for_topic = State()
    waiting_for_answer = State()

class AddDeadline(StatesGroup):
    waiting_for_subject = State()
    waiting_for_task = State()
    waiting_for_date = State()

class AddSchedule(StatesGroup):
    waiting_for_day = State()
    waiting_for_time = State()
    waiting_for_subject = State()

class AddGrade(StatesGroup):
    waiting_for_subject = State()
    waiting_for_label = State()
    waiting_for_grade = State()

class AddNote(StatesGroup):
    waiting_for_subject = State()
    waiting_for_content = State()

class ViewNotes(StatesGroup):
    waiting_for_subject = State()

# ── Keyboards ─────────────────────────────────────────────────────────────────
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 Запитати AI", callback_data="ask_ai"),
         InlineKeyboardButton(text="🎲 Тест-питання", callback_data="quiz_ai")],
        [InlineKeyboardButton(text="📅 Розклад", callback_data="schedule"),
         InlineKeyboardButton(text="📌 Дедлайни", callback_data="deadlines")],
        [InlineKeyboardButton(text="📊 Оцінки", callback_data="grades"),
         InlineKeyboardButton(text="📝 Конспекти", callback_data="notes")],
        [InlineKeyboardButton(text="ℹ️ Про бота", callback_data="about")],
    ])

def back_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Головне меню", callback_data="main_menu")]
    ])

# ── /start ────────────────────────────────────────────────────────────────────
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    init_db()
    await message.answer(
        f"👋 Привіт, <b>{message.from_user.first_name}</b>!\n\n"
        "Я <b>StudentHelper</b> — твій навчальний помічник 🎓\n\n"
        "• 🤖 AI-відповіді на навчальні питання\n"
        "• 🎲 Випадкові тест-питання для самоперевірки\n"
        "• 📅 Розклад пар\n"
        "• 📌 Дедлайни\n"
        "• 📊 Калькулятор оцінок\n"
        "• 📝 Конспекти по предметах\n\n"
        "Обери, що тебе цікавить:",
        reply_markup=main_menu()
    )

@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("📋 Головне меню:", reply_markup=main_menu())

@router.callback_query(F.data == "main_menu")
async def cb_main_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("📋 Головне меню:", reply_markup=main_menu())

# ── About ─────────────────────────────────────────────────────────────────────
@router.callback_query(F.data == "about")
async def cb_about(call: CallbackQuery):
    await call.message.edit_text(
        "ℹ️ <b>StudentHelper Bot</b>\n\n"
        "Розроблено студентом НУБіП України як навчальний проєкт.\n\n"
        "<b>Функції:</b>\n"
        "• AI-відповіді на навчальні запитання (GPT-4o-mini)\n"
        "• Тест-питання для самоперевірки\n"
        "• Управління розкладом занять\n"
        "• Відстеження дедлайнів\n"
        "• Калькулятор оцінок і середнього балу\n"
        "• Збереження конспектів по предметах\n\n"
        "<b>Стек:</b> Python, aiogram 3, OpenAI API, SQLite",
        reply_markup=back_button()
    )

# ── ASK AI ────────────────────────────────────────────────────────────────────
@router.callback_query(F.data == "ask_ai")
async def cb_ask_ai(call: CallbackQuery, state: FSMContext):
    await state.set_state(AskAI.waiting_for_question)
    await call.message.edit_text(
        "🤖 <b>AI-асистент</b>\n\n"
        "Напиши своє навчальне питання!\n\n"
        "<i>Наприклад: «Поясни що таке рекурсія» або «Як працює TCP/IP?»</i>\n\n"
        "Для виходу: /menu",
        reply_markup=None
    )

@router.message(AskAI.waiting_for_question)
async def process_ai_question(message: Message, state: FSMContext):
    await message.answer("⏳ Думаю над відповіддю...")
    answer = await ask_ai(message.text)
    await state.clear()
    await message.answer(f"🤖 <b>Відповідь AI:</b>\n\n{answer}", reply_markup=main_menu())

# ── QUIZ AI ───────────────────────────────────────────────────────────────────
@router.callback_query(F.data == "quiz_ai")
async def cb_quiz_ai(call: CallbackQuery, state: FSMContext):
    await state.set_state(QuizAI.waiting_for_topic)
    await call.message.edit_text(
        "🎲 <b>Тест-питання</b>\n\n"
        "Напиши тему або предмет — я згенерую питання для самоперевірки!\n\n"
        "<i>Наприклад: «алгоритми», «бази даних», «мережі»</i>\n\n"
        "Для виходу: /menu",
        reply_markup=None
    )

@router.message(QuizAI.waiting_for_topic)
async def process_quiz_topic(message: Message, state: FSMContext):
    await message.answer("🎲 Генерую питання...")
    prompt = (
        f"Згенеруй одне навчальне питання з теми «{message.text}» для студента IT-спеціальності. "
        "Питання має бути чітким та конкретним. Після питання напиши рядок «---» і правильну відповідь. "
        "Формат:\nПИТАННЯ: <текст питання>\n---\nВІДПОВІДЬ: <текст відповіді>"
    )
    result = await ask_ai(prompt)

    parts = result.split("---")
    question_part = parts[0].strip()
    answer_part = parts[1].strip() if len(parts) > 1 else ""

    await state.update_data(answer=answer_part, topic=message.text)
    await state.set_state(QuizAI.waiting_for_answer)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💡 Показати відповідь", callback_data="show_quiz_answer")],
        [InlineKeyboardButton(text="🎲 Ще питання", callback_data="quiz_ai")],
        [InlineKeyboardButton(text="⬅️ Головне меню", callback_data="main_menu")],
    ])
    await message.answer(f"🎲 <b>Питання:</b>\n\n{question_part}", reply_markup=kb)

@router.callback_query(F.data == "show_quiz_answer", QuizAI.waiting_for_answer)
async def cb_show_quiz_answer(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    answer = data.get("answer", "Відповідь недоступна")
    await state.clear()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Ще питання", callback_data="quiz_ai")],
        [InlineKeyboardButton(text="⬅️ Головне меню", callback_data="main_menu")],
    ])
    await call.message.edit_text(
        f"{call.message.text}\n\n✅ <b>Відповідь:</b>\n\n{answer}",
        reply_markup=kb
    )

# ── SCHEDULE ──────────────────────────────────────────────────────────────────
@router.callback_query(F.data == "schedule")
async def cb_schedule(call: CallbackQuery):
    rows = get_schedule(call.from_user.id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Додати пару", callback_data="add_schedule")],
        [InlineKeyboardButton(text="🗑 Видалити пару", callback_data="del_schedule_list")] if rows else [],
        [InlineKeyboardButton(text="⬅️ Головне меню", callback_data="main_menu")],
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
        [InlineKeyboardButton(text="⬅️ Скасувати", callback_data="schedule")],
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

@router.callback_query(F.data == "del_schedule_list")
async def cb_del_schedule_list(call: CallbackQuery):
    rows = get_schedule(call.from_user.id)
    buttons = [[InlineKeyboardButton(
        text=f"🗑 {row[1]} {row[2]} — {row[3]}",
        callback_data=f"delsch_{row[0]}"
    )] for row in rows]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="schedule")])
    await call.message.edit_text("Обери пару для видалення:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data.startswith("delsch_"))
async def cb_delete_schedule(call: CallbackQuery):
    sid = int(call.data.replace("delsch_", ""))
    delete_schedule(sid, call.from_user.id)
    await call.answer("✅ Пару видалено")
    rows = get_schedule(call.from_user.id)
    if not rows:
        await call.message.edit_text("📅 Розклад порожній.", reply_markup=back_button())
    else:
        buttons = [[InlineKeyboardButton(
            text=f"🗑 {row[1]} {row[2]} — {row[3]}",
            callback_data=f"delsch_{row[0]}"
        )] for row in rows]
        buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="schedule")])
        await call.message.edit_text("Обери пару для видалення:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# ── DEADLINES ─────────────────────────────────────────────────────────────────
@router.callback_query(F.data == "deadlines")
async def cb_deadlines(call: CallbackQuery):
    rows = get_deadlines(call.from_user.id)
    kb_rows = [[InlineKeyboardButton(text="➕ Додати дедлайн", callback_data="add_deadline")]]
    if rows:
        kb_rows.append([InlineKeyboardButton(text="🗑 Видалити дедлайн", callback_data="del_deadline_list")])
    kb_rows.append([InlineKeyboardButton(text="⬅️ Головне меню", callback_data="main_menu")])
    if not rows:
        text = "📌 <b>Дедлайни</b>\n\nСписок порожній. Молодець!"
    else:
        text = "📌 <b>Твої дедлайни:</b>\n\n"
        for i, (_, subject, task, due_date) in enumerate(rows, 1):
            text += f"{i}. 📚 <b>{subject}</b>\n   📝 {task}\n   📅 до {due_date}\n\n"
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))

@router.callback_query(F.data == "add_deadline")
async def cb_add_deadline(call: CallbackQuery, state: FSMContext):
    await state.set_state(AddDeadline.waiting_for_subject)
    await call.message.edit_text("📌 <b>Новий дедлайн</b>\n\n📚 Напиши назву предмету:", reply_markup=None)

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
        f"✅ Дедлайн додано!\n\n📚 {data['subject']}\n📝 {data['task']}\n📅 до {message.text}",
        reply_markup=main_menu()
    )

@router.callback_query(F.data == "del_deadline_list")
async def cb_del_deadline_list(call: CallbackQuery):
    rows = get_deadlines(call.from_user.id)
    buttons = [[InlineKeyboardButton(
        text=f"🗑 {row[1]} — {row[3]}",
        callback_data=f"deldl_{row[0]}"
    )] for row in rows]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="deadlines")])
    await call.message.edit_text("Обери дедлайн для видалення:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data.startswith("deldl_"))
async def cb_delete_deadline(call: CallbackQuery):
    did = int(call.data.replace("deldl_", ""))
    delete_deadline(did, call.from_user.id)
    await call.answer("✅ Видалено")
    rows = get_deadlines(call.from_user.id)
    if not rows:
        await call.message.edit_text("📌 Дедлайни відсутні.", reply_markup=back_button())
    else:
        buttons = [[InlineKeyboardButton(
            text=f"🗑 {row[1]} — {row[3]}",
            callback_data=f"deldl_{row[0]}"
        )] for row in rows]
        buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="deadlines")])
        await call.message.edit_text("Обери дедлайн для видалення:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# ── GRADES ────────────────────────────────────────────────────────────────────
@router.callback_query(F.data == "grades")
async def cb_grades(call: CallbackQuery):
    rows = get_subjects_with_grades(call.from_user.id)
    all_grades = get_grades(call.from_user.id)
    kb_rows = [[InlineKeyboardButton(text="➕ Додати оцінку", callback_data="add_grade")]]
    if all_grades:
        kb_rows.append([InlineKeyboardButton(text="🗑 Видалити оцінку", callback_data="del_grade_list")])
    kb_rows.append([InlineKeyboardButton(text="⬅️ Головне меню", callback_data="main_menu")])
    if not rows:
        text = "📊 <b>Оцінки</b>\n\nОцінок ще немає. Додай першу!"
    else:
        total_all = [g[2] for g in all_grades]
        avg_all = sum(total_all) / len(total_all)
        text = "📊 <b>Твої оцінки:</b>\n\n"
        for subject, avg, count in rows:
            bar = "█" * int(avg / 20) + "░" * (5 - int(avg / 20))
            text += f"📚 <b>{subject}</b>\n   Середній бал: <b>{avg:.1f}</b> [{bar}] ({count} оц.)\n\n"
        text += f"━━━━━━━━━━━━━━━\n🏆 Загальний середній бал: <b>{avg_all:.1f}</b>"
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))

@router.callback_query(F.data == "add_grade")
async def cb_add_grade(call: CallbackQuery, state: FSMContext):
    await state.set_state(AddGrade.waiting_for_subject)
    await call.message.edit_text("📊 <b>Нова оцінка</b>\n\n📚 Напиши назву предмету:", reply_markup=None)

@router.message(AddGrade.waiting_for_subject)
async def process_grade_subject(message: Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await state.set_state(AddGrade.waiting_for_label)
    await message.answer("🏷 За що оцінка? (наприклад: <code>Контрольна робота</code>, <code>Лабораторна №3</code>)\n\nАбо напиши «-» щоб пропустити:")

@router.message(AddGrade.waiting_for_label)
async def process_grade_label(message: Message, state: FSMContext):
    label = None if message.text.strip() == "-" else message.text.strip()
    await state.update_data(label=label)
    await state.set_state(AddGrade.waiting_for_grade)
    await message.answer("🔢 Введи оцінку (за 100-бальною шкалою, наприклад: <code>85</code>):")

@router.message(AddGrade.waiting_for_grade)
async def process_grade_value(message: Message, state: FSMContext):
    try:
        grade = float(message.text.replace(",", "."))
        if not (0 <= grade <= 100):
            raise ValueError
    except ValueError:
        await message.answer("❌ Введи число від 0 до 100:")
        return
    data = await state.get_data()
    add_grade(message.from_user.id, data["subject"], grade, data.get("label"))
    await state.clear()
    label_str = f" ({data['label']})" if data.get("label") else ""
    await message.answer(
        f"✅ Оцінку додано!\n\n📚 {data['subject']}{label_str}\n🔢 Оцінка: <b>{grade:.0f}/100</b>",
        reply_markup=main_menu()
    )

@router.callback_query(F.data == "del_grade_list")
async def cb_del_grade_list(call: CallbackQuery):
    rows = get_grades(call.from_user.id)
    buttons = [[InlineKeyboardButton(
        text=f"🗑 {row[1]} — {row[2]:.0f}" + (f" ({row[3]})" if row[3] else ""),
        callback_data=f"delgr_{row[0]}"
    )] for row in rows]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="grades")])
    await call.message.edit_text("Обери оцінку для видалення:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data.startswith("delgr_"))
async def cb_delete_grade(call: CallbackQuery):
    gid = int(call.data.replace("delgr_", ""))
    delete_grade(gid, call.from_user.id)
    await call.answer("✅ Видалено")
    rows = get_grades(call.from_user.id)
    if not rows:
        await call.message.edit_text("📊 Оцінки відсутні.", reply_markup=back_button())
    else:
        buttons = [[InlineKeyboardButton(
            text=f"🗑 {row[1]} — {row[2]:.0f}" + (f" ({row[3]})" if row[3] else ""),
            callback_data=f"delgr_{row[0]}"
        )] for row in rows]
        buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="grades")])
        await call.message.edit_text("Обери оцінку для видалення:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# ── NOTES ─────────────────────────────────────────────────────────────────────
@router.callback_query(F.data == "notes")
async def cb_notes(call: CallbackQuery):
    subjects = get_note_subjects(call.from_user.id)
    kb_rows = [[InlineKeyboardButton(text="➕ Додати конспект", callback_data="add_note")]]
    if subjects:
        kb_rows.append([InlineKeyboardButton(text="📖 Переглянути конспекти", callback_data="view_notes")])
    kb_rows.append([InlineKeyboardButton(text="⬅️ Головне меню", callback_data="main_menu")])
    if not subjects:
        text = "📝 <b>Конспекти</b>\n\nКонспектів ще немає. Додай перший!"
    else:
        text = f"📝 <b>Конспекти</b>\n\nПредмети з конспектами ({len(subjects)}):\n\n"
        text += "\n".join(f"• {s}" for s in subjects)
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))

@router.callback_query(F.data == "add_note")
async def cb_add_note(call: CallbackQuery, state: FSMContext):
    await state.set_state(AddNote.waiting_for_subject)
    await call.message.edit_text("📝 <b>Новий конспект</b>\n\n📚 Напиши назву предмету:", reply_markup=None)

@router.message(AddNote.waiting_for_subject)
async def process_note_subject(message: Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await state.set_state(AddNote.waiting_for_content)
    await message.answer(
        f"📚 Предмет: <b>{message.text}</b>\n\n"
        "✏️ Напиши текст конспекту (можна кілька абзаців):\n\n"
        "<i>Для виходу: /menu</i>"
    )

@router.message(AddNote.waiting_for_content)
async def process_note_content(message: Message, state: FSMContext):
    data = await state.get_data()
    add_note(message.from_user.id, data["subject"], message.text)
    await state.clear()
    await message.answer(
        f"✅ Конспект збережено!\n\n📚 Предмет: <b>{data['subject']}</b>",
        reply_markup=main_menu()
    )

@router.callback_query(F.data == "view_notes")
async def cb_view_notes(call: CallbackQuery, state: FSMContext):
    subjects = get_note_subjects(call.from_user.id)
    if not subjects:
        await call.message.edit_text("📝 Конспектів немає.", reply_markup=back_button())
        return
    buttons = [[InlineKeyboardButton(text=f"📚 {s}", callback_data=f"viewnotes_{s}")] for s in subjects]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="notes")])
    await call.message.edit_text("Обери предмет:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data.startswith("viewnotes_"))
async def cb_view_notes_subject(call: CallbackQuery):
    subject = call.data.replace("viewnotes_", "")
    notes = get_notes_by_subject(call.from_user.id, subject)
    text = f"📚 <b>{subject}</b> — конспекти ({len(notes)}):\n\n"
    for i, (nid, content, created_at) in enumerate(notes, 1):
        date = created_at[:10] if created_at else ""
        preview = content[:200] + ("..." if len(content) > 200 else "")
        text += f"<b>{i}. [{date}]</b>\n{preview}\n\n"
    buttons = [[InlineKeyboardButton(text=f"🗑 Видалити #{i+1}", callback_data=f"delnote_{notes[i][0]}")] for i in range(len(notes))]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="view_notes")])
    await call.message.edit_text(text[:4000], reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data.startswith("delnote_"))
async def cb_delete_note(call: CallbackQuery):
    nid = int(call.data.replace("delnote_", ""))
    delete_note(nid, call.from_user.id)
    await call.answer("✅ Конспект видалено")
    await call.message.edit_text("✅ Конспект видалено.", reply_markup=back_button())
