import os
import asyncio
import telebot
from telethon import TelegramClient
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors import FloodWaitError
import config

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode=None)
print("🤖 Бот запущен. Команды: /massjoin, /massspam, /status, /help")

async def join_one(client, link):
    try:
        if '+' in link:
            hash_part = link.split('+')[1]
        elif 'joinchat/' in link:
            hash_part = link.split('joinchat/')[1]
        else:
            hash_part = link
        await client(ImportChatInviteRequest(hash_part))
        me = await client.get_me()
        print(f"[+] {me.first_name} зашёл")
        return True
    except FloodWaitError as e:
        print(f"[!] Ждём {e.seconds} сек")
        await asyncio.sleep(e.seconds)
        return False
    except Exception as e:
        print(f"[-] Ошибка: {e}")
        return False

async def spam_one(client, chat_id, messages):
    for i in range(config.SPAM_COUNT):
        try:
            msg = messages[i % len(messages)]
            await client.send_message(chat_id, msg)
            await asyncio.sleep(config.SPAM_INTERVAL)
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except:
            break
    return True

async def load_sessions():
    if not os.path.exists(config.SESSION_DIR):
        os.makedirs(config.SESSION_DIR)
        print(f"📁 Создана папка {config.SESSION_DIR}/")
        return []
    files = [f for f in os.listdir(config.SESSION_DIR) if f.endswith('.session')]
    if not files:
        print(f"❌ Нет сессий в {config.SESSION_DIR}/")
        return []
    clients = []
    for f in files:
        path = os.path.join(config.SESSION_DIR, f[:-8])
        client = TelegramClient(path, config.API_ID, config.API_HASH)
        await client.start()
        clients.append(client)
        print(f"[+] Загружен {f}")
    return clients

async def mass_join():
    clients = await load_sessions()
    if not clients:
        return 0
    tasks = [join_one(c, config.TARGET_LINK) for c in clients]
    results = await asyncio.gather(*tasks)
    for c in clients:
        await c.disconnect()
    return sum(results)

async def mass_spam(chat_id):
    clients = await load_sessions()
    if not clients:
        return 0
    msgs = [f"🔥 РЕЙД 🔥\n{config.TARGET_LINK}", f"💀 ВСЕ СЮДА 💀\n{config.TARGET_LINK}", "████████████████████", f"👉 {config.TARGET_LINK} 👈"]
    tasks = [spam_one(c, chat_id, msgs) for c in clients]
    results = await asyncio.gather(*tasks)
    for c in clients:
        await c.disconnect()
    return len([r for r in results if r])

@bot.message_handler(commands=['start'])
def start(msg):
    if msg.chat.id in config.ADMINS:
        bot.reply_to(msg, "✅ Бот готов. /massjoin — зайти в группу, /massspam — спам, /status — сессии")
    else:
        bot.reply_to(msg, "❌ Доступ закрыт")

@bot.message_handler(commands=['help'])
def help_cmd(msg):
    if msg.chat.id in config.ADMINS:
        bot.reply_to(msg, "/massjoin — вход в группу\n/massspam — спам в этот чат\n/status — кол-во сессий")

@bot.message_handler(commands=['status'])
def status_cmd(msg):
    if msg.chat.id not in config.ADMINS:
        return
    if os.path.exists(config.SESSION_DIR):
        count = len([f for f in os.listdir(config.SESSION_DIR) if f.endswith('.session')])
        bot.reply_to(msg, f"📊 Сессий: {count}")
    else:
        bot.reply_to(msg, "❌ Папка sessions_real/ не найдена")

@bot.message_handler(commands=['massjoin'])
def join_cmd(msg):
    if msg.chat.id not in config.ADMINS:
        return
    bot.reply_to(msg, "🚀 Запускаю вход...")
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        count = loop.run_until_complete(mass_join())
        bot.reply_to(msg, f"✅ Зашло {count} аккаунтов")
    except Exception as e:
        bot.reply_to(msg, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['massspam'])
def spam_cmd(msg):
    if msg.chat.id not in config.ADMINS:
        return
    bot.reply_to(msg, f"💣 Спам {config.SPAM_COUNT} сообщений с каждого...")
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        count = loop.run_until_complete(mass_spam(msg.chat.id))
        bot.reply_to(msg, f"✅ {count} акков отработали")
    except Exception as e:
        bot.reply_to(msg, f"❌ Ошибка: {e}")

if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)