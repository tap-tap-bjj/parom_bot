import pickle
from access_file import login_SRV, password_SRV, bot_token_SRV, chat_id_my
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from telegram import Bot, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters



def change_time():
    try:
        car_row = WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#tbl_list > div > main > div > div._31h96hQp > div > div:nth-child(3) > div > div:nth-child(6) > div > div > span')))
        car_row.click()
        browser.find_element(By.CSS_SELECTOR, '#lyt_btn_edit').click()
        browser.find_element(By.CSS_SELECTOR, '#btn_request_reschedule').click()
        date = WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div/div[3]/div[2]/div/div[2]/div[2]/div[3]/div[2]/div/div[3]/div/div/div/div[1]/div[3]/div/div[1]/div/input')))
        while True:
            try:
                time.sleep(10)
                date.send_keys(Keys.CONTROL + 'a')
                date.send_keys(Keys.DELETE)
                date.send_keys(today)
                WebDriverWait(browser, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-id="lbl_limit"] span')))
                mesta = browser.find_elements(By.CSS_SELECTOR, '[data-id="lbl_limit"] span')
                mesta_list = [x.text.split(' /')[0] for x in mesta]
                print(mesta_list)
                for i in mesta_list:
                    if i == '8':
                        continue
                    else:
                        print('Появилось место!')
                        bot.send_message(chat_id=chat_id_my, text='Появилось место!!!!!!')
                        continue
            except Exception as e:
                print(f'Ошибка в цикле {e}')

    except Exception as e:
        print(f'Ошибка в change_time {e}')


def add_cookie_srv():
    try:
        cookies = pickle.load(open("cookies_srv.pkl", "rb"))
        browser.get(url_zayavki)
        # delete the current cookies
        browser.delete_all_cookies()
        # add cookies from pickled-txt or a txt file
        for cookie in cookies:
            browser.add_cookie(cookie)
        time.sleep(3)
        browser.refresh()
        time.sleep(3)
    except Exception as e:
        print(f'Ошибка в куках {e}')

def get_cook_srv(): # Функция для записи куков АТИ
    browser.get(url_main)
    browser.find_element(By.CSS_SELECTOR, '#lyt_chk_clone_1').click()
    browser.find_element(By.CSS_SELECTOR, '#txt_login input').send_keys(login_SRV)
    browser.find_element(By.CSS_SELECTOR, '#txt_password input').send_keys(password_SRV)
    browser.find_element(By.ID, 'btn_login').click()
    time.sleep(3)
    pickle.dump(browser.get_cookies(), open("cookies_srv.pkl", "wb"))

if __name__ == '__main__':
    browser = webdriver.Chrome()
    browser.implicitly_wait(10)

    bot = Bot(token=bot_token_SRV)

    url_main = "https://srv-go.ru/"
    url_zayavki = 'https://srv-go.ru/?&data=%7B%22node%22%3A%22eqf_requests%22%7D'
    today = '20.09.2023'
    #browser.get(url_zayavki)
    get_cook_srv()
    #add_cookie_srv()

    change_time()
