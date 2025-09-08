#!/usr/bin/python
# encoding: utf-8

import re
from scriptLattes.geradorDePaginasWeb import *
from scriptLattes.util import similaridade_entre_cadeias


class ProducaoArtistica:
    tipo = "Produção artística/cultural"
    item = None  # dado bruto
    idMembro = None
    idLattes = None

    relevante = None
    autores = None
    titulo = None
    ano = None
    chave = None
    complemento = None  # tudo que estiver à direita do ano identificado

    def __init__(self, idMembro, partesDoItem, relevante):
        # partesDoItem[0]: Numero (NAO USADO)
        # partesDoItem[1]: Descricao
        self.idMembro = set([idMembro])
        self.relevante = relevante

        # Normaliza espaços múltiplos
        self.item = re.sub(r'\s+', ' ', partesDoItem[1]).strip()

        texto = self.item

        # === 1) Separar AUTORES / RESTANTE (prioriza " espaço . espaço ") ===
        # Ex.: "ROZESTRATEN, A. S.; GUTIERREZ, R. L. M. . Logomarca do Grupo..."
        m_sep_dot = re.search(r'\s\.\s', texto[:160])  # janela curta para evitar falsos-positivos longe
        if m_sep_dot:
            self.autores = texto[:m_sep_dot.start()].strip().rstrip('.;,').strip()
            resto = texto[m_sep_dot.end():].strip()
        else:
            # Heurística antiga: '.. ' logo após iniciais (padrão comum)
            pos_dd = texto.find('.. ')
            if 0 <= pos_dd <= 80:
                self.autores = texto[:pos_dd+1].rstrip('.').strip()
                resto = texto[pos_dd+3:].strip()
            else:
                # Fallback: primeiro período que fecha a sentença inicial
                m = re.match(r'^(?P<autores>.+?\.)\s*(?P<resto>.+)$', texto)
                if m:
                    self.autores = m.group('autores').strip().rstrip('.').strip()
                    resto = m.group('resto').strip()
                else:
                    # Último recurso
                    self.autores, _, resto = texto.partition('. ')
                    self.autores = self.autores.strip().rstrip('.').strip()
                    resto = resto.strip()

        # === 2) Detectar ANO (último) e derivar TITULO / COMPLEMENTO ===
        matches = list(re.finditer(r'(?:19|20)\d{2}\b', resto))
        self.ano = ''
        self.complemento = ''
        if matches:
            last = matches[-1]
            self.ano = resto[last.start():last.end()].strip().rstrip('.,')

            # Título = tudo ANTES do último ano
            head = resto[:last.start()].strip()
            # Remove separadores finais redundantes
            head = re.sub(r'[\s\.\,\;\:\-\–]+$', '', head).strip()
            self.titulo = head if head else ''

            # Complemento = tudo APÓS o ano
            tail = resto[last.end():].strip()
            tail = re.sub(r'^[\s\.\,\-\;\:]+', '', tail).strip().rstrip('.,;:').strip()
            self.complemento = tail
        else:
            # Sem ano: usa primeira sentença como título
            titulo, sep, resto2 = resto.partition('. ')
            if not sep:
                m2 = re.match(r'^(?P<t>.+?)\.\s*(?P<r>.+)$', resto)
                if m2:
                    titulo = m2.group('t')
                    resto2 = m2.group('r')
                else:
                    titulo = resto
                    resto2 = ''
            self.titulo = titulo.strip().rstrip('.,;:').strip()
            self.complemento = resto2.strip().rstrip('.,;:').strip()

        # Chave de comparação
        self.chave = self.autores


    def compararCom(self, objeto):
        if self.idMembro.isdisjoint(objeto.idMembro) and similaridade_entre_cadeias(self.titulo, objeto.titulo):
            self.idMembro.update(objeto.idMembro)

            if len(self.autores) < len(objeto.autores):
                self.autores = objeto.autores

            if len(self.titulo) < len(objeto.titulo):
                self.titulo = objeto.titulo

            return self
        else:
            return None


    def html(self, listaDeMembros):
        s = self.autores + '. <b>' + (self.titulo or '') + '</b>. '
        s += (str(self.ano) + '.') if str(self.ano).isdigit() else '.'
        if self.complemento:
            s += ' ' + self.complemento
        return s


    def json(self):
        def nv(x):
            return x if x not in (None, '', []) else None

        return {
            "Autores": nv(self.autores),
            "Título": nv(self.titulo),
            "Descrição": nv(self.complemento),
        }


    # ------------------------------------------------------------------------ #
    def __str__(self):
        try:
            autores = self.autores.encode('utf8', 'replace')
        except Exception:
            autores = str(self.autores)

        try:
            titulo = (self.titulo or '').encode('utf8', 'replace')
        except Exception:
            titulo = str(self.titulo)

        try:
            item = self.item.encode('utf8', 'replace')
        except Exception:
            item = str(self.item)

        s  = "\n[PRODUCAO ARTISTICA] \n"
        s += "+ID-MEMBRO   : " + str(self.idMembro) + "\n"
        s += "+RELEVANTE   : " + str(self.relevante) + "\n"
        s += "+AUTORES     : " + autores + "\n"
        s += "+TITULO      : " + titulo + "\n"
        s += "+ANO         : " + str(self.ano) + "\n"
        s += "+COMPLEMENTO : " + (self.complemento or '') + "\n"
        s += "+item        : " + item + "\n"
        return s

