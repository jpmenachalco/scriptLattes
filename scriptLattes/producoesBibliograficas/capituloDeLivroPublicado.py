#!/usr/bin/python
# encoding: utf-8
# filename: capituloDeLivroPublicado.py
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

class CapituloDeLivroPublicado:
    item = None # dado bruto
    idMembro = None

    relevante = None
    autores = None
    titulo = None
    livro = None
    edicao = None
    editora = None
    ano = None
    volume = None
    paginas = None
    chave = None

    def __init__(self, idMembro, partesDoItem='',  relevante=''):
        self.idMembro = set([])
        self.idMembro.add(idMembro)

        if not partesDoItem=='':
            # partesDoItem[0]: Numero (NAO USADO)
            # partesDoItem[1]: Descricao do livro (DADO BRUTO)

            self.item = partesDoItem[1]
            self.relevante = relevante

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

            partes = partes.rpartition(" p.")
            if partes[1]=='': # se nao existem paginas
                self.paginas = ''
                partes = partes[2]
            else:
                self.paginas = partes[2].strip().rstrip(".").rstrip("-").strip()
                partes = partes[0]

            partes = partes.rpartition(" v. ")
            if partes[1]=='': # se nao existem informacao de volume
                self.volume = ''
                partes = partes[2]
            else:
                self.volume = partes[2].rstrip(".").rstrip(",")
                partes = partes[0]

            partes = partes.rpartition(", ")
            self.ano = partes[2].strip().rstrip(".").rstrip(",")
            partes = partes[0]

            partes = partes.rpartition(". ed. ")
            if partes[1]=='': # se nao existe edicao
                self.edicao = ''
                partes = partes[2]
            else:
                partes = partes[0].rpartition(" ")
                self.edicao = partes[2]
                partes = partes[0]

            partes = partes.rpartition(": ")
            if partes[1]=='': # se nao existe editora 
                self.editora = ''
                partes = partes[2]
            else:
                self.editora = partes[2].strip()
                partes = partes[0]

            partes = partes.rpartition(" In: ")
            if partes[1]=='': # se nao existe titulo de livro 
                self.livro = ''
                partes = partes[2]
            else:
                self.livro = partes[2].strip().rstrip(".")
                partes = partes[0]

            self.titulo = partes.strip().rstrip(".")
            self.chave = self.autores # chave de comparação entre os objetos

        else:
            self.relevante = ''
            self.autores = ''
            self.titulo = ''
            self.livro = ''
            self.edicao = ''
            self.editora = ''
            self.ano = ''
            self.volume = ''
            self.paginas = ''
            self.chave = ''


    def compararCom(self, objeto):
        if self.idMembro.isdisjoint(objeto.idMembro) and similaridade_entre_cadeias(self.titulo, objeto.titulo):
            # Os IDs dos membros são agrupados. 
            # Essa parte é importante para a criação do GRAFO de colaborações
            self.idMembro.update(objeto.idMembro)

            if len(self.autores)<len(objeto.autores):
                self.autores = objeto.autores

            if len(self.titulo)<len(objeto.titulo):
                self.titulo = objeto.titulo

            if len(self.livro)<len(objeto.livro):
                self.livro = objeto.livro

            if len(self.edicao)<len(objeto.edicao):
                self.edicao = objeto.edicao
            
            if len(self.editora)<len(objeto.editora):
                self.editora = objeto.editora

            if len(self.volume)<len(objeto.volume):
                self.volume = objeto.volume

            if len(self.paginas)<len(objeto.paginas):
                self.paginas = objeto.paginas

            return self
        else: # nao similares
            return None


    def html(self, listaDeMembros):
        s = self.autores + '. <b>' + self.titulo + '</b>. Em: ' + self.livro + '. '
        s+= self.edicao + ' ed. '       if not self.edicao==''  else ''
        s+= ': ' + self.editora + '. '  if not self.editora==''  else ''
        s+= str(self.ano) + '.'         if str(self.ano).isdigit() else ''

        s+= 'v. ' + self.volume + ', '  if not self.volume== '' else ''
        s+= 'p. ' + self.paginas + '. ' if not self.paginas=='' else '.'

        s+= menuHTMLdeBuscaPB(self.titulo)
        return s



    def ris(self):
        paginas = self.paginas.split('-')
        if len(paginas)<2:
            p1 = self.paginas
            p2 = ''
        else:
            p1 = paginas[0]
            p2 = paginas[1]
        s = '\n'
        s+= '\nTY  - CHAP'
        s+= '\nAU  - '+self.autores
        s+= '\nT1  - '+self.titulo
        s+= '\nTI  - '+self.livro
        s+= '\nIS  - '+self.edicao
        s+= '\nPB  - '+self.editora
        s+= '\nPY  - '+str(self.ano)
        s+= '\nVL  - '+self.volume
        s+= '\nSP  - '+p1
        s+= '\nEP  - '+p2
        s+= '\nER  - '
        return s

    # ------------------------------------------------------------------------ #
    def __str__(self):
        s  = "\n[CAPITULO DE LIVRO PUBLICADO] \n"
        s += "+ID-MEMBRO   : " + str(self.idMembro) + "\n"
        s += "+RELEVANTE   : " + str(self.relevante) + "\n"
        s += "+AUTORES     : " + self.autores + "\n"
        s += "+TITULO      : " + self.titulo + "\n"
        s += "+LIVRO       : " + self.livro + "\n"
        s += "+EDICAO      : " + self.edicao + "\n"
        s += "+EDITORA     : " + self.editora + "\n"
        s += "+ANO         : " + str(self.ano) + "\n"
        s += "+VOLUME      : " + self.volume + "\n"
        s += "+PAGINAS     : " + self.paginas + "\n"
        s += "+item        : " + self.item + "\n"
        return s
