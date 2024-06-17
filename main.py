from fastapi import FastAPI
from pydantic import BaseModel
from statistics import mean, median, stdev
from json import loads

aplicativo = FastAPI()

class Itens(BaseModel):
    nome: str
    id: str
    Linguagem_de_programacao: float
    Engenharia_de_software: float
    Algoritmos: float
    Estrutura_de_dados: float


def banco_de_dados():
    with open("alunos_salvos.txt", "r") as arquivo:
        return arquivo.readlines()


@aplicativo.get('/Alunos_Registrados')
def banco_alunos():

    conteudo = banco_de_dados()
    
    for posicao, item in enumerate(conteudo):
        conteudo[posicao] = loads(item.replace("'", '"'))

    return conteudo


@aplicativo.post('/Adicionar_Aluno')
def criar_aluno(aluno: Itens):

    pessoa = dict()
    notas = dict()

    with open("alunos_salvos.txt", "r") as arquivo:
        linhas = arquivo.read().split(",")

    if aluno.nome == '':
        return {'detail': 'Você precisa digitar o nome do aluno.'}

    for linha in linhas:
        if 'id' in linha:
            if linha[8:-1] == aluno.id or aluno.id == '':
                return {'detail': 'Atenção, ou você deixou de colocar o id ou ele está repetido, por favor, mude o id.'}

    for pessoa_itens in list(aluno)[:2:]:
        pessoa[pessoa_itens[0]] = pessoa_itens[1]

    for corrigir_nota in list(aluno)[2::]:
        if corrigir_nota[1] < 0 or corrigir_nota[1] > 10:
            return {'detail': 'As matérias só aceitam nota entre 0 e 10.'}
        notas[corrigir_nota[0]] = round(corrigir_nota[1], 1)

    pessoa['notas'] = notas

    with open("alunos_salvos.txt", "a+") as arquivo:
        arquivo.write(f'{pessoa}\n')

    return {'detail': 'Aluno cadastrado com sucesso'}


@aplicativo.get('/Ver_resultados_do_aluno/{id_pedido}')
def nota_pega_por_id(id_pedido: str):

    with open("alunos_salvos.txt", "r") as arquivo:
        linhas = arquivo.read().split(",")

    try:
        for item in range(len(linhas)):
            if linhas[item][2:4] == 'id':
                if linhas[item][8:-1] == id_pedido:
                    linha_aluno = item // 5

        with open("alunos_salvos.txt", "r") as arquivo:
            conteudo = arquivo.readlines()[linha_aluno]

        return loads(conteudo.replace("'", '"'))

    except:
        return {'detail': 'O id digitado não está registrado em nosso banco de dados.'}


@aplicativo.get('/Ver_resultados_da_disciplina/{nome_disciplina}')
def resultado_disciplina(nome_disciplina: str):

    nome_disciplina = nome_disciplina.strip().capitalize().replace(' ', '_')

    aluno_e_nota = dict()
    dicionario_organizado = dict()

    linhas = banco_de_dados()

    try:
        for linha in linhas:
            nome = ''
            permitido = False
            numero_nota = ''

            for palavra in linha.split():
                if permitido:
                    for numero in palavra:
                        if numero != ',' and numero != '}':
                            numero_nota += numero
                    for c in linha[10:]:
                        if c == "'":
                            aluno_e_nota[nome] = round(float(numero_nota), 1)
                            break
                        nome += c
                    break
                if nome_disciplina in palavra:
                    permitido = True
                    continue

        if len(aluno_e_nota) == 0:
            return {'detail': f'Não existe resultado para a disciplina de {nome_disciplina}'}
        else:
            for item in sorted(aluno_e_nota.items(), key=lambda x: x[1]):
                dicionario_organizado[item[0]] = item[1]
            return dicionario_organizado

    except:
        return {'detail': 'O nome da matéria digita está incorreto.'}


@aplicativo.get('/Recuperar_dados_estatísticos/{nome_disciplina}')
def estatisticos(nome_disciplina: str):

    nome_disciplina = nome_disciplina.strip().capitalize().replace(' ', '_')

    dados = list()

    linhas = banco_de_dados()

    try:
        for linha in linhas:
            numero_nota = ''       
            permitido = False

            for palavra in linha.split():
                if permitido:
                    for letra in palavra:
                        if letra != ',' and letra != '}':
                            numero_nota += letra
                    dados.append(float(numero_nota))
                    break
                if nome_disciplina in palavra:
                    permitido = True
                    continue

        return {'media': round(mean(dados), 1), 'mediana': round(median(dados), 1), 'desvio_padrao': round(stdev(dados), 1)}

    except:
        return {'detail': 'O nome da matéria digita está incorreto.'}


@aplicativo.get('/Alunos_com_baixo_desempenho/{nome_disciplina}')
def alunos_baixo_desempenho(nome_disciplina: str):

    nome_disciplina = nome_disciplina.strip().capitalize().replace(' ', '_')

    aluno_e_nota = dict()
    dicionario_arrumado = dict()

    linhas = banco_de_dados()

    try:
        for linha in linhas:
            nome = ''
            permitido = False
            numero_nota = ''

            for palavra in linha.split():
                if permitido:
                    for letra in palavra:
                        if letra != ',' and letra != '}':
                            numero_nota += letra
                    if float(numero_nota) < 6:
                        for c in linha[10:]:
                            if c == "'":
                                aluno_e_nota[nome] = round(float(numero_nota), 1)
                                break
                            nome += c
                    break
                if nome_disciplina in palavra:
                    permitido = True
                    continue
    
        if len(aluno_e_nota) == 0:
            return {'detail': f'Não há alunos com nota vermelha para a disciplina {nome_disciplina}.'}
        else:
            for item in sorted(aluno_e_nota.items(), key=lambda x: x[1]):
                dicionario_arrumado[item[0]] = item[1]
            return dicionario_arrumado
    
    except:
        return {'detail': 'O nome da matéria digita está incorreto.'}
