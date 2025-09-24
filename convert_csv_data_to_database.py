from config import get_config
from decimal import Decimal
import psycopg2
import csv
import os
from multiprocessing import Pool

CONFIG = get_config()

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

def sanitize_scrap_number(value: str) -> str | Decimal | None:
    if len(value) == 0: return None;
    return Decimal(value.replace(',', '.'))

def insert_data_in_database(rows: list[dict[str,str]]):
    connection = psycopg2.connect("dbname=%s user=%s password=%s host=%s port=%s" % (CONFIG["db_database"], CONFIG["db_user"], CONFIG["db_password"], CONFIG["db_host"], CONFIG["db_port"]))
    cursor = connection.cursor()
    for row in rows:
        cursor.execute(INSERT_DADO_INMET, row)
    connection.commit()
    
def import_data_from_file(file: str):
    print(f'Importing {file} started')
    csv_data = []
    params = []
    with open(os.path.join(CONFIG['output_location'], file)) as csv_file:
        csv_data = list(csv.reader(csv_file, delimiter=CONFIG['csv_delimiter']))
    for data in csv_data[1:]:
        params.append({
            'estacao': CONFIG['stations'][file.replace('.csv', '')] if file != 'bela vista.csv' else 'A757',
            'data': data[0],
            'utc': data[1],
            'temperatura': sanitize_scrap_number(data[2]),
            'temperatura_max': sanitize_scrap_number(data[3]),
            'temperatura_min': sanitize_scrap_number(data[4]),
            'umidade': sanitize_scrap_number(data[5]),
            'umidade_max': sanitize_scrap_number(data[6]),
            'umidade_min': sanitize_scrap_number(data[7]),
            'pto_orvalho': sanitize_scrap_number(data[8]),
            'pto_orvalho_max': sanitize_scrap_number(data[9]),
            'pto_orvalho_min': sanitize_scrap_number(data[10]),
            'pressao': sanitize_scrap_number(data[11]),
            'pressao_max': sanitize_scrap_number(data[12]),
            'pressao_min': sanitize_scrap_number(data[13]),
            'vento': sanitize_scrap_number(data[14]),
            'vento_dir': sanitize_scrap_number(data[15]),
            'vento_raj': sanitize_scrap_number(data[16]),
            'radiacao': sanitize_scrap_number(data[17]),
            'chuva': sanitize_scrap_number(data[18]),
        })
    insert_data_in_database(params)
    print(f'{file} imported successfully')



def start():
    print('Csv data import started')
    files = list(filter(lambda x : x.endswith('.csv'), os.listdir(CONFIG['output_location'])))
    for file in files:
        import_data_from_file(file)        
    print('Starting database insertion')
    print('Finished database insertion')
    print('Csv data imported')

start()