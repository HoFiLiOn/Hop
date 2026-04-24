import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TARGET = "user0669"
COOKIES_FOLDER = "accounts/"

def report_all():
    if not os.path.exists(COOKIES_FOLDER):
        print("❌ Сначала добавь аккаунты папку accounts/ с .json файлами кук")
        return
    
    account_files = [f for f in os.listdir(COOKIES_FOLDER) if f.endswith('.json')]
    print(f"Найдено аккаунтов: {len(account_files)}")
    
    for acc_file in account_files:
        print(f"➡️ Работаю с {acc_file}")
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(options=options)
        driver.get("https://web.telegram.org/k/")
        
        with open(os.path.join(COOKIES_FOLDER, acc_file), 'r') as f:
            cookies = json.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()
        time.sleep(5)
        
        driver.get(f"https://t.me/{TARGET}")
        time.sleep(3)
        
        try:
            menu = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='More actions']"))
            )
            menu.click()
            time.sleep(1)
            driver.find_element(By.XPATH, "//div[contains(text(), 'Report')]").click()
            time.sleep(1)
            driver.find_element(By.XPATH, "//div[contains(text(), 'Spam')]").click()
            time.sleep(1)
            driver.find_element(By.XPATH, "//button[contains(text(), 'Report')]").click()
            print(f"[+] Репорт с {acc_file} отправлен")
        except Exception as e:
            print(f"[-] {acc_file} ошибка: {e}")
        
        driver.quit()
        time.sleep(10)

if __name__ == "__main__":
    report_all()