#!/usr/bin/python
# encoding: utf-8


import datetime
import unicodedata
import re
from scriptLattes.util import similaridade_entre_cadeias


class ProjetoDeExtensao:
    tipo = "Projeto de extensão"
    idMembro = None
    anoInicio = None
    anoConclusao = None
    nome = ''
    descricao = ''
    integrantes = []
    financiadores = []
    chave = None
    ano = None

    def __init__(self, idMembro, partesDoItem):
        # partesDoItem[0]: Periodo do projeto de extensão
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

        self.descricao = list([])
        if len(partesDoItem) > 2:
            self.descricao.append(partesDoItem[2])
        else:
            self.descricao.append("")

        # Extrair integrantes e papéis da descrição
        self.integrantes = []
        if len(partesDoItem) > 2:
            self._extrair_integrantes(partesDoItem[2])

        # Extrair financiadores da descrição
        self.financiadores = []
        if len(partesDoItem) > 2:
            self._extrair_financiadores(partesDoItem[2])

        self.chave = self.nome # chave de comparação entre os objetos

        # Conversao para int quando aplicavel
        try:
            self.anoInicio = int(self.anoInicio)
        except:
            self.anoInicio = 0

        try:
            self.anoConclusao = int(self.anoConclusao)
        except:
            if 'Atual' in self.anoConclusao:
                self.anoConclusao = datetime.datetime.now().year
            else:
                self.anoConclusao = 0

        self.ano = self.anoInicio # para comparação entre objetos

    def _extrair_integrantes(self, texto_descricao):
        """Extrai lista de integrantes e seus papéis da descrição do projeto"""
        # Procura pelo padrão "Integrantes: ... " na descrição
        # Melhorada para capturar até o final ou próximo ponto/vírgula
        match = re.search(r'Integrantes:\s*([^.]*?)(?:\.|$|Financiador)', texto_descricao)
        if match:
            integrantes_texto = match.group(1).strip()
            # Divide por " / " para separar os integrantes
            integrantes_lista = [item.strip() for item in integrantes_texto.split(' / ') if item.strip()]
            
            for integrante in integrantes_lista:
                # Divide nome e papel por " - "
                if ' - ' in integrante:
                    nome, papel = integrante.split(' - ', 1)
                    self.integrantes.append({
                        'nome': nome.strip(),
                        'papel': papel.strip()
                    })
                else:
                    # Se não tem papel definido, adiciona como "Integrante"
                    self.integrantes.append({
                        'nome': integrante.strip(),
                        'papel': 'Integrante'
                    })

    def _extrair_financiadores(self, texto_descricao):
        """Extrai lista de financiadores da descrição do projeto"""
        # Procura pelo padrão "Financiador(es): ... " na descrição
        match = re.search(r'Financiador\(es\):\s*([^.]*?)(?:\.|$)', texto_descricao)
        if match:
            financiadores_texto = match.group(1).strip()
            # Divide por " / " para separar múltiplos financiadores
            financiadores_lista = [item.strip() for item in financiadores_texto.split(' / ') if item.strip()]
            
            for financiador in financiadores_lista:
                # Separa nome do financiador e tipo de apoio por " - "
                if ' - ' in financiador:
                    nome, tipo_apoio = financiador.split(' - ', 1)
                    self.financiadores.append({
                        'nome': nome.strip(),
                        'tipo_apoio': tipo_apoio.strip()
                    })
                else:
                    # Se não tem tipo de apoio definido, adiciona como "Financiamento"
                    self.financiadores.append({
                        'nome': financiador.strip(),
                        'tipo_apoio': 'Financiamento'
                    })

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
            nome_membro = nome_membro.replace(u'\xa0', ' ')
            
            for a in m.nomeEmCitacoesBibliograficas.split(';'):
                if len(a)>0:
                    nome_membro = nome_membro.replace(a.strip(), '<a style="text-decoration: none" href="' + m.url + '">' + a.strip() + '</a>')

            s += '<br>Integrante: ' + nome_membro

        return s

    def json(self):
        def nv(x):
            return x if x not in (None, '', []) else None
        
        # preparar integrantes para JSON
        integrantes_json = []
        if self.integrantes:
            integrantes_json = [
                {
                    "nome": integrante["nome"],
                    "papel": integrante["papel"]
                }
                for integrante in self.integrantes
            ]

        # preparar financiadores para JSON
        financiadores_json = []
        if self.financiadores:
            financiadores_json = [
                {
                    "nome": financiador["nome"],
                    "tipo_apoio": financiador["tipo_apoio"]
                }
                for financiador in self.financiadores
            ]

        result = {
            "nome": nv(self.nome),
            "ano_inicio": nv(str(self.anoInicio) if self.anoInicio != 0 else None),
            "ano_conclusao": nv(str(self.anoConclusao) if self.anoConclusao != 0 else None),
            "descricao": nv(self.descricao),
            "tipo": nv(self.tipo)
        }

        # Adicionar integrantes se existirem
        if integrantes_json:
            result["integrantes"] = integrantes_json

        # Adicionar financiadores se existirem
        if financiadores_json:
            result["financiadores"] = financiadores_json

        return result

    def compararCom(self, objeto):
        if set(self.idMembro).isdisjoint(set(objeto.idMembro)) and similaridade_entre_cadeias(self.nome, objeto.nome):
            # Os IDs dos membros são agrupados.
            # Essa parte é importante para a geracao do relorio de projetos
            self.idMembro.extend(objeto.idMembro)

            self.descricao.extend(objeto.descricao) # Apenas juntamos as descrições
            
            # Combinar integrantes (evitando duplicatas por nome)
            nomes_existentes = set(integrante['nome'] for integrante in self.integrantes)
            for integrante in objeto.integrantes:
                if integrante['nome'] not in nomes_existentes:
                    self.integrantes.append(integrante)
                    nomes_existentes.add(integrante['nome'])

            # Combinar financiadores (evitando duplicatas por nome)
            financiadores_existentes = set(financiador['nome'] for financiador in self.financiadores)
            for financiador in objeto.financiadores:
                if financiador['nome'] not in financiadores_existentes:
                    self.financiadores.append(financiador)
                    financiadores_existentes.add(financiador['nome'])

            return self
        else: # nao similares
            return None

    # ------------------------------------------------------------------------ #
    def __str__(self):
        s  = "\n[PROJETO DE EXTENSÃO] \n"
        s += "+ID-MEMBRO   : " + str(self.idMembro) + "\n"
        s += "+ANO INICIO  : " + str(self.anoInicio) + "\n"
        s += "+ANO CONCLUS.: " + str(self.anoConclusao) + "\n"
        s += "+NOME        : " + self.nome + "\n"
        s += "+DESCRICAO   : " + str(self.descricao) + "\n"
        return s