#!/usr/bin/env python 
# encoding: utf-8

import os
import shutil
import sys
import re
import unicodedata
from rapidfuzz.distance import Levenshtein


SEP     = os.path.sep
BASE    = 'scriptLattes' + SEP
ABSBASE = os.path.abspath('.') + SEP



def buscarArquivo(filepath, arquivoConfiguracao=None):
    if not arquivoConfiguracao:
        arquivoConfiguracao = sys.argv[1]
    curdir = os.path.abspath(os.path.curdir)
    if not os.path.isfile(filepath) and arquivoConfiguracao:
        # vamos tentar mudar o diretorio para o atual do arquivo
        os.chdir(os.path.abspath(os.path.join(arquivoConfiguracao, os.pardir)))
    if not os.path.isfile(filepath):
        # se ainda nao existe, tentemos ver se o arquivo não está junto com o config
        filepath = os.path.abspath(os.path.basename(filepath))
    else:
        # se encontramos, definimos então caminho absoluto
        filepath = os.path.abspath(filepath)
    os.chdir(curdir)
    return filepath


def copiarArquivos(dir):
    base = ABSBASE
    try:
        dst = os.path.join(dir, 'css')
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(os.path.join(base, 'css'), dst)
    except OSError as e:
        pass  # provavelmente diretório já existe
        #logging.warning(e)

    try:
        dst = os.path.join(dir, 'js')
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(os.path.join(base, 'js'), dst)
    except OSError as e:
        pass  # provavelmente diretório já existe
        #logging.warning(e)
    # shutil.copy2(os.path.join(base, 'js', 'jquery.min.js'), dir)
    # shutil.copy2(os.path.join(base, 'js', 'highcharts.js'), dir)
    # shutil.copy2(os.path.join(base, 'js', 'exporting.js'), dir)
    # shutil.copy2(os.path.join(base, 'js', 'drilldown.js'), dir)
    # shutil.copy2(os.path.join(base, 'js', 'jquery.dataTables.min.js'), dir)
    # shutil.copy2(os.path.join(base, 'js', 'jquery.dataTables.rowGrouping.js'), dir)

    print(f"\n[ARQUIVOS SALVOS NO SEGUINTE DIRETÓRIO]\n{format(os.path.abspath(dir))}")

# ---------------------------------------------------------------------------- #
def similaridade_entre_cadeias(str1, str2, qualis=False):
    '''
    Compara duas cadeias de caracteres e retorna a medida de similaridade entre elas, entre 0 e 1, onde 1 significa que as cadeias são idênticas ou uma é contida na outra.
    :param str1:
    :param str2:
    '''
    str1 = str1.strip().lower()
    str2 = str2.strip().lower()

    # caso especial
    if ('apresentação'==str1 or 'apresentação'==str2 or 'apresentacao'==str1 or 'apresentacao'==str2 ):
        return 0

    if len(str1) == 0 or len(str2) == 0:
        return 0

    if len(str1) >= 50 and len(str2) >= 50 and (str1 in str2 or str2 in str1):
        return 1

    distancia  = distancia_Levenshtein(str1, str2)
    ratio = ...
 
    if len(str1) >= 10 and len(str2) >= 10 and (ratio >= 0.93 or distancia <= 5):
        return 1

    return 0


def criarDiretorio(dir):
    if not os.path.exists(dir):
        try:
            os.makedirs(dir)
        ### except OSError as exc:
        except:
            print("\n[ERRO] Não foi possível criar ou atualizar o diretório: " + dir.encode('utf8'))
            print("[ERRO] Você conta com as permissões de escrita? \n")
            return 0
    return 1

# Combining Dictionaries Of Lists
def merge_dols(dol1, dol2):
    if type(dol1) == list:
        #print(f"LISTA: {dol1}")
        result = {**dol2}
    else:
        result = {**dol1, **dol2}
    # result = dict(dol1, **dol2)
    # result = dict()
    result.update((k, dol1[k] + dol2[k]) for k in set(dol1).intersection(dol2))
    return result


def eliminar_acentuacao(texto: str) -> str:
    """
    Remove a acentuação de uma string, mantendo apenas os caracteres base.
    """
    nfkd = unicodedata.normalize('NFKD', texto)
    return ''.join(
        c for c in nfkd
        if not unicodedata.combining(c)
    )

def normalizar_texto(texto: str) -> str:
    """
    Normaliza uma string para comparação:
      1. Remove acentuação.
      2. Converte para minúsculas.
      3. Remove tudo que não for letra (a–z) ou dígito (0–9).
    """
    # 1) retirar acentos
    texto_sem_acentos = eliminar_acentuacao(texto)
    # 2) caixa baixa
    texto_minusculo = texto_sem_acentos.lower()
    # 3) remove pontuação, espaços e demais caracteres
    texto_limpo = re.sub(r'[^a-z0-9]', '', texto_minusculo)
    return texto_limpo


def distancia_levenshtein(a: str, b: str) -> int:
    """
    Calcula a distância de Levenshtein entre as cadeias a e b
    (algoritmo de Wagner–Fischer).
    Complexidade: O(n·m) em tempo e O(min(n, m)) em espaço.
    """
    n, m = len(a), len(b)
    # garante que n >= m
    if n < m:
        return distancia_levenshtein(b, a)

    anterior = list(range(m + 1))
    for i, ca in enumerate(a, start=1):
        atual = [i] + [0] * m
        for j, cb in enumerate(b, start=1):
            custo_inserir    = anterior[j] + 1
            custo_deletar    = atual[j - 1] + 1
            custo_substituir = anterior[j - 1] + (ca != cb)
            atual[j] = min(custo_inserir, custo_deletar, custo_substituir)
        anterior = atual

    return anterior[m]


def similaridade_entre_cadeias(cadeia1: str, cadeia2: str, qualis: bool = False) -> int:
    """
    Retorna 1 se as cadeias são consideradas similares, caso contrário 0.
    Critérios:
      - Se uma das cadeias normalizadas for 'apresentacao', 'introducao' ou 'prefacio', retorna 0.
      - Se ambas tiverem len >= 50 e uma contida na outra, retorna 1.
      - Caso contrário, calcula distância e ratio:
         ratio = 1 - (distância / max_len)
      - Se len(cadeia) >= 10 e (ratio >= 0.93 ou distância <= 5), retorna 1.
    """
    # 1) normalização
    c1 = normalizar_texto(cadeia1)
    c2 = normalizar_texto(cadeia2)

    # caso especial
    especiais = {'apresentacao', 'introducao', 'prefacio'}
    if c1 in especiais or c2 in especiais:
        return 0

    # cadeias vazias falham
    if not c1 or not c2:
        return 0

    # contenção para textos longos: um prefixo de outro
    if len(c1) >= 50 and len(c2) >= 50 and (c1 in c2 or c2 in c1):
        return 1

    # cálculo de distância e ratio
    distancia = Levenshtein.distance(c1, c2)
    max_len   = max(len(c1), len(c2))
    ratio     = 1.0 - distancia / max_len if max_len > 0 else 0.0

    # critério final para cadeias longas
    if len(c1) >= 10 and len(c2) >= 10 and (ratio >= 0.93 or distancia <= 5):
        return 1

    return 0

