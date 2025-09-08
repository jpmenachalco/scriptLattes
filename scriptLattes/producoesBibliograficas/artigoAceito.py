#!/usr/bin/python
# encoding: utf-8


from scriptLattes.geradorDePaginasWeb import *
from scriptLattes.util import similaridade_entre_cadeias


class ArtigoAceito:
    tipo = "Artigo aceito"
    item = None # dado bruto
    idMembro = None
    qualis = None
    qualissimilar = None
    issn = ''

    doi = None
    relevante = None
    autores = None
    titulo = None
    revista = None
    paginas = None
    volume = None
    numero = None
    ano = None
    chave = None

    def __init__(self, idMembro, partesDoItem='', doi='', relevante=''):
        self.idMembro = set([])
        self.idMembro.add(idMembro)

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
            self.ano = partes[2].strip().rstrip(".")

            partes = partes[0].rpartition("p. ")
            if partes[1]=='': # se nao existe paginas
                self.paginas = ''
                partes = partes[2]
            else:
                self.paginas = partes[2].strip()
                partes = partes[0]

            partes = partes.rpartition(", n. ")
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

            partes = partes.rpartition(". ")
            self.titulo = partes[0].strip()
            self.revista = partes[2].strip()

            self.chave = self.autores # chave de comparação entre os objetos

        else:
            self.doi = ''
            self.relevante = ''
            self.autores = ''
            self.titulo = ''
            self.revista = ''
            self.paginas = ''
            self.volume = ''
            self.numero = ''
            self.ano = ''


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

            return self
        else: # nao similares
            return None



    def html(self, listaDeMembros):
        s = self.autores + '. <b>' + self.titulo + '</b>. ' + self.revista + '. '
        s+= 'v. ' + self.volume + ', '  if not self.volume==''  else ''
        s+= 'n. ' + self.numero + ', '  if not self.numero== '' else ''
        s+= 'p. ' + self.paginas + ', ' if not self.paginas=='' else ''
        s+= str(self.ano) + '. '         if str(self.ano).isdigit() else '. '

        if self.doi:
            s += (
                f'<a href="{self.doi}" target="_blank" '
                'style="margin-left:4px; text-decoration:none; '
                'font-size:0.7em; background-color:#121212; color:#FFFFFF; '
                'padding:0 4px; border-radius:2px; vertical-align:middle;">'
                '[doi]'
                '</a>'
            )

        s+= menuHTMLdeBuscaPB(self.titulo)
        s+= formata_qualis(self.qualis, self.qualissimilar)
        return s


    def json(self):
        def nv(x):
            return x if x not in (None, '', []) else None

        # normalizar DOI
        doi = nv(getattr(self, "doi", None))
        if doi:
            d = str(doi).strip()
            if d.lower().startswith("doi:"):
                d = d[4:].strip()
            doi = d

        return {
            "Autores": nv(self.autores),
            "Título": nv(self.titulo),
            "Veículo": nv(self.revista),
            "Volume": nv(self.volume),
            "Páginas": nv(self.paginas),
            "DOI": doi,
        }

    # ------------------------------------------------------------------------ #
    def __str__(self):
        s  = "\n[ARTIGO ACEITO PARA PUBLICACAO] \n"
        s += "+ID-MEMBRO   : " + str(self.idMembro) + "\n"
        s += "+RELEVANTE   : " + str(self.relevante) + "\n"
        s += "+DOI         : " + self.doi.encode('utf8','replace') + "\n"
        s += "+AUTORES     : " + self.autores.encode('utf8','replace') + "\n"
        s += "+TITULO      : " + self.titulo.encode('utf8','replace') + "\n"
        s += "+REVISTA     : " + self.revista.encode('utf8','replace') + "\n"
        s += "+PAGINAS     : " + self.paginas.encode('utf8','replace') + "\n"
        s += "+VOLUME      : " + self.volume.encode('utf8','replace') + "\n"
        s += "+NUMERO      : " + self.numero.encode('utf8','replace') + "\n"
        s += "+ANO         : " + str(self.ano) + "\n"
        s += "+item        : " + self.item.encode('utf8','replace') + "\n"
        return s
