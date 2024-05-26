# INMET-Scraping
![Static Badge](https://img.shields.io/badge/LICENSE-MIT-blue) ![Static Badge](https://img.shields.io/badge/Status-In%20development-yellow)

## Sobre
O objetivo deste projeto é coletar dados meteorológicos em tempo real do site do Instituto Nacional de Meteorologia do Brasil (INMET)

## Tecnologies and requeriments
* `Python 3`
* `Selenium`
* `Selenium WebDriver`
* `Pandas`

## Related links

* [Portal do INMET](https://portal.inmet.gov.br/)
* [Catálogo de Estações Automáticas do INMET](https://portal.inmet.gov.br/paginas/catalogoaut)
* [Catálogo de Estações Convencionais do INMET](https://portal.inmet.gov.br/paginas/catalogoman)
* [Banco de Dados do INMET (para download de dados históricos)](https://bdmep.inmet.gov.br/)

## Sobre os dados em tempo real do INMET
O INMET prove em seu portal diferentes tipos de dados. Os dados em tempo real são atualizados a cada hora e podemos acessá-los por meio de tabelas HTML para cada estação.
Como as tabelas são geradas de forma dinâmica foi necessário a utilização de um web driver para a extração dos dados.

**Solução:** Coletar os dados após a execução do script de requisição e criação das tabelas.

### Como este programa funciona?
Basicamente o programa principal segue os seguintes passos:
1. Acessa o link de uma estação específica.
2. Aguarda o script JS gerar a tabela.
3. Coleta os dados da tabela HTML.
4. Insere estes dados na tabela atualmente existente em seu diretório.
5. Se for o primeiro registro do dia cria o backup dos documentos .csv.
6. Realiza esse processo para todas as estações selecionadas.


## Configurando o programa

### Configurações iniciais

Primeiramente você deve ter em mente quais estações deseja coletar os dados em tempo real. Com as estações em mãos coloque-as no arquivo `stations.py` na forma 'nome da estação':'código da estação'.

Se for a primeira vez rodando o script é necessário antes fazer o download dos dados históricos no [Banco de Dados do INMET](https://bdmep.inmet.gov.br/).
No portal você pode optar por quais estações e quais dados quer baixar.

Para o programa de configuração inicial funcionar você deve selecionar:
* Tipo de pontuação: Ponto
* Tipo de Dados: Dados Horários
* Tipo de Estação: Automáticas
* Variáveis: Todas, exceto: 
  * Pressão atmosférica reduzida nivel do mar.
  * Temperatura da CPU da Estação.
  * Tensão da bateria da estação.
Quando os arquivos estiverem disponíveis coloque-os na pasta de sua preferência junto com o script `InitialConfig.py`.
Esse script irá configurar e formatar os arquivos na melhor forma.

### Configurações finais
Agora basta colocar o programa INMET-Spider.py na pasta junto com os arquivos das estações e iniciá-lo.
Para deixar o arquivo rodando automaticamente é necessário criar um cronjob para iniciar o arquivo de hora em hora.
