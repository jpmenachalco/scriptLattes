#!/usr/bin/python
# encoding: utf-8


import datetime
import unicodedata
from scriptLattes.util import similaridade_entre_cadeias


class ProjetoDePesquisa:
    tipo = "Projeto de pesquisa"
    idMembro = None
    anoInicio = None
    anoConclusao = None
    nome = ''
    descricao = ''
    chave = None
    ano = None

    def __init__(self, idMembro, partesDoItem):
        # partesDoItem[0]: Periodo do projeto de pesquisa
        # partesDoItem[1]: cargo e titulo do projeto
        # partesDoItem[2]: Descricao (resto)

        self.idMembro = list([])
        self.idMembro.append(idMembro)

        anos = partesDoItem[0].partition("-")
        self.anoInicio = anos[0].strip()
        self.anoConclusao = anos[2].strip()

        # detalhe = partesDoItem[1].rpartition(":")
        #self.cargo = detalhe[0].strip()
        #self.nome = detalhe[2].strip()
        self.nome = partesDoItem[1]

        self.descricao= list([])
        self.descricao.append(partesDoItem[2])

        self.chave = self.nome # chave de comparação entre os objetos

        self.ano = self.anoInicio # para comparação entre objetos


    def html(self, listaDeMembros):
        if self.anoConclusao==datetime.datetime.now().year:
            self.anoConclusao = 'Atual'

        if self.anoInicio==0 and self.anoConclusao==0:
            s = '<span class="projects"> (*) </span> '
        else:
            s = '<span class="projects">' + str(self.anoInicio) + '-' + str(self.anoConclusao) + '</span>. '
        s+= '<b>' +  self.nome  + '</b>'

        for i in range(0, len(self.idMembro)):
            s+= '<br><i><font size=-1>'+ self.descricao[i] +'</font></i>'
            m = listaDeMembros[ self.idMembro[i] ]
            
            nome_membro = m.nomeCompleto
            s+= '<br><i><font size=-1>Membro: <a href="'+m.url+'">'+nome_membro+'</a>.</font>'

        return s


    def json(self):
        def nv(x):
            return x if x not in (None, '', []) else None

        # normaliza ano de conclusão (caso seja o ano atual → "Atual")
        ano_conc = self.anoConclusao
        if ano_conc == datetime.datetime.now().year:
            ano_conc = "Atual"

        # período
        periodo = None
        if self.anoInicio or self.anoConclusao:
            periodo = f"{self.anoInicio}-{ano_conc}"

        return {
            "Título": nv(self.nome),
            "Período": nv(periodo),
            # opcional: se quiser juntar descrições dos membros em texto único
            "Descrição": "; ".join(self.descricao) if getattr(self, "descricao", None) else None,
            # opcional: pode mostrar IDs de membros associados
            "Membros": ", ".join(map(str, self.idMembro)) if getattr(self, "idMembro", None) else None,
        }


    def compararCom(self, objeto):
        if set(self.idMembro).isdisjoint(set(objeto.idMembro)) and similaridade_entre_cadeias(self.nome, objeto.nome):
            # Os IDs dos membros são agrupados.
            # Essa parte é importante para a geracao do relorio de projetos
            self.idMembro.extend(objeto.idMembro)

            self.descricao.extend(objeto.descricao) # Apenas juntamos as descrições

            return self
        else: # nao similares
            return None



    # ------------------------------------------------------------------------ #
    def __str__(self):
        s  = "\n[PROJETO DE PESQUISA] \n"
        s += "+ID-MEMBRO   : " + str(self.idMembro) + "\n"
        s += "+ANO INICIO  : " + str(self.anoInicio) + "\n"
        s += "+ANO CONCLUS.: " + str(self.anoConclusao) + "\n"
        s += "+NOME        : " + self.nome + "\n"
        s += "+DESCRICAO   : " + str(self.descricao) + "\n"
        return s

