from config import get_config
from decimal import Decimal
from mysql import connector
import csv
import os

CONFIG = get_config()

INSERT_DADO_INMET = """
INSERT INTO inmet.dados_estacoes (estacao, data, utc, temperatura, umidade, pto_orvalho, pressao, vento, radiacao, chuva)
    VALUE (%(estacao)s, str_to_date(%(data)s, '%Y-%m-%d'), %(utc)s, %(temperatura)s, %(umidade)s, %(pto_orvalho)s, %(pressao)s, %(vento)s, %(radiacao)s, %(chuva)s)
    ON DUPLICATE KEY UPDATE
                        temperatura = %(temperatura)s,
                        umidade     = %(umidade)s,
                        pto_orvalho = %(pto_orvalho)s,
                        pressao     = %(pressao)s,
                        vento       = %(vento)s,
                        radiacao    = %(radiacao)s,
                        chuva       = %(chuva)s;
"""

def sanitize_scrap_number(value: str) -> str | Decimal | None:
    if len(value) == 0: return None;
    return Decimal(value.replace(',', '.'))

def insert_data_in_database(rows: list[dict[str,str]]):
    connection = connector.connect(
        host=CONFIG["db_host"],
        user=CONFIG["db_user"],
        password=CONFIG["db_password"],
        buffered=True,
    )
    cursor = connection.cursor()
    for row in rows:
        cursor.execute(INSERT_DADO_INMET, row)
    connection.commit()


def start():
    print('Csv data import started')
    files = filter(lambda x : x.endswith('.csv'), os.listdir(CONFIG['output_location']))
    params : list[dict[str, str | Decimal | None]] = []
    csv_data : list[list[str]] = []
    for file in files:
        print(f'Importing {file} started')
        with open(os.path.join(CONFIG['output_location'], file)) as csv_file:
            csv_data = list(csv.reader(csv_file, delimiter=CONFIG['csv_delimiter']))
        for data in csv_data:
            params.append({
                'estacao': CONFIG['stations'][file.replace('.csv', '')],
                'data': data[0],
                'utc': data[1],
                'temperatura': sanitize_scrap_number(data[2]),
                'umidade': sanitize_scrap_number(data[5]),
                'pto_orvalho': sanitize_scrap_number(data[8]),
                'pressao': sanitize_scrap_number(data[11]),
                'vento': sanitize_scrap_number(data[14]),
                'radiacao': sanitize_scrap_number(data[17]),
                'chuva': sanitize_scrap_number(data[18]),
            })
        print(f'{file} imported successfully')
    print('Starting database insertion')
    insert_data_in_database(params)
    print('Finished database insertion')
    print('Csv data imported')







start()