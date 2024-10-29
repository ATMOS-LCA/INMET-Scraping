from selenium import webdriver
from selenium.webdriver.ie.webdriver import WebDriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from Logger import Logger
import time
from datetime import datetime, UTC
import csv
import os
import shutil
from rank_columns import generate_top
from config import get_config

TODAY = datetime.now(UTC).strftime('%Y-%m-%d')
CONFIG = get_config()
logger = Logger()


def start_browser(show_browser: bool = False) -> WebDriver:
    '''
    This function only starts the browser.
    :param show_browser: a boolean, True for the browser be showed, False for hide it.
    '''
    logger.log("Starting WebDriver")
    service = Service(GeckoDriverManager().install())
    firefox_options = Options()
    if not show_browser:
        firefox_options.add_argument('--headless')
    logger.log("WebDriver started")
    return webdriver.Firefox(service=service, options=firefox_options)

def verify_data_availability(browser: WebDriver, station: str, get_link_again: int, limit_attempts: int) -> bool:
    """
    Verify if the data is available to be downloaded.
    :param browser: navigator webdriver
    :param station: station to be verified
    :param get_link_again: time, in seconds to wait before try to access link again.
    :param limit_attempts: number limit of tries to access the link.
    """
    value = False
    element_to_verify = '//thead/tr[1]/th[1]'
    count = 0
    logger.log(f"Verifying data availability for station {station}")
    while not value:
        try:
            value = browser.find_element(By.XPATH, element_to_verify).is_displayed()
            logger.log(f'Data available in {count + 1} attempt! Keep going!')
        except Exception:
            logger.log(f'{count} attempt: Data still is unavailable. Trying again...')
            time.sleep(1)
            if count == get_link_again:
                browser.get(f'{CONFIG['scrap_url']}{station}/')
            elif count == limit_attempts:
                logger.log(f'Retry limit exceeded')
                break
            count += 1
    return value

def read_table(table_name: str) -> list:
    """
    receives a .csv file name and its delimiter, in current directory
    and return this file as a list.
    :param table_name: name of .csv file to be read.
    :param separator: the separator of the .csv file. As default is the coma.
    """
    logger.log(f"Reading table {table_name}")
    data = []
    with open(table_name, 'r', encoding='utf8') as csv_file:
        data = list(csv.reader(csv_file, delimiter=CONFIG['csv_delimiter']))
    return data

def download_data(browser: WebDriver) ->  list[list[str]]:
    """
    Downloads the actual station data table and return it as a list.
    """
    data = browser.find_elements(By.XPATH, '//tbody/tr/td[1]')
    hora = browser.find_elements(By.XPATH, '//tbody/tr/td[2]')
    temp_inst = browser.find_elements(By.XPATH, '//tbody/tr/td[3]')
    temp_max = browser.find_elements(By.XPATH, '//tbody/tr/td[4]')
    temp_min = browser.find_elements(By.XPATH, '//tbody/tr/td[5]')
    umidade_inst = browser.find_elements(By.XPATH, '//tbody/tr/td[6]')
    umidade_max = browser.find_elements(By.XPATH, '//tbody/tr/td[7]')
    umidade_min = browser.find_elements(By.XPATH, '//tbody/tr/td[8]')
    pto_orvalho_inst = browser.find_elements(By.XPATH, '//tbody/tr/td[9]')
    pto_orvalho_max = browser.find_elements(By.XPATH, '//tbody/tr/td[10]')
    pto_orvalho_min = browser.find_elements(By.XPATH, '//tbody/tr/td[11]')
    pressao_inst = browser.find_elements(By.XPATH, '//tbody/tr/td[12]')
    pressao_max = browser.find_elements(By.XPATH, '//tbody/tr/td[13]')
    pressao_min = browser.find_elements(By.XPATH, '//tbody/tr/td[14]')
    vento_vel = browser.find_elements(By.XPATH, '//tbody/tr/td[15]')
    vento_dir = browser.find_elements(By.XPATH, '//tbody/tr/td[16]')
    vento_raj = browser.find_elements(By.XPATH, '//tbody/tr/td[17]')
    radiacao = browser.find_elements(By.XPATH, '//tbody/tr/td[18]')
    chuva = browser.find_elements(By.XPATH, '//tbody/tr/td[19]')
    #  Preparing data
    new_rows = []
    for i in range(len(hora)):
        new_rows.append([
            f'{data[i].text.split('/')[2]}-{data[i].text.split('/')[1]}-{data[i].text.split('/')[0]}',
            hora[i].text,
            temp_inst[i].text,
            temp_max[i].text,
            temp_min[i].text,
            umidade_inst[i].text,
            umidade_max[i].text,
            umidade_min[i].text,
            pto_orvalho_inst[i].text,
            pto_orvalho_max[i].text,
            pto_orvalho_min[i].text,
            pressao_inst[i].text,
            pressao_max[i].text,
            pressao_min[i].text,
            vento_vel[i].text,
            vento_dir[i].text,
            vento_raj[i].text,
            radiacao[i].text,
            chuva[i].text
        ])
    return new_rows

def backup_tables() -> None:
    """
    Copy all .csv files to a backup folder. If this folder doesn't exists, it will be created.
    """
    if not os.path.exists(f'{CONFIG.output_location}/backup'): os.mkdir(f'{CONFIG.output_location}/backup')
    # Create a backup folder named with actual date
    backup_folder = f'{CONFIG.output_location}/backup/{TODAY}'
    if not os.path.exists(backup_folder): os.mkdir(backup_folder)
    #Get the file names in the folder
    files = os.listdir(path=CONFIG.output_location)
    #Copy all csv files to the backup folder
    for file in files:
        if '.csv' in file and 'TEMP' not in file:
            shutil.copy2(f'{CONFIG.output_location}/{file}', f'{backup_folder}/{file}')

def update_csv(table_name: str, old_table: list, new_rows: list) -> None:
    """
    NEED TO CREATE: DOCUMENTATION 
    """
    shutil.copyfile(f"{CONFIG['output_location']}/{table_name}", f'{CONFIG['output_location']}/TEMP{table_name}')
    logger.log(f"updating table {table_name}")
    try:
        with open(f'{CONFIG['output_location']}/TEMP{table_name}', 'w', encoding='utf8', newline='') as csv_table:
            table = csv.writer(csv_table, delimiter=CONFIG['csv_delimiter'])
            if TODAY == old_table[-1][0]:
                old_table = old_table[0:-24]
            else:
                logger.log('First register today')
                #If it is the first register the day and its the first station, create backup
                if verify_actual_station(CONFIG['stations'][table_name[:-4]]) == [True, False]:
                    backup_tables()
            table.writerows(old_table)
            table.writerows(new_rows)
        os.remove(table_name)
        os.rename(f'{CONFIG['output_location']}/TEMP{table_name}', f"{CONFIG['output_location']}/{table_name}")
        logger.log(f'{table_name} DATA SUCCESSFULLY UPDATED!')
    except Exception as e:
        os.remove(f'{CONFIG['output_location']}/TEMP{table_name}')
        logger.log(f'ERROR!!! FAILED TO WRITE NEW CSV FILE FOR {table_name}!!! \n Exception: {e}')
        # NEED TO CREATE: LOG FOR ERROR TO WRITE NEW CSV

def create_csv(table_name: str, rows: list):
    logger.log(f"creating table {table_name}")
    with open(f"{CONFIG['output_location']}/{table_name}", 'w', encoding='utf8', newline='') as tabela_csv:
        csv.writer(tabela_csv, delimiter=CONFIG['csv_delimiter']).writerows(rows)
    logger.log(f'{table_name} DATA SUCCESSFULLY CREATED!')

def verify_actual_station(actual_station: str) -> list:
    """
    Verify if the actual station is the first or last station. Returns a list with the status.
    The first element in the list is the first station status and the second is the last station status.
    :param actual_station: the code of actual station.
    """
    station_status = [False, False]
    first_key = list(CONFIG['stations'])[0]
    first_station = CONFIG['stations'][first_key]
    last_key = list(CONFIG['stations'])[-1]
    last_station = CONFIG['stations'][last_key]
    if first_station == actual_station:
        station_status[0] = True
    if last_station == actual_station:
        station_status[1] = True 
    return station_status 

def start():
    logger.log("Starting INMET scrapping")
    browser = start_browser(show_browser=False)
    join = []
    for station in CONFIG['stations']:
        logger.log(f"Reading station {station} | code {CONFIG['stations'][station]}")
        browser.get(f'{CONFIG['scrap_url']}{CONFIG['stations'][station]}/')
        if not verify_data_availability(browser, CONFIG['stations'][station], CONFIG['scrap_link_retry'],CONFIG['scrap_rate_limit']):
            logger.log(f"Data unavailable for station {station}, skipping")
            continue
        station_csv_name = f'{station}.csv'
        new_rows = download_data(browser)
        for new_row in new_rows:
            join.append([CONFIG['stations'][station], station] + new_row)
        old_table = []
        file_exist = True
        try:
            old_table = read_table(station_csv_name)  ### VERIFY ITERATION TO READ .CSV FILES
        except FileNotFoundError:
            logger.log(f"Table {station_csv_name} not found")
            file_exist = False
        if file_exist:
            update_csv(f'{station_csv_name}', old_table, new_rows)
            continue
        create_csv(station_csv_name, new_rows)
    browser.quit()
    logger.log("INMET scraping finished")
    generate_top(join, CONFIG['top_size'], TODAY, CONFIG['output_location'])

start()