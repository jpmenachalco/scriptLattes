#!/usr/bin/env python 
# encoding: utf-8
#
#
#  scriptLattes
#  Copyright http://scriptlattes.sourceforge.net/
#
#  Este programa é um software livre; você pode redistribui-lo e/ou 
#  modifica-lo dentro dos termos da Licença Pública Geral GNU como 
#  publicada pela Fundação do Software Livre (FSF); na versão 2 da 
#  Licença, ou (na sua opinião) qualquer versão.
#
#  Este programa é distribuído na esperança que possa ser util, 
#  mas SEM NENHUMA GARANTIA; sem uma garantia implicita de ADEQUAÇÂO a qualquer
#  MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a
#  Licença Pública Geral GNU para maiores detalhes.
#
#  Você deve ter recebido uma cópia da Licença Pública Geral GNU
#  junto com este programa, se não, escreva para a Fundação do Software
#  Livre(FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#
#import logging
import os
import shutil
import sys
import Levenshtein

SEP     = os.path.sep
BASE    = 'scriptLattes' + SEP
ABSBASE = os.path.abspath('.') + SEP


class OutputStream:
    def __init__(self, output, encoding):
        self.encoding = encoding
        self.output = output

    def write(self, text):
        try:
            text = text.decode(self.encoding)
        except:
            try:
                text = text.decode('utf8').encode('iso-8859-1')
            except:
                try:
                    text = text.encode('iso-8859-1')
                except:
                    pass
        try:
            self.output.write(text)
        except:
            try:
                self.output.write(str(text))
            except:
                self.output.write('ERRO na impressao')


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

    # shutil.copy2(os.path.join(base, 'css', 'scriptLattes.css'), dir)
    # shutil.copy2(os.path.join(base, 'css', 'jquery.dataTables.css'), dir)

    #shutil.copy2(os.path.join(base, 'imagens', 'lattesPoint0.png'), dir)
    #shutil.copy2(os.path.join(base, 'imagens', 'lattesPoint1.png'), dir)
    #shutil.copy2(os.path.join(base, 'imagens', 'lattesPoint2.png'), dir)
    #shutil.copy2(os.path.join(base, 'imagens', 'lattesPoint3.png'), dir)
    #shutil.copy2(os.path.join(base, 'imagens', 'lattesPoint_shadow.png'), dir)
    shutil.copy2(os.path.join(base, 'imagens', 'doi.png'), dir)

    try:
        dst = os.path.join(dir, 'images')
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(os.path.join(base, 'images'), dst)
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
    :param qualis:
    :return: A medida de similaridade entre as cadeias, de 0 a 1.
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

    if qualis:
        dist = Levenshtein.ratio(str1, str2)
        if len(str1) >= 10 and len(str2) >= 10 and dist >= 0.90:
            # return 1
            return dist

    else:
        if len(str1) >= 10 and len(str2) >= 10 and Levenshtein.distance(str1, str2) <= 5:
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

