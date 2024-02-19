#!/usr/bin/python
# encoding: utf-8
# filename: producaoArtistica.py
#
#  scriptLattes V8
#  Copyright 2005-2013: Jesús P. Mena-Chalco e Roberto M. Cesar-Jr.
#  http://scriptlattes.sourceforge.net/
#
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

from scriptLattes.geradorDePaginasWeb import *
from scriptLattes.util import similaridade_entre_cadeias


class ProducaoArtistica:
    item = None # dado bruto
    idMembro = None
    idLattes = None

    relevante = None
    autores = None
    titulo = None
    ano = None
    chave = None


    def __init__(self, idMembro, partesDoItem, relevante):
        # partesDoItem[0]: Numero (NAO USADO)
        # partesDoItem[1]: Descricao
        self.idMembro = set([])
        self.idMembro.add(idMembro)

        self.relevante = relevante
        self.item = partesDoItem[1]

        # Dividir o item na suas partes constituintes
        #if " . " in self.item:
        #    partes = self.item.partition(" . ")
        #else:
        #    partes = self.item.partition(".. ")

        if " . " in self.item and len(self.item.partition(" . ")[2])>=30:
            partes = self.item.partition(" . ")
        elif (".. " in self.item) and len(self.item.partition(".. ")[2])>=30:
            partes = self.item.partition(".. ")
        else: 
            partes = self.item.partition(". ")

        self.autores = partes[0].strip()
        partes = partes[2]

        partes = partes.partition(". ")
        self.titulo = partes[0].strip().rstrip(".").rstrip(",")
        partes = partes[2]

        aux = re.findall('((?:19|20)\d\d)\\b', partes)
        if len(aux)>0:
            self.ano = aux[-1].strip().rstrip(".").rstrip(",")
        else:
            self.ano = ''

        self.chave = self.autores # chave de comparação entre os objetos


    def compararCom(self, objeto):
        if self.idMembro.isdisjoint(objeto.idMembro) and similaridade_entre_cadeias(self.titulo, objeto.titulo):
            # Os IDs dos membros são agrupados. 
            # Essa parte é importante para a criação do GRAFO de colaborações
            self.idMembro.update(objeto.idMembro)

            if len(self.autores)<len(objeto.autores):
                self.autores = objeto.autores

            if len(self.titulo)<len(objeto.titulo):
                self.titulo = objeto.titulo

            return self
        else: # nao similares
            return None


    def html(self, listaDeMembros):
        s = self.autores + '. <b>' + self.titulo + '</b>. '
        s+= str(self.ano) + '.'  if str(self.ano).isdigit() else '.'
        s+= menuHTMLdeBuscaPA(self.titulo)
        return s


    # ------------------------------------------------------------------------ #
    def __str__(self):
        s  = "\n[PRODUCAO ARTISTICA] \n"
        s += "+ID-MEMBRO   : " + str(self.idMembro) + "\n"
        s += "+RELEVANTE   : " + str(self.relevante) + "\n"
        s += "+AUTORES     : " + self.autores.encode('utf8','replace') + "\n"
        s += "+TITULO      : " + self.titulo.encode('utf8','replace') + "\n"
        s += "+ANO         : " + str(self.ano) + "\n"
        s += "+item        : " + self.item.encode('utf8','replace') + "\n"
        return s
