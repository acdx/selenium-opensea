from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pyvirtualdisplay import Display  # this is for linux server workaround
import threading
import time

EXTENSION_PATH = '10.0.2_0.crx'
SEED_STRING = "SEED_STRING_HERE"
PASSWORD_STRING = "PASSWORD_STRING_HERE"
NUM_INSTANCES = 4 # Change this to increase number of agents
USE_HEADLESS = False


def startup_selenium_and_metamask(driver):

    # Wait for metamask tab to popup
    windows = driver.window_handles
    driver.switch_to.window(windows[0])
    time.sleep(1.5)

    # Click on "Get Started"
    driver.find_element_by_xpath('//button[text()="Get Started"]').click()
    time.sleep(1.5)

    # Click on "Import wallet"
    driver.find_element_by_xpath('//button[text()="Import wallet"]').click()
    time.sleep(1.5)

    # Click on "No Thanks"
    driver.find_element_by_xpath('//button[text()="No Thanks"]').click()
    time.sleep(1.5)

    # Fill seed and password stuff
    inputs = driver.find_elements_by_xpath('//input')
    time.sleep(1.5)
    inputs[0].send_keys(SEED_STRING)
    inputs[1].send_keys(PASSWORD_STRING)
    inputs[2].send_keys(PASSWORD_STRING)

    # Confirm all forms
    driver.find_element_by_css_selector('.first-time-flow__terms').click()
    time.sleep(1.5)
    driver.find_element_by_xpath('//button[text()="Import"]').click()
    time.sleep(3)
    driver.find_element_by_xpath('//button[text()="All Done"]').click()
    time.sleep(1.5)
    driver.close()
    windows = driver.window_handles
    driver.switch_to.window(windows[0])
    return driver


def run_one_bot_instance():
    # For linux server only (non-gui command-line servers)
    # display = Display(visible=0, size=(800, 600))
    # display.start()

    opt = webdriver.ChromeOptions()

    if USE_HEADLESS: # enable this only if you're running on a server / dont want too many popups
        opt.add_argument("--headless")
    opt.add_extension(EXTENSION_PATH)

    with webdriver.Chrome(options=opt) as driver:
        print(f"{threading.currentThread().getName()}: Initializing metamask extension...")
        driver = startup_selenium_and_metamask(driver)

        # Login to metamask on opensea
        print(f"{threading.currentThread().getName()}: Logging into metamask...")
        driver.get("https://opensea.io/wallet/locked?referrer=%2Faccount")
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[text()="Sign In"]')))
        except Exception:
            print(f"{threading.currentThread().getName()}: unable to find sign_in_button")

        # Login to the popup for metamask
        driver.find_element_by_xpath('//button[text()="Sign In"]').click()
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        windows = driver.window_handles
        driver.switch_to.window(windows[1])
        time.sleep(3)
        driver.find_element_by_xpath('//button[text()="Next"]').click()
        time.sleep(1.5)
        driver.find_element_by_xpath('//button[text()="Connect"]').click()
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(1))
        # Switch back to main window
        windows = driver.window_handles
        driver.switch_to.window(windows[0])

        for i in range(1, 7778): # change the range to change number of pages
            print(f"{threading.currentThread().getName()}: Getting collection item {i}")
            driver.get(f"https://opensea.io/assets/0x3bf2922f4520a8ba0c2efc3d2a1539678dad5e9d/{i}")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[text()="Make Offer"]')))
            driver.find_element_by_xpath('//button[text()="Make Offer"]').click()

            print(f"{threading.currentThread().getName()}: Making bid...")
            price_input = driver.find_element_by_xpath("/html/body/div[8]/div/div/div/section/div[1]/div[2]/div/div[1]/input")
            price_input.send_keys("0.0001")
            offer_expiration_type = driver.find_element_by_xpath("/html/body/div[8]/div/div/div/section/div[2]/div[2]/div[1]/div[1]")
            offer_expiration_type.click()
            time.sleep(1.5)
            custom_date_type = driver.find_element_by_xpath('//span[text()="Custom date"]')
            custom_date_type.click()
            time.sleep(1.5)

            print(f"{threading.currentThread().getName()}: Confirming bid...")
            print(f"{threading.currentThread().getName()}: Collection item {i} successfully bid!")

if __name__ == "__main__":
    thread_list = list()
    for i in range(NUM_INSTANCES):
        t = threading.Thread(name='Bot agent {}'.format(i), target=run_one_bot_instance)
        t.start()
        time.sleep(1)
        print(t.name + ' started!')
        thread_list.append(t)

    for thread in thread_list:
        thread.join()
