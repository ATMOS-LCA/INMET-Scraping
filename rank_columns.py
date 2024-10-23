import os
import pandas as pd
from pprint import pprint

HEADER = ['Cod. Estação', 'Nome Estação', 'Data', 'Hora', 'Temperatura Inst. (°C)', 'Temperatura Max. (°C)',
          'Temperatura Min. (°C)', 'Umidade Inst. (%)', 'Umidade Max. (%)', 'Umidade Min. (%)',
          'Pto. Orvalho Inst. (°C)', 'Pto. Orvalho Max. (°C)', 'Pto. Orvalho Min. (°C)', 'Pressão Inst. (hPa)',
          'Pressão Max. (hPa)', 'Pressão Min. (hPa)', 'Vento Vel. (m/s)', 'Vento Dir. (°)', 'Vento Raj. (m/s)',
          'Radiação (Kj/m²)', 'Precipitação (mm)']

def generate_top(data: list[list[str]], size: int, date: str, output_path: str) -> None:
    BASE_PATH = f"{output_path}/ranks/{date}"
    if not os.path.exists(BASE_PATH): os.makedirs(BASE_PATH)
    df = pd.DataFrame(data, columns=HEADER)
    pprint(df)
    grouped = df.groupby('Cod. Estação')
    max_temp = grouped['Temperatura Inst. (°C)'].max().reset_index()
    max_temp = max_temp.sort_values(by='Temperatura Inst. (°C)', ascending=False).reset_index()
    max_temp = max_temp.drop(columns='index')
    max_temp = max_temp.head(size)
    max_temp.replace('', '-')
    max_temp.to_csv(f'{BASE_PATH}/top{size}_temperatura_maxima.csv')
    pprint(max_temp)
    min_temp = grouped['Temperatura Inst. (°C)'].min().reset_index()
    min_temp = min_temp.sort_values(by='Temperatura Inst. (°C)', ascending=True).reset_index()
    min_temp = min_temp.drop(columns='index')
    min_temp = min_temp.head(size)
    min_temp.replace('', '-')
    min_temp.to_csv(f'{BASE_PATH}/top{size}_temperatura_minima.csv')
    pprint(min_temp)
    umid = grouped['Umidade Inst. (%)'].min().reset_index()
    umid = umid.sort_values(by='Umidade Inst. (%)', ascending=True).reset_index()
    umid = umid.drop(columns='index')
    umid = umid.head(size)
    umid = pd.DataFrame(umid)
    umid.to_csv(f'{BASE_PATH}/top{size}_umidade_relativa.csv')
    pprint(umid)
    precip = grouped['Precipitação (mm)'].max().reset_index()
    precip = precip.sort_values(by='Precipitação (mm)', ascending=False).reset_index()
    precip = precip.drop(columns='index')
    precip = precip.head(size)
    precip.replace('', '-')
    precip.to_csv(f'{BASE_PATH}/top{size}_precipitacao.csv')
    pprint(precip)