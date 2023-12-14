import configparser
import json
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


def log(text):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f'{timestamp} - {text}\n'
    log_filename = 'logs/TriggerSyncCheck ' + datetime.datetime.now().strftime('%Y-%m-%d') + '.txt'
    with open(log_filename, 'a') as log_file:
        log_file.write(log_message)


def alert_slack(message):
    payload = {
        "text": f"*{vp_name}*: {message}",
    }

    headers = {
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        log(f"ERROR ||  HTTP Error: {err}")
    except requests.exceptions.ConnectionError as err:
        log(f"ERROR ||  Error Connecting: {err}")
    except requests.exceptions.RequestException as err:
        log(f"ERROR || {err}")


def check_loading():
    try:
        loading_flag = True
        is_object_loaded = True
        loop_count = 0
        while loading_flag or is_object_loaded:
            loop_count = loop_count + 1
            if loop_count >= 50:
                break
            loading_flag = driver.execute_script("return loadActiveTabFlag;")
            is_object_loaded = driver.execute_script("return isObjectLoaded;")
            if loading_flag is None:
                loading_flag = True
            if is_object_loaded is None:
                is_object_loaded = True
            time.sleep(5)
    except Exception as e:
        log(f'ERROR || Check Loading || {e}')


def login():
    current_url = driver.current_url
    if "/vportal/login.html" not in current_url:
        logout()
        driver.get(url)
        driver.implicitly_wait(60)
        log(f"Current URL is: {current_url}")
    # Login to V-Portal
    username = driver.find_element(By.ID, 'username')
    username.send_keys(os.environ.get('VP-Username'))
    password = driver.find_element(By.ID, 'password')
    password.send_keys(os.environ.get('VP-Password'))
    password.send_keys(Keys.RETURN)
    WebDriverWait(driver, 30).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "loading.ui-state-default.ui-state-active"))
    )
    time.sleep(5)
    log(f'V-Portal Login Successful')


def logout():
    # Logout
    driver.execute_script("window.location.href = '/vportal/logout.html?myAuthTypeScript=OWN'")
    driver.implicitly_wait(60)
    log(f'Logged out Successful')


def login_open_project(p):
    # Login to V-Portal
    login()

    # Open Project
    current_url = driver.current_url
    if "/vportal/viewProjectList.html" in current_url or "/vportal/loginSuccess.html" in current_url:
        try:
            js_code = f"openProjectDB('#gridProjectList',{p})"
            driver.execute_script(js_code)
            check_loading()
            log(f'Project: {p} || Project Opened')
        except Exception as e:
            log(f"ERROR || Project {p} not found || {e}")
            pass

    driver.implicitly_wait(60)


def get_project_details():
    try:
        # Login to V-Portal
        login()

        # Get all project details
        driver.execute_script(f"window.location.href = '/vportal/getAllProjects.html?'")
        driver.implicitly_wait(60)
        project_response = json.loads(str(BeautifulSoup(driver.page_source, 'html.parser').body.text))
        log("Got the project details")

        logout()

        return project_response["rows"]
    except Exception as e:
        log(f"ERROR || {e}")
        alert_slack(f"Error getting project details")


def get_project_name(p):
    project_name = None
    for project in project_details:
        if project['projectId'] == p:
            project_name = project['projectName']
            break
    return project_name


def trigger_request(p, engine, attempts=3):
    try:
        # Login and Open Project
        login_open_project(p)

        # Check the synchronization status
        driver.execute_script(
            f"window.location.href = '/vportal/triggerEngineSynch.html?mode={engine}&manualTrigger=Y'")
        driver.implicitly_wait(60)
        trigger_status = BeautifulSoup(driver.page_source, 'html.parser').body.text
        if trigger_status == "SUCCESS":
            log(f'Project: {p} || Triggered Sync for {engine} Successful')
        else:
            log(f'Project: {p} || Triggered Sync for {engine} Failed: {trigger_status}')

        # Logout
        logout()
    except Exception as e:
        log(f"ERROR || Trigger Request || {e}")
        if attempts >= 1:
            log(f"ERROR || Retrying || Attempts left: {attempts}")
            time.sleep(60)
            return trigger_request(p, engine, attempts - 1)
        else:
            log("ERROR || Out of attempts. Exiting.")


def trigger_sync(p):
    try:
        # Trigger Request
        trigger_request(p, "APPR")
        trigger_request(p, "NAPPR")

        # Login and Open Project
        login_open_project(p)

        # Open Approved Engine
        js_code = "javascript:openTab('Test App',null,'contentTesting.html?mode=APPR',true)"
        driver.execute_script(js_code)
        check_loading()
        log(f'Project: {p} || Approved Engine Triggered ')

        # Open Non-Approved Engine
        js_code = "javascript:openTab('Test N-App',null,'contentTesting.html?mode=NAPPR',true)"
        driver.execute_script(js_code)
        check_loading()
        log(f'Project: {p} || Non-Approved Engine Triggered ')

        # Logout
        logout()

        log(f'Project: {p} || Trigger Sync Successful')
        alert_slack(f"{get_project_name(p)} - Trigger Sync Successful")
    except Exception as e:
        log(f"ERROR || Trigger Sync || {e}")
        alert_slack(f"{get_project_name(p)} - Trigger Sync Error!")


def get_engine_sync_status(p, engine):
    # Login and Open Project
    login_open_project(p)

    # Check the synchronization status
    driver.execute_script(f"window.location.href = '/vportal/getEngineSyncStatus.html?mode={engine}'")

    while True:
        driver.implicitly_wait(60)
        sync_status_response = driver.page_source
        sync_status = BeautifulSoup(sync_status_response, 'html.parser').body.text

        if sync_status == "C":
            log(f"Project: {p} || Engine: {engine} || Synch Complete")
            alert_slack(f"{get_project_name(p)} - Engine: {engine} - Synch Complete")
            break
        elif sync_status == "P":
            log(f"Project: {p} || Engine: {engine} || Synch in Progress")
            time.sleep(60)
            driver.refresh()
            log(f"Project: {p} || Engine: {engine} || Checking the sync status again")
        else:
            log(f"Project: {p} || Engine: {engine} || Synch process failed!")
            alert_slack(f"{get_project_name(p)} - Engine: {engine} - Synch failed")
            break

    # Logout
    logout()


def check_engine_sync(p):
    log("Starting Engine Sync Check")
    driver.implicitly_wait(300)
    try:
        get_engine_sync_status(p, "APPR")
        get_engine_sync_status(p, "NAPPR")
    except Exception as e:
        log(f"ERROR || {e}")
        alert_slack(f"{get_project_name(p)} - Error Checking Sync Status")


def trigger_and_check(projects):
    for p in projects:
        # Trigger Engine Sync
        trigger_sync(p)
        # Check if the engine has synced
        check_engine_sync(p)


# Create a ConfigParser instance
config = configparser.ConfigParser()

# Read the config file
config.read('config.ini')

# Access the values
url = config.get('V-Portal', 'url')
vp_name = config.get('V-Portal', 'name')
projects_list = config.get('Projects', 'projects')
all_projects = [int(project) for project in projects_list.split(',')]
webhook_url = config.get('Slack', 'webhook')

chrome_options = Options()
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("enable-automation")
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-browser-side-navigation")
chrome_options.add_argument("--disable-gpu")
chrome_options.page_load_strategy = 'eager'

# specify path for webdriver
driver = webdriver.Chrome(options=chrome_options, service=ChromeService(ChromeDriverManager().install()))

# navigate to the website
driver.get(url)
driver.implicitly_wait(60)

# Get Project Details
project_details = get_project_details()

# Trigger sync and check sync status
trigger_and_check(all_projects)

# close the browser
driver.quit()
