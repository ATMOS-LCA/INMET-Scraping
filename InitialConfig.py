from stations import stations
import shutil
import os
import csv
import pandas as pd


#Made backup before start process
def backup_tables() -> None:
    '''
    Copy all .csv files to a backup folder. If this folder doesn't exists, it will be created.
    '''
    backup_folder = './initial_backup'
    if not os.path.exists(backup_folder): os.mkdir(backup_folder)

    #Get the file names in the folder
    files = os.listdir()
    #Copy all csv files to the backup folder
    for file in files:
        if '.csv' in file: 
            shutil.copy2(f'./{file}', f'{backup_folder}/{file}')



#Rename the files

def organize_files():
    files = os.listdir()
    for station in stations:
        station_name = station
        station_code = stations[station]
        for file in files:
            if station_code in file:
                write_new_csv(file, read_table(file, ';'))
                os.rename(f'{file}', f'{station}.csv')
                df = pd.read_csv(f'{station}.csv', sep = ';')
                # RENAMING COLUMNS
                df.rename(columns = {
                    'Data Medicao': 'Data',
                    'Hora Medicao': 'Hora',
                    'PRECIPITACAO TOTAL, HORARIO(mm)': 'Precipitação (mm)',
                    'PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA(mB)': 'Pressão Inst. (hPa)',
                    'PRESSAO ATMOSFERICA MAX.NA HORA ANT. (AUT)(mB)':'Pressão Min. (hPa)',
                    'PRESSAO ATMOSFERICA MIN. NA HORA ANT. (AUT)(mB)':'Pressão Max. (hPa)',
                    'RADIACAO GLOBAL(Kj/m²)':'Radiação (Kj/m²)',
                    'TEMPERATURA DO AR - BULBO SECO, HORARIA(°C)':'Temperatura Inst. (°C)',
                    'TEMPERATURA DO PONTO DE ORVALHO(°C)':'Pto. Orvalho Inst. (°C)',
                    'TEMPERATURA MAXIMA NA HORA ANT. (AUT)(°C)':'Temperatura Max. (°C)',
                    'TEMPERATURA MINIMA NA HORA ANT. (AUT)(°C)':'Temperatura Min. (°C)',
                    'TEMPERATURA ORVALHO MAX. NA HORA ANT. (AUT)(°C)':'Pto. Orvalho Max. (°C)',
                    'TEMPERATURA ORVALHO MIN. NA HORA ANT. (AUT)(°C)':'Pto. Orvalho Min. (°C)',
                    'UMIDADE REL. MAX. NA HORA ANT. (AUT)(%)':'Umidade Max. (%)',
                    'UMIDADE REL. MIN. NA HORA ANT. (AUT)(%)':'Umidade Min. (%)',
                    'UMIDADE RELATIVA DO AR, HORARIA(%)':'Umidade Inst. (%)',
                    'VENTO, DIRECAO HORARIA (gr)(° (gr))':'Vento Dir. (°)',
                    'VENTO, RAJADA MAXIMA(m/s)':'Vento Raj. (m/s)',
                    'VENTO, VELOCIDADE HORARIA(m/s)':'Vento Vel. (m/s)'
                }, inplace=True)
                # FILLING 'HORA' COLUMN WITH ZERO LEFT
                df.replace({
                    'Hora': {
                        0: '0000',
                        100: '0100',
                        200: '0200',
                        300: '0300',
                        400: '0400',
                        500: '0500',
                        600: '0600',
                        700: '0700',
                        800: '0800',
                        900: '0900',
                    }
                }, inplace=True)

                # CHANGING COLUMN ORDER
                df = df[[
                    'Data',
                    'Hora',
                    'Temperatura Inst. (°C)',
                    'Temperatura Max. (°C)',
                    'Temperatura Min. (°C)',
                    'Umidade Inst. (%)',
                    'Umidade Max. (%)',
                    'Umidade Min. (%)',
                    'Pto. Orvalho Inst. (°C)',
                    'Pto. Orvalho Max. (°C)',
                    'Pto. Orvalho Min. (°C)',
                    'Pressão Inst. (hPa)',
                    'Pressão Max. (hPa)',
                    'Pressão Min. (hPa)',
                    'Vento Vel. (m/s)',
                    'Vento Dir. (°)',
                    'Vento Raj. (m/s)',
                    'Radiação (Kj/m²)',
                    'Precipitação (mm)'
                    ]]
                df.to_csv(f'{station}.csv', index=False, sep=';')

 
def read_table(table_name: str, separator: str = ',') -> list:
    '''
    receives a .csv file name and his delimiter, in current directory
    and return this file as a list.
    :param table_name: name of .csv file to be readed.
    :param separator: the separator of the .csv file. As default is the coma.
    '''
    data = []
    with open(table_name, 'r', encoding='utf8') as csv_file:
        table = csv.reader(csv_file, delimiter=separator)
        data = list(table)
    return data


#Remove first 10 lines of each .csv

def write_new_csv(table_name: str, old_table: list):
    '''
    
    NEED TO CREATE: DOCUMENTATION
    '''
    shutil.copyfile(table_name, f'TEMP{table_name}')
    try:
        with open(f'TEMP{table_name}', 'w', encoding='utf8', newline='') as tabela_csv:
            tabela = csv.writer(tabela_csv, delimiter=';')
            old_table = old_table[10:-1]
            tabela.writerows(old_table)
        os.remove(table_name)
        os.rename(f'TEMP{table_name}', table_name)
        print(f'{table_name} DATA SUCCESFULLY UPDATED!')
    except:
        os.remove(f'TEMP{table_name}')
        print(f'ERROR!!! FAILED TO WRITE NEW CSV FILE FOR {table_name}!!!')


backup_tables()

organize_files()



