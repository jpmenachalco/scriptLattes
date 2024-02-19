#!/usr/bin/python
# encoding: utf-8
# filename: organizacaoDeEvento.py
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


import re
from scriptLattes.util import similaridade_entre_cadeias


class OrganizacaoDeEvento:
    item = None  # dado bruto
    idMembro = []

    autores = None
    nomeDoEvento = None
    natureza = None
    ano = None
    chave = None

    def __init__(self, idMembro, partesDoItem=''):
        self.idMembro = set([])
        self.idMembro.add(idMembro)

        if not partesDoItem == '':
            # partesDoItem[0]: Numero (NAO USADO)
            # partesDoItem[1]: Descricao
            self.item = partesDoItem[1]

            # Dividir o item na suas partes constituintes
            partes = self.item.partition(" . ")
            self.autores = partes[0].strip()
            partes = partes[2]

            aux = re.findall(' \((.*?)\)', partes)
            if len(aux) > 0:
                self.natureza = aux[-1]
                partes = partes.rpartition(" (")
                partes = partes[0]
            else:
                self.natureza = ''

            aux = re.findall('\. ((?:19|20)\d\d)\\b', partes)
            if len(aux) > 0:
                self.ano = aux[-1]
                partes = partes.rpartition(" ")
                partes = partes[0]
            else:
                self.ano = ''

            self.nomeDoEvento = partes.strip().rstrip(".").rstrip(",")
            self.chave = self.autores  # chave de comparação entre os objetos

        else:
            self.autores = ''
            self.nomeDoEvento = ''
            self.natureza = ''
            self.ano = ''

    def compararCom(self, objeto):
        if self.idMembro.isdisjoint(objeto.idMembro) and similaridade_entre_cadeias(self.nomeDoEvento,
                                                                                    objeto.nomeDoEvento):
            # Os IDs dos membros são agrupados.
            # Essa parte é importante para a criação do GRAFO de colaborações
            self.idMembro.update(objeto.idMembro)

            if len(self.autores) < len(objeto.autores):
                self.autores = objeto.autores

            if len(self.nomeDoEvento) < len(objeto.nomeDoEvento):
                self.nomeDoEvento = objeto.nomeDoEvento

            if len(self.natureza) < len(objeto.natureza):
                self.natureza = objeto.natureza

            return self
        else:  # nao similares
            return None

    def html(self, listaDeMembros):
        s = self.autores + '. <b>' + self.nomeDoEvento + '</b>. '
        s += str(self.ano) + '. ' if str(self.ano).isdigit() else '. '
        s += self.natureza if not self.natureza == '' else ''
        return s

    # ------------------------------------------------------------------------ #
    def __str__(self):
        s = "\n[ORGANIZACAO DE EVENTO]\n"
        s += "+ID-MEMBRO   : " + str(self.idMembro) + "\n"
        s += "+AUTORES     : " + self.autores.encode('utf8', 'replace') + "\n"
        s += "+EVENTO      : " + self.nomeDoEvento.encode('utf8', 'replace') + "\n"
        s += "+ANO         : " + str(self.ano) + "\n"
        s += "+NATUREZA    : " + self.natureza.encode('utf8', 'replace') + "\n"
        #		s += "+item         : @@" + self.item.encode('utf8','replace') + "@@\n"
        return s
