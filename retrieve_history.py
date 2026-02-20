from decimal import Decimal
from config import get_config
from Logger import Logger
import os
import csv
import psycopg2

def read_csv(file_path: str, delimiter: str) -> list[list[str]]:
    encodings = ['utf-8', 'iso-8859-1', 'cp1252', 'ascii']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file_csv:
                return list(csv.reader(file_csv, delimiter=delimiter))
        except UnicodeDecodeError:
            continue
        except Exception as e:
            raise e
    
    raise UnicodeDecodeError('utf-8', b'', 0, 1, f'Could not decode file {file_path} with any of the attempted encodings: {encodings}')

CONFIG = get_config()
HIST_FILES_PATH = './dados_historicos'
DB_CONN = psycopg2.connect("dbname=%s user=%s password=%s host=%s port=%s" % (CONFIG["db_database"], CONFIG["db_user"], CONFIG["db_password"], CONFIG["db_host"], CONFIG["db_port"]))
INSERT_DADO_INMET = """
INSERT INTO inmet.dados_estacoes (estacao, data, utc, temperatura, temperatura_min, temperatura_max, umidade, umidade_min, umidade_max, pto_orvalho, pto_orvalho_min, pto_orvalho_max, pressao, pressao_min, pressao_max, vento, vento_dir, vento_raj, radiacao, chuva)
VALUES (%(estacao)s, TO_DATE(%(data)s, 'YYYY-MM-DD'), %(utc)s, %(temperatura)s, %(temperatura_min)s, %(temperatura_max)s, %(umidade)s, %(umidade_min)s, %(umidade_max)s, %(pto_orvalho)s, %(pto_orvalho_min)s, %(pto_orvalho_max)s, %(pressao)s, %(pressao_min)s, %(pressao_max)s, %(vento)s, %(vento_dir)s, %(vento_raj)s, %(radiacao)s, %(chuva)s)
ON CONFLICT (estacao, data, utc) 
DO UPDATE SET
    temperatura = %(temperatura)s,
    temperatura_min = %(temperatura_min)s,
    temperatura_max = %(temperatura_max)s,
    umidade     = %(umidade)s,
    umidade_min = %(umidade_min)s,
    umidade_max = %(umidade_max)s,
    pto_orvalho = %(pto_orvalho)s,
    pto_orvalho_min = %(pto_orvalho_min)s,
    pto_orvalho_max = %(pto_orvalho_max)s,
    pressao     = %(pressao)s,
    pressao_min = %(pressao_min)s,
    pressao_max = %(pressao_max)s,
    vento       = %(vento)s,
    vento_dir   = %(vento_dir)s,
    vento_raj   = %(vento_raj)s,
    radiacao    = %(radiacao)s,
    chuva       = %(chuva)s;
"""
logger = Logger()

def sanitize_scrap_number(value: str) -> str | Decimal | None:
    if len(value) == 0 or value == '-9999': return None;
    return Decimal(value.replace(',', '.'))

def insert_data_in_database(rows: list[dict[str,str | Decimal | None]]):
    cursor = DB_CONN.cursor()
    for row in rows:
        cursor.execute(INSERT_DADO_INMET, row)
    DB_CONN.commit()
    cursor.close()
def test_connection():
    cursor = DB_CONN.cursor()
    cursor.execute("SELECT 1;")
    DB_CONN.commit()
    cursor.close()
    

def start():
    logger.log('start retrieve of historic data')
    logger.log('testing connection with database')
    test_connection()
    logger.log('database connected')
    files = os.listdir(HIST_FILES_PATH)
    logger.log('got %s databases, starting iteration' % (len(files)))
    csv_data = []
    for file in files:
        logger.log('reading data from %s' % (file))
        params : list[dict[str, str | Decimal | None]] = []
        csv_data : list[list[str]] = []
        csv_data = read_csv(os.path.join(HIST_FILES_PATH, file), CONFIG['csv_delimiter'])
        estacao = csv_data[3][1]
        csv_data = csv_data[9:]
        for data in csv_data:
            params.append({
            'estacao': estacao,
            'data': data[0],
            'utc': str(data[1]).replace(':', '').removesuffix(' UTC'),
            'temperatura': sanitize_scrap_number(data[7]),
            'temperatura_min': sanitize_scrap_number(data[10]),
            'temperatura_max': sanitize_scrap_number(data[9]),
            'umidade': sanitize_scrap_number(data[15]),
            'umidade_min': sanitize_scrap_number(data[14]),
            'umidade_max': sanitize_scrap_number(data[13]),            
            'pto_orvalho': sanitize_scrap_number(data[8]),
            'pto_orvalho_min': sanitize_scrap_number(data[12]),
            'pto_orvalho_max': sanitize_scrap_number(data[11]),
            'pressao': sanitize_scrap_number(data[3]),
            'pressao_min': sanitize_scrap_number(data[5]),
            'pressao_max': sanitize_scrap_number(data[4]),
            'vento': sanitize_scrap_number(data[18]),
            'vento_dir': sanitize_scrap_number(data[16]),
            'vento_raj': sanitize_scrap_number(data[17]),
            'radiacao': sanitize_scrap_number(data[6]),
            'chuva': sanitize_scrap_number(data[2])
            })
        logger.log('read finished successfully for %s' % (file))
        logger.log('starting persistency in database')
        insert_data_in_database(params)
        logger.log('data persisted successfully for %s' % (file))
        
start()

