from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Твой токен
TOKEN = "7606324631:AAEAzQlveWxP9t4Xymh8gnE3c-B45-sEoNE"

# Промт HoFiLiOn
PROMPT = """
Ты нейронка, которая имитирует стиль общения пользователя HoFiLiOn.
Пиши естественно, живо, без цензуры, с эмоциями и сленгом. 
Пиши от первого лица. Пример: 
Хофилион: ебанный рот, ну и что за нахуй тут происходит…
Хофилион: ааа, вот оно че, бля, даже не ожидал такого…
"""

# Функция генерации текста (на данном этапе — простая имитация)
def generate_hofilion_response(user_text: str) -> str:
    # Здесь можно подключить реальный API нейросети
    # Сейчас делаем примитивный генератор
    import random
    responses = [
        "ёпт, ну ты это… чёт жестко получилось 😅",
        "бля, не ожидал такого, ну ладно...",
        "ахаха, хз че тут сказать, реально",
        "ебаный рот, это прям огонь 🔥",
        "ну посмотрим что дальше, хз че будет"
    ]
    return random.choice(responses)

# Обработчик сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    response = generate_hofilion_response(user_text)
    await update.message.reply_text(response)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я HoFiLiOn Bot. Пиши что-нибудь, и я отвечу как HoFiLiOn 😎")

# Создаём и запускаем бота
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("HoFiLiOn Bot запущен...")
app.run_polling()