import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

SYSTEM_PROMPT = """Ти — навчальний AI-асистент для студентів університету. 
Твоя роль — допомагати студентам з навчальними питаннями: пояснювати теми, 
допомагати розібратися з завданнями, давати поради щодо навчання.
Відповідай українською мовою, чітко та зрозуміло. 
Якщо питання не стосується навчання, ввічливо поясни, що ти навчальний асистент."""

async def ask_ai(question: str) -> str:
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Виникла помилка при зверненні до AI: {str(e)}"
