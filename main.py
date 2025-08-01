import os
import openai
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from duckduckgo_search import ddg

openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

def search_ukrainian_law(query):
    results = ddg(f"{query} site:zakon.rada.gov.ua", max_results=1)
    return results[0]["href"] if results else None

async def ask_gpt(query, law_url):
    context = ""
    if law_url:
        try:
            law_html = requests.get(law_url, timeout=10).text[:3000]
            context = f"Витяг із закону: {law_html}"
        except:
            context = "Не вдалося отримати текст закону."

    prompt = f"""
Ти — юридичний консультант з українського права. Відповідай офіційно, стисло, базуючись на законодавстві.
Питання: {query}
{context}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    law_url = search_ukrainian_law(query)
    answer = await ask_gpt(query, law_url)
    await update.message.reply_text(answer)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вітаю! Напишіть юридичне питання. Я знайду норму закону і сформулюю відповідь.")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    app.run_polling()
