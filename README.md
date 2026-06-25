# StudentHelper Bot 🎓

Telegram-бот для допомоги студентам в організації навчального процесу.

## Функції

- 🤖 **AI-асистент** — відповіді на навчальні питання (GPT-4o-mini)
- 📅 **Розклад** — зберігання та перегляд розкладу пар
- 📌 **Дедлайни** — управління списком навчальних завдань

## Стек

- Python 3.11+
- aiogram 3
- OpenAI API (GPT-4o-mini)
- SQLite

## Запуск

1. Клонуй репозиторій:
```bash
git clone https://github.com/ipz25-ftymoshenko-lgtm/StudentHelper-bot
cd StudentHelper-bot
```

2. Встанови залежності:
```bash
pip install -r requirements.txt
```

3. Створи файл `.env`:
```
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
```

4. Запусти бота:
```bash
python main.py
```

## Отримання токенів

- **BOT_TOKEN** — через [@BotFather](https://t.me/BotFather) у Telegram
- **OPENAI_API_KEY** — на [platform.openai.com](https://platform.openai.com)
