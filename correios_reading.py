import json
import re
import os
from modules.correios_rast import rastreio
from modules.correios_rast import isCod
from more_itertools import sliced 

# Limpa janela
clear = lambda: os.system('cls')
clear()
print('')

# Verifica se o arquivo existe e cria caso não exista
try:
    print('Carregando arquivo...')
    entrada = open('rastreio.txt', 'r')
    print('Arquivo carregado.')
except:
    entrada = open('rastreio.txt', 'w')
    print('Falha ao carregar arquivo. Criando arquivo...')
    entrada.close()
    entrada = open('rastreio.txt', 'r')
    print('Arquivo carregado com sucesso.')

# Verifica se o arquivo existe e cria caso não exista
try:
    output = open('output.txt', 'r')
except:
    output = open('output.txt', 'w')
    output.close()
    output = open('output.txt', 'r')

# Lê listas de entrada e saída de dados
leitorSaida = output.readlines()
leitorSaida.clear()
leitorEntrada = entrada.readlines()

# Usando JSON response dos Correios
listaObjetos = list(sliced(''.join(leitorEntrada).strip(),13))

# Verifica se o usuário deseja adicionar novos itens à lista
while input('Deseja incluir uma nova encomenda à lista? [Y/N]').upper() == 'Y':
    qst2 = input('Informe o código de rastreio: ').upper()
    if len(qst2.strip()) == 13:
        if isCod(qst2) == True:
            for item in listaObjetos:
                if qst2.strip() == item:
                    print('O código informado já foi cadastrado.')
                    break
                else:
                    listaObjetos.append(qst2)
                    break
        else:
            print('O código informado é inválido.')
            break
    else:
        print('O código informado é inválido.')

# Verifica se há itens na lista
contaLista = len(listaObjetos)
if contaLista == 0:
    print('')
    print('NENHUM ITEM ENCONTRADO.')
    print('')

# Loop que pega resultados e insere na lista e remove caracteres indesejados das strings extraídas do JSON reponse do site dos Correios
n = False
removeTxt = 'Informar nº do documento para a fiscalização e entrega do seu objeto. Clique aqui'
for item in listaObjetos:
    try:
        objeto = rastreio(item)
        print('=================')
        leitorSaida.append('=================\n')
        print('INFORMAÇÕES DE RASTREIO DO OBJETO: ' +item)
        leitorSaida.append('INFORMAÇÕES DE RASTREIO DO OBJETO: ' +item +'\n')
        print('=================')
        leitorSaida.append('=================\n')
        for mov in objeto:
            joint = mov['data'].splitlines()
            title = mov['title'].splitlines()
            text = mov['text'].splitlines()
            stringjoint = ''.join(joint)
            stringjoint = re.sub('\s+',' ', stringjoint) # Remove espaços multiplos
            if stringjoint.endswith(' /'):
                stringjoint = stringjoint[:-2]
            stringtitle = ''.join(title)
            stringtext = ''.join(text)
            stringtext = re.sub(' / para País ', ' para País em BRASIL ', stringtext)
            print(stringjoint)
            leitorSaida.append(stringjoint +'\n')
            print(stringtitle)
            leitorSaida.append(stringtitle +'\n')
            if not stringtext == '': # Remove mensagem de "informar documento" se string não estiver vazia
                if re.search(removeTxt, stringtext):
                    newTxt = stringtext.replace(removeTxt,'')
                    if not newTxt.strip() == '':
                        leitorSaida.append(newTxt +'\n')
                        print(newTxt)
                else:
                    leitorSaida.append(stringtext +'\n')
                    print(stringtext)
            leitorSaida.append('-----------------\n')
            print('-----------------')
            if re.search('entregue ao destinatário', stringtitle):
                n = True
        if n == True:         
            if input('O objeto ' +item +' foi entregue, deseja removê-lo da lista de objetos? [Y/N]').upper() == 'Y':
                listaObjetos.remove(item)
                print(item +' removido da lista de rastreio.')
        print('')
        leitorSaida.append('\n')
        n = False    
    except:
        print('Impossível localizar o objeto ' +item +'.')
        leitorSaida.append('Impossível localizar o objeto ' +item +'.\n')
        print(item +' removido da lista de rastreamentos.')
        leitorSaida.append(item +' removido da lista de rastreamentos.\n')
        leitorSaida.append('-----------------\n')
        print('-----------------\n')
        listaObjetos.remove(item)
    

# Grava e fecha os arquivos
output = open('output.txt', 'w')
output.writelines(leitorSaida)
output.close()
mypath = os.path.dirname(os.path.abspath(__file__))
print('Resultados salvos em "' +mypath +r'\rastreio.txt"')
entrada = open('rastreio.txt', 'w')
entrada.writelines(listaObjetos)
entrada.close()
print('Lista de objetos atualizada.')
print('')

# Abre txt
openfile = lambda: os.system('output.txt')
if input('Deseja abrir o arquivo de texto com os resultados? [Y/N]').upper() == 'Y':
    openfile()