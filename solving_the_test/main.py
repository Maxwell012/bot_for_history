from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, InvalidArgumentException
from bs4 import BeautifulSoup
import requests
from time import sleep
from threading import RLock
import random
import os

from data_base.all_connection import thread_connection, db
from create_logger import create_logger


########################################################################################################################


logger_main = create_logger(__name__)

rlock = RLock()

def main(data):
        try:
                # chrome_options = Options()
                # chrome_options.binary_location = os.getenv('GOOGLE_CHROME_BIN')
                # chrome_options.add_argument('--no-sandbox')
                # chrome_options.add_argument('--disable-gpu')
                # chrome_options.add_argument('-- headless')
                # browser = webdriver.Chrome(executable_path=os.getenv('CHROMEDRIVER_PATH'),
                #                            chrome_options=chrome_options)
                # browser.maximize_window()

                options = Options()
                options.binary_location = os.getenv('GOOGLE_CHROME_BIN')
                options.add_argument("disable-infobars")                # disabling infobars
                options.add_argument("--disable-extensions")            # disabling extensions
                options.add_argument("--disable-gpu")                   # applicable to windows os only
                options.add_argument("--disable-dev-shm-usage")         # overcome limited resource problems
                # options.add_argument("--no-sandbox")                    # Bypass OS security model
                options.add_argument("--headless")

                browser = webdriver.Chrome(executable_path=os.getenv('CHROMEDRIVER_PATH'), options=options)
                # browser = webdriver.Chrome('chromedriver/chromedriver', options=options)
                browser.set_window_size(1920, 1080)
        except Exception as ex:
                logger_main.critical('Error appeared while creating chromedriver', exc_info=True)
                send_message(data['chat_id'], data['token'], ex)
                return

        try:
                browser.get(data['link'])
                sleep(2)
                start_button = browser.find_element(By.NAME, value='startQuiz')
                start_button.click()
                test_execution(browser)
                List_name, List_value = right_answer(browser)

                browser.find_element(by=By.NAME, value='restartQuiz').click()
                sleep(0.1)
                start_button.click()

                test_execution(browser, List_name, List_value, data['time'], data['incorrect_answer'])
                result = send_data(browser, data['email'], data['surname'])

                with rlock:
                        # browser.find_element(by=By.TAG_NAME, value='body').screenshot('Result.png')
                        browser.get_screenshot_as_file('Result.png')
                        browser.quit()
                        send_message(data['chat_id'], data['token'], result)
        except NoSuchElementException as ex:
                logger_main.warning('The link does not correct or the server is overloaded', exc_info=True)
                send_message(data['chat_id'], data['token'], ex)
        except InvalidArgumentException as ex:
                logger_main.warning('The link does not correct', exc_info=True)
                send_message(data['chat_id'], data['token'], ex)
        except Exception as ex:
                logger_main.error('Not obvious error', exc_info=True)
                send_message(data['chat_id'], data['token'], ex)

def test_execution(browser, List_name=None, List_value=None, time=0, inccorect_answer=0):
        """Заполнение правильных ответов"""

        if inccorect_answer != 0:
                list_range = list(range(len(List_value)))
                if inccorect_answer > len(List_value):
                        inccorect_answer = len(List_value)
                for item in range(inccorect_answer):
                        tmp = random.choice(list_range)
                        list_range.remove(tmp)
                        if List_value[tmp] == '4' or List_value[tmp] == '3':
                                List_value[tmp] = 2
                        else:
                                List_value[tmp] = 3

        item = 0
        number_answer = 0
        for Check in browser.find_elements(by=By.NAME, value='check'):
                if List_name:
                        answer = browser.find_elements(by=By.CLASS_NAME,
                                                       value="wpProQuiz_questionInput")[number_answer]
                        name_answer = answer.get_attribute('name')
                        value_correct_answer = List_value[List_name.index(name_answer)]
                        sleep(time)

                        browser.execute_script(
                                "arguments[0].click();",
                                browser.find_element(
                                        by=By.XPATH,
                                        value=f"//input[@name='{name_answer}' and "
                                              f"@value='{value_correct_answer}']"
                                )
                        )
                        number_answer += 4

                Check.click()
                browser.find_elements(by=By.NAME, value='next')[item].click()
                item = item + 1

def right_answer(browser):
        List_name = []
        List_value = []
        for item in browser.find_elements(
                by=By.XPATH,
                value="//li[@class='wpProQuiz_questionListItem wpProQuiz_answerCorrect']//label//input"
        ):
                List_name.append(item.get_attribute('name'))
                List_value.append(item.get_attribute('value'))
        return List_name, List_value


def send_data(browser, mail, surname):
        try:
                browser.find_element(by=By.NAME, value='wpProQuiz_toplistName').send_keys(surname)
                browser.find_element(by=By.NAME, value='wpProQuiz_toplistEmail').send_keys(mail)
                browser.find_element(by=By.NAME, value='wpProQuiz_toplistAdd').click()
                browser.find_element(by=By.TAG_NAME, value='body').send_keys(Keys.HOME)
        except NoSuchElementException as ex:
                return 'error_send_data'

def send_message(chat_id, token, result):
        data = {
                'chat_id': chat_id
        }
        params = {
                'parse_mode': 'html'
        }
        url = f"https://api.telegram.org/bot{token}"

        if result == None or result == 'error_send_data':
                if result:
                        caption = '<b>❗ Тест вже закритий ❗</b>\n\n' \
                                  '<i>Або вам потрібно лише фото, ' \
                                  'або ви занадто пізно вирішили проходити тестування 🙁</i>'
                else:
                        caption = '<b>Тест пройдений 🫡</b>'

                data['caption'] = caption

                with open('Result.png', 'rb') as f:
                        files = {'document': f}
                        r = requests.post(url=f'{url}/sendDocument', data=data, files=files, params=params)

                os.remove('Result.png')
                logger_main.info('The code executing without any mistakes')
        else:
                if isinstance(result, InvalidArgumentException):
                        caption = '❗ Ви відправили не корректне посилання ❗'
                elif isinstance(result, NoSuchElementException):
                        caption = '<b>❗ Ви надіслали не коректне посилання, ' \
                                  'або сервери сайту перенавантажені ❗</b>\n\n' \
                                  '<i>Якщо проблема не зникає з часом, прошу вас написати мені в чат </i>'
                else:
                        caption = '<b>❗ Незрозуміла помилка, напишіть будь ласка мені в чат❗</b>'

                with rlock:
                        db.db_sync_update_amount_test(chat_id, thread_connection)

                data['text'] = caption
                r = requests.post(url=f'{url}/sendMessage', data=data, params=params)
                logger_main.info(f'The sms send to client: {r.status_code}')


########################################################################################################################


async def time_for_test(link, time):
        if time == 0:
                time_for_pass_test = 10 + 30
        else:
                page = requests.get(link)
                soup = BeautifulSoup(page.text, "html.parser")

                amount_question = len(soup.findAll('li', class_='wpProQuiz_listItem'))
                time_for_pass_test = (time * amount_question) + 30

        time_for_pass_test_minutes = time_for_pass_test // 60
        time_for_pass_test_seconds = time_for_pass_test - time_for_pass_test_minutes * 60
        text = f'⏳ Виконання тесту ≈ {time_for_pass_test_minutes} хв {time_for_pass_test_seconds} с'
        return text


