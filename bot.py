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

# ========== ИМПОРТ QWEN (локальная нейросеть) ==========
# Установка: pip install transformers torch accelerate
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    QWEN_AVAILABLE = True
except ImportError:
    print("⚠️ Установи transformers: pip install transformers torch accelerate")
    QWEN_AVAILABLE = False

# ========== ЗАГРУЗКА QWEN ==========
class QwenChat:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_model(self):
        """Загружаем Qwen2.5-0.5B (лёгкая версия)"""
        if not QWEN_AVAILABLE:
            return False
        
        try:
            print(f"🚀 Загружаю Qwen на {self.device}...")
            model_name = "Qwen/Qwen2.5-0.5B-Instruct"
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto",
                trust_remote_code=True
            )
            print("✅ Qwen загружена!")
            return True
        except Exception as e:
            print(f"❌ Ошибка загрузки Qwen: {e}")
            return False
    
    def generate_hofilion_style(self, user_input="", max_length=150):
        """Генерирует ответ в стиле HoFiLiOn"""
        if self.model is None:
            return self._fallback_response(user_input)
        
        # Промт для стиля HoFiLiOn
        system_prompt = """Ты HoFiLiOn. Пиши как он: с матом, сленгом, эмоционально. 
Короткие и длинные фразы. Эмодзи. Без цензуры. От первого лица.
Примеры:
- "ебаный рот, ну и что за нахуй тут происходит"
- "ааа, вот оно че, бля, даже не ожидал такого"
- "ну ладно, посмотрим что дальше, хз че там будет"
- "короче, пиздец полный, я в ахуе"
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input if user_input else "ну че, как дела?"}
        ]
        
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        inputs = self.tokenizer([text], return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_length,
                temperature=0.9,
                top_p=0.95,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        
        # Чистим ответ
        response = response.strip()
        if not response:
            response = self._fallback_response(user_input)
        
        return response
    
    def _fallback_response(self, user_input=""):
        """Фолбэк если Qwen не загрузилась"""
        fallbacks = [
            "ебаный рот, че за нахуй тут происходит 🤘",
            "ну хз, кароче, я хз",
            "бля, чет я завис, повтори",
            "ахахах, заебись короче",
            "пиздец, не знаю че сказать"
        ]
        return random.choice(fallbacks)

# ========== ЦЕПЬ МАРКОВА (для фолбэка) ==========
class MarkovChain:
    def __init__(self):
        self.chain = defaultdict(list)
        self.words = []
    
    def train(self, text):
        sentences = re.split(r'[.!?…]+', text)
        for sentence in sentences:
            words = sentence.strip().split()
            if len(words) < 2:
                continue
            for i in range(len(words) - 1):
                self.chain[words[i]].append(words[i + 1])
                self.words.append(words[i])
    
    def train_from_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            self.train(f.read())
    
    def generate(self, max_words=15):
        if not self.chain:
            return "пока не обучен 🤷"
        seed = random.choice(list(self.chain.keys()))
        result = [seed]
        current = seed
        for _ in range(max_words - 1):
            if current not in self.chain:
                break
            next_word = random.choice(self.chain[current])
            result.append(next_word)
            current = next_word
        return ' '.join(result)

# ========== БАЗА СТИЛЯ ==========
HOFILION_EMOJI = ["😂", "🤣", "😈", "🔥", "💀", "🤡", "👀", "😏", "🤷", "🙄", "😎", "🤘"]

def style_response(text):
    """Доводим ответ до стиля HoFiLiOn"""
    if not text:
        return "ну хз 🤷"
    
    # Добавляем эмодзи если нет
    if not any(emoji in text for emoji in HOFILION_EMOJI):
        if random.random() > 0.5:
            text = f"{text} {random.choice(HOFILION_EMOJI)}"
    
    # Делаем нижний регистр для аутентичности (кроме эмоций)
    text = text.lower()
    
    return text

# ========== ИНИЦИАЛИЗАЦИЯ ==========
qwen = QwenChat()
markov = MarkovChain()

# Обучаем цепь Маркова на примерах
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
"""
markov.train(EXAMPLE_TEXTS)

# ========== ОБРАБОТЧИКИ ==========
logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ну че, заебись, работаю на Qwen 🤘")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    # Пытаемся использовать Qwen
    try:
        if qwen.model is None:
            # Загружаем модель при первом сообщении
            if not qwen.load_model():
                # Если не загрузилась — используем цепь Маркова
                response = markov.generate()
            else:
                response = qwen.generate_hofilion_style(user_message)
        else:
            response = qwen.generate_hofilion_style(user_message)
    except Exception as e:
        print(f"Ошибка Qwen: {e}")
        response = markov.generate()
    
    # Стилизуем ответ
    response = style_response(response)
    
    await update.message.reply_text(response)

async def qwen_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Принудительно используем Qwen"""
    user_message = ' '.join(context.args) if context.args else "расскажи что-нибудь"
    
    if qwen.model is None:
        if not qwen.load_model():
            await update.message.reply_text("Qwen не загрузилась, чет пошло не так 🤷")
            return
    
    response = qwen.generate_hofilion_style(user_message)
    response = style_response(response)
    await update.message.reply_text(response)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статус"""
    qwen_status = "✅ загружена" if qwen.model else "❌ не загружена"
    await update.message.reply_text(
        f"🤘 HoFiLiOn Bot\n"
        f"Qwen: {qwen_status}\n"
        f"Цепь Маркова: {len(markov.chain)} цепочек\n"
        f"Работает на {qwen.device if qwen.model else 'cpu'}"
    )

# ========== ЗАПУСК ==========
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("qwen", qwen_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤘 HoFiLiOn Bot запущен на Qwen!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()