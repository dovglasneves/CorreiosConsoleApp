import json
import re
import os
from correios_rast import rastreio
from correios_rast import isCod
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
    print('Falha ao carregar arquivo. \nCriando arquivo...')
    entrada.close()
    entrada = open('rastreio.txt', 'r')
    print('Arquivo carregado com sucesso.')

# Constantes
print('Para responder às perguntas você pode usar Y para confirmar ou qualquer outra tecla para ignorar.\n\nRASTREAMENTO CORREIOS v1.81')
actions = ' [Y/N]'
    
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
while input('Deseja incluir uma nova encomenda à lista?' +actions).upper() == 'Y':
    qst2 = input('Informe o código de rastreio: ').upper()
    if len(qst2.strip()) == 13:
        for item in listaObjetos:
            if qst2.strip() == item:
                print('O código informado já foi cadastrado.')
                break
            else:
                listaObjetos.append(qst2)
                print('Objeto ' +qst2 +' adicionado com sucesso.')                    
                break
    else:
        print('O código informado é inválido.')
    if len(listaObjetos) == 0: # Inclui direto se não houverem itens na lista   
        if len(qst2.strip()) == 13:
            listaObjetos.append(qst2)
            print('Objeto ' +qst2 +' adicionado com sucesso.')
        else:
            print('O código informado é inválido.')            


# Verifica se há itens na lista
contaLista = len(listaObjetos)
if contaLista == 0:
    print('')
    print('NENHUM ITEM ENCONTRADO.')
    print('')

# Loop que pega resultados e insere na lista
removeTxt = 'Informar nº do documento para a fiscalização e entrega do seu objeto. Clique aqui'
listaTemp = listaObjetos
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
            stringtext = re.sub(' / para País ', ' para País BRASIL ', stringtext)
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
                if input('O objeto ' +item +' foi entregue, deseja removê-lo da lista de objetos?' +actions).upper() == 'Y':
                    listaTemp.remove(item)
                    print(item +' removido da lista de rastreio.')
            leitorSaida.append('\n')
    except:
        print('Impossível localizar o objeto ' +item +'.')
        leitorSaida.append('Impossível localizar o objeto ' +item +'.\n')
        if input('O objeto ' +item +' não foi encontrado, deseja removê-lo?' +actions) == 'Y':
            print(item +' removido da lista de rastreamentos.')
            leitorSaida.append(item +' removido da lista de rastreamentos.\n')
            listaTemp.remove(item)
        leitorSaida.append('-----------------\n')
        print('-----------------\n')
listaObjetos = listaTemp    

# Grava e fecha os arquivos
output = open('output.txt', 'w')
output.writelines(leitorSaida)
output.close()
mypath = os.path.dirname(os.path.abspath(__file__))
print('Resultados salvos em "' +mypath +r'\rastreio.txt"')
entrada = open('rastreio.txt', 'w')
entrada.writelines(listaObjetos)
entrada.close()
print('Lista de objetos atualizada. \n')

# Abre txt
openfile = lambda: os.system('output.txt')
if input('Deseja abrir o arquivo de texto com os resultados?' +actions).upper() == 'Y':
    openfile()