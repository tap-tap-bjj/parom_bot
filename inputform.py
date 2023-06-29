from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import logging
import argparse
from telegram import Bot

# Журнал логов
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Токен Telegram
bot_token = '6121370662:AAGuOtP_Di7TZNA4b0V4qxn1NCn_MJyijC8'
chat_id = '351583809'
bot = Bot(token=bot_token)


try:
    # Создание парсера аргументов командной строки
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='Ссылка на сайт')

    # Парсинг аргументов командной строки
    args = parser.parse_args()

    # Получение значения ссылки из аргументов командной строки
    url = args.url

    # Инициализация браузера
    # Путь к исполняемому файлу chromedriver
    path_to_chromedriver = 'C:\chromedriver\chromedriver.exe'

    # Создание объекта сервиса
    service = Service(path_to_chromedriver)

    # Создание объекта опций
    options = Options()
    # options.add_argument("--headless")  # Запуск Chrome в режиме без графического интерфейса
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    # Создание экземпляра браузера Chrome
    browser = webdriver.Chrome(service=service, options=options)

    def first_step(browser, site_url, selector1, selector2):
        """
        Проверяет сайт на наличие изменений.
        Возвращает новый текст (если сайт изменился) или None (если сайт не изменился).
        """
        browser.get(site_url)

        # Ожидание полной загрузки сайта
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector2)))

        # Если указаны селекторы, выполняем дополнительные действия перед проверкой
        if selector1:
            element = browser.find_element(By.CSS_SELECTOR, selector1)
            element.click()

            # Ожидание загрузки сайта после выбора элемента
            time.sleep(1)

        if selector2:
            element = browser.find_element(By.CSS_SELECTOR, selector2)
            element.click()

            # Ожидание загрузки сайта после выбора элемента
            time.sleep(1)

        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#departureDate')))

    # Словарb с данными для заполнения полей
    data_car = {
        '[placeholder="Введите марку"]': ['Schmitz', 'Schmitz'],
        '[placeholder="Введите модель"]': ['SKO24', 'Schmitz'],
        '[placeholder="Введите цвет"]': ['Белый', 'Белый'],
        '[placeholder="A000AA39"]': ['АН4495 39', 'АН1909 39'],
        '#transport_weight': ['9260', '9500']} # Данные прицепов
    data_car_const = {
        '#length': '14',
        '#width': '2,55',
        '#height': '4',
        '#cargo': 'Сборный',
        '#form > div > form > div.card-body > div > div:nth-child(8) > div.input-group > input': '32',
        '#form > div > form > div.card-body > div > div:nth-child(9) > div.input-group > input': '20000'} # Габариты прицепа и груз
    data_firm = {'[placeholder="Введите должность"]': 'Ген. директор',
                 '[placeholder="Введите фамилию"]': 'Низельник',
                 '[placeholder="Введите имя"]': 'Илья',
                 '[placeholder="Введите отчество"]': 'Геннадьевич',
                 '[placeholder="Введите номер"]': '+79097889191',
                 '[placeholder="Введите почту"]': 'transstandart39@gmail.com'} # Данные фирмы

    # Получаем количество повторов
    num_repeats = len(data_car['[placeholder="Введите марку"]'])

    # Цикл для заполнения формы
    for i in range(num_repeats):
        if url == 'https://imex-service.ru/booking/':
            selector1_1 = "#departureRoute option[value='1']"
            selector1_2 = "#transportType option[value='TR']"
            first_step(browser, url, selector1_2, selector1_2)
        elif url == 'https://booking.transbc.ru/':
            selector2_1 = "#departureRoute option[value='0']"
            selector2_2 = "#transportType option[value='TR']"
            first_step(browser, url, selector2_1, selector2_2)

        # Выбор доступной даты из списка
        # Нахождение элемента выпадающего списка по селектору
        dropdown = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#departureDate')))
        dropdown.click()
        select = Select(dropdown)

        # Получение количества опций в выпадающем списке
        options_count = len(select.options)
        # Выбор первого элемента
        if options_count >= i:
            select.select_by_index(i)
        else:
            select.select_by_index(0)

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
            browser.execute_script("arguments[0].scrollIntoView();",
                                   checkbox)
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

        time.sleep(1)
        bot.send_message(chat_id=chat_id, text=f'''Заявка на прицеп № {data_car['[placeholder="A000AA39"]'][i]} на сайте {url} заполнена!\n 
        {browser.find_element(By.CSS_SELECTOR, 'ul.list-group.mb-3').text}''')
        continue

except Exception as e:
    # Ошибка возникла, записываем сообщение в журнал
    logging.error("Произошла ошибка: %s", str(e))

    # Отправляем сообщение в чат бота
    bot.send_message(chat_id=chat_id, text=f"Произошла ошибка: {str(e)}")

    raise  # Повторное возбуждение ошибки для прекращения выполнения кода


# не забываем оставить пустую строку в конце файла
