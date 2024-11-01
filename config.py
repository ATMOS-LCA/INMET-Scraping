from json import load, dump
import os

DEFAULT_CONFIG = {
  "output_location": "/home/alanlopes/dev/INMET-Scraping/data",
  "scrap_url": "https://tempo.inmet.gov.br/TabelaEstacoes/",
  "top_size": 12,
  "scrap_rate_limit": 20,
  "scrap_link_retry": 10,
  "csv_delimiter": ";",
  "stations": {
    "agua clara":"A756",
    "amambai":"A750",
    "aquidauana":"A719",
    "bataguassu":"A759",
    "campo grande":"A702",
    "cassilandia":"A742",
    "chapadao do sul":"A730",
    "corumba":"A724",
    "costa rica":"A760",
    "coxim":"A720",
    "dourados":"A721",
    "itaquirai":"A752",
    "ivinhema":"A709",
    "jardim":"A758",
    "juti":"A749",
    "maracaju":"A731",
    "miranda":"A722",
    "nhumirim":"A717",
    "paranaiba":"A710",
    "ponta pora":"A703",
    "porto murtinho":"A723",
    "rio brilhante":"A743",
    "sao gabriel do oeste":"A732",
    "sete quedas":"A751",
    "sidrolandia":"A754",
    "sonora":"A761",
    "tres lagoas":"A704"
  }
}

def get_config() -> dict:
    """
    Busca a configuração do script em $HOME/.config/inmet-scrap; caso não a encontre, irá criá-la neste caminho.
    """
    home_path = os.environ.get("HOME") or os.environ.get("USERPROFILE")
    config_path = os.path.join(home_path, '.config','inmet-scrap')
    if not os.path.exists(config_path): os.makedirs(config_path)
    config_file_path = os.path.join(config_path, 'config.json')
    if not os.path.exists(config_file_path):
        config = create_config_file(config_path, home_path)
    else:
        with open(f'{config_path}/config.json', 'r') as f: config = load(f)
    if not os.path.exists(config['output_location']): os.makedirs(config['output_location'])
    return config

def create_config_file(config_path: str, home_path: str) -> dict:
    """
    Cria configuração no caminho definido nos parametros, definindo por padrão o caminho de saída como $HOME/inmet-data
    :param config_path: Caminho da configuração, sendo ele sempre $HOME/.config/inmet-scrap
    :param home_path: Pasta home do computador onde está rodando
    """
    output_default_path = os.path.join(home_path, 'inmet-data')
    if not os.path.exists(output_default_path): os.makedirs(output_default_path)
    DEFAULT_CONFIG['output_location'] = output_default_path
    with open(os.path.join(config_path, 'config.json'), 'w') as f:
        dump(DEFAULT_CONFIG, f)
    return dict(DEFAULT_CONFIG)

