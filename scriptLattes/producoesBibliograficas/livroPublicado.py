#!/usr/bin/python
# encoding: utf-8


from scriptLattes.geradorDePaginasWeb import *
from scriptLattes.util import similaridade_entre_cadeias


class LivroPublicado:
    tipo = "Livros publicados/organizados ou edições"
    item = None # dado bruto
    idMembro = None

    relevante = None
    autores = None
    titulo = None
    edicao = None
    ano = None
    volume = None
    paginas = None
    editora = None
    chave = None

    def __init__(self, idMembro, partesDoItem='', relevante=''):
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

            partes = partes.rpartition("p .")  # <---modificacao na P.Lattes
            if partes[1]=='': # se nao existem paginas
                self.paginas = ''
                partes = partes[2]
            else:
                partes = partes[0].rpartition(". ")
                self.paginas = partes[2]
                partes = partes[0]

            partes = partes.rpartition(" v. ")
            if partes[1]=='': # se nao existem informacao de volume
                self.volume = ''
                partes = partes[2]
            else:
                self.volume = partes[2].rstrip(".")
                partes = partes[0]

            partes = partes.rpartition(", ")
            self.ano = partes[2].strip().rstrip(".")
            partes = partes[0]

            partes = partes.rpartition(". ed. ")
            self.editora = partes[2]

            if partes[1]=='': # se nao existe edicao
                self.edicao = ''
                partes = partes[2]
            else:
                partes = partes[0].rpartition(" ")
                self.edicao = partes[2]
                partes = partes[0]


            self.titulo = partes.strip().rstrip(".")
            self.chave = self.autores # chave de comparação entre os objetos


        else:
            relevante = ''
            autores = ''
            titulo = ''
            edicao = ''
            ano = ''
            volume = ''
            paginas = ''
            editora = ''


    def compararCom(self, objeto):
        if self.idMembro.isdisjoint(objeto.idMembro) and similaridade_entre_cadeias(self.titulo, objeto.titulo):
            # Os IDs dos membros são agrupados.
            # Essa parte é importante para a criação do GRAFO de colaborações
            self.idMembro.update(objeto.idMembro)

            if len(self.autores)<len(objeto.autores):
                self.autores = objeto.autores

            if len(self.titulo)<len(objeto.titulo):
                self.titulo = objeto.titulo

            if len(self.edicao)<len(objeto.edicao):
                self.edicao = objeto.edicao

            if len(self.volume)<len(objeto.volume):
                self.volume = objeto.volume

            if len(self.paginas)<len(objeto.paginas):
                self.paginas = objeto.paginas

            return self
        else: # nao similares
            return None


    def html(self, listaDeMembros):
        s = self.autores + '. <b>' + self.titulo + '</b>. '
        s+= self.edicao + ' ed. '       if not self.edicao==''  else ''
        s += self.editora + ', ' if not self.editora == ''  else ''
        s += str(self.ano) + '. ' if str(self.ano).isdigit() else ''

        s+= 'v. ' + self.volume + ', '  if not self.volume== '' else ''
        s+= 'p. ' + self.paginas + '. ' if not self.paginas=='' else '.'

        s += menuHTMLdeBuscaPB(self.titulo)
        return s

    def json(self):
        def nv(x):
            return x if x not in (None, '', []) else None

        return {
            "Autores": nv(self.autores),
            "Título": nv(self.titulo),
            "Edição": nv(self.edicao),
            "Editora": nv(self.editora),
            "Páginas": nv(self.paginas),
        }
        
    def ris(self):
        paginas = self.paginas.split('-')
        if len(paginas)<2:
            p1 = self.paginas
            p2 = ''
        else:
            p1 = paginas[0]
            p2 = paginas[1]
        s = '\n'
        s+= '\nTY  - BOOK'
        s+= '\nAU  - '+self.autores
        s+= '\nTI  - '+self.titulo
        s+= '\nIS  - '+self.edicao
        s+= '\nPY  - '+str(self.ano)
        s+= '\nVL  - '+self.volume
        s+= '\nSP  - '+p1
        s+= '\nEP  - '+p2
        s+= '\nER  - '
        return s

    # ------------------------------------------------------------------------ #
    def __str__(self):
        s  = "\n[LIVRO PUBLICADO] \n"
        s += "+ID-MEMBRO   : " + str(self.idMembro) + "\n"
        s += "+RELEVANTE   : " + str(self.relevante) + "\n"
        s += "+AUTORES     : " + self.autores.encode('utf8','replace') + "\n"
        s += "+TITULO      : " + self.titulo.encode('utf8','replace') + "\n"
        s += "+EDICAO      : " + self.edicao.encode('utf8','replace') + "\n"
        s += "+EDITORES    : " + self.editora.encode('utf8', 'replace') + "\n"
        s += "+ANO         : " + str(self.ano) + "\n"
        s += "+VOLUME      : " + self.volume.encode('utf8','replace') + "\n"
        s += "+PAGINAS     : " + self.paginas.encode('utf8','replace') + "\n"
        s += "+item        : " + self.item.encode('utf8','replace') + "\n"
        return s
