#!/usr/bin/python
# encoding: utf-8

import re
from scriptLattes.util import similaridade_entre_cadeias


class ParticipacaoEmEvento:
    tipo = "Participação em evento"
    item = None        # dado bruto
    idMembro = None    # set de IDs

    ano = None
    evento = None
    apresentacao = None
    tipo_evento = None
    chave = None       # para comparação

    def __init__(self, idMembro, partesDoItem=''):
        self.idMembro = set([idMembro])

        if partesDoItem:
            # partesDoItem[0]: Numero (NAO USADO)
            # partesDoItem[1]: Descricao
            self.item = partesDoItem[1]
            self._parse_item(self.item)
            # chave de comparação: evento + ano + apresentação (quando houver)
            base = f"{self.evento or ''}::{self.ano or ''}::{self.apresentacao or ''}"
            self.chave = base.strip(':')
        else:
            self.item = ''
            self.ano = ''
            self.evento = None
            self.apresentacao = None
            self.tipo_evento = None
            self.chave = ''

    # --------- parsing robusto do item bruto ---------
    def _parse_item(self, s: str):
        txt = " ".join((s or "").split())  # normaliza espaços

        # 1) padrão completo: <evento> . <apresentacao> . <ano> . (<tipo>).
        m = re.match(
            r"^(?P<evento>.+?)\.\s*(?P<apresentacao>.+?)\.\s*(?P<ano>\d{4})\.\s*\((?P<tipo>[^)]+)\)\.?\s*$",
            txt, flags=re.IGNORECASE
        )
        if m:
            self.evento = m.group("evento").strip() or None
            self.apresentacao = m.group("apresentacao").strip() or None
            self.ano = m.group("ano").strip() or ''
            self.tipo_evento = m.group("tipo").strip() or None
            return

        # 2) fallback: captura "(Tipo)" no final, e ultimo ano AAAA
        tipo = None
        m_tipo = re.search(r"\(([^)]+)\)\.?\s*$", txt)
        if m_tipo:
            tipo = m_tipo.group(1).strip()
            txt = txt[:m_tipo.start()].rstrip(". ").strip()

        ano = None
        m_ano = re.search(r"(\d{4})\.?\s*$", txt)
        if m_ano:
            ano = m_ano.group(1)
            txt = txt[:m_ano.start()].rstrip(". ").strip()

        # 3) separa evento / apresentação pelo primeiro ponto (com ou sem espaço)
        partes = re.split(r"\.\s*", txt, maxsplit=1)
        if len(partes) == 2:
            evento, apresentacao = partes[0].strip(), partes[1].strip()
        else:
            evento, apresentacao = txt, None

        self.evento = evento or None
        self.apresentacao = apresentacao or None
        self.ano = ano or ''
        self.tipo_evento = tipo or None

    # --------- mesclagem com outro objeto semelhante ---------
    def compararCom(self, objeto):
        # evita unir objetos do mesmo(s) membro(s)
        if self.idMembro.isdisjoint(objeto.idMembro) and similaridade_entre_cadeias(self.item, objeto.item):
            # Une conjuntos de membros
            self.idMembro.update(objeto.idMembro)

            # Mantém representação mais rica/longa quando houver
            if len(self.item or "") < len(objeto.item or ""):
                self.item = objeto.item

            # Prefere campos preenchidos; se ambos preenchidos, fica com o mais longo (tende a ser mais informativo)
            def _pick(a, b):
                if not a and b: return b
                if a and b and len(str(b)) > len(str(a)): return b
                return a

            self.evento = _pick(self.evento, objeto.evento)
            self.apresentacao = _pick(self.apresentacao, objeto.apresentacao)
            self.tipo_evento = _pick(self.tipo_evento, objeto.tipo_evento)

            # Ano: mantém o válido (4 dígitos); se ambos válidos e diferentes, fica com o mais “confiável” (não muda aqui)
            def _ano_ok(v): return bool(re.fullmatch(r"\d{4}", str(v or "")))
            if not _ano_ok(self.ano) and _ano_ok(objeto.ano):
                self.ano = objeto.ano

            # Atualiza chave
            base = f"{self.evento or ''}::{self.ano or ''}::{self.apresentacao or ''}"
            self.chave = base.strip(':')

            return self
        else:
            return None

    # --------- HTML  ---------
    def html(self, listaDeMembros):
        # mantém compatibilidade com sua interface anterior
        return self.item or ""

    # --------- Saída estruturada para a tabela ---------
    def json(self):
        def nv(x):  # None se vazio
            return x if x not in (None, '', [], {}) else None

        return {
            "Evento": nv(self.evento),
            "Apresentação": nv(self.apresentacao),
            "Tipo de Evento": nv(self.tipo_evento),
        }

    # ------------------------------------------------------------------------ #
    def __str__(self):
        s = "\n[PARTICIPACAO EM EVENTO] \n"
        s += "+ID-MEMBRO   : " + str(self.idMembro) + "\n"
        s += "+item        : @@" + (self.item or "") + "@@\n"
        s += "+evento      : " + str(self.evento) + "\n"
        s += "+apresentacao: " + str(self.apresentacao) + "\n"
        s += "+ano         : " + str(self.ano) + "\n"
        s += "+tipo_evento : " + str(self.tipo_evento) + "\n"
        return s

