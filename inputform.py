from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import requests
from fake_useragent import UserAgent
from twocaptcha import TwoCaptcha
import random
import time
import logging
from telegram import Bot, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Журнал логов
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Токен Telegram
bot_token = '6384150489:AAHAh62Z2gK5VcLkiAonoXbsD_W9ttnzXUY'
chat_id = '351583809'
bot = Bot(token=bot_token)

# Словарb с данными для заполнения полей
data_car = {
    '[placeholder="Введите марку"]': ['Schmitz', 'Schmitz', 'Schmitz'],
    '[placeholder="Введите модель"]': ['SKO24', 'Schmitz', 'SKO24'],
    '[placeholder="Введите цвет"]': ['Белый', 'Белый', 'Белый'],
    '[placeholder="A000AA39"]': ['АН4495 39', 'АН1909 39', 'AO0683 39'],
    '#transport_weight': ['9260', '9500', '9470']}  # Данные прицепов
data_car_const = {
    '#length': '14',
    '#width': '2,55',
    '#height': '4',
    '#cargo': 'Сборный',
    '#form > div > form > div.card-body > div > div:nth-child(8) > div.input-group > input': '32',
    '#form > div > form > div.card-body > div > div:nth-child(9) > div.input-group > input': '20000'}  # Габариты прицепа и груз
data_firm = {'[placeholder="Введите должность"]': 'Ген. директор',
             '[placeholder="Введите фамилию"]': 'Низельник',
             '[placeholder="Введите имя"]': 'Илья',
             '[placeholder="Введите отчество"]': 'Геннадьевич',
             '[placeholder="Введите номер"]': '+79097889191',
             '[placeholder="Введите почту"]': 'transstandart39@gmail.com'}  # Данные фирмы

# Создание экземпляра Updater и передача токена
updater = Updater(token=bot_token, use_context=True)
dispatcher = updater.dispatcher

# Определение элементов меню
menu_items1 = [['Заполнить сайт IMEX', 'Заполнить сайт TBC']]
menu_items2 = [
    [f'''Заполнить: {data_car['[placeholder="A000AA39"]'][0]}''', f'''Заполнить: {data_car['[placeholder="A000AA39"]'][1]}'''],
    [f'''Заполнить: {data_car['[placeholder="A000AA39"]'][2]}''', '<<Заполнить все прицепы>>'],
    ['Назад']
]

# Создание клавиатуры меню
keyboard1 = ReplyKeyboardMarkup(menu_items1, resize_keyboard=True)
keyboard2 = ReplyKeyboardMarkup(menu_items2, resize_keyboard=True)

# Определение состояний
STATE_MAIN_MENU, STATE_SITE_SELECTION, STATE_CAR_SELECTION = range(3)

bot.send_message(chat_id=chat_id, text='Привет я бот для заполнения заявок нажми /start и погнали')

# Функция для отправки сообщений с меню
def send_menu_message(chat_id, text, reply_markup):
    updater.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

# Обработчик команды /start
def start(update, context):
    user = update.effective_user
    context.user_data['state'] = STATE_MAIN_MENU
    send_menu_message(user.id, 'Выберите сайт для заполнения:', keyboard1)

# Обработчик сообщений
def handle_message(update, context):
    user = update.effective_user
    message = update.message.text

    if context.user_data['state'] == STATE_MAIN_MENU:
        if message == 'Заполнить сайт IMEX':
            context.user_data['state'] = STATE_SITE_SELECTION
            context.user_data['url'] = 'https://imex-service.ru/booking/'
            send_menu_message(user.id, 'Заполняем IMEX. Выберите машину для заполнения:', keyboard2)
        elif message == 'Заполнить сайт TBC':
            context.user_data['state'] = STATE_SITE_SELECTION
            context.user_data['url'] = 'https://booking.transbc.ru/'
            send_menu_message(user.id, 'Заполняем TBC. Выберите машину для заполнения:', keyboard2)

    elif context.user_data['state'] == STATE_SITE_SELECTION:
        if message == 'Назад':
            context.user_data['state'] = STATE_MAIN_MENU
            send_menu_message(user.id, 'Выберите сайт для заполнения:', keyboard1)
        else:
            url = context.user_data['url']
            # Присваивание соответствующих значений переменным в вашем коде
            if message == 'Заполнить: АН4495 39':
                start = 0
                stop = 1
                send_menu_message(user.id, 'Заполняем АН4495 39', keyboard2)
            elif message == 'Заполнить: АН1909 39':
                start = 1
                stop = 2
                send_menu_message(user.id, 'Заполняем АН1909 39', keyboard2)
            elif message == 'Заполнить: AO0683 39':
                start = 2
                stop = 3
                send_menu_message(user.id, 'Заполняем AO0683 39', keyboard2)
            elif message == '<<Заполнить все прицепы>>':
                start = 0
                stop = 3
                send_menu_message(user.id, 'Заполняем все прицепы', keyboard2)


            fill_zayvka(start, stop, url)
            context.user_data['state'] = STATE_MAIN_MENU
            send_menu_message(user.id, 'Выберите сайт для заполнения:', keyboard1)

def first_step(browser, site_url, selector1, selector2):
    """
    Проверяет сайт на наличие изменений.
    Возвращает новый текст (если сайт изменился) или None (если сайт не изменился).
    """
    browser.get(site_url)

    # Ожидание полной загрузки сайта
    WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector2)))

    # Если указаны селекторы, выполняем дополнительные действия перед проверкой
    if selector1:
        element = browser.find_element(By.CSS_SELECTOR, selector1)
        element.click()
        time.sleep(1)

    if selector2:
        element = browser.find_element(By.CSS_SELECTOR, selector2)
        element.click()
        time.sleep(1)
    WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#departureDate')))

# Словарь для решений Captcha
dict_resut = {}

#Функция принимает путь к изображению, отправляет в API 2captcha и возвращает словарь со словом
def sender_solve(path):
    solver = TwoCaptcha('19e92c38787ad78bdf448c4dc6a04f44')
    bot.send_message(chat_id=chat_id, text='2) Изображение отправленно для разгадывания:')
    result = solver.normal(path, param='ru')
    bot.send_message(chat_id=chat_id, text=f'3) От API пришёл ответ: {result}')
    #API вернёт словарь {'captchaId': '72447681441', 'code': 'gbkd'}
    #Обновляем словарь для дальнейшего извлечения ID капчи и отправки репорта
    dict_resut.update(result)
    return result['code']

def captcha():
    #Переключаемся на iframe капчи
    WebDriverWait(browser, 10).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[title='SmartCaptcha checkbox widget']")))

    #Ожидаем кнопку и кликаем по ней
    time.sleep(1)
    element = browser.find_element(By.CSS_SELECTOR, 'input[class="CheckboxCaptcha-Button"]')
    browser.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(1)
    WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[class="CheckboxCaptcha-Button"]')))
    time.sleep(1)
    element.click()
    time.sleep(1)

    #Возвращаемся к основному коду на странице
    browser.switch_to.default_content()

    try:
        #Переключаемся на новый iframe с картинкой
        WebDriverWait(browser, 5).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[title='SmartCaptcha advanced widget']")))

        #Хардкодим имя картинки
        img_names = 'img_yandex.png'
        with open(img_names, 'wb') as file:
            #Извлекаем атрибут src из тега в котором хранится ссылка на изображение
            img = browser.find_element(By.CSS_SELECTOR, 'img[alt="Задание с картинкой"]').get_attribute('src')
            #Делаем простой requests запрос для скачивания картинки и её записи в файл
            file.write(requests.get(img).content)
            bot.send_message(chat_id=chat_id, text=f'1) url image: {img}')

        sender_solve(img_names)
        bot.send_message(chat_id=chat_id, text=f'4) {dict_resut["code"]}')

        #Вставлям необходимую часть словаря dict_resut в котором лежит разгаданное слова с капчи
        browser.find_element(By.CSS_SELECTOR, 'input[class="Textinput-Control"]').send_keys(dict_resut['code'])

        #Кликаем на кнопку отправить
        browser.find_element(By.CSS_SELECTOR, 'button[class="CaptchaButton CaptchaButton_view_action"]').click()

        #Возвращаемся к основному коду на странице
        browser.switch_to.default_content()
    except Exception as E:
        # Ошибка возникла, записываем сообщение в журнал
        logging.error("Произошла ошибка в капче: %s", str(E))

        # Отправляем сообщение в чат бота
        bot.send_message(chat_id=chat_id, text=f"Ошибка в капче (возможно не понадобилась картинка): {str(E)}")

def fill_zayvka(arg1, arg2, url):
    for i in range(arg1, arg2):
        try:
        # Цикл для заполнения формы первой вкладки
            if url == 'https://imex-service.ru/booking/':
                selector1_1 = "#departureRoute option[value='1']"
                selector1_2 = "#transportType option[value='TR']"
                first_step(browser, url, selector1_1, selector1_2)
            elif url == 'https://booking.transbc.ru/':
                selector2_1 = "#departureRoute option[value='3']"
                selector2_2 = "#transportType option[value='TR']"
                first_step(browser, url, selector2_1, selector2_2)

            # Выбор доступной даты из списка
            # Нахождение элемента выпадающего списка по селектору
            dropdown = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#departureDate')))
            # Прокручиваем страницу до видимости элемента
            browser.execute_script("arguments[0].scrollIntoView();", dropdown)
            dropdown.click()
            select = Select(dropdown)
            # Выбор случайного элемента по индексу
            select.select_by_index(random.choice(range(len(select.options))))

            # Ожидание появления кнопки "Продолжить"
            button = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-success")))
            # Прокручиваем страницу до видимости элемента
            browser.execute_script("arguments[0].scrollIntoView();", button)
            time.sleep(1)
            button.click()
            time.sleep(1)

            # Переходим на вкладку "Транспорт и груз"
            # Отмечаем чекбокс Груз-Есть
            checkbox = browser.find_element(By.CSS_SELECTOR, "#radio10")
            browser.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});", checkbox)
            time.sleep(1)
            if not checkbox.is_selected():
                checkbox.click()
            browser.execute_script("arguments[0].scrollIntoView();", browser.find_element(By.CSS_SELECTOR, 'h4'))

            # Заполняем инпуты "Данные прицепа"
            for key, value in data_car.items():
                # Находим поле ввода по CSS-селектору и вводим соответствующее значение
                input_field = browser.find_element(By.CSS_SELECTOR, key)
                browser.execute_script("arguments[0].scrollIntoView();", input_field)
                input_field.clear()
                input_field.send_keys(value[i]) # Значение для каждого прицепа выбирается отдельно по индексу значения

            # Заполняем инпуты "Габариты прицепа и груз"
            for key, value in data_car_const.items():
                # Находим поле ввода по CSS-селектору и вводим соответствующее значение
                input_field = browser.find_element(By.CSS_SELECTOR, key)
                input_field.send_keys(Keys.CONTROL + 'a')
                input_field.send_keys(Keys.DELETE)
                browser.execute_script("arguments[0].scrollIntoView();", input_field)
                input_field.send_keys(value)

            # Ждем чуть и продолжить
            button = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-success")))
            browser.execute_script("arguments[0].scrollIntoView();", button)
            time.sleep(1)
            button.click()
            time.sleep(1)

            # Переход на вкладку "Данные"
            # Отмечаем нужные чекбоксы на юр. лицо и одну фирму
            data_chekbox = ['#company-ul-Плательщик', '#matchPayer-Отправитель', '#matchPayer-Получатель', '#PaymentBill']
            for value in data_chekbox:
                checkbox = browser.find_element(By.CSS_SELECTOR, value)
                browser.execute_script("arguments[0].scrollIntoView();", checkbox)
                time.sleep(1)
                if not checkbox.is_selected():
                    checkbox.click()

            # Заполняем ИНН
            inn_input = browser.find_element(By.CSS_SELECTOR, '[title="ИНН"]')
            browser.execute_script("arguments[0].scrollIntoView();", inn_input)
            inn_input.clear()
            inn_input.send_keys('3906982908')

            # Клац по кнопке заполнить и ждем заполнения
            time.sleep(1)
            button_zapolnit = browser.find_element(By.CSS_SELECTOR, 'button.btn-success')
            button_zapolnit.click()
            time.sleep(1)
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[placeholder="Введите должность"]')))
            time.sleep(1)

            # Заполняем инпуты "Данные фирмы"
            for key, value in data_firm.items():
                # Находим поле ввода по CSS-селектору и вводим соответствующее значение
                input_field = browser.find_element(By.CSS_SELECTOR, key)
                browser.execute_script("arguments[0].scrollIntoView();", input_field)
                input_field.clear()
                input_field.send_keys(value)

            # Действия для кнопки "Capcha"))))
            captcha()

            bot.send_message(chat_id=chat_id, text=f"Данные заявки: \n {browser.find_element(By.CSS_SELECTOR, 'ul.list-group.mb-3').text}")

            # Finally. Нажатие кнопки оформить
            button = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-success")))
            browser.execute_script("arguments[0].scrollIntoView();", button)
            time.sleep(1)
            button.click() # Убираем финальную кнопку оформить на всякий
            time.sleep(1)

            bot.send_message(chat_id=chat_id, text=f'''Заявка на прицеп № {data_car['[placeholder="A000AA39"]'][i]} на сайте {url} заполнена!''')
            continue

        except Exception as e:
            # Ошибка возникла, записываем сообщение в журнал
            logging.error("Произошла ошибка: %s", str(e))

            # Отправляем сообщение в чат бота
            bot.send_message(chat_id=chat_id, text=f"Произошла ошибка: {str(e)}")
            continue

            # raise  # Повторное возбуждение ошибки для прекращения выполнения кода



if __name__ == '__main__':
    # Регистрация обработчиков
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_message))

    # Запуск бота
    updater.start_polling()

    # Инициализация браузера
    # Путь к исполняемому файлу chromedriver
    path_to_chromedriver = '/usr/bin/chromedriver'

    # Создание объекта сервиса
    service = Service(path_to_chromedriver)

    # Создание объекта опций
    ua = UserAgent()
    options = Options()
    options.add_argument("--headless")  # Запуск Chrome в режиме без графического интерфейса
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"--user-agent={ua}")

    # Создание экземпляра браузера Chrome
    browser = webdriver.Chrome(service=service, options=options)
    browser.implicitly_wait(10)
