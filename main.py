import time
import datetime
import logging
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from telegram import Update, ReplyKeyboardMarkup, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import ssl
import certifi

# Токен Telegram
bot_token = '6152013861:AAGh-ONBf89GzgvHvKZk6-6tUPEgb21idao'
chat_id = '351583809'

# Создайте SSL-контекст с дополнительными параметрами
context = ssl.create_default_context(cafile=certifi.where())

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
    ['/set_interval']
]

# список кнопок при инициализации клавиатуры
keyboard = ReplyKeyboardMarkup(commands, resize_keyboard=True)


def send_telegram_message(text):
    """
    Отправляет сообщение в Telegram.
    """
    bot.send_message(chat_id=chat_id, text=text)
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={text}"
    requests.get(url)


def check_site(browser, site_url, selector1, selector2):
    """
    Проверяет сайт на наличие изменений.
    Возвращает новый текст (если сайт изменился) или None (если сайт не изменился).
    """
    browser.get(site_url)

    # Ожидание полной загрузки сайта
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//body")))

    # Если указаны селекторы, выполняем дополнительные действия перед проверкой
    if selector1:
        element = browser.find_element(By.CSS_SELECTOR, selector1)
        element.click()

        # Ожидание загрузки сайта после выбора элемента
        time.sleep(2)

    if selector2:
        element = browser.find_element(By.CSS_SELECTOR, selector2)
        element.click()

        # Ожидание загрузки сайта после выбора элемента
        time.sleep(2)

    new_text = browser.find_element(By.CSS_SELECTOR, "input.form-control").text

    if site_url in site_states:
        old_text = site_states[site_url]
        if new_text != old_text:
            # Сохраняем новое состояние сайта
            site_states[site_url] = new_text
            message = f"Изменение на сайте {site_url}:\n{new_text}"
            send_telegram_message(message)
            return new_text
    else:
        # Сайт еще не отслеживается, сохраняем его состояние
        site_states[site_url] = new_text

    return None


def start(update: Update, context: CallbackContext):
    """Обработчик команды /start"""
    context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я бот для отслеживания изменений на сайтах.")


def check_sites(update: Update, context: CallbackContext):
    """Обработчик команды /check_sites"""
    # Проверяем сайт https://imex-service.ru/booking/
    site_url1 = "https://imex-service.ru/booking/"
    selector1 = "#departureRoute option[value='1']"
    selector2 = "#transportType option[value='TR']"
    new_text1 = check_site(browser, site_url1, selector1, selector2)
    if new_text1 is not None:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Изменение на сайте {site_url1}:\n{new_text1}")

    # Проверяем сайт https://booking.transbc.ru/
    site_url2 = "https://booking.transbc.ru/"
    selector1 = "#departureRoute option[value='3']"
    selector2 = "#transportType option[value='TR']"
    new_text2 = check_site(browser, site_url2, selector1, selector2)
    if new_text2 is not None:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Изменение на сайте {site_url2}:\n{new_text2}")


def set_interval(update: Update, context: CallbackContext):
    """Обработчик команды /set_interval"""
    context.bot.send_message(chat_id=update.effective_chat.id, text="Введите интервал в секундах:")


def interval_input(update: Update, context: CallbackContext):
    """Обработчик ввода интервала"""
    interval = int(update.message.text)
    context.job_queue.run_repeating(check_sites_periodically, interval, context=interval, first=0)

    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Функция check_sites_periodically будет "
                                                                  f"выполняться каждые {interval} секунд.")


def check_sites_periodically(context: CallbackContext):
    """
    Выполняет периодическую проверку сайтов и отправляет отчет каждые 12 часов.
    """
    current_time = time.strftime("%H:%M:%S", time.localtime())
    # context.bot.send_message(chat_id=chat_id, text=f"Периодическая проверка сайтов. Время: {current_time}")

    # Проверяем сайт https://imex-service.ru/booking/
    site_url1 = "https://imex-service.ru/booking/"
    selector1 = "#departureRoute option[value='1']"
    selector2 = "#transportType option[value='TR']"
    new_text1 = check_site(browser, site_url1, selector1, selector2)
    if new_text1 is not None:
        context.bot.send_message(chat_id=chat_id, text=f"Изменение на сайте {site_url1}:\n{new_text1}")

    # Проверяем сайт https://booking.transbc.ru/
    site_url2 = "https://booking.transbc.ru/"
    selector1 = "#departureRoute option[value='3']"
    selector2 = "#transportType option[value='TR']"
    new_text2 = check_site(browser, site_url2, selector1, selector2)
    if new_text2 is not None:
        context.bot.send_message(chat_id=chat_id, text=f"Изменение на сайте {site_url2}:\n{new_text2}")

    # Запускаем функцию daily_report для вывода ежедневного отчета
    daily_report(context)


# Переменная для отслеживания времени последнего отчета
last_daily_report_time = None

# Список для хранения журнала логов
log = []

def daily_report(context: CallbackContext):
    """
    Выводит ежедневный отчет, включающий количество проведенных проверок,
    изменения на сайтах и журнал логов.
    """
    global log, last_daily_report_time

    # Проверяем, прошло ли достаточно времени с момента последнего отчета
    if last_daily_report_time is None or datetime.datetime.now().hour == 0:
        # Обновляем время последнего отчета
        last_daily_report_time = datetime.datetime.now()

        # Переменные для отчета
        total_checks = 0
        changes = []

        # Перебираем сайты для проверки
        for site_url in site_states.keys():
            total_checks += 1
            if site_states[site_url] not in log:
                changes.append((site_url, site_states[site_url]))
                log.append(site_states[site_url])

        # Отправляем отчет
        report = f"Ежедневный отчет:\n\n"
        report += f"Количество проведенных проверок за 24 часа: {total_checks}\n"

        if len(changes) > 0:
            report += f"\nИзменения на сайтах:\n"
            for change in changes:
                site_url, change_time = change
                report += f"Сайт: {site_url}\nВремя изменения: {change_time}\n\n"
        else:
            report += f"\nИзменений на сайтах не обнаружено.\n"

        # Добавляем журнал логов
        report += f"\nЖурнал логов:\n"
        report += "\n".join(log)

        # Отправляем отчет в Telegram
        send_telegram_message(report)

    # Планируем следующий отчет через 24 часа
    context.job_queue.run_once(daily_report, 24 * 60 * 60, context=context)


if __name__ == '__main__':
    # Инициализация браузера
    browser = webdriver.Chrome()

    # Инициализация бота
    updater = Updater(token=bot_token, use_context=True)
    dispatcher = updater.dispatcher

    # Регистрация обработчиков команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("check_sites", check_sites))
    dispatcher.add_handler(CommandHandler("set_interval", set_interval))
    dispatcher.add_handler(MessageHandler(filters=Filters.text & ~Filters.command, callback=interval_input))
    # Запуск бота
    updater.start_polling()
    updater.idle()
