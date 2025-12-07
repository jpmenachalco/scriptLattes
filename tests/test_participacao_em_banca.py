import sys
from unittest.mock import MagicMock
sys.modules['bs4'] = MagicMock()
sys.modules['selenium'] = MagicMock()
sys.modules['selenium.webdriver'] = MagicMock()
sys.modules['selenium.webdriver.common'] = MagicMock()
sys.modules['selenium.webdriver.common.keys'] = MagicMock()
sys.modules['selenium.webdriver.common.by'] = MagicMock()
sys.modules['selenium.common'] = MagicMock()
sys.modules['selenium.common.exceptions'] = MagicMock()
sys.modules['selenium.webdriver.chrome'] = MagicMock()
sys.modules['selenium.webdriver.chrome.service'] = MagicMock()
sys.modules['networkx'] = MagicMock()
sys.modules['networkx.readwrite'] = MagicMock()

import unittest
from scriptLattes.parserLattes import ParserLattes
from scriptLattes.producoesUnitarias.participacaoEmBanca import ParticipacaoEmBanca

class TestParticipacaoEmBanca(unittest.TestCase):
    def test_parsing_banca_trabalho(self):
        html = """
        <div class="title-wrapper">
            <h1>Bancas</h1>
        </div>
        <div class="layout-cell layout-cell-11">
            <div class="layout-cell-pad-5">
                <div class="inst_back">Participação em bancas de trabalhos de conclusão</div>
            </div>
        </div>
        
        <div class="layout-cell layout-cell-11">
            <div class="layout-cell-pad-5 text-align-right">
                1.
                <div class="layout-cell-pad-5">
                    MOURA, E. S.; BARCELLOS, M. P.; NASCIMENTO, E. L.. Participação em banca de SILVA, N. D., PAULA, Z. E., MORAES, R. F..Sistema de Orçamento de Obra Distribuído. 2003. Trabalho de Conclusão de Curso (Graduação em Sistemas de Informação) - Faculdade Vitoriana de Ensino Superior.
                </div>
            </div>
        </div>
        """
        parser = ParserLattes(1, html)
        self.assertEqual(len(parser.listaParticipacaoEmBancaTrabalho), 1)
        banca = parser.listaParticipacaoEmBancaTrabalho[0]
        self.assertEqual(banca.ano, '2003')
        self.assertIn("Sistema de Orçamento de Obra Distribuído", banca.titulo)

    def test_parsing_banca_comissao(self):
        html = """
        <div class="title-wrapper">
            <h1>Bancas</h1>
        </div>
        <div class="layout-cell layout-cell-11">
            <div class="layout-cell-pad-5">
                <div class="inst_back">Participação em bancas de comissões julgadoras</div>
            </div>
        </div>
        
        <div class="layout-cell layout-cell-11">
            <div class="layout-cell-pad-5 text-align-right">
                1.
                <div class="layout-cell-pad-5">
                    BARCELLOS, M. P.. Banca de concurso para professor adjunto. 2010. Universidade Federal do Espírito Santo.
                </div>
            </div>
        </div>
        """
        parser = ParserLattes(1, html)
        self.assertEqual(len(parser.listaParticipacaoEmBancaComissao), 1)
        banca = parser.listaParticipacaoEmBancaComissao[0]
        self.assertEqual(banca.ano, '2010')
        self.assertIn("Banca de concurso para professor adjunto", banca.titulo)

if __name__ == '__main__':
    unittest.main()
