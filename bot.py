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
BLOCKED_SITES_FILE = "blocked_sites.json"
SUPPORT_FILE = "support_tickets.json"
SETTINGS_FILE = "settings.json"

# ========== НАСТРОЙКИ ==========
DEFAULT_SETTINGS = {
    'target_signatures': 1000,
    'blocking_started': False,
    'blocking_announced': False
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

# ========== ИНИЦИАЛИЗАЦИЯ ==========
def init_files():
    for f in [SIGNATURES_FILE, BANNED_USERS_FILE, BLOCKED_SITES_FILE, SUPPORT_FILE]:
        if not os.path.exists(f):
            with open(f, 'w', encoding='utf-8') as file:
                json.dump({}, file, ensure_ascii=False)
    if not os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, 'w', encoding='utf-8') as file:
            json.dump([], file, ensure_ascii=False)
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)

init_files()

# ========== РАБОТА С ДАННЫМИ ==========
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
        check_target_reached()
        return True
    return False

def get_signature_count():
    return len(get_signatures())

def get_remaining_signatures():
    settings = load_settings()
    target = settings.get('target_signatures', 1000)
    current = get_signature_count()
    return max(0, target - current)

def check_target_reached():
    settings = load_settings()
    target = settings.get('target_signatures', 1000)
    current = get_signature_count()
    
    if current >= target and not settings.get('blocking_started', False):
        settings['blocking_started'] = True
        save_settings(settings)
        notify_all_users_about_target()
        return True
    return False

def notify_all_users_about_target():
    sigs = get_signatures()
    text = """<b>© Роскомнадзор</b>

<b>ОФИЦИАЛЬНОЕ УВЕДОМЛЕНИЕ</b>

Целевой показатель в <b>1000 подписей</b> достигнут.

В соответствии с принятой программой цифрового надзора, <b>© Роскомнадзор</b> инициирует мероприятия по ограничению доступа к информационным ресурсам.

<b>Блокировка начинается.</b>

—
<i>Цифровой контроль. Законность. Порядок.</i>"""

    for user_id in sigs.keys():
        try:
            bot.send_message(int(user_id), text, parse_mode='HTML')
        except:
            pass

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

# ========== БЛОКИРОВКИ ==========
SITES_LIST = [
    {'name': 'Telegram', 'emoji': '📱'},
    {'name': 'YouTube', 'emoji': '📺'},
    {'name': 'Instagram', 'emoji': '📸'},
    {'name': 'TikTok', 'emoji': '🎵'},
    {'name': 'Facebook', 'emoji': '📘'},
    {'name': 'WhatsApp', 'emoji': '💬'},
    {'name': 'X (Twitter)', 'emoji': '🐦'},
]

def get_blocked_sites():
    return load_data(BLOCKED_SITES_FILE)

def block_site(site_name):
    blocked = get_blocked_sites()
    if site_name not in blocked:
        blocked[site_name] = {
            'date': str(datetime.now()),
            'reason': 'По результатам сбора подписей граждан'
        }
        save_data(BLOCKED_SITES_FILE, blocked)
        return True
    return False

def is_blocking_started():
    settings = load_settings()
    return settings.get('blocking_started', False)

# ========== ПОДДЕРЖКА (СВЯЗЬ С РКН) ==========
def get_tickets():
    return load_data(SUPPORT_FILE)

def create_ticket(user_id, username, first_name, message):
    tickets = get_tickets()
    uid = str(user_id)
    
    if uid not in tickets:
        tickets[uid] = {
            'user_id': user_id,
            'username': username,
            'first_name': first_name,
            'tickets': []
        }
    
    ticket_id = len(tickets[uid]['tickets']) + 1
    
    tickets[uid]['tickets'].append({
        'id': ticket_id,
        'message': message,
        'date': str(datetime.now()),
        'status': 'open',
        'admin_response': None,
        'response_date': None
    })
    
    save_data(SUPPORT_FILE, tickets)
    return ticket_id

def add_response(user_id, ticket_id, response):
    tickets = get_tickets()
    uid = str(user_id)
    
    if uid in tickets:
        for ticket in tickets[uid]['tickets']:
            if ticket['id'] == ticket_id:
                ticket['admin_response'] = response
                ticket['response_date'] = str(datetime.now())
                ticket['status'] = 'closed'
                save_data(SUPPORT_FILE, tickets)
                return True
    return False

def get_user_tickets(user_id):
    tickets = get_tickets()
    uid = str(user_id)
    if uid in tickets:
        return tickets[uid]['tickets']
    return []

# ========== КЛАВИАТУРЫ ==========
def main_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)
    
    kb.add(
        types.InlineKeyboardButton("📝 Подписать петицию", callback_data="sign"),
        types.InlineKeyboardButton("📢 Лента обращений", callback_data="feed"),
        types.InlineKeyboardButton("✍️ Написать обращение", callback_data="write"),
        types.InlineKeyboardButton("⚠️ Проверить статус", callback_data="status"),
        types.InlineKeyboardButton("📊 Статистика", callback_data="stats"),
        types.InlineKeyboardButton("📞 Связь с РКН", callback_data="support")
    )
    
    if is_blocking_started():
        kb.add(types.InlineKeyboardButton("🔒 Начать блокировку", callback_data="blocking_menu"))
    
    return kb

def support_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("📝 Новое обращение", callback_data="new_ticket"),
        types.InlineKeyboardButton("📋 Мои обращения", callback_data="my_tickets"),
        types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")
    )
    return kb

def tickets_list_keyboard(user_id):
    tickets = get_user_tickets(user_id)
    kb = types.InlineKeyboardMarkup(row_width=1)
    
    for ticket in tickets[-5:]:
        status_emoji = "✅" if ticket['status'] == 'closed' else "🟡"
        kb.add(types.InlineKeyboardButton(
            f"{status_emoji} Обращение #{ticket['id']} ({ticket['date'][:10]})",
            callback_data=f"ticket_{ticket['id']}"
        ))
    
    kb.add(types.InlineKeyboardButton("◀️ Назад", callback_data="support"))
    return kb

def blocking_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=1)
    
    blocked = get_blocked_sites()
    
    for site in SITES_LIST:
        if site['name'] in blocked:
            status = "✅ ЗАБЛОКИРОВАНО"
        else:
            status = "⬜ ДОСТУПНО"
        kb.add(types.InlineKeyboardButton(
            f"{site['emoji']} {site['name']} — {status}",
            callback_data=f"block_{site['name']}"
        ))
    
    kb.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main"))
    return kb

def admin_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🚫 Забанить", callback_data="admin_ban"),
        types.InlineKeyboardButton("✅ Разбанить", callback_data="admin_unban"),
        types.InlineKeyboardButton("📝 Список подписавших", callback_data="admin_signatures"),
        types.InlineKeyboardButton("🗑️ Удалить пост", callback_data="admin_delete_post"),
        types.InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        types.InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast"),
        types.InlineKeyboardButton("🎯 Сбросить цель", callback_data="admin_reset_target"),
        types.InlineKeyboardButton("📞 Ответить на обращение", callback_data="admin_support"),
        types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")
    )
    return kb

def back_keyboard():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main"))
    return kb

# ========== ТЕКСТЫ ==========
START_TEXT = """
© <b>Роскомнадзор</b>
<b>Центр управления цифровым надзором</b>

Добро пожаловать в официальный Telegram-бот © РКН.

<b>Функциональные возможности:</b>
📝 Подписать петицию — поддержать инициативы по регулированию
📢 Лента обращений — публичное пространство для заявлений
✍️ Написать обращение — направить сообщение в адрес © РКН
⚠️ Проверить статус — информация о наличии ограничений
📊 Статистика — актуальные данные о подписях
📞 Связь с РКН — задать вопрос или оставить обращение

<i>Цифровой контроль. Законность. Порядок.</i>
"""

STATS_TEXT = """
© <b>Роскомнадзор</b>
<b>СТАТИСТИКА ПОДПИСЕЙ</b>

📝 <b>Всего подписей:</b> <code>{signatures}</code>
🎯 <b>Целевой показатель:</b> <code>{target}</code>
📊 <b>Осталось до блокировок:</b> <code>{remaining}</code>

<b>Статус программы блокировок:</b>
{blocking_status}

<i>При достижении 1000 подписей будут инициированы мероприятия по ограничению доступа к информационным ресурсам.</i>
"""

# ========== КОМАНДЫ ==========
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    
    if is_banned(user_id):
        bot.send_message(user_id, "🚫 <b>Доступ ограничен</b>\n\nВаш аккаунт внесен в список лиц, в отношении которых применяются меры цифрового контроля.", parse_mode='HTML')
        return
    
    bot.send_message(user_id, START_TEXT, parse_mode='HTML', reply_markup=main_keyboard())

@bot.message_handler(commands=['help'])
def help_cmd(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.send_message(user_id, "🚫 Доступ ограничен.")
        return
    
    text = """
© <b>Роскомнадзор</b>
<b>СПРАВОЧНАЯ ИНФОРМАЦИЯ</b>

<b>Команды:</b>
/start — главное меню
/help — настоящая справка
/sign — подписать петицию
/feed — лента обращений
/post [текст] — оставить обращение
/status — проверить статус
/stats — статистика подписей

<i>© Роскомнадзор. Все права защищены.</i>
"""
    bot.send_message(user_id, text, parse_mode='HTML', reply_markup=back_keyboard())

@bot.message_handler(commands=['sign'])
def sign_cmd(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.send_message(user_id, "🚫 Доступ ограничен.")
        return
    
    username = message.from_user.username or message.from_user.first_name
    first_name = message.from_user.first_name
    
    if add_signature(user_id, username, first_name):
        count = get_signature_count()
        remaining = get_remaining_signatures()
        
        text = f"""
✅ <b>Подпись принята</b>

<b>© Роскомнадзор</b> подтверждает включение вашей подписи в реестр граждан, поддержавших инициативу.

<b>Текущая статистика:</b>
📝 Всего подписей: <code>{count}</code>
🎯 До целевого показателя: <code>{remaining}</code>

<i>При достижении 1000 подписей будут инициированы мероприятия по ограничению доступа.</i>
"""
        bot.send_message(user_id, text, parse_mode='HTML', reply_markup=back_keyboard())
    else:
        bot.send_message(user_id, "❌ <b>Ошибка регистрации</b>\n\nВаша подпись уже присутствует в реестре.", parse_mode='HTML', reply_markup=back_keyboard())

@bot.message_handler(commands=['status'])
def status_cmd(message):
    user_id = message.from_user.id
    
    if is_banned(user_id):
        text = "🚫 <b>СТАТУС: ОГРАНИЧЕН</b>\n\nВ отношении вашего аккаунта применяются меры цифрового контроля."
        bot.send_message(user_id, text, parse_mode='HTML', reply_markup=back_keyboard())
    else:
        sigs = get_signatures()
        if str(user_id) in sigs:
            text = f"✅ <b>СТАТУС: НОРМАЛЕН</b>\n\nПодпись в реестре: {sigs[str(user_id)]['date'][:19]}"
        else:
            text = "⚠️ <b>СТАТУС: ПОД НАБЛЮДЕНИЕМ</b>\n\nРекомендуется подписать петицию."
        bot.send_message(user_id, text, parse_mode='HTML', reply_markup=back_keyboard())

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.send_message(user_id, "🚫 Доступ ограничен.")
        return
    
    count = get_signature_count()
    target = load_settings().get('target_signatures', 1000)
    remaining = get_remaining_signatures()
    blocking_started = is_blocking_started()
    
    if blocking_started:
        blocking_status = "🔴 <b>АКТИВИРОВАНА</b> — мероприятия проводятся"
    else:
        blocking_status = f"⚪ <b>ОЖИДАНИЕ</b> — осталось {remaining} подписей"
    
    text = STATS_TEXT.format(
        signatures=count,
        target=target,
        remaining=remaining,
        blocking_status=blocking_status
    )
    bot.send_message(user_id, text, parse_mode='HTML', reply_markup=back_keyboard())

@bot.message_handler(commands=['feed'])
def feed_cmd(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.send_message(user_id, "🚫 Доступ ограничен.")
        return
    
    posts = get_posts()
    if not posts:
        text = "📢 <b>ЛЕНТА ОБРАЩЕНИЙ</b>\n\nОбращения отсутствуют."
        bot.send_message(user_id, text, parse_mode='HTML', reply_markup=back_keyboard())
        return
    
    kb = types.InlineKeyboardMarkup(row_width=2)
    for post in posts[:10]:
        name = post['first_name'][:15] if post['first_name'] else post['username'] or "Аноним"
        kb.add(types.InlineKeyboardButton(f"❤️ {post['likes']} | {name}", callback_data=f"view_{post['id']}"))
    kb.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main"))
    
    bot.send_message(user_id, "📢 <b>ЛЕНТА ОБРАЩЕНИЙ</b>\n\nВыберите обращение:", parse_mode='HTML', reply_markup=kb)

@bot.message_handler(commands=['post'])
def post_cmd(message):
    user_id = message.from_user.id
    
    if is_banned(user_id):
        bot.send_message(user_id, "🚫 Доступ ограничен.")
        return
    
    text = message.text.replace('/post', '', 1).strip()
    if not text:
        text = """
✍️ <b>НАПИСАНИЕ ОБРАЩЕНИЯ</b>

Используйте формат:
<code>/post Текст обращения</code>

<b>Требования:</b>
• Максимум 500 символов
• Запрещена нецензурная лексика
"""
        bot.send_message(user_id, text, parse_mode='HTML', reply_markup=back_keyboard())
        return
    
    if len(text) > 500:
        bot.send_message(user_id, "❌ <b>Ошибка</b>\n\nПревышена максимальная длина (500 символов).", parse_mode='HTML')
        return
    
    username = message.from_user.username or message.from_user.first_name
    first_name = message.from_user.first_name
    
    add_post(user_id, username, first_name, text)
    
    text = f"""
✅ <b>ОБРАЩЕНИЕ ПРИНЯТО</b>

Ваше обращение зарегистрировано.

<b>Номер регистрации:</b> #{len(get_posts())}

<i>© Роскомнадзор. Все обращения подлежат обязательному рассмотрению.</i>
"""
    bot.send_message(user_id, text, parse_mode='HTML', reply_markup=back_keyboard())

@bot.message_handler(commands=['admin'])
def admin_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ <b>Ошибка авторизации</b>\n\nНедостаточно прав.", parse_mode='HTML')
        return
    
    text = "🔧 <b>ПАНЕЛЬ УПРАВЛЕНИЯ</b>\n<i>© Роскомнадзор — Административный интерфейс</i>\n\nВыберите действие:"
    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=admin_keyboard())

# ========== ОБРАБОТКА СООБЩЕНИЙ ДЛЯ ПОДДЕРЖКИ ==========
@bot.message_handler(func=lambda message: message.from_user.id != ADMIN_ID and not message.text.startswith('/'))
def handle_support_message(message):
    """Если пользователь в режиме ожидания ответа на обращение"""
    # Проверяем, есть ли у пользователя ожидающий режим
    # Это временное решение, в реальном боте лучше использовать state machine
    pass

# ========== КОЛБЭКИ ==========
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    data = call.data
    
    # Проверка бана
    if data not in ["admin_ban", "admin_unban", "admin_signatures", "admin_delete_post", 
                    "admin_stats", "admin_broadcast", "admin_reset_target", "admin_support",
                    "back_to_main", "blocking_menu", "support", "new_ticket", "my_tickets"]:
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "🚫 Доступ ограничен", show_alert=True)
            return
    
    # Назад
    if data == "back_to_main":
        if is_banned(user_id):
            bot.edit_message_text("🚫 Доступ ограничен", call.message.chat.id, call.message.message_id)
            return
        bot.edit_message_text(START_TEXT, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=main_keyboard())
        bot.answer_callback_query(call.id)
        return
    
    # Подпись
    if data == "sign":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "🚫 Доступ ограничен", show_alert=True)
            return
        
        username = call.from_user.username or call.from_user.first_name
        first_name = call.from_user.first_name
        
        if add_signature(user_id, username, first_name):
            count = get_signature_count()
            remaining = get_remaining_signatures()
            
            text = f"""
✅ <b>Подпись принята</b>

<b>© Роскомнадзор</b> подтверждает включение вашей подписи в реестр.

<b>Текущая статистика:</b>
📝 Всего подписей: <code>{count}</code>
🎯 До целевого показателя: <code>{remaining}</code>

<i>При достижении 1000 подписей будут инициированы мероприятия по ограничению доступа.</i>
"""
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=back_keyboard())
        else:
            bot.answer_callback_query(call.id, "Ваша подпись уже присутствует в реестре", show_alert=True)
        return
    
    # Статус
    if data == "status":
        if is_banned(user_id):
            text = "🚫 <b>СТАТУС: ОГРАНИЧЕН</b>"
        else:
            sigs = get_signatures()
            if str(user_id) in sigs:
                text = f"✅ <b>СТАТУС: НОРМАЛЕН</b>\n\nПодпись в реестре: {sigs[str(user_id)]['date'][:19]}"
            else:
                text = "⚠️ <b>СТАТУС: ПОД НАБЛЮДЕНИЕМ</b>\n\nРекомендуется подписать петицию."
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=back_keyboard())
        bot.answer_callback_query(call.id)
        return
    
    # Статистика
    if data == "stats":
        count = get_signature_count()
        target = load_settings().get('target_signatures', 1000)
        remaining = get_remaining_signatures()
        blocking_started = is_blocking_started()
        
        if blocking_started:
            blocking_status = "🔴 <b>АКТИВИРОВАНА</b>"
        else:
            blocking_status = f"⚪ <b>ОЖИДАНИЕ</b> — осталось {remaining} подписей"
        
        text = STATS_TEXT.format(
            signatures=count,
            target=target,
            remaining=remaining,
            blocking_status=blocking_status
        )
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=back_keyboard())
        bot.answer_callback_query(call.id)
        return
    
    # Лента
    if data == "feed":
        posts = get_posts()
        if not posts:
            text = "📢 <b>ЛЕНТА ОБРАЩЕНИЙ</b>\n\nОбращения отсутствуют."
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=back_keyboard())
        else:
            kb = types.InlineKeyboardMarkup(row_width=2)
            for post in posts[:10]:
                name = post['first_name'][:15] or post['username'] or "Аноним"
                kb.add(types.InlineKeyboardButton(f"❤️ {post['likes']} | {name}", callback_data=f"view_{post['id']}"))
            kb.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main"))
            bot.edit_message_text("📢 <b>ЛЕНТА ОБРАЩЕНИЙ</b>\n\nВыберите обращение:", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=kb)
        bot.answer_callback_query(call.id)
        return
    
    # Написать обращение
    if data == "write":
        text = """
✍️ <b>НАПИСАНИЕ ОБРАЩЕНИЯ</b>

Используйте команду:
<code>/post Текст обращения</code>

<b>Требования:</b>
• Максимум 500 символов
• Запрещена нецензурная лексика
"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=back_keyboard())
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
            text = f"""
📢 <b>ОБРАЩЕНИЕ №{post['id']}</b>

<b>Автор:</b> {name}
<b>Дата:</b> {post['date'][:19]}

<b>Текст:</b>
{post['text']}

<b>Поддержка:</b> ❤️ {post['likes']}
"""
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton(f"❤️ Поддержать ({post['likes']})", callback_data=f"like_{post_id}"))
            kb.add(types.InlineKeyboardButton("◀️ Назад", callback_data="feed"))
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=kb)
        else:
            bot.answer_callback_query(call.id, "Обращение не найдено")
        return
    
    # Лайк
    if data.startswith("like_"):
        post_id = int(data[5:])
        if like_post(post_id, user_id):
            bot.answer_callback_query(call.id, "✅ Поддержка учтена")
            posts = get_posts()
            post = None
            for p in posts:
                if p['id'] == post_id:
                    post = p
                    break
            if post:
                name = post['first_name'] or post['username'] or "Аноним"
                text = f"""
📢 <b>ОБРАЩЕНИЕ №{post['id']}</b>

<b>Автор:</b> {name}
<b>Дата:</b> {post['date'][:19]}

<b>Текст:</b>
{post['text']}

<b>Поддержка:</b> ❤️ {post['likes']}
"""
                kb = types.InlineKeyboardMarkup()
                kb.add(types.InlineKeyboardButton(f"❤️ Поддержать ({post['likes']})", callback_data=f"like_{post_id}"))
                kb.add(types.InlineKeyboardButton("◀️ Назад", callback_data="feed"))
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=kb)
        else:
            bot.answer_callback_query(call.id, "Вы уже поддержали это обращение", show_alert=True)
        return
    
    # ========== ПОДДЕРЖКА (СВЯЗЬ С РКН) ==========
    if data == "support":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "🚫 Доступ ограничен", show_alert=True)
            return
        
        text = """
📞 <b>СВЯЗЬ С РКН</b>

Вы можете написать обращение в службу поддержки © Роскомнадзор.

<b>Доступные действия:</b>
• <b>Новое обращение</b> — задать вопрос или оставить заявление
• <b>Мои обращения</b> — просмотреть историю и ответы

<i>Среднее время ответа: до 24 часов.</i>
"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=support_keyboard())
        bot.answer_callback_query(call.id)
        return
    
    if data == "new_ticket":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "🚫 Доступ ограничен", show_alert=True)
            return
        
        bot.edit_message_text(
            "📝 <b>НОВОЕ ОБРАЩЕНИЕ</b>\n\nОтправьте текст вашего обращения одним сообщением.\n\nМаксимум 500 символов.\n\n<i>Нажмите «Отмена», чтобы вернуться назад.</i>",
            call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=back_keyboard()
        )
        bot.register_next_step_handler(call.message, process_new_ticket, user_id)
        bot.answer_callback_query(call.id)
        return
    
    if data == "my_tickets":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "🚫 Доступ ограничен", show_alert=True)
            return
        
        tickets = get_user_tickets(user_id)
        if not tickets:
            text = "📋 <b>МОИ ОБРАЩЕНИЯ</b>\n\nУ вас нет обращений в службу поддержки.\n\nИспользуйте «Новое обращение», чтобы задать вопрос."
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=back_keyboard())
        else:
            kb = tickets_list_keyboard(user_id)
            bot.edit_message_text("📋 <b>МОИ ОБРАЩЕНИЯ</b>\n\nВыберите обращение для просмотра:", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=kb)
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("ticket_"):
        ticket_id = int(data[7:])
        tickets = get_user_tickets(user_id)
        ticket = None
        for t in tickets:
            if t['id'] == ticket_id:
                ticket = t
                break
        
        if ticket:
            status_text = "✅ <b>ЗАКРЫТО</b>" if ticket['status'] == 'closed' else "🟡 <b>ОЖИДАЕТ ОТВЕТА</b>"
            
            text = f"""
📋 <b>ОБРАЩЕНИЕ #{ticket['id']}</b>

<b>Дата:</b> {ticket['date'][:19]}
<b>Статус:</b> {status_text}

<b>Ваше сообщение:</b>
{ticket['message']}
"""
            if ticket['admin_response']:
                text += f"""

<b>Ответ © РКН:</b>
{ticket['admin_response']}

<b>Дата ответа:</b> {ticket['response_date'][:19]}
"""
            else:
                text += "\n\n<i>Ответ еще не поступил. Пожалуйста, ожидайте.</i>"
            
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton("◀️ Назад", callback_data="my_tickets"))
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=kb)
        else:
            bot.answer_callback_query(call.id, "Обращение не найдено")
        return
    
    # ========== БЛОКИРОВКИ ==========
    if data == "blocking_menu":
        if not is_blocking_started():
            bot.answer_callback_query(call.id, "Программа блокировок еще не активирована", show_alert=True)
            return
        
        text = """
🔒 <b>ПРОГРАММА БЛОКИРОВОК</b>
<i>© Роскомнадзор — Управление доступом</i>

Выберите ресурс для применения мер ограничения.
"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=blocking_keyboard())
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("block_"):
        site_name = data[6:]
        
        if block_site(site_name):
            text = f"""
✅ <b>МЕРЫ ПРИНЯТЫ</b>

Доступ к ресурсу <b>{site_name}</b> ограничен на основании общественной поддержки.

<i>© Роскомнадзор. Цифровой контроль.</i>
"""
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=back_keyboard())
        else:
            bot.answer_callback_query(call.id, f"Ресурс {site_name} уже заблокирован", show_alert=True)
        return
    
    # ========== АДМИН-КОЛБЭКИ ==========
    if data == "admin_ban":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Недостаточно прав")
            return
        bot.send_message(ADMIN_ID, "🚫 Введите ID пользователя для ограничения доступа:")
        bot.register_next_step_handler(call.message, ban_user_step)
        bot.answer_callback_query(call.id)
        return
    
    if data == "admin_unban":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Недостаточно прав")
            return
        bot.send_message(ADMIN_ID, "✅ Введите ID пользователя для снятия ограничений:")
        bot.register_next_step_handler(call.message, unban_user_step)
        bot.answer_callback_query(call.id)
        return
    
    if data == "admin_signatures":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Недостаточно прав")
            return
        sigs = get_signatures()
        if not sigs:
            bot.send_message(ADMIN_ID, "📝 Реестр подписей пуст.")
        else:
            text = "📝 <b>РЕЕСТР ПОДПИСАВШИХ</b>\n\n"
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
            bot.send_message(ADMIN_ID, "📢 Обращения отсутствуют.")
        else:
            kb = types.InlineKeyboardMarkup(row_width=1)
            for post in posts[:20]:
                name = post['first_name'] or post['username'] or "Аноним"
                kb.add(types.InlineKeyboardButton(f"#{post['id']} | {name}", callback_data=f"delpost_{post['id']}"))
            kb.add(types.InlineKeyboardButton("◀️ Назад", callback_data="admin_panel"))
            bot.edit_message_text("🗑️ <b>УДАЛЕНИЕ ОБРАЩЕНИЙ</b>\n\nВыберите обращение:", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=kb)
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("delpost_"):
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Недостаточно прав")
            return
        post_id = int(data[8:])
        if delete_post(post_id):
            bot.answer_callback_query(call.id, "✅ Обращение удалено")
            text = "🔧 <b>ПАНЕЛЬ УПРАВЛЕНИЯ</b>\n\nВыберите действие:"
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=admin_keyboard())
        else:
            bot.answer_callback_query(call.id, "❌ Обращение не найдено")
        return
    
    if data == "admin_stats":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Недостаточно прав")
            return
        count = get_signature_count()
        posts_count = len(get_posts())
        banned_count = len(load_data(BANNED_USERS_FILE))
        blocked_count = len(get_blocked_sites())
        tickets_count = sum(len(t['tickets']) for t in get_tickets().values())
        settings = load_settings()
        
        text = f"""
📊 <b>СТАТИСТИКА СИСТЕМЫ</b>

<b>Подписи в реестре:</b> {count}
<b>Целевой показатель:</b> {settings.get('target_signatures', 1000)}
<b>Программа блокировок:</b> {'АКТИВНА' if settings.get('blocking_started') else 'ОЖИДАНИЕ'}
<b>Заблокировано ресурсов:</b> {blocked_count}
<b>Обращений граждан:</b> {posts_count}
<b>Обращений в поддержку:</b> {tickets_count}
<b>Ограниченных аккаунтов:</b> {banned_count}

<i>Данные актуальны на {datetime.now().strftime('%d.%m.%Y %H:%M')}</i>
"""
        bot.send_message(ADMIN_ID, text, parse_mode='HTML')
        bot.answer_callback_query(call.id)
        return
    
    if data == "admin_broadcast":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Недостаточно прав")
            return
        bot.send_message(ADMIN_ID, "📢 Введите текст для рассылки всем подписавшим:")
        bot.register_next_step_handler(call.message, broadcast_step)
        bot.answer_callback_query(call.id)
        return
    
    if data == "admin_reset_target":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Недостаточно прав")
            return
        settings = load_settings()
        settings['blocking_started'] = False
        settings['blocking_announced'] = False
        save_settings(settings)
        bot.send_message(ADMIN_ID, "✅ Целевой показатель сброшен. Программа блокировок деактивирована.")
        bot.answer_callback_query(call.id)
        return
    
    if data == "admin_support":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Недостаточно прав")
            return
        
        tickets = get_tickets()
        open_tickets = []
        
        for uid, data in tickets.items():
            for ticket in data['tickets']:
                if ticket['status'] == 'open':
                    open_tickets.append((uid, data['first_name'], data['username'], ticket))
        
        if not open_tickets:
            bot.send_message(ADMIN_ID, "📞 Нет открытых обращений в поддержку.")
        else:
            kb = types.InlineKeyboardMarkup(row_width=1)
            for uid, name, username, ticket in open_tickets[:10]:
                kb.add(types.InlineKeyboardButton(
                    f"#{ticket['id']} | {name} (@{username})",
                    callback_data=f"reply_ticket_{uid}_{ticket['id']}"
                ))
            bot.send_message(ADMIN_ID, "📞 <b>ОТКРЫТЫЕ ОБРАЩЕНИЯ</b>\n\nВыберите для ответа:", parse_mode='HTML', reply_markup=kb)
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("reply_ticket_"):
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Недостаточно прав")
            return
        
        parts = data.split("_")
        target_user_id = int(parts[2])
        ticket_id = int(parts[3])
        
        tickets = get_tickets()
        ticket = None
        for t in tickets.get(str(target_user_id), {}).get('tickets', []):
            if t['id'] == ticket_id:
                ticket = t
                break
        
        if ticket:
            bot.send_message(ADMIN_ID, f"📝 <b>Ответ на обращение #{ticket_id}</b>\n\n<b>Пользователь:</b> {ticket['message'][:100]}...\n\nВведите текст ответа:", parse_mode='HTML')
            bot.register_next_step_handler(call.message, process_admin_response, target_user_id, ticket_id)
        else:
            bot.send_message(ADMIN_ID, "❌ Обращение не найдено")
        bot.answer_callback_query(call.id)
        return
    
    if data == "admin_panel":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Недостаточно прав")
            return
        text = "🔧 <b>ПАНЕЛЬ УПРАВЛЕНИЯ</b>\n\nВыберите действие:"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=admin_keyboard())
        bot.answer_callback_query(call.id)
        return

# ========== ШАГИ ДЛЯ ПОЛЬЗОВАТЕЛЯ ==========
def process_new_ticket(message, user_id):
    """Обработка нового обращения от пользователя"""
    if message.text == "◀️ Назад" or message.text == "/start":
        start_cmd(message)
        return
    
    text = message.text.strip()
    if len(text) > 500:
        bot.send_message(user_id, "❌ Слишком длинное сообщение. Максимум 500 символов.")
        bot.send_message(user_id, "📝 Отправьте текст обращения заново:")
        bot.register_next_step_handler(message, process_new_ticket, user_id)
        return
    
    username = message.from_user.username or message.from_user.first_name
    first_name = message.from_user.first_name
    
    ticket_id = create_ticket(user_id, username, first_name, text)
    
    bot.send_message(user_id, f"✅ <b>Обращение #{ticket_id} принято!</b>\n\nСпециалист © РКН ответит в ближайшее время.\n\nВы можете отслеживать статус в разделе «Мои обращения».", parse_mode='HTML')
    
    # Уведомляем админа
    bot.send_message(ADMIN_ID, f"📞 <b>НОВОЕ ОБРАЩЕНИЕ #{ticket_id}</b>\n\n<b>От:</b> {first_name} (@{username}) ID: {user_id}\n<b>Текст:</b>\n{text[:200]}", parse_mode='HTML')

# ========== ШАГИ ДЛЯ АДМИНА ==========
def ban_user_step(message):
    try:
        user_id = int(message.text.strip())
        ban_user(user_id)
        bot.send_message(ADMIN_ID, f"✅ Пользователь {user_id} внесен в список ограниченных.")
        try:
            bot.send_message(user_id, "🚫 <b>УВЕДОМЛЕНИЕ © РКН</b>\n\nВаш доступ ограничен.", parse_mode='HTML')
        except:
            pass
    except:
        bot.send_message(ADMIN_ID, "❌ Ошибка. Введите корректный ID.")

def unban_user_step(message):
    try:
        user_id = int(message.text.strip())
        unban_user(user_id)
        bot.send_message(ADMIN_ID, f"✅ Пользователь {user_id} исключен из списка ограниченных.")
        try:
            bot.send_message(user_id, "✅ <b>УВЕДОМЛЕНИЕ © РКН</b>\n\nОграничения сняты.", parse_mode='HTML')
        except:
            pass
    except:
        bot.send_message(ADMIN_ID, "❌ Ошибка. Введите корректный ID.")

def broadcast_step(message):
    text = message.text
    sigs = get_signatures()
    count = 0
    
    for user_id in sigs.keys():
        try:
            bot.send_message(int(user_id), f"📢 <b>ОФИЦИАЛЬНОЕ УВЕДОМЛЕНИЕ © РКН</b>\n\n{text}", parse_mode='HTML')
            count += 1
        except:
            pass
    
    bot.send_message(ADMIN_ID, f"✅ Рассылка завершена. Получателей: {count}")

def process_admin_response(message, target_user_id, ticket_id):
    """Обработка ответа админа на обращение"""
    response = message.text.strip()
    
    if add_response(target_user_id, ticket_id, response):
        bot.send_message(ADMIN_ID, f"✅ Ответ на обращение #{ticket_id} отправлен.")
        try:
            bot.send_message(target_user_id, f"📞 <b>ОТВЕТ © РКН</b>\n\n<b>Обращение #{ticket_id}</b>\n\n{response}\n\n<i>Статус: закрыто</i>", parse_mode='HTML')
        except:
            pass
    else:
        bot.send_message(ADMIN_ID, f"❌ Ошибка при отправке ответа на обращение #{ticket_id}.")

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("=" * 50)
    print("© Роскомнадзор — Бот цифрового надзора")
    print("=" * 50)
    print(f"👑 Администратор: {ADMIN_ID}")
    print(f"📝 Целевой показатель: {load_settings().get('target_signatures', 1000)} подписей")
    print(f"🔒 Статус блокировок: {'АКТИВЕН' if is_blocking_started() else 'ОЖИДАНИЕ'}")
    print("=" * 50)
    print("✅ Бот готов к работе")
    print("=" * 50)
    bot.infinity_polling()