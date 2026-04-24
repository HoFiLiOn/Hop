import os
import time
import json
import telebot
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import config

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode=None)
print("🤖 Бот для сноса (без сессий) запущен")

def ensure_folders():
    if not os.path.exists(config.COOKIES_FOLDER):
        os.makedirs(config.COOKIES_FOLDER)

def report_with_chrome(account_cookie_file):
    """Открывает браузер, логинится по кукам и репортит цель"""
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = webdriver.Chrome(options=options)
    driver.get("https://web.telegram.org/k/")
    
    # Загружаем куки
    with open(account_cookie_file, 'r') as f:
        cookies = json.load(f)
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()
    time.sleep(5)
    
    # Переход на цель
    driver.get(config.TARGET_URL)
    time.sleep(3)
    
    try:
        # Клик на три точки
        menu = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='More actions']"))
        )
        menu.click()
        time.sleep(1)
        
        # Клик на Report
        report_btn = driver.find_element(By.XPATH, "//div[contains(text(), 'Report')]")
        report_btn.click()
        time.sleep(1)
        
        # Выбор причины
        reason = driver.find_element(By.XPATH, "//div[contains(text(), 'Spam')]")
        reason.click()
        time.sleep(1)
        
        # Подтверждение
        confirm = driver.find_element(By.XPATH, "//button[contains(text(), 'Report')]")
        confirm.click()
        print(f"[+] Репорт отправлен с {account_cookie_file}")
        time.sleep(2)
        driver.quit()
        return True
    except Exception as e:
        print(f"[-] Ошибка с {account_cookie_file}: {e}")
        driver.quit()
        return False

def add_account_manual():
    """Интерактивная сессия для добавления нового аккаунта"""
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    driver.get("https://web.telegram.org/k/")
    input("👉 Войди в аккаунт в открывшемся окне браузера, потом нажми Enter...")
    
    cookies = driver.get_cookies()
    account_name = input("Введи имя для этого аккаунта (например, acc1): ")
    cookie_file = f"{config.COOKIES_FOLDER}/{account_name}.json"
    with open(cookie_file, 'w') as f:
        json.dump(cookies, f)
    print(f"✅ Аккаунт сохранён как {cookie_file}")
    driver.quit()

@bot.message_handler(commands=['start'])
def start(msg):
    if msg.chat.id not in config.ADMINS:
        return
    bot.reply_to(msg, "👑 Без-сессионный снос\n/addaccount — добавить аккаунт\n/raid — запустить репорт со всех\n/list — список аккаунтов")

@bot.message_handler(commands=['addaccount'])
def add_cmd(msg):
    if msg.chat.id not in config.ADMINS:
        return
    bot.reply_to(msg, "🌐 Открываю браузер... Авторизуйся, потом вернись сюда и нажми /done")
    add_account_manual()
    bot.reply_to(msg, "✅ Готово. Можешь добавить ещё или использовать /raid")

@bot.message_handler(commands=['list'])
def list_cmd(msg):
    if msg.chat.id not in config.ADMINS:
        return
    ensure_folders()
    accounts = [f.replace('.json', '') for f in os.listdir(config.COOKIES_FOLDER) if f.endswith('.json')]
    if not accounts:
        bot.reply_to(msg, "❌ Нет сохранённых аккаунтов. Сначала /addaccount")
    else:
        bot.reply_to(msg, f"📋 Аккаунты ({len(accounts)}):\n" + "\n".join(accounts))

@bot.message_handler(commands=['raid'])
def raid_cmd(msg):
    if msg.chat.id not in config.ADMINS:
        return
    ensure_folders()
    account_files = [os.path.join(config.COOKIES_FOLDER, f) for f in os.listdir(config.COOKIES_FOLDER) if f.endswith('.json')]
    if not account_files:
        bot.reply_to(msg, "❌ Нет аккаунтов. Используй /addaccount")
        return
    
    bot.reply_to(msg, f"🚀 Запускаю репорт с {len(account_files)} аккаунтов на @{config.TARGET_USERNAME}...")
    success = 0
    for acc_file in account_files:
        if report_with_chrome(acc_file):
            success += 1
    bot.reply_to(msg, f"✅ Отправлено репортов: {success} из {len(account_files)}")

if __name__ == "__main__":
    ensure_folders()
    bot.polling(none_stop=True, interval=0)