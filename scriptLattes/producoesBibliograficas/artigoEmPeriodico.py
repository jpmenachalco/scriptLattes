#!/usr/bin/python
# encoding: utf-8
#
#
# scriptLattes V8
# Copyright 2005-2013: Jesús P. Mena-Chalco e Roberto M. Cesar-Jr.
# http://scriptlattes.sourceforge.net/
#
#
# Este programa é um software livre; você pode redistribui-lo e/ou 
# modifica-lo dentro dos termos da Licença Pública Geral GNU como 
# publicada pela Fundação do Software Livre (FSF); na versão 2 da 
# Licença, ou (na sua opinião) qualquer versão.
#
# Este programa é distribuído na esperança que possa ser util, 
# mas SEM NENHUMA GARANTIA; sem uma garantia implicita de ADEQUAÇÂO a qualquer
# MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a
# Licença Pública Geral GNU para maiores detalhes.
#
# Você deve ter recebido uma cópia da Licença Pública Geral GNU
# junto com este programa, se não, escreva para a Fundação do Software
# Livre(FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#


from scriptLattes.geradorDePaginasWeb import *
from scriptLattes.util import similaridade_entre_cadeias

class ArtigoEmPeriodico:
    item = None  # dado bruto
    idMembro = None
    # qualis = None
    # qualissimilar = None

    # doi = None
    # relevante = None
    # autores = None
    # titulo = None
    # revista = None
    # volume = None
    # paginas = None
    # numero = None
    # ano = None
    resto = None
    chave = None
    # issn = None

    def __init__(self, idMembro, partesDoItem='', doi='', relevante='', complemento=''):
        self.idMembro = set([])
        self.idMembro.add(idMembro)

        self.doi = ''
        self.relevante = ''
        self.autores = ''
        self.titulo = ''
        self.revista = ''
        self.volume = ''
        self.paginas = ''
        self.numero = ''
        self.ano = ''
        self.issn = ''
        self.qualis = None
        self.qualissimilar = None

        if not partesDoItem=='':
            # partesDoItem[0]: Numero (NAO USADO)
            # partesDoItem[1]: Descricao do artigo (DADO BRUTO)
            self.item = partesDoItem[1]
            self.doi = doi
            self.relevante = relevante

            # Dividir o item na suas partes constituintes (autores e o resto)
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

            # Verificar quando há um numero de autores > que 25
            if partes[1]=='': # muitos autores (mais de 25) e o lattes insere etal. termina lista com ;
                partes = self.item.partition(" ; ")
                a = partes[0].partition(", et al.") # remocao do et al.
                a = a[0] + a[2] # estes autores nao estao bem separados pois falta ';'
                b = a.replace(', ','*')
                c = b.replace(' ',' ; ')
                self.autores = c.replace('*',', ')
            else:
                self.autores = partes[0].strip()

            # Processando o resto (tudo menos autores)
            partes = partes[2].rpartition(", ")
            ano = partes[2].strip().rstrip(".")

            aux = re.findall('\\b((?:19|20)\d\d)\\b', ano)
            if len(aux) > 0:
                self.ano = aux[-1].strip().rstrip(".").rstrip(",")
            else:
                self.ano = ''


            partes = partes[0].rpartition("p. ")
            if partes[1]=='': # se nao existe paginas
                self.paginas = ''
                partes = partes[2]
            else:
                self.paginas = partes[2].strip()
                partes = partes[0]

            partes = partes.rpartition(", n.")
            if partes[1]=='': # se nao existe numero
                self.numero = ''
                partes = partes[2]
            else:
                self.numero = partes[2].strip().rstrip(",")
                partes = partes[0]

            partes = partes.rpartition(", v. ")
            if partes[1]=='': # se nao existe volume
                self.volume = ''
                partes = partes[2]
            else:
                self.volume = partes[2].strip().rstrip(",")
                partes = partes[0]

            p1 = partes.partition(". ")
            p2 = partes.rpartition(". ")
            if len(p1[0])>len(p2[2]):
                self.titulo = p2[0].strip()
                self.revista = p2[2].strip()
            else:
                self.titulo = p1[0].strip()
                self.revista = p1[2].strip()

            self.chave = self.autores # chave de comparação entre os objetos


        # usando os dados complementares (obtidos do div/cvuri)
        nomePeriodicoParte = complemento.split("nomePeriodico=")

        if (len(nomePeriodicoParte) == 2):
            self.revista = nomePeriodicoParte[1].strip()

        complementoPartes = complemento.split("&")
        for parametro in complementoPartes:
            partes = parametro.split("=")
            if len(partes) == 2:
                parametroNome = partes[0].strip()
                parametroValor = partes[1].strip()
                if parametroNome == "issn":
                    self.issn = str(parametroValor)
                    if len(self.issn) == 8:  # '-' not in self.issn
                        self.issn = self.issn[:4] + '-' + self.issn[4:]
                if parametroNome == "volume":
                    self.volume = parametroValor
                if parametroNome == "titulo":
                    self.titulo = parametroValor
                # if parametroNome=="nomePeriodico": self.revista = parametroValor


    def compararCom(self, objeto):
        if self.idMembro.isdisjoint(objeto.idMembro) and similaridade_entre_cadeias(self.titulo, objeto.titulo):
            # Os IDs dos membros são agrupados.
            # Essa parte é importante para a criação do GRAFO de colaborações
            self.idMembro.update(objeto.idMembro)

            if len(self.doi)<len(objeto.doi):
                self.doi = objeto.doi

            if len(self.autores)<len(objeto.autores):
                self.autores = objeto.autores

            if len(self.titulo)<len(objeto.titulo):
                self.titulo = objeto.titulo

            if len(self.revista)<len(objeto.revista):
                self.revista = objeto.revista

            if len(self.paginas)<len(objeto.paginas):
                self.paginas = objeto.paginas

            if len(self.volume)<len(objeto.volume):
                self.volume = objeto.volume

            if len(self.numero)<len(objeto.numero):
                self.numero = objeto.numero

            if len(self.issn) < len(objeto.issn):
                self.issn = objeto.issn

            return self
        else: # nao similares
            return None



# caso difícil: falta melhorar a separacao entre TITULO e NOME-DE-REVISTA
#
#+AUTORES     : Jelinek, Herbert F. ; Cree, Michael J. ; Leandro, Jorge J. G. ; Soares, João V. B. ; Cesar, Roberto M. ; Luckie, A.
#+TITULO      : Automated segmentation of retinal blood vessels and identification of proliferative diabetic retinopathy. Journal of the Optical Society of America
#+REVISTA     : A, Optics Image Science and Vision
#+ANO         : 2007
#+PAGINAS     : 1448
#+NUMERO      :
#+VOLUME      : 24
#+item        : 
#
# Automated segmentation of retinal blood vessels and identification of
# proliferative diabetic retinopathy. Journal of the Optical Society of
# America. A, Optics Image Science and Vision

    def html(self, listaDeMembros):
        s = self.autores + '. <b>' + self.titulo + '</b>. <font color=#330066>' + self.revista + '</font>. '
        s+= 'v. ' + self.volume + ', '  if not self.volume==''  else ''
        s+= 'n. ' + self.numero + ', '  if not self.numero== '' else ''
        s+= 'p. ' + self.paginas + ', ' if not self.paginas=='' else ''
        s+= 'issn: ' + self.issn + ', ' if not self.issn == ''    else ''
        s+= str(self.ano) + '.'         if str(self.ano).isdigit() else '.'

        if not self.doi=='':
            s+= ' <a href="'+self.doi+'" target="_blank" style="PADDING-RIGHT:4px;"><img border=0 src="doi.png"></a>'

        s += menuHTMLdeBuscaPB(self.titulo)
        s += formata_qualis(self.qualis, self.qualissimilar)
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
        s+= '\nTY  - JOUR'
        s+= '\nAU  - '+self.autores
        s+= '\nTI  - '+self.titulo
        s+= '\nJO  - '+self.revista
        s+= '\nVL  - '+self.volume
        s+= '\nIS  - '+self.numero
        s+= '\nSP  - '+p1
        s+= '\nEP  - '+p2
        s+= '\nPY  - '+str(self.ano)
        s+= '\nL2  - '+self.doi
        s+= '\nL3  - '+self.issn
        s+= '\nER  - '
        return s

    def csv(self, nomeCompleto=""):
        if self.qualis == None:
            self.qualis = ''
        if self.qualissimilar == None:
            self.qualissimilar = ''
        s = "artigoEmPeriodico\t"

        #if type(nomeCompleto) == bytes:
        #    nomeCompleto = nomeCompleto.decode()
        #nomeCompleto = str(nomeCompleto)

        # FIXME: self.qualis estava dando erro de conversão; remediado temporariamente usando str(); verificar se comportamento está correto
        if nomeCompleto=="": # tratamento grupal
            s += (
                f"{str(self.ano)}\t{self.doi}\t{self.issn}\t{self.titulo}\t"
                f"{self.revista}\t \t{self.autores}\t{self.qualis}\t{self.qualissimilar}"
            )
        else: # tratamento individual
            s += (
                f"{nomeCompleto}\t{str(self.ano)}\t{self.doi}\t{self.issn}\t{self.titulo}\t"
                f"{self.revista}\t \t{self.autores}\t{self.qualis}\t{self.qualissimilar}"
            )
        return s


    # ------------------------------------------------------------------------ #
    def __str__(self):
        s  = "\n[ARTIGO EM PERIODICO] \n"
        s += "+ID-MEMBRO   : " + str(self.idMembro) + "\n"
        s += "+RELEVANTE   : " + str(self.relevante) + "\n"
        s += "+DOI         : " + self.doi + "\n"
        s += "+AUTORES     : " + self.autores + "\n"
        s += "+TITULO      : " + self.titulo + "\n"
        s += "+REVISTA     : " + self.revista + "\n"
        s += "+PAGINAS     : " + self.paginas + "\n"
        s += "+VOLUME      : " + self.volume + "\n"
        s += "+NUMERO      : " + self.numero + "\n"
        s += "+ANO         : " + str(self.ano) + "\n"
        s += "+ISSN        : " + str(self.issn) + "\n"
        s += "+item        : " + self.item + "\n"
        return s
