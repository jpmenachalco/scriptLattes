#!/usr/bin/python
# encoding: utf-8
# filename: orientacaoConcluida.py
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


class OrientacaoConcluida:
    item = None  # dado bruto
    idMembro = []
    idOrientando = ''

    nome = None
    tituloDoTrabalho = None
    ano = None  # ano de conclusao
    instituicao = None
    agenciaDeFomento = None
    tipoDeOrientacao = None
    chave = None

    def __init__(self, idMembro, partesDoItem='', idOrientando=''):
        self.idMembro = set([])
        self.idMembro.add(idMembro)

        if not partesDoItem == '':
            # partesDoItem[0]: Numero (NAO USADO)
            # partesDoItem[1]: Descricao
            self.item = partesDoItem[1]
            self.idOrientando = str(idOrientando)

            # Dividir o item na suas partes constituintes
            partes = self.item.partition(". Orientador: ")
            if not partes[1] == '':
                self.tipoDeOrientacao = 'Orientador'
                partes = partes[0]
            else:
                partes = self.item.partition(". Co-Orientador: ")
                if not partes[1] == '':
                    self.tipoDeOrientacao = 'Co-orientador'
                    partes = partes[0]
                else:
                    self.tipoDeOrientacao = 'Supervisor'
                    partes = partes[0].rpartition('. ')
                    partes = partes[0]

            partes1 = partes.rpartition(". ")
            partes = partes1[2].rpartition(", ")
            if not partes[1] == '':
                self.instituicao = partes[0]
                self.agenciaDeFomento = partes[2]
            else:
                self.instituicao = partes[2]
                self.agenciaDeFomento = ''

            partes = partes1[0]
            aux = re.findall('((?:19|20)\d\d)\\b', partes)
            if len(aux) > 0:
                #self.ano = aux[0]  # .strip().rstrip(".").rstrip(",")
                self.ano = aux[-1].strip().rstrip(".").rstrip(",")

                aux = re.findall('(.*). (?:19|20)\d\d\\b', partes)
                partes = aux[0]
            else:
                self.ano = ''
                partes = partes.rpartition('. ')
                partes = partes[0]

            partes = partes.rpartition('. ')
            if not partes[1] == '':
                self.nome = partes[0].strip(".").strip(",")
                self.tituloDoTrabalho = partes[2]
            else:
                self.nome = partes[2].strip(".").strip(",")
                self.tituloDoTrabalho = ''

            self.chave = self.nome  # chave de comparação entre os objetos

        else:
            self.nome = ''
            self.tituloDoTrabalho = ''
            self.ano = ''
            self.instituicao = ''
            self.agenciaDeFomento = ''
            self.tipoDeOrientacao = ''

    def compararCom(self, objeto):
        if self.idMembro.isdisjoint(objeto.idMembro) and similaridade_entre_cadeias(self.nome, objeto.nome):
            # Os IDs dos membros são agrupados.
            # Essa parte é importante para a criação do GRAFO de colaborações
            self.idMembro.update(objeto.idMembro)

            if len(self.tituloDoTrabalho) < len(objeto.tituloDoTrabalho):
                self.tituloDoTrabalho = objeto.tituloDoTrabalho

            if len(self.instituicao) < len(objeto.instituicao):
                self.instituicao = objeto.instituicao

            if len(self.agenciaDeFomento) < len(objeto.agenciaDeFomento):
                self.agenciaDeFomento = objeto.agenciaDeFomento

            return self
        else:  # nao similares
            return None

    def html(self, listaDeMembros):
        s = '<a href="http://lattes.cnpq.br/' + self.idOrientando + '">' + self.nome + '</a>' if len(
            self.idOrientando) == 16 else self.nome
        s += '. <b>' + self.tituloDoTrabalho + '</b>. '
        s += self.instituicao + ', ' if not self.instituicao == ''  else ''
        s += self.agenciaDeFomento + '. ' if not self.agenciaDeFomento == ''  else '. '

        s += str(self.ano) + '.' if str(self.ano).isdigit() else '.'

        lista = list(self.idMembro)
        if len(lista) == 1:
            m = listaDeMembros[lista[0]]
            s += '<br><i><font size=-1>' + self.tipoDeOrientacao + ': <a href="' + m.url + '">' + m.nomeCompleto + '</a>.</font>'
        else:
            s += '<br><i><font size=-1>Orientadores: '
            for i in lista:
                m = listaDeMembros[i]
                s += '<a href="' + m.url + '">' + m.nomeCompleto + '</a>, '
            s = s.rstrip(', ') + '.</font></i>'

        return s

    # ------------------------------------------------------------------------ #
    def __str__(self):
        s = "\n[ORIENTANDO] \n"
        s += "+ID-ALUNO     : " + self.idOrientando + "\n"
        s += "+NOME         : " + self.nome + "\n"
        s += "+TITULO TRAB. : " + self.tituloDoTrabalho + "\n"
        s += "+ANO CONCLUS. : " + str(self.ano) + "\n"
        s += "+INSTITUICAO  : " + self.instituicao + "\n"
        s += "+AGENCIA      : " + self.agenciaDeFomento + "\n"
        s += "+TIPO ORIENTA.: " + self.tipoDeOrientacao + "\n"
        #		s += "+item         : @@" + self.item.encode('utf8','replace') + "@@\n"

        return s
