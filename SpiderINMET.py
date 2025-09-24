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
import psycopg2
from config import get_config
from decimal import Decimal

TODAY = datetime.now(UTC).strftime('%Y-%m-%d')
CONFIG = get_config()
logger = Logger()

INSERT_DADO_INMET = """
INSERT INTO inmet.dados_estacoes (estacao, data, utc, temperatura, temperatura_min, temperatura_max, umidade, umidade_min, umidade_max, pto_orvalho, pto_orvalho_min, pto_orvalho_max, pressao, pressao_min, pressao_max, vento, vento_dir, vento_raj, radiacao, chuva)
VALUES (
    %(estacao)s,
    TO_DATE(%(data)s, 'YYYY-MM-DD'),
    %(utc)s,
    %(temperatura)s,
    %(temperatura_min)s,
    %(temperatura_max)s,
    %(umidade)s,
    %(umidade_min)s,
    %(umidade_max)s,
    %(pto_orvalho)s,
    %(pto_orvalho_min)s,
    %(pto_orvalho_max)s,
    %(pressao)s,
    %(pressao_min)s,
    %(pressao_max)s,
    %(vento)s,
    %(vento_dir)s,
    %(vento_raj)s,
    %(radiacao)s,
    %(chuva)s)
ON CONFLICT (estacao, data, utc) 
DO UPDATE SET
    temperatura = %(temperatura)s,
    temperatura_min = %(temperatura_min)s,
    temperatura_max = %(temperatura_max)s,    
    umidade     = %(umidade)s,
    umidade_min = %(umidade_min)s, 
    umidade_max = %(umidade_max)s, 
    pto_orvalho = %(pto_orvalho)s,
    pto_orvalho_max = %(pto_orvalho_max)s,
    pto_orvalho_min = %(pto_orvalho_min)s,
    pressao     = %(pressao)s,
    pressao_min = %(pressao_min)s,
    pressao_max = %(pressao_max)s,
    vento       = %(vento)s,
    vento_dir   = %(vento_dir)s,
    vento_raj   = %(vento_raj)s,
    radiacao    = %(radiacao)s,
    chuva       = %(chuva)s;
"""

def get_db_connection():
    return psycopg2.connect("dbname=%s user=%s password=%s host=%s port=%s" % (CONFIG["db_database"], CONFIG["db_user"], CONFIG["db_password"], CONFIG["db_host"], CONFIG["db_port"]))

def start_browser(show_browser: bool = False) -> WebDriver:
    logger.log("Starting WebDriver")
    service = Service(GeckoDriverManager().install())
    firefox_options = Options()
    if not show_browser:
        firefox_options.add_argument('--headless')
    logger.log("WebDriver started")
    return webdriver.Firefox(service=service, options=firefox_options)

def verify_data_availability(browser: WebDriver, station: str, get_link_again: int, limit_attempts: int) -> bool:
    value = False
    element_to_verify = '//thead/tr[1]/th[1]'
    count = 0
    logger.log("Verifying data availability for station %s" % (station))
    while not value:
        try:
            value = browser.find_element(By.XPATH, element_to_verify).is_displayed()
            logger.log('Data available in %s attempt! Keep going!' % (count + 1))
        except:
            logger.log('%s attempt: Data still is unavailable. Trying again...' % (count))
            time.sleep(1)
            if count == get_link_again:
                browser.get('%s%s/' % (CONFIG["scrap_url"], station))
            elif count == limit_attempts:
                logger.log('Retry limit exceeded')
                break
            count += 1
    return value

def read_table(file_name: str) -> list[list[str]]:
    logger.log("Reading table %s" % (file_name))
    with open('%s/%s' % (CONFIG["output_location"], file_name), 'r', encoding='utf8') as csv_file:
        return list(csv.reader(csv_file, delimiter=CONFIG['csv_delimiter']))

def sanitize_scrap_number(value: str) -> str | Decimal | None:
    if len(value) == 0: return None
    return Decimal(value.replace(',', '.'))

def download_data(browser: WebDriver, station: str) ->  list[dict[str, str | Decimal | None]]:
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
    new_rows = []

    for i in range(len(hora)):
        new_rows.append({
                'estacao': station,
                'data': '%s-%s-%s' % (data[i].text.split('/')[2], data[i].text.split('/')[1], data[i].text.split('/')[0]),
                'utc': hora[i].text,
                'temperatura': sanitize_scrap_number(str(temp_inst[i].text)),
                'temperatura_min': sanitize_scrap_number(str(temp_min[i].text)),
                'temperatura_max': sanitize_scrap_number(str(temp_max[i].text)),
                'umidade': sanitize_scrap_number(str(umidade_inst[i].text)),
                'umidade_min': sanitize_scrap_number(str(umidade_min[i].text)),
                'umidade_max': sanitize_scrap_number(str(umidade_max[i].text)),
                'pto_orvalho': sanitize_scrap_number(str(pto_orvalho_inst[i].text)),
                'pto_orvalho_min': sanitize_scrap_number(str(pto_orvalho_min[i].text)),
                'pto_orvalho_max': sanitize_scrap_number(str(pto_orvalho_max[i].text)),
                'pressao': sanitize_scrap_number(str(pressao_inst[i].text)),
                'pressao_min': sanitize_scrap_number(str(pressao_min[i].text)),
                'pressao_max': sanitize_scrap_number(str(pressao_max[i].text)),
                'vento': sanitize_scrap_number(str(vento_vel[i].text)),
                'vento_dir': sanitize_scrap_number(str(vento_dir[i].text)),
                'vento_raj': sanitize_scrap_number(str(vento_raj[i].text)),
                'radiacao': sanitize_scrap_number(str(radiacao[i].text)),
                'chuva': sanitize_scrap_number(str(chuva[i].text)),
            })
    return new_rows

def backup_tables() -> None:
    if not os.path.exists('%s/backup' % (CONFIG["output_location"])): os.mkdir('%s/backup' % (CONFIG["output_location"]))
    backup_folder = '%s/backup/%s' % (CONFIG["output_location"], TODAY)
    if not os.path.exists(backup_folder): os.mkdir(backup_folder)
    files = os.listdir(path=CONFIG['output_location'])
    for file in files:
        if '.csv' in file and 'TEMP' not in file:
            shutil.copy2('%s/%s' % (CONFIG["output_location"], file), '%s/%s' % (backup_folder, file))

def update_csv(table_name: str, old_table_rows: list[list[str]], new_rows: list[list[str]]) -> None:
    shutil.copyfile("%s/%s" % (CONFIG['output_location'], table_name), '%s/TEMP%s' % (CONFIG['output_location'], table_name))
    logger.log("updating table %s" % (table_name))
    try:
        with open('%s/TEMP%s' % (CONFIG['output_location'], table_name), 'w', encoding='utf8', newline='') as csv_table:
            table = csv.writer(csv_table, delimiter=CONFIG['csv_delimiter'])
            if TODAY == old_table_rows[-1][0]:
                old_table_rows = old_table_rows[0:-24]
            else:
                logger.log('First register today')
                if verify_actual_station(CONFIG['stations'][table_name[:-4]]) == [True, False]:
                    backup_tables()
            table.writerows(old_table_rows)
            table.writerows(new_rows)
        os.remove("%s/%s" % (CONFIG['output_location'], table_name))
        os.rename('%s/TEMP%s' % (CONFIG['output_location'], table_name), "%s/%s" % (CONFIG['output_location'], table_name))
        logger.log('%s DATA SUCCESSFULLY UPDATED!' % (table_name))
    except Exception as e:
        os.remove('%s/TEMP%s' % (CONFIG['output_location'], table_name))
        logger.log('Exception thrown while trying to update table \n Exception: %s' % (e))

def create_csv(table_name: str, rows: list[list[str]]):
    logger.log("creating table %s" % (table_name))
    with open("%s/%s" % (CONFIG['output_location'], table_name), 'w', encoding='utf8', newline='') as tabela_csv:
        csv.writer(tabela_csv, delimiter=CONFIG['csv_delimiter']).writerows(rows)
    logger.log('%s DATA SUCCESSFULLY CREATED!' % (table_name))

def verify_actual_station(actual_station: str) -> list:
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

def insert_data_in_database(rows: list[dict[str,str]]):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        for row in rows:
            cursor.execute(INSERT_DADO_INMET, row)
        conn.commit()
    except Exception as e:
        print(rows)
        logger.log("Database error: %s" % (e))
    finally:
        if conn:
            conn.close()

def start():
    logger.log("Starting INMET scrapping")
    browser = start_browser(show_browser=False)
    rows: list[dict[str, str | Decimal | None]] = []
    for station in CONFIG['stations']:
        logger.log("Reading station %s | code %s" % (station, CONFIG['stations'][station]))
        browser.get('%s%s/' % (CONFIG['scrap_url'], CONFIG['stations'][station]))
        if not verify_data_availability(browser, CONFIG['stations'][station], CONFIG['scrap_link_retry'],CONFIG['scrap_rate_limit']):
            logger.log("Data unavailable for station %s, skipping" % (station))
            continue
        rows += download_data(browser, CONFIG['stations'][station])
    insert_data_in_database(rows)
    browser.quit()
    logger.log("INMET scraping finished")

start()