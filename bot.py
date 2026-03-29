import random
import numpy
import telegram
import telegram.ext

from telegram import Update
from telegram.ext import ApplicationBuilder
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import ContextTypes
from telegram.ext import filters

# Токен бота
TOKEN = "7606324631:AAEAzQlveWxP9t4Xymh8gnE3c-B45-sEoNE"

# Мини-нейросеть: учится на твоих примерах HoFiLiOn
class HoFiLiOnNN:
    def __init__(self):
        # Примитивная “память” ответов
        self.examples = [
            "ебаный рот, ну и что за нахуй тут происходит…",
            "ааа, вот оно че, бля, даже не ожидал такого…",
            "ну ладно, посмотрим что дальше, хз че там будет",
            "бля, реально жестко, хз как так вышло 😅",
            "ахах, ёпт, это прям огонь 🔥"
        ]

    # "Обучение" — просто добавляем примеры
    def train(self, text):
        self.examples.append(text)

    # Генерация ответа: случайная комбинация слов из примеров
    def generate(self, prompt=""):
        # Можно добавить простое смешение слов
        base = random.choice(self.examples)
        words = base.split()
        random.shuffle(words)
        # Частично сохраняем структуру
        cut = random.randint(int(len(words)/2), len(words))
        return " ".join(words[:cut])

# Создаём нейросеть
nn = HoFiLiOnNN()

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я HoFiLiOn Bot. Пиши что-нибудь, и я отвечу как HoFiLiOn 😎")

# Обработчик сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    # "Обучаем" сеть на твоём сообщении
    nn.train(user_text)
    # Генерируем ответ
    response = nn.generate(user_text)
    await update.message.reply_text(response)

# Создаём приложение и добавляем обработчики
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("HoFiLiOn Bot запущен...")
app.run_polling()