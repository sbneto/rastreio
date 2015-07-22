__author__ = 'Samuel'

import requests
import flask
from collections import OrderedDict
from bs4 import BeautifulSoup


app = flask.Flask(__name__)

# fazer tb para http://websro.correios.com.br/sro_bin/txect01$.startup?P_LINGUA=001&P_TIPO=001
HEADERS = OrderedDict([
    ('Host', 'www2.correios.com.br'),
    ('Connection', 'keep-alive'),
    ('Content-Length', '36'),
    ('Cache-Control', 'max-age=0'),
    ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
    ('Origin', 'http://www2.correios.com.br'),
    ('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36'),
    ('Content-Type', 'application/x-www-form-urlencoded'),
    ('Referer', 'http://www2.correios.com.br/sistemas/rastreamento/'),
    ('Accept-Encoding', 'gzip, deflate'),
    ('Accept-Language', 'en-US,en;q=0.8,pt-BR;q=0.6,pt;q=0.4')
])


def escape(text):
    return text.replace('\r', '').replace('\n', '')


def remove_empty(strings):
    return [s for s in strings if s != '']


def get_highlight(soup):
    table = soup.find('div', {'class': 'highlightSRO'}).find('div', {'display:block': True})
    desc = escape(table.find('strong').text)
    desc_split = remove_empty(escape(table.find('strong').find_next_sibling().text).split(' '))
    timestamp = ' '.join(desc_split[0:2])
    place = ' '.join(desc_split[2:])
    return [timestamp, place, desc]


def get_history(soup):
    table_dt = soup.find('table', {'class': 'listEvent sro'}).find_all('td', {'class': 'sroDtEvent'})
    table_desc = soup.find('table', {'class': 'listEvent sro'}).find_all('td', {'class': 'sroLbEvent'})
    table = []
    for i in range(0, len(table_dt)):
        split_dt = remove_empty(escape(table_dt[i].text).split(' '))
        timestamp = ' '.join(split_dt[0:2])
        place = ' '.join(split_dt[2:])
        desc = ' '.join(remove_empty(escape(table_desc[i].text).split(' ')))
        line = [timestamp, place, desc]
        table.append(line)
    return table


def rastrear(codigo):
    payload = 'objetos=%s&btnPesq=Buscar' % codigo.upper()
    r = requests.post('http://www2.correios.com.br/sistemas/rastreamento/resultado.cfm',
                      headers=HEADERS,
                      data=payload)
    soup = BeautifulSoup(r.text, 'html.parser')
    return [get_highlight(soup)] + get_history(soup)


@app.route('/rastreio/<codigo>')
def rastreio(codigo):
    return '<br>'.join(' --- '.join(line) for line in rastrear(codigo))


codigos = ['LC762162912US',
           'DM570110837BR',
           'DM570798121BR',
           'PI656572677BR',
           'RL103928137CN',
           'DM618163632BR']

if __name__ == '__main__':
    app.run()