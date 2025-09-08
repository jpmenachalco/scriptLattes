#!/usr/bin/python
# encoding: utf-8


from scriptLattes.geradorDePaginasWeb import *
from scriptLattes.util import similaridade_entre_cadeias


class ProcessoOuTecnica:
    tipo = "Processo ou técnica"
    item = None # dado bruto
    idMembro = None

    relevante = None
    autores = None
    titulo = None
    ano = None
    natureza = None # tipo de producao
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

        aux = re.findall(' \((.*?)\)', partes)
        if len(aux)>0:
            self.natureza = aux[-1]
            partes = partes.rpartition(" (")
            partes = partes[0]
        else:
            self.natureza = ''

        aux = re.findall(' ((?:19|20)\d\d)\\b', partes)
        if len(aux)>0:
            self.ano = aux[-1] #.strip().rstrip(".").rstrip(",")
            partes = partes.rpartition(" ")
            partes = partes[0]
        else:
            self.ano = ''

        self.titulo = partes.strip().rstrip(".").rstrip(",")
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

            if len(self.natureza)<len(objeto.natureza):
                self.natureza = objeto.natureza

            return self
        else: # nao similares
            return None


    def html(self, listaDeMembros):
        s = self.autores + '. <b>' + self.titulo + '</b>. '
        s+= str(self.ano) + '.'  if str(self.ano).isdigit() else '.'
        s+= self.natureza        if not self.natureza=='' else ''

        s+= menuHTMLdeBuscaPT(self.titulo)
        return s


    def json(self):
        def nv(x):
            return x if x not in (None, '', []) else None

        return {
            "Autores": nv(self.autores),
            "Título": nv(self.titulo),
            "Natureza": nv(self.natureza),
        }

    # ------------------------------------------------------------------------ #
    def __str__(self):
        s  = "\n[PROCESSO OU TECNICA] \n"
        s += "+ID-MEMBRO   : " + str(self.idMembro) + "\n"
        s += "+RELEVANTE   : " + str(self.relevante) + "\n"
        s += "+AUTORES     : " + self.autores.encode('utf8','replace') + "\n"
        s += "+TITULO      : " + self.titulo.encode('utf8','replace') + "\n"
        s += "+ANO         : " + str(self.ano) + "\n"
        s += "+NATUREZA    : " + self.natureza.encode('utf8','replace') + "\n"
        s += "+item        : " + self.item.encode('utf8','replace') + "\n"
        return s
