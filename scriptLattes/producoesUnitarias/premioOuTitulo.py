#!/usr/bin/python
# encoding: utf-8


class PremioOuTitulo:
    tipo = "Prêmio e título"
    idMembro = None

    ano = ''
    descricao = ''
    chave = None

    def __init__(self, idMembro, partesDoItem):
        # partesDoItem[0]: Ano
        # partesDoItem[1]: Descricao do titulo ou premio
        self.idMembro = set([])
        self.idMembro.add(idMembro)

        self.ano = partesDoItem[0].strip()
        self.descricao = partesDoItem[1].strip()
        self.chave = self.descricao  # chave de comparação entre os objetos

    def compararCom(self, objeto):
        return None

    # Prêmios considerados de forma individual
    # if self.idMembro.isdisjoint(objeto.idMembro) and similaridade_entre_cadeias(self.descricao, objeto.descricao):
    #	# Os IDs dos membros são agrupados.
    #	# Essa parte é importante para a criação do GRAFO de colaborações
    #	self.idMembro.update(objeto.idMembro)
    #
    #	if len(self.descricao)<len(objeto.descricao):
    #		self.descricao = objeto.descricao
    #
    #	return self
    # else: # nao similares
    #	return None


    def html(self, listaDeMembros):
        s = self.descricao + '. '
        s += str(self.ano) + '.' if str(self.ano).isdigit() else '.'

        m = listaDeMembros[list(self.idMembro)[0]]
        s += '<br><i><font size=-1>Membro: <a href="' + m.url + '">' + m.nomeCompleto + '</a>.</font>'

        return s


    def json(self):
        def nv(x):
            return x if x not in (None, '', []) else None

        membros_ids = None
        if getattr(self, "idMembro", None):
            try:
                membros_ids = ", ".join(map(str, self.idMembro))
            except Exception:
                membros_ids = str(self.idMembro)

        return {
            "Descrição": nv(self.descricao),
            "Membros (IDs)": nv(membros_ids),
        }



    # ------------------------------------------------------------------------ #
    def __str__(self):
        s = "\n[PREMIO OU TITULO] \n"
        s += "+ID-MEMBROL  : " + str(self.idMembro) + "\n"
        s += "+ANO         : " + str(self.ano) + "\n"
        s += "+DESCRICAO   : " + self.descricao.encode('utf8', 'replace') + "\n"
        return s
