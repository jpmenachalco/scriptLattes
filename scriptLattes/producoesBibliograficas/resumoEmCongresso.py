#!/usr/bin/python
# encoding: utf-8

import re
from scriptLattes.geradorDePaginasWeb import *
from scriptLattes.util import similaridade_entre_cadeias


class ResumoEmCongresso:
    tipo = "Resumo em congresso"
    item = None  # dado bruto
    idMembro = None

    doi = None
    relevante = None
    autores = None
    titulo = None
    nomeDoEvento = None
    ano = None
    volume = None
    numero = None
    paginas = None
    chave = None

    def __init__(self, idMembro, partesDoItem='', doi='', relevante=''):
        self.idMembro = set([])
        self.idMembro.add(idMembro)

        if not partesDoItem == '':
            # partesDoItem[0]: Numero (NAO USADO)
            # partesDoItem[1]: Descricao do artigo (DADO BRUTO)
            self.item = partesDoItem[1]
            self.doi = doi
            self.relevante = relevante

            # Dividir o item nas suas partes constituintes
            if " . " in self.item and len(self.item.partition(" . ")[2]) >= 30:
                partes = self.item.partition(" . ")
            elif (".. " in self.item) and len(self.item.partition(".. ")[2]) >= 30:
                partes = self.item.partition(".. ")
            else:
                partes = self.item.partition(". ")

            self.autores = partes[0].strip()
            partes = partes[2]

            # Ano
            aux = re.findall(r', ((?:19|20)\d\d)\b', partes)
            if len(aux) > 0:
                self.ano = aux[-1].strip().rstrip(".").rstrip(",")
            else:
                self.ano = ''

            # Páginas
            partes = partes.rpartition(" p. ")
            if partes[1] == '':
                self.paginas = ''
                partes = partes[2]
            else:
                self.paginas = partes[2].rstrip(".")
                partes = partes[0]

            # Número
            partes = partes.rpartition(", n. ")
            if partes[1] == '':
                self.numero = ''
                partes = partes[2]
            else:
                self.numero = partes[2].strip().rstrip(",")
                partes = partes[0]

            # Volume
            partes = partes.rpartition(" v. ")
            if partes[1] == '':
                self.volume = ''
                partes = partes[2]
            else:
                self.volume = partes[2].rstrip(".").rstrip(",")
                partes = partes[0]

            # Ano (refinado)
            aux = re.findall(r', ((?:19|20)\d\d)\b', partes)
            if len(aux) > 0:
                partes = partes.rpartition(",")
                self.ano = aux[-1].strip().rstrip(".").rstrip(",")
                partes = partes[0]

            # Evento
            partes = partes.rpartition(" In: ")
            if partes[1] == '':
                self.nomeDoEvento = ''
                partes = partes[2]
            else:
                self.nomeDoEvento = partes[2].strip().rstrip(".").rstrip(",")
                partes = partes[0]

            self.titulo = partes.strip().rstrip(".").rstrip(",")
            self.chave = self.autores
        else:
            self.doi = ''
            self.relevante = ''
            self.autores = ''
            self.titulo = ''
            self.nomeDoEvento = ''
            self.ano = ''
            self.volume = ''
            self.numero = ''
            self.paginas = ''

    def compararCom(self, objeto):
        if self.idMembro.isdisjoint(objeto.idMembro) and similaridade_entre_cadeias(self.titulo, objeto.titulo):
            # agrupar IDs dos membros (para grafo de colaborações)
            self.idMembro.update(objeto.idMembro)

            if len(self.doi) < len(objeto.doi):
                self.doi = objeto.doi
            if len(self.autores) < len(objeto.autores):
                self.autores = objeto.autores
            if len(self.titulo) < len(objeto.titulo):
                self.titulo = objeto.titulo
            if len(self.nomeDoEvento) < len(objeto.nomeDoEvento):
                self.nomeDoEvento = objeto.nomeDoEvento
            if len(self.volume) < len(objeto.volume):
                self.volume = objeto.volume
            if len(self.numero) < len(objeto.numero):
                self.numero = objeto.numero
            if len(self.paginas) < len(objeto.paginas):
                self.paginas = objeto.paginas

            return self
        else:
            return None

    def html(self, listaDeMembros):
        s = self.autores + '. <b>' + self.titulo + '</b>. '
        s += 'Em: ' + self.nomeDoEvento + ', ' if not self.nomeDoEvento == '' else ''
        s += 'v. ' + self.volume + ', ' if not self.volume == '' else ''
        s += 'n. ' + self.numero + ', ' if not self.numero == '' else ''
        s += 'p. ' + self.paginas + ', ' if not self.paginas == '' else ''
        s += str(self.ano) + '. ' if str(self.ano).isdigit() else '. '

        if self.doi:
            s += (
                f'<a href="{self.doi}" target="_blank" '
                'style="margin-left:4px; text-decoration:none; '
                'font-size:0.7em; background-color:#121212; color:#FFFFFF; '
                'padding:0 4px; border-radius:2px; vertical-align:middle;">'
                '[doi]'
                '</a>'
            )

        s += menuHTMLdeBuscaPB(self.titulo)
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
            "Veículo": nv(self.nomeDoEvento),
            "Volume": nv(self.volume),
            "Páginas": nv(self.paginas),
            "DOI": doi,
        }

    def ris(self):
        paginas = self.paginas.split('-')
        if len(paginas) < 2:
            p1 = self.paginas
            p2 = ''
        else:
            p1 = paginas[0]
            p2 = paginas[1]
        s = '\n'
        s += '\nTY  - CONF'
        s += '\nAU  - ' + self.autores
        s += '\nT1  - ' + self.titulo
        s += '\nTI  - ' + self.nomeDoEvento
        s += '\nVL  - ' + self.volume
        s += '\nIS  - ' + self.numero
        s += '\nSP  - ' + p1
        s += '\nEP  - ' + p2
        s += '\nPY  - ' + str(self.ano)
        s += '\nL2  - ' + self.doi
        s += '\nER  - '
        return s

    def __str__(self):
        s = "\n[RESUMO EM CONGRESSO] \n"
        s += "+ID-MEMBRO   : " + str(self.idMembro) + "\n"
        s += "+RELEVANTE   : " + str(self.relevante) + "\n"
        s += "+DOI         : " + self.doi + "\n"
        s += "+AUTORES     : " + self.autores + "\n"
        s += "+TITULO      : " + self.titulo + "\n"
        s += "+NOME EVENTO : " + self.nomeDoEvento + "\n"
        s += "+ANO         : " + str(self.ano) + "\n"
        s += "+VOLUME      : " + self.volume + "\n"
        s += "+NUMERO      : " + self.numero + "\n"
        s += "+PAGINAS     : " + self.paginas + "\n"
        s += "+item        : " + str(self.item) + "\n"
        return s

