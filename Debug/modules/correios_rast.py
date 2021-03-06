#! /usr/bin/python
# -*- coding: utf-8 -*-

from lxml import html
import requests
import argparse
import re
import os
import sys

GR = '\033[0;30m'  # gray
RR = '\033[1;31m'  # red bold
R = '\033[0;31m'  # red
GG = '\033[1;32m'  # green bold
G = '\033[0;32m'  # green
YY = '\033[1;33m'  # yellow bold
Y = '\033[0;33m'  # yellow
BB = '\033[1;34m'  # blue bold
B = '\033[0;34m'  # blue
P = '\033[1;35m'  # purple
C = '\033[0;36m'  # cyan
D = '\033[0;0m'   # default


def parseArgs():
    parser = argparse.ArgumentParser(
        prog='rastreio',
        usage='%(prog)s [OPTIONS]',
        description='Script para rastrear pacotes dos correios'
    )

    parser.add_argument("-c", metavar="<codigo1[,codigo2,codigo3],...>", type=str, help="códigos para rastreio")
    parser.add_argument("-f", metavar="caminho", type=str, help="caminho do arquivo com os códigos")
    parser.add_argument("-o", metavar="arquivo", type=str, help="arquivo de saida dos resultados")
    parser.add_argument("-r", "--auto-remove", action="store_true", help="remove do arquivo objetos já entregues (apenas se usado com -f)")

    args = parser.parse_args()

    if args.c is None and args.f is None:
        parser.print_help()
        exit(1)

    return args


def escape(strarr):
    text = ' '.join(strarr)

    if sys.version_info.major == 2:
        text = text.encode('utf-8', 'ignore')

    text = text.replace('\r', ' ').replace('\t', ' ').strip()
    text = re.sub(' +', ' ', text)

    return text


def outputObjs(objs, output):
    if output:
        cp = os.getcwd()
        full_path = os.path.join(cp, output)

        print('Escrevendo no arquivo %s' % (full_path,))

        if full_path[-5:] == '.html':
            writeHtml(objs, full_path)
        else:
            with open(full_path, 'w') as file:
                for obj in objs:
                    file.write(header(obj['cod'], False) + os.linesep)

                    for mov in obj['movimentacoes']:
                        file.write(mov['data'] + os.linesep)
                        file.write('=> '+mov['title'].encode('utf-8', 'ignore') + os.linesep)
                        file.write(mov['text'] + os.linesep)
                        file.write('-'*50 + os.linesep)

    else:
        for obj in objs:
            print(header(obj['cod']))

            for mov in obj['movimentacoes']:
                print(YY + mov['data'])
                print(check(mov['title']) + C + mov['title'])
                print(D + mov['text'])
                print(P + '-'*50 + D)


def writeHtml(objs, full_path):
    HTML_STR = '''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
      <title>Rastreamento de Objetos</title>
      <meta http-equiv="content-type" content="text/html; charset=UTF-8">
      <meta charset="utf-8">
      <meta name="description" content="Rastreamento de Objetos dos Correios">
      <meta name="keywords" content="rastreamento,correios,websro,status,pedido atrasado,link rastreamento correios">
      <meta name="author" content="Rennan Cockles">
      <style type="text/css">

        table {
            border-collapse: collapse;
            border-spacing: 5px;
            padding: 10px;
            width: 80%;
        }

        table, th, td {
            border: 1px solid black;
        }

        .true {
            background-color: #037208;
            color: white;
        }
        
      </style>
    </head>

    <body>
        <center>
        <br>
        <div class="container">
    '''

    for obj in objs:
        body = '''
            <div>
                <h2>{}</h2>
                </br>
                <table class="table table-bordered {}">
                    <thead>
                        <tr>
                            <th>Data / Hora</th>
                            <th colspan="3">Status / Localidade</th>
                        </tr>
                    </thead>
                    <tbody>

        '''.format(obj['cod'], str(isEntregue(obj)).lower())

        for mov in obj['movimentacoes']:
            body += '''
            <tr>
                <td rowspan="2">{}</td>
                <td colspan="2"><strong>{}</strong></td>
            </tr>
            <tr>  
                <td colspan="2">{}</td>
            </tr>

            '''.format(mov['data'], mov['title'].encode('utf-8', 'ignore'), mov['text'])

        body += '''
                </tbody>
            </table>
        </div>
        '''

        HTML_STR += body

    HTML_STR += '''
        </div>
    </body>
    </html>
    '''

    with open(full_path, 'w') as file:
        file.write(HTML_STR)


def extractFromFile(path):
    cp = os.getcwd()
    full_path = os.path.join(cp, path)

    return [line.rstrip() for line in open(full_path) if isCod(line.rstrip())]


def writeInFile(path, objs):
    cp = os.getcwd()
    full_path = os.path.join(cp, path)

    with open(full_path, 'w') as file:
        [file.write(obj['cod'] + os.linesep) for obj in objs if not isEntregue(obj)]


def header(cod, color=True):
    if color:
        return G+'''
            ###################
            #  %s%s%s  #
            ###################
        ''' % (D, cod, G)
    else:
        return '''
            ###################
            #  %s  #
            ###################
        ''' % (cod,)


def isCod(cod):
    if re.match('^[a-zA-Z]{2}[0-9]{9}[a-zA-Z]{2}$', cod):
        return True
    return False


def isEntregue(obj):
    titles = [mov['title'] for mov in obj['movimentacoes']]
    return True in ['entregue' in title for title in titles]


def check(status):
    if 'postado' in status:
        color = RR
    elif 'entregue' in status:
        color = GG
    elif 'entrega' in status:
        color = YY
    else:
        color = BB

    return color + '=> '


def rastreio(obj):
    movimentacoes = []
    s = requests.Session()

    obj_post = {
        'objetos': obj,
        'btnPesq': '+Buscar'
    }

    s.headers.update({
        'Host': 'www2.correios.com.br',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'http://www2.correios.com.br/sistemas/rastreamento/default.cfm',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': '37',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })

    r = s.post('https://www2.correios.com.br/sistemas/rastreamento/resultado.cfm?', data=obj_post, allow_redirects=True)
    r.encoding = 'ISO-8859-1'

    if r.status_code == 200:
        if r.text.find('listEvent') == -1:
            print('[#] Erro na requisição')
            return None

        tree = html.fromstring(r.text.encode('latin1'))
        trs = tree.xpath('//table[contains(@class,"listEvent")]/tr')

        for tr in trs:
            tds = tr.xpath('./td')

            data = escape(tds[0].xpath('./text() | ./label/text()'))
            text = escape(tds[1].xpath('./text()'))
            title = tds[1].xpath('./strong/text()')[0]

            movimentacoes.append({'data': data, 'title': title, 'text': text})

    return movimentacoes


if __name__ == '__main__':
    args = parseArgs()
    auto_remove = args.auto_remove
    codigos = []

    if args.f:
        codigos += extractFromFile(args.f)

    if args.c:
        codigos += [cod for cod in args.c.split(',') if isCod(cod)]

    # remove duplicatas
    codigos = list(set(codigos))

    if len(codigos) >= 1:
        objs = [{'cod': cod, 'movimentacoes': rastreio(cod)} for cod in codigos]

        outputObjs(objs, args.o)

        if auto_remove and args.f:
            writeInFile(args.f, objs)
