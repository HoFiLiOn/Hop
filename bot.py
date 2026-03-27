import telebot
from telebot import types
import json
import os
import random
from datetime import datetime

# ========== КОНФИГ ==========
TOKEN = "8027822584:AAGesipnTcDYELUWoUDTyS4eeT2o88zooqI"
ADMIN_ID = 8388843828

bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

# ========== ФАЙЛЫ ==========
SIGNATURES_FILE = "signatures.json"
BANNED_USERS_FILE = "banned_users.json"
POSTS_FILE = "posts.json"

def init_files():
    for f in [SIGNATURES_FILE, BANNED_USERS_FILE, POSTS_FILE]:
        if not os.path.exists(f):
            with open(f, 'w', encoding='utf-8') as file:
                json.dump({} if f != POSTS_FILE else [], file, ensure_ascii=False)

init_files()

def load_data(file):
    with open(file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ========== ПЕТИЦИИ ==========
def get_signatures():
    return load_data(SIGNATURES_FILE)

def add_signature(user_id, username, first_name):
    sigs = get_signatures()
    if str(user_id) not in sigs:
        sigs[str(user_id)] = {
            'username': username,
            'first_name': first_name,
            'date': str(datetime.now())
        }
        save_data(SIGNATURES_FILE, sigs)
        return True
    return False

def get_signature_count():
    return len(get_signatures())

# ========== БАНЫ ==========
def is_banned(user_id):
    banned = load_data(BANNED_USERS_FILE)
    return str(user_id) in banned

def ban_user(user_id, reason="Нарушение правил"):
    banned = load_data(BANNED_USERS_FILE)
    banned[str(user_id)] = {'reason': reason, 'date': str(datetime.now())}
    save_data(BANNED_USERS_FILE, banned)

def unban_user(user_id):
    banned = load_data(BANNED_USERS_FILE)
    if str(user_id) in banned:
        del banned[str(user_id)]
        save_data(BANNED_USERS_FILE, banned)

# ========== ЛЕНТА ==========
def get_posts():
    return load_data(POSTS_FILE)

def add_post(user_id, username, first_name, text):
    posts = get_posts()
    posts.insert(0, {
        'id': len(posts) + 1 if posts else 1,
        'user_id': user_id,
        'username': username,
        'first_name': first_name,
        'text': text,
        'date': str(datetime.now()),
        'likes': 0,
        'liked_by': []
    })
    save_data(POSTS_FILE, posts)

def like_post(post_id, user_id):
    posts = get_posts()
    for post in posts:
        if post['id'] == post_id:
            if user_id not in post['liked_by']:
                post['likes'] += 1
                post['liked_by'].append(user_id)
                save_data(POSTS_FILE, posts)
                return True
            else:
                return False
    return False

def delete_post(post_id):
    posts = get_posts()
    for i, post in enumerate(posts):
        if post['id'] == post_id:
            posts.pop(i)
            save_data(POSTS_FILE, posts)
            return True
    return False

# ========== КЛАВИАТУРЫ ==========
def main_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📝 Подписать петицию", callback_data="sign"),
        types.InlineKeyboardButton("📢 Лента обращений", callback_data="feed"),
        types.InlineKeyboardButton("✍️ Написать обращение", callback_data="write"),
        types.InlineKeyboardButton("⚠️ Проверить статус", callback_data="status"),
        types.InlineKeyboardButton("📊 Статистика", callback_data="stats")
    )
    return kb

def admin_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🚫 Забанить", callback_data="admin_ban"),
        types.InlineKeyboardButton("✅ Разбанить", callback_data="admin_unban"),
        types.InlineKeyboardButton("📝 Список подписавших", callback_data="admin_signatures"),
        types.InlineKeyboardButton("🗑️ Удалить пост", callback_data="admin_delete_post"),
        types.InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")
    )
    return kb

def back_keyboard():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main"))
    return kb

# ========== ТЕКСТЫ ==========
START_TEXT = """
𝗔⃞+ <b>Роскомнадзор — Центр управления цифровым надзором</b>

Добро пожаловать в официальный бот РКН!

<b>Доступные функции:</b>
📝 Подписать петицию — поддержать замедление соцсетей
📢 Лента обращений — посмотреть что пишут граждане
✍️ Написать обращение — оставить пост в ленте
⚠️ Проверить статус — узнать, не заблокированы ли вы
📊 Статистика — количество подписей

<i>Внимание! Бот ведет мониторинг активности.</i>
"""

HELP_TEXT = """
𝗔⃞+ <b>Помощь по боту</b>

<b>Команды:</b>
/start — главное меню
/help — эта справка
/sign — подписать петицию
/feed — лента обращений
/post [текст] — оставить обращение
/status — проверить статус
/stats — статистика подписей

<b>Кнопки в меню:</b>
📝 Подписать петицию — добавить свою подпись
📢 Лента — посмотреть обращения других
✍️ Написать — создать новое обращение
⚠️ Статус — проверить блокировку
📊 Статистика — количество подписей
"""

# ========== КОМАНДЫ ==========
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    
    if is_banned(user_id):
        bot.send_message(user_id, "🚫 <b>Вы заблокированы Роскомнадзором</b>\n\nПричина: нарушение правил цифрового этикета.", parse_mode='HTML')
        return
    
    text = START_TEXT
    bot.send_message(user_id, text, parse_mode='HTML', reply_markup=main_keyboard())

@bot.message_handler(commands=['help'])
def help_cmd(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.send_message(user_id, "🚫 Вы заблокированы.")
        return
    bot.send_message(user_id, HELP_TEXT, parse_mode='HTML', reply_markup=back_keyboard())

@bot.message_handler(commands=['sign'])
def sign_cmd(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.send_message(user_id, "🚫 Вы заблокированы.")
        return
    
    username = message.from_user.username or message.from_user.first_name
    first_name = message.from_user.first_name
    
    if add_signature(user_id, username, first_name):
        count = get_signature_count()
        text = f"✅ <b>Подпись принята!</b>\n\nСпасибо за поддержку замедления социальных сетей.\n\n📊 Всего подписей: <b>{count}</b>\n\n⚠️ Ваш трафик замедлен на 0.01% в знак солидарности."
        bot.send_message(user_id, text, parse_mode='HTML', reply_markup=back_keyboard())
    else:
        bot.send_message(user_id, "❌ Вы уже подписывали петицию.\n\nСпасибо за поддержку!", parse_mode='HTML', reply_markup=back_keyboard())

@bot.message_handler(commands=['status'])
def status_cmd(message):
    user_id = message.from_user.id
    
    if is_banned(user_id):
        text = "🚫 <b>СТАТУС: ЗАБЛОКИРОВАН</b>\n\nПричина: нарушение правил использования информационных ресурсов.\n\nДля разблокировки обратитесь в поддержку."
        bot.send_message(user_id, text, parse_mode='HTML', reply_markup=back_keyboard())
    else:
        sigs = get_signatures()
        if str(user_id) in sigs:
            text = "✅ <b>СТАТУС: НОРМАЛЕН</b>\n\nВы подписали петицию о замедлении соцсетей.\nВаш трафик обрабатывается в штатном режиме."
        else:
            text = "⚠️ <b>СТАТУС: ПОД НАБЛЮДЕНИЕМ</b>\n\nВы еще не подписали петицию. Рекомендуем поддержать инициативу."
        bot.send_message(user_id, text, parse_mode='HTML', reply_markup=back_keyboard())

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.send_message(user_id, "🚫 Вы заблокированы.")
        return
    
    count = get_signature_count()
    posts_count = len(get_posts())
    text = f"📊 <b>Статистика РКН</b>\n\n📝 Подписей под петицией: <b>{count}</b>\n📢 Обращений в ленте: <b>{posts_count}</b>\n🚫 Заблокировано пользователей: <b>{len(load_data(BANNED_USERS_FILE))}</b>\n\n<i>Актуально на {datetime.now().strftime('%d.%m.%Y %H:%M')}</i>"
    bot.send_message(user_id, text, parse_mode='HTML', reply_markup=back_keyboard())

@bot.message_handler(commands=['feed'])
def feed_cmd(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.send_message(user_id, "🚫 Вы заблокированы.")
        return
    
    posts = get_posts()
    if not posts:
        bot.send_message(user_id, "📢 <b>Лента обращений пуста</b>\n\nБудьте первым, кто оставит обращение!\nИспользуйте /post [текст]", parse_mode='HTML', reply_markup=back_keyboard())
        return
    
    kb = types.InlineKeyboardMarkup(row_width=2)
    for post in posts[:10]:
        name = post['first_name'][:15] if post['first_name'] else post['username'] or "Аноним"
        kb.add(types.InlineKeyboardButton(f"❤️ {post['likes']} | {name}", callback_data=f"view_{post['id']}"))
    kb.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main"))
    
    bot.send_message(user_id, "📢 <b>Лента обращений</b>\n\nНажмите на обращение, чтобы прочитать:", parse_mode='HTML', reply_markup=kb)

@bot.message_handler(commands=['post'])
def post_cmd(message):
    user_id = message.from_user.id
    
    if is_banned(user_id):
        bot.send_message(user_id, "🚫 Вы заблокированы и не можете оставлять обращения.")
        return
    
    text = message.text.replace('/post', '', 1).strip()
    if not text:
        bot.send_message(user_id, "✍️ <b>Написать обращение</b>\n\nОтправьте текст обращения после команды:\n<code>/post Ваше обращение</code>\n\nМаксимум 500 символов.", parse_mode='HTML')
        return
    
    if len(text) > 500:
        bot.send_message(user_id, "❌ Слишком длинное обращение. Максимум 500 символов.")
        return
    
    username = message.from_user.username or message.from_user.first_name
    first_name = message.from_user.first_name
    
    add_post(user_id, username, first_name, text)
    bot.send_message(user_id, "✅ <b>Обращение опубликовано!</b>\n\nВаше обращение добавлено в ленту.", parse_mode='HTML', reply_markup=back_keyboard())

@bot.message_handler(commands=['admin'])
def admin_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Недостаточно прав.")
        return
    
    text = "🔧 <b>Админ-панель РКН</b>\n\nВыберите действие:"
    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=admin_keyboard())

# ========== КОЛБЭКИ ==========
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    data = call.data
    
    # Проверка бана для основных действий
    if data not in ["admin_ban", "admin_unban", "admin_signatures", "admin_delete_post", "admin_stats", "back_to_main"]:
        if is_banned(user_id) and data != "status":
            bot.answer_callback_query(call.id, "🚫 Вы заблокированы!", show_alert=True)
            return
    
    # Главное меню
    if data == "back_to_main":
        bot.edit_message_text(START_TEXT, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=main_keyboard())
        bot.answer_callback_query(call.id)
        return
    
    # Подпись
    if data == "sign":
        username = call.from_user.username or call.from_user.first_name
        first_name = call.from_user.first_name
        
        if add_signature(user_id, username, first_name):
            count = get_signature_count()
            text = f"✅ <b>Подпись принята!</b>\n\nСпасибо за поддержку замедления социальных сетей.\n\n📊 Всего подписей: <b>{count}</b>\n\n⚠️ Ваш трафик замедлен на 0.01% в знак солидарности."
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=back_keyboard())
        else:
            bot.answer_callback_query(call.id, "Вы уже подписали петицию!", show_alert=True)
        return
    
    # Статус
    if data == "status":
        if is_banned(user_id):
            text = "🚫 <b>СТАТУС: ЗАБЛОКИРОВАН</b>\n\nПричина: нарушение правил использования информационных ресурсов."
        else:
            sigs = get_signatures()
            if str(user_id) in sigs:
                text = "✅ <b>СТАТУС: НОРМАЛЕН</b>\n\nВы подписали петицию о замедлении соцсетей."
            else:
                text = "⚠️ <b>СТАТУС: ПОД НАБЛЮДЕНИЕМ</b>\n\nВы еще не подписали петицию."
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=back_keyboard())
        bot.answer_callback_query(call.id)
        return
    
    # Статистика
    if data == "stats":
        count = get_signature_count()
        posts_count = len(get_posts())
        text = f"📊 <b>Статистика РКН</b>\n\n📝 Подписей: <b>{count}</b>\n📢 Обращений: <b>{posts_count}</b>\n🚫 Заблокировано: <b>{len(load_data(BANNED_USERS_FILE))}</b>"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=back_keyboard())
        bot.answer_callback_query(call.id)
        return
    
    # Лента
    if data == "feed":
        posts = get_posts()
        if not posts:
            text = "📢 <b>Лента обращений пуста</b>"
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=back_keyboard())
        else:
            kb = types.InlineKeyboardMarkup(row_width=2)
            for post in posts[:10]:
                name = post['first_name'][:15] if post['first_name'] else post['username'] or "Аноним"
                kb.add(types.InlineKeyboardButton(f"❤️ {post['likes']} | {name}", callback_data=f"view_{post['id']}"))
            kb.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main"))
            bot.edit_message_text("📢 <b>Лента обращений</b>\n\nНажмите на обращение:", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=kb)
        bot.answer_callback_query(call.id)
        return
    
    # Написать обращение
    if data == "write":
        bot.edit_message_text("✍️ <b>Написать обращение</b>\n\nОтправьте текст командой:\n<code>/post Ваше обращение</code>\n\nМаксимум 500 символов.", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=back_keyboard())
        bot.answer_callback_query(call.id)
        return
    
    # Просмотр поста
    if data.startswith("view_"):
        post_id = int(data[5:])
        posts = get_posts()
        post = None
        for p in posts:
            if p['id'] == post_id:
                post = p
                break
        
        if post:
            name = post['first_name'] or post['username'] or "Аноним"
            text = f"📢 <b>Обращение #{post['id']}</b>\n\n👤 <b>{name}</b>\n📅 {post['date'][:19]}\n\n{post['text']}\n\n❤️ Лайков: {post['likes']}"
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton(f"❤️ Лайк ({post['likes']})", callback_data=f"like_{post_id}"))
            kb.add(types.InlineKeyboardButton("◀️ Назад", callback_data="feed"))
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=kb)
        else:
            bot.answer_callback_query(call.id, "Пост не найден")
        return
    
    # Лайк
    if data.startswith("like_"):
        post_id = int(data[5:])
        if like_post(post_id, user_id):
            bot.answer_callback_query(call.id, "❤️ Лайк поставлен!")
            # Обновляем просмотр
            posts = get_posts()
            post = None
            for p in posts:
                if p['id'] == post_id:
                    post = p
                    break
            if post:
                name = post['first_name'] or post['username'] or "Аноним"
                text = f"📢 <b>Обращение #{post['id']}</b>\n\n👤 <b>{name}</b>\n📅 {post['date'][:19]}\n\n{post['text']}\n\n❤️ Лайков: {post['likes']}"
                kb = types.InlineKeyboardMarkup()
                kb.add(types.InlineKeyboardButton(f"❤️ Лайк ({post['likes']})", callback_data=f"like_{post_id}"))
                kb.add(types.InlineKeyboardButton("◀️ Назад", callback_data="feed"))
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=kb)
        else:
            bot.answer_callback_query(call.id, "Вы уже лайкнули этот пост!", show_alert=True)
        return
    
    # ========== АДМИН-КОЛБЭКИ ==========
    if data == "admin_ban":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Недостаточно прав")
            return
        bot.send_message(ADMIN_ID, "🚫 Введите ID пользователя для блокировки:\nПример: 123456789")
        bot.register_next_step_handler(call.message, ban_user_step)
        bot.answer_callback_query(call.id)
        return
    
    if data == "admin_unban":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Недостаточно прав")
            return
        bot.send_message(ADMIN_ID, "✅ Введите ID пользователя для разблокировки:")
        bot.register_next_step_handler(call.message, unban_user_step)
        bot.answer_callback_query(call.id)
        return
    
    if data == "admin_signatures":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Недостаточно прав")
            return
        sigs = get_signatures()
        if not sigs:
            bot.send_message(ADMIN_ID, "📝 Нет подписей.")
        else:
            text = "📝 <b>Список подписавших петицию:</b>\n\n"
            for uid, data in list(sigs.items())[:50]:
                text += f"• {data['first_name']} (@{data['username']}) — ID: {uid}\n"
            bot.send_message(ADMIN_ID, text, parse_mode='HTML')
        bot.answer_callback_query(call.id)
        return
    
    if data == "admin_delete_post":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Недостаточно прав")
            return
        posts = get_posts()
        if not posts:
            bot.send_message(ADMIN_ID, "📢 Нет постов для удаления.")
        else:
            kb = types.InlineKeyboardMarkup(row_width=1)
            for post in posts[:20]:
                name = post['first_name'] or post['username'] or "Аноним"
                kb.add(types.InlineKeyboardButton(f"#{post['id']} | {name}", callback_data=f"delpost_{post['id']}"))
            kb.add(types.InlineKeyboardButton("◀️ Назад", callback_data="admin_panel"))
            bot.edit_message_text("🗑️ <b>Выберите пост для удаления:</b>", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=kb)
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("delpost_"):
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Недостаточно прав")
            return
        post_id = int(data[8:])
        if delete_post(post_id):
            bot.answer_callback_query(call.id, "✅ Пост удален!")
            # Обновляем админ-панель
            text = "🔧 <b>Админ-панель РКН</b>\n\nВыберите действие:"
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=admin_keyboard())
        else:
            bot.answer_callback_query(call.id, "❌ Пост не найден")
        return
    
    if data == "admin_stats":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Недостаточно прав")
            return
        count = get_signature_count()
        posts_count = len(get_posts())
        banned_count = len(load_data(BANNED_USERS_FILE))
        text = f"📊 <b>Полная статистика РКН</b>\n\n📝 Подписей: {count}\n📢 Обращений: {posts_count}\n🚫 Заблокировано: {banned_count}\n\n👥 Всего пользователей в БД: {len([f for f in os.listdir('.') if f == SIGNATURES_FILE])}"
        bot.send_message(ADMIN_ID, text, parse_mode='HTML')
        bot.answer_callback_query(call.id)
        return
    
    if data == "admin_panel":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Недостаточно прав")
            return
        text = "🔧 <b>Админ-панель РКН</b>\n\nВыберите действие:"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=admin_keyboard())
        bot.answer_callback_query(call.id)
        return

# ========== ШАГИ ДЛЯ АДМИНА ==========
def ban_user_step(message):
    try:
        user_id = int(message.text.strip())
        ban_user(user_id)
        bot.send_message(ADMIN_ID, f"✅ Пользователь {user_id} заблокирован!")
        try:
            bot.send_message(user_id, "🚫 <b>Вас заблокировал Роскомнадзор</b>\n\nПричина: нарушение правил цифрового этикета.", parse_mode='HTML')
        except:
            pass
    except:
        bot.send_message(ADMIN_ID, "❌ Неверный ID")

def unban_user_step(message):
    try:
        user_id = int(message.text.strip())
        unban_user(user_id)
        bot.send_message(ADMIN_ID, f"✅ Пользователь {user_id} разблокирован!")
        try:
            bot.send_message(user_id, "✅ <b>Вы разблокированы Роскомнадзором</b>\n\nВаш доступ восстановлен.", parse_mode='HTML')
        except:
            pass
    except:
        bot.send_message(ADMIN_ID, "❌ Неверный ID")

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("🤖 РКН Бот запущен!")
    print(f"👑 Админ ID: {ADMIN_ID}")
    print("✅ Бот готов к работе")
    bot.infinity_polling()