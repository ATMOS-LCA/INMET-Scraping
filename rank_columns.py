import os

import pandas as pd

from pandas import DataFrame
from pandas.core.groupby import DataFrameGroupBy


HEADER = ['Cod. Estação', 'Nome Estação', 'Data', 'Hora', 'Temperatura Inst. (°C)', 'Temperatura Max. (°C)',
          'Temperatura Min. (°C)', 'Umidade Inst. (%)', 'Umidade Max. (%)', 'Umidade Min. (%)',
          'Pto. Orvalho Inst. (°C)', 'Pto. Orvalho Max. (°C)', 'Pto. Orvalho Min. (°C)', 'Pressão Inst. (hPa)',
          'Pressão Max. (hPa)', 'Pressão Min. (hPa)', 'Vento Vel. (m/s)', 'Vento Dir. (°)', 'Vento Raj. (m/s)',
          'Radiação (Kj/m²)', 'Precipitação (mm)']

def generate_top(data: list[list[str]], size: int, date: str, output_path: str) -> None:
    """
    Raqueia as colunas Temperatura Inst. (°C), Umidade Inst. (%) e Precipitação (mm)  com dados de todas as estações
    :param data: Matriz com dados de todas as estações
    :param size: Tamanho do rank
    :param date: Data do rank
    :param output_path: Caminho base para os arquivos do rank
    """
    BASE_PATH = f"{output_path}/ranks/{date}"
    if not os.path.exists(BASE_PATH): os.makedirs(BASE_PATH)
    df = remove_none_rows(pd.DataFrame(data, columns=HEADER).replace('', None), ['Temperatura Inst. (°C)', 'Umidade Inst. (%)', 'Precipitação (mm)'])
    grouped = df.groupby('Cod. Estação')
    rank_column(grouped, 'Temperatura Inst. (°C)', False, size, BASE_PATH, 'temperatura_maxima')
    rank_column(grouped, 'Temperatura Inst. (°C)', True, size, BASE_PATH, 'temperatura_minima', 'min')
    rank_column(grouped, 'Umidade Inst. (%)', False, size, BASE_PATH, 'umidade_relativa', 'min')
    rank_column(grouped, 'Precipitação (mm)', False, size, BASE_PATH, 'precipitacao')


def rank_column(groupedData: DataFrameGroupBy, target_column: str, ascending: bool, size: int, output_path: str,
                name: str, method: str = 'max') -> None:
    ((groupedData[target_column].max().reset_index() if method == 'max' else groupedData[target_column]
      .min()
      .reset_index())
     .sort_values(by=target_column, ascending=ascending)
     .head(size)
     .to_csv(f'{output_path}/top{size}_{name}.csv'))
