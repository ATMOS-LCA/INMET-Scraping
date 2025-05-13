from decimal import Decimal
from config import get_config
from Logger import Logger
import os
import csv
import psycopg2

CONFIG = get_config()
HIST_FILES_PATH = './data_old_test'
DB_CONN = psycopg2.connect("dbname=%s user=%s password=%s host=%s port=%s" % (CONFIG["db_database"], CONFIG["db_user"], CONFIG["db_password"], CONFIG["db_host"], CONFIG["db_port"]))
INSERT_DADO_INMET = """
INSERT INTO inmet.dados_estacoes (estacao, data, utc, temperatura, umidade, pto_orvalho, pressao, vento, vento_dir, vento_raj, radiacao, chuva)
VALUES (%(estacao)s, TO_DATE(%(data)s, 'YYYY-MM-DD'), %(utc)s, %(temperatura)s, %(umidade)s, %(pto_orvalho)s, %(pressao)s, %(vento)s, %(vento_dir)s, %(vento_raj)s, %(radiacao)s, %(chuva)s)
ON CONFLICT (estacao, data, utc) 
DO UPDATE SET
    temperatura = %(temperatura)s,
    umidade     = %(umidade)s,
    pto_orvalho = %(pto_orvalho)s,
    pressao     = %(pressao)s,
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
        with open(os.path.join(HIST_FILES_PATH, file), 'r') as file_csv:
            csv_data = list(csv.reader(file_csv, delimiter=CONFIG['csv_delimiter']))
        estacao = csv_data[3][1]
        csv_data = csv_data[9:]
        for data in csv_data:
            params.append({
            'estacao': estacao,
            'data': data[0],
            'utc': str(data[1]).replace(':', '').removesuffix(' UTC'),
            'temperatura': sanitize_scrap_number(data[7]),
            'umidade': sanitize_scrap_number(data[15]),
            'pto_orvalho': sanitize_scrap_number(data[8]),
            'pressao': sanitize_scrap_number(data[4]),
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

