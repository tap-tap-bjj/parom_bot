import time
import logging
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from telegram import Update, ReplyKeyboardMarkup, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
import ssl
import certifi
import os
from fake_useragent import UserAgent

# Токен Telegram
bot_token = '6121370662:AAGuOtP_Di7TZNA4b0V4qxn1NCn_MJyijC8'
chat_id = '351583809'

# Peremenaya tekushego vremeni i intervala proverki
current_time = time.strftime("%H:%M:%S", time.localtime())

# УСТАНОВКА ИНТЕРВАЛА ПРОВЕРКИ!!!
interval = 60

#Сайты для проверки
site_url1 = "https://imex-service.ru/booking/"
site_url2 = "https://booking.transbc.ru/"

# Создайте SSL-контекст с дополнительными параметрами
updater_context = ssl.create_default_context(cafile=certifi.where())

# Создайте экземпляр бота с настроенным SSL-контекстом
bot = Bot(token=bot_token)

# Журнал логов
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Словарь для хранения состояния каждого сайта
site_states = {}

# список кнопок с командами
commands = [
    ['/start', '/check_sites'],
    ['/view_site_states'], ['/fill_site_IMEX', '/fill_site_TBC']
]

# список кнопок при инициализации клавиатуры
keyboard = ReplyKeyboardMarkup(commands, resize_keyboard=True, one_time_keyboard=True)

# Отправка сообщения в чат Telegram
bot.send_message(chat_id=chat_id, text=f"Запуск бота! Время сервера: {current_time} (мск)", reply_markup=keyboard)

def view_site_states(update: Update, context: CallbackContext):
    """Обработчик команды /view_site_states"""
    # Преобразование словаря site_states в строку
    print(site_states)
    site_states_str = '\n'.join([f"{url}: {state}" for url, state in site_states.items()])
    bot.send_message(chat_id=chat_id, text=f"Состояние сайтов:\n{site_states_str}")


def check_site(browser, site_url, selector1, selector2):
    """
    Проверяет сайт на наличие изменений.
    Возвращает новый текст (если сайт изменился) или None (если сайт не изменился).
    """
    browser.get(site_url)

    # Ожидание полной загрузки сайта
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector2)))

    # Если указаны селекторы, выполняем дополнительные действия перед проверкой
    if selector1:
        element = browser.find_element(By.CSS_SELECTOR, selector1)
        element.click()

        # Ожидание загрузки сайта после выбора элемента
        time.sleep(3)

    if selector2:
        element = browser.find_element(By.CSS_SELECTOR, selector2)
        element.click()

        # Ожидание загрузки сайта после выбора элемента
        time.sleep(3)

    new_text = browser.find_element(By.CSS_SELECTOR, "div.col-lg-12.col-xl-4").text

    if site_url in site_states:
        old_text = site_states[site_url]
        if new_text != old_text:
            # Сохраняем новое состояние сайта
            site_states[site_url] = new_text
            return new_text
        else:
            return None
    else:
        # Сайт еще не отслеживается, сохраняем его состояние
        site_states[site_url] = new_text
        bot.send_message(chat_id=chat_id, text=f"Сайт {site_url} еще не отслеживается, сохраняем его состояние: \n {new_text}")
        return None


def start(update: Update, context: CallbackContext):
    """Обработчик команды /start"""

    context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я бот для отслеживания изменений на сайтах.", reply_markup=keyboard)


def check_sites(update: Update, context: CallbackContext):
    """Обработчик команды /check_sites"""
    # Проверяем сайт https://imex-service.ru/booking/
    selector1_1 = "#departureRoute option[value='1']"
    selector1_2 = "#transportType option[value='TR']"
    new_text1 = check_site(browser, site_url1, selector1_1, selector1_2)
    if new_text1 is not None:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Изменение на сайте {site_url1} {current_time}:\n{new_text1}")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Сайт {site_url1} не изменился.")

    # Проверяем сайт https://booking.transbc.ru/
    selector2_1 = "#departureRoute option[value='3']"
    selector2_2 = "#transportType option[value='TR']"
    new_text2 = check_site(browser, site_url2, selector2_1, selector2_2)
    if new_text2 is not None:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Изменение на сайте {site_url2} {current_time}:\n{new_text2}")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Сайт {site_url2} не изменился.")


def check_sites_periodically(context: CallbackContext):
    """
    Выполняет периодическую проверку сайтов и # отправляет отчет каждые 12 часов.
    """

    # Проверяем сайт https://imex-service.ru/booking/
    selector1_1 = "#departureRoute option[value='1']"
    selector1_2 = "#transportType option[value='TR']"
    new_text1 = check_site(browser, site_url1, selector1_1, selector1_2)
    if new_text1 is not None:
        context.bot.send_message(chat_id=chat_id, text=f"Изменение на сайте {site_url1}:\n{new_text1} время {current_time}")

    # Проверяем сайт https://booking.transbc.ru/
    selector2_1 = "#departureRoute option[value='3']"
    selector2_2 = "#transportType option[value='TR']"
    new_text2 = check_site(browser, site_url2, selector2_1, selector2_2)
    if new_text2 is not None:
        context.bot.send_message(chat_id=chat_id, text=f"Изменение на сайте {site_url2}:\n{new_text2} время {current_time}")

    # Запускаем функцию daily_report для вывода ежедневного отчета
    # daily_report(context)

def execute_inputform_file(url):
    # Путь к исполняемому файлу, который нужно запустить
    file_path = 'inputform.py'

    # Создание команды запуска другого файла с передачей аргументов
    command = f'python {file_path} --url "{url}"'

    # Запуск команды
    os.system(command)

def fill_site1(update: Update, context: CallbackContext):
    """Обработчик команды /fill_site1"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Запускаю заполнение сайта {site_url1}")
    execute_inputform_file(site_url1)

def fill_site2(update: Update, context: CallbackContext):
    """Обработчик команды /fill_site2"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Запускаю заполнение сайта {site_url2}")
    execute_inputform_file(site_url2)




if __name__ == '__main__':
    # Инициализация браузера
    # Путь к исполняемому файлу chromedriver
    path_to_chromedriver = '/usr/bin/chromedriver'

    # Создание объекта сервиса
    service = Service(path_to_chromedriver)

    # Создание объекта опций
    options = Options()
    ua = UserAgent()
    options.add_argument("--headless")  # Запуск Chrome в режиме без графического интерфейса
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"--user-agent={ua}")


    # Создание экземпляра браузера Chrome
    browser = webdriver.Chrome(service=service, options=options)

    # Инициализация бота
    updater = Updater(token=bot_token, use_context=True)
    dispatcher = updater.dispatcher

    # Запуск периодической проверки
    updater.job_queue.run_repeating(check_sites_periodically, interval=interval, context=updater_context)

    # Регистрация обработчиков команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("check_sites", check_sites))
    dispatcher.add_handler(CommandHandler("view_site_states", view_site_states))
    dispatcher.add_handler(CommandHandler("fill_site_IMEX", fill_site1))
    dispatcher.add_handler(CommandHandler("fill_site_TBC", fill_site2))

    # Запуск бота
    updater.start_polling(poll_interval=0)
    updater.idle()
