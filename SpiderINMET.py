# Created by Rafael Silva 
# E-mail: rafaelps.fis@gmail.com
# 06/02/2024 UTC
# Updated in 26/05/2024


from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import csv
from stations import stations
import os
import shutil


def start_browser(show_browser: bool = False):
    '''
    This function only starts the browser.
    :param show_browser: a boolean, True for the browser be showed, False for hide it.
    '''
    service = Service(GeckoDriverManager().install())
    firefox_options = Options()
    if show_browser == False:
        firefox_options.add_argument('--headless')
    global browser
    browser = webdriver.Firefox(service=service, options=firefox_options)


def getting_link(parent: str, child: str):
    '''
    Receives a string, compose the link with this string and the parent link and get this link on browser.
    :param child: an string, the final of the link to be composed.
    '''
    composedLink = f'{parent}{child}/'
    browser.get(composedLink)


def verify_data_availability(getLinkAgain: int, limitAttempts: int) -> bool:
    '''
    Verify if the data is available to be downloaded.
    :param getLinkAgain: time, in seconds to wait before try to access link again.
    :param limitAttemps: number limit of tries to access the link.
    '''
    value = False
    element_to_verify = '//thead/tr[1]/th[1]'
    count = 0
    while value == False:
        try:
            value = browser.find_element(By.XPATH, element_to_verify).is_displayed()
            print(f'Data available in {count+1} attempt! Keep going!')

        except:
            print(f'{count} attempt: Data still is unavailable. Trying again...')
            time.sleep(1)
            if count == getLinkAgain:
                getting_link(parentLink, station)
            elif count == limitAttempts:
                break
                # CREATE LOG REPORT
            count += 1
            pass
        # CREATE VALIDATION USING 'CONTINUE' TO JUMP A STATION IF IT IS UNAVAILABLE
    return value

def read_table(table_name: str, separator: str = ',') -> list:
    '''
    receives a .csv file name and its delimiter, in current directory
    and return this file as a list.
    :param table_name: name of .csv file to be readed.
    :param separator: the separator of the .csv file. As default is the coma.
    '''
    data = []
    with open(table_name, 'r', encoding='utf8') as csv_file:
        table = csv.reader(csv_file, delimiter=separator)
        data = list(table)
    return data
    

def download_data():
    '''
    Downloads the actual station data table and return it as a list.
    '''
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
        temp_data = [
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
        ]
        new_rows.append(temp_data)
    return new_rows

def backup_tables() -> None:
    '''
    Copy all .csv files to a backup folder. If this folder doesn't exists, it will be created.
    '''
    if not os.path.exists('./backup'): os.mkdir('./backup')
    #Create a backup folder named with actual date
    backup_folder = f'./backup/{today}'
    if not os.path.exists(backup_folder): os.mkdir(backup_folder)

    #Get the file names in the folder
    files = os.listdir()
    #Copy all csv files to the backup folder
    for file in files:
        if '.csv' in file and 'TEMP' not in file:
            shutil.copy2(f'./{file}', f'{backup_folder}/{file}')

def write_new_csv(table_name: str, old_table: list):
    '''
    NEED TO CREATE: DOCUMENTATION 
    '''
    shutil.copyfile(table_name, f'TEMP{table_name}')
    try:
        with open(f'TEMP{table_name}', 'w', encoding='utf8', newline='') as tabela_csv:
            tabela = csv.writer(tabela_csv, delimiter=';')
            if today == old_table[-1][0]:
                old_table = old_table[0:-24]
            else:
                print('First register today')
                #If it is the first register the day and its the first station, create backup
                if verify_actual_station(stations[table_name[:-4]]) == [True, False]:
                    backup_tables()

            tabela.writerows(old_table)
            tabela.writerows(new_rows)
        os.remove(table_name)
        os.rename(f'TEMP{table_name}', table_name)
        print(f'{table_name} DATA SUCCESFULLY UPDATED!')
    except:
        os.remove(f'TEMP{table_name}')
        print(f'ERROR!!! FAILED TO WRITE NEW CSV FILE FOR {table_name}!!!')
        # NEED TO CREATE: LOG FOR ERROR TO WRITE NEW CSV


def verify_actual_station(actual_station: str) -> list:
    '''
    Verify if the actual station is the first or last station. Returns a list with the status.
    The first element in the list is the first station status and the second is the last station status.
    :param actual_station: the code of actual station.
    '''
    station_status = [False, False]
    first_key = list(stations)[0]
    first_station = stations[first_key]
    last_key = list(stations)[-1]
    last_station = stations[last_key]
    
    if first_station == actual_station:
        station_status[0] = True
    if last_station == actual_station:
        station_status[1] = True 
    return station_status 





###############################################################
#                      PRINCIPAL MODE                         #
###############################################################


today = datetime.today().strftime('%Y-%m-%d')

parentLink = 'https://tempo.inmet.gov.br/TabelaEstacoes/'

start_browser(show_browser = False)

for station in stations:
    getting_link(parentLink, stations[station])
    if not verify_data_availability(10, 20):
        # NEED TO CREATE: LOG FOR UNAVAILABLE DATA IN THE DAY 
        continue
    
    stationCsvName = f'{station}.csv'
    new_rows = download_data()
    old_table = read_table(f'{stationCsvName}', ';') ### VERIFY ITERATION TO READ .CSV FILES
    write_new_csv(f'{stationCsvName}', old_table)
    
browser.quit()
    

