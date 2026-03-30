import random
import re
import os
import json
import logging
from collections import defaultdict
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== НАСТРОЙКИ ==========
TOKEN = "8376850903:AAEvWNLCJTA2U_Yblx271ov5JYzGsxA5IJg"

# ========== ОБУЧАЕМАЯ МОДЕЛЬ (Цепь Маркова) ==========
class MarkovChain:
    def __init__(self):
        self.chain = defaultdict(list)
        self.words = []
    
    def train(self, text):
        """Обучаемся на тексте: разбиваем на слова и строим переходы"""
        # Чистим текст, но сохраняем знаки препинания для стиля
        sentences = re.split(r'[.!?…]+', text)
        
        for sentence in sentences:
            words = sentence.strip().split()
            if len(words) < 2:
                continue
            
            for i in range(len(words) - 1):
                key = words[i]
                next_word = words[i + 1]
                self.chain[key].append(next_word)
                self.words.append(key)
    
    def train_from_file(self, filepath):
        """Обучаемся из файла с текстами"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            self.train(content)
    
    def generate(self, seed_word=None, max_words=30):
        """Генерируем текст в стиле HoFiLiOn"""
        if not self.chain:
            return "пока ничему не научился, дай текстов 🤷"
        
        # Если нет seed'а или он не в цепочке — берём случайное слово
        if not seed_word or seed_word not in self.chain:
            seed_word = random.choice(list(self.chain.keys()))
        
        result = [seed_word]
        current = seed_word
        
        for _ in range(max_words - 1):
            if current not in self.chain:
                break
            
            next_words = self.chain[current]
            if not next_words:
                break
            
            next_word = random.choice(next_words)
            result.append(next_word)
            current = next_word
        
        return ' '.join(result)

# ========== БАЗА СТИЛЕЙ И ЭМОЦИЙ ==========
HOFILION_STYLE = {
    "начало": [
        "ну че там…", "бля, смотри", "короче", "слушай", "вообще пиздец",
        "ахахах", "да ну нахуй", "интересно", "хз короче"
    ],
    "связки": [
        "короче", "типа", "ну", "бля", "ебать", "пиздец", "ахаха", "серьезно"
    ],
    "концовки": [
        "хз", "ну такое", "кароче так", "вот и всё", "а я хз", "посмотрим чё будет"
    ],
    "эмодзи": ["😂", "🤣", "😈", "🔥", "💀", "🤡", "👀", "😏", "🤷", "🙄"]
}

def add_hofilion_style(text):
    """Добавляет сленг, эмоции и манеру HoFiLiOn к сгенерированному тексту"""
    words = text.split()
    
    # Добавляем случайное начало
    if random.random() > 0.6:
        start = random.choice(HOFILION_STYLE["начало"])
        text = f"{start}, {text}"
    
    # Вставляем связки
    if len(words) > 5 and random.random() > 0.7:
        pos = random.randint(2, len(words) - 2)
        connector = random.choice(HOFILION_STYLE["связки"])
        words.insert(pos, connector)
        text = ' '.join(words)
    
    # Добавляем концовку
    if random.random() > 0.6:
        end = random.choice(HOFILION_STYLE["концовки"])
        text = f"{text}… {end}"
    
    # Добавляем эмодзи
    if random.random() > 0.5:
        emoji = random.choice(HOFILION_STYLE["эмодзи"])
        text = f"{text} {emoji}"
    
    return text.lower()

# ========== ИНИЦИАЛИЗАЦИЯ МОДЕЛИ ==========
markov = MarkovChain()

# Создаём файл с примерами текстов в стиле HoFiLiOn
EXAMPLE_TEXTS = """
ебаный рот, ну и что за нахуй тут происходит
ааа, вот оно че, бля, даже не ожидал такого
ну ладно, посмотрим что дальше, хз че там будет
бля, это пиздец какой-то, я в шоке
короче, сижу такой, думаю, а нахуя это всё
серьезно? это что за хуйня
ахахах, ну ты даешь, я бы так не смог
вообще кайф, заебись всё
ну хз, может быть, а может и нет
бля, опять эти глюки, ебаный в рот
типа, я вообще не понял че произошло
пиздец, ну и денек
короче, я пас, делайте что хотите
"""

# Сохраняем в файл и обучаем
with open("hofilion_train.txt", "w", encoding="utf-8") as f:
    f.write(EXAMPLE_TEXTS)

markov.train_from_file("hofilion_train.txt")

# ========== ОБРАБОТЧИКИ БОТА ==========
logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ну че, заебись, работаем 🤘")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    # Генерируем ответ
    if random.random() > 0.3:
        # Используем обученную модель
        seed = random.choice(list(markov.chain.keys()))
        generated = markov.generate(seed_word=seed, max_words=random.randint(8, 20))
    else:
        # Используем готовые фразы
        generated = random.choice(EXAMPLE_TEXTS.strip().split('\n'))
    
    # Стилизуем под HoFiLiOn
    response = add_hofilion_style(generated)
    
    # Если сообщение слишком короткое или пустое — добавляем эмоцию
    if len(response) < 10:
        response = f"{response} {random.choice(HOFILION_STYLE['эмодзи'])}"
    
    await update.message.reply_text(response)

async def train_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для дообучения на новых текстах"""
    if context.args:
        new_text = ' '.join(context.args)
        markov.train(new_text)
        
        # Сохраняем в файл
        with open("hofilion_train.txt", "a", encoding="utf-8") as f:
            f.write(f"\n{new_text}")
        
        await update.message.reply_text("заебись, запомнил 👌")
    else:
        await update.message.reply_text("а че писать-то? дай текст, обучусь")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика модели"""
    words_count = len(markov.words)
    chains_count = len(markov.chain)
    await update.message.reply_text(
        f"статистика:\n"
        f"- слов в словаре: {words_count}\n"
        f"- цепочек переходов: {chains_count}\n"
        f"- стиль: хойлион-кор 🤘"
    )

# ========== ЗАПУСК ==========
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("train", train_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("бот на хуях работает 🤘")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()