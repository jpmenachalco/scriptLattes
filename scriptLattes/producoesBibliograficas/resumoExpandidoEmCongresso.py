#!/usr/bin/python
# encoding: utf-8


from scriptLattes.geradorDePaginasWeb import *
from scriptLattes.util import similaridade_entre_cadeias


class ResumoExpandidoEmCongresso:
    tipo = "Resumo expandido em congresso"
    item = None # dado bruto
    idMembro = None
    qualis = None
    qualissimilar = None

    doi = None
    relevante = None
    autores = None
    titulo = None
    nomeDoEvento = None
    ano = None
    volume = None
    paginas = None
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

            partes = partes.rpartition(" p. ")
            if partes[1]=='': # se nao existem paginas
                self.paginas = ''
                partes = partes[2]
            else:
                self.paginas = partes[2].rstrip(".").rstrip(",")
                partes = partes[0]

            partes = partes.rpartition(" v. ")
            if partes[1]=='': # se nao existem informacao de volume
                self.volume = ''
                partes = partes[2]
            else:
                self.volume = partes[2].rstrip(".").rstrip(",")
                partes = partes[0]

            aux = re.findall(', ((?:19|20)\d\d)\\b', partes)

            if len(aux)>0:
                partes = partes.rpartition(",")
                self.ano = aux[-1].strip().rstrip(".").rstrip(",")
                partes = partes[0]

            else:
                self.ano = ''

            ###		partes = partes.rpartition(". ")
            ###		self.tituloDosAnais = partes[2].strip().rstrip('.').rstrip(",")
            ###		partes = partes[0]

            partes = partes.rpartition(" In: ")
            if partes[1]=='': # se nao existe nome do evento
                self.nomeDoEvento = ''
                partes = partes[2]
            else:
                self.nomeDoEvento = partes[2].strip().rstrip(".")
                partes = partes[0]

            self.titulo = partes.strip().rstrip(".")
            self.chave = self.autores # chave de comparação entre os objetos

        else:
            self.doi = ''
            self.relevante = ''
            self.autores = ''
            self.titulo = ''
            self.nomeDoEvento = ''
            self.ano = ''
            self.volume = ''
            self.paginas = ''



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

            if len(self.nomeDoEvento)<len(objeto.nomeDoEvento):
                self.nomeDoEvento = objeto.nomeDoEvento

            if len(self.volume)<len(objeto.volume):
                self.volume = objeto.volume

            if len(self.paginas)<len(objeto.paginas):
                self.paginas = objeto.paginas

            return self
        else: # nao similares
            return None


    def html(self, listaDeMembros):
        s = self.autores + '. <b>' + self.titulo + '</b>. '
        s+= 'Em: ' + self.nomeDoEvento + ', '  if not self.nomeDoEvento==''  else ''
        s+= 'v. ' + self.volume + ', '  if not self.volume==''  else ''
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
            "Veículo": nv(self.nomeDoEvento),
            "Páginas": nv(self.paginas),       
            "DOI": doi,
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
        s+= '\nTY  - CONF'
        s+= '\nAU  - '+self.autores
        s+= '\nT1  - '+self.titulo
        s+= '\nTI  - '+self.nomeDoEvento
        s+= '\nVL  - '+self.volume
        s+= '\nSP  - '+p1
        s+= '\nEP  - '+p2
        s+= '\nPY  - '+str(self.ano)
        s+= '\nL2  - '+self.doi
        s+= '\nER  - '
        return s


    def csv(self, nomeCompleto=""):
        if self.qualis == None:
            self.qualis = ''
        if self.qualissimilar == None:
            self.qualissimilar = ''
        s  = "resumoExpandidoEmCongresso\t"
        if nomeCompleto=="": # tratamento grupal
            s +=  str(self.ano) +"\t"+ self.titulo +"\t"+ self.nomeDoEvento +"\t"+ self.autores +"\t"+ self.qualis +"\t"+ self.qualissimilar
        else: # tratamento individual
            s += nomeCompleto +"\t"+ str(self.ano) +"\t"+ self.titulo +"\t"+ self.nomeDoEvento +"\t"+ self.autores +"\t"+ self.qualis +"\t"+ self.qualissimilar
        return s

    # ------------------------------------------------------------------------ #
    def __str__(self):
        s  = "\n[RESUMO EXPANDIDO EM CONGRESSO] \n"
        s += "+ID-MEMBRO   : " + str(self.idMembro) + "\n"
        s += "+RELEVANTE   : " + str(self.relevante) + "\n"
        s += "+DOI         : " + self.doi + "\n"
        s += "+AUTORES     : " + self.autores + "\n"
        s += "+TITULO      : " + self.titulo + "\n"
        s += "+NOME EVENTO : " + self.nomeDoEvento + "\n"
        s += "+ANO         : " + str(self.ano) + "\n"
        s += "+VOLUME      : " + self.volume + "\n"
        s += "+PAGINAS     : " + self.paginas + "\n"
        s += "+item        : " + self.item + "\n"

        return s
