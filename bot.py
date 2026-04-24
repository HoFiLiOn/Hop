import os
import asyncio
import telebot
from telethon import TelegramClient
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.types import InputReportReasonSpam, InputReportReasonViolence, InputReportReasonChildAbuse
import config

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode=None)
print("🎯 Бот репорта на @user0669 запущен")

async def report_one(session_path, target):
    client = TelegramClient(session_path, config.API_ID, config.API_HASH)
    await client.start()
    try:
        # Несколько причин для надёжности
        await client(ReportPeerRequest(peer=target, reason=InputReportReasonSpam(), message="Спам и реклама"))
        await asyncio.sleep(1)
        await client(ReportPeerRequest(peer=target, reason=InputReportReasonViolence(), message="Угрозы и насилие"))
        await asyncio.sleep(1)
        await client(ReportPeerRequest(peer=target, reason=InputReportReasonChildAbuse(), message="Детская порнография"))
        print(f"[+] Репорт с {session_path} на @{target}")
        return True
    except Exception as e:
        print(f"[-] Ошибка {session_path}: {e}")
        return False
    finally:
        await client.disconnect()

async def mass_report():

    if not os.path.exists(config.SESSION_DIR):
        print(f"❌ Папка {config.SESSION_DIR} не найдена")
        return 0

    sessions = [f for f in os.listdir(config.SESSION_DIR) if f.endswith('.session')]
    if not sessions:
        print("❌ Нет сессий в папке")
        return 0

    print(f"📋 Найдено сессий: {len(sessions)}")
    tasks = []
    for sess in sessions:
        path = os.path.join(config.SESSION_DIR, sess[:-8])
        tasks.append(report_one(path, config.TARGET_USERNAME))

    results = await asyncio.gather(*tasks)
    success = sum(results)
    print(f"✅ Отправлено репортов: {success} из {len(sessions)}")
    return success

@bot.message_handler(commands=['start'])
def start(msg):
    if msg.chat.id not in config.ADMINS:
        return
    bot.reply_to(msg, f"🎯 Цель: @{config.TARGET_USERNAME}\n/report — запустить масс-репорт")

@bot.message_handler(commands=['report'])
def report_cmd(msg):
    if msg.chat.id not in config.ADMINS:
        return
    bot.reply_to(msg, f"🚀 Запускаю репорт на @{config.TARGET_USERNAME}...")
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        count = loop.run_until_complete(mass_report())
        bot.reply_to(msg, f"✅ Отправлено репортов: {count}")
    except Exception as e:
        bot.reply_to(msg, f"❌ Ошибка: {e}")

if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)