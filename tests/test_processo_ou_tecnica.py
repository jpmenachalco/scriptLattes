
import unittest
from scriptLattes.producoesTecnicas.processoOuTecnica import ProcessoOuTecnica

class TestProcessoOuTecnica(unittest.TestCase):
    def test_extraction_with_year(self):
        # Simulate a standard entry
        partesDoItem = [None, "BARCELLOS, M. P.. Instrumento de Avaliação. 2024."]
        pt = ProcessoOuTecnica("id123", partesDoItem, False)
        self.assertEqual(pt.ano, "2024")
        self.assertEqual(pt.titulo, "Instrumento de Avaliação")

    def test_extraction_user_case(self):
        # Simulate the user's case where year might be missing or 0
        # We don't know the exact input string yet, so we'll try a few variations
        
        # Variation 1: Year present
        partesDoItem = [None, "BARCELLOS, M. P.. Instrumento de Avaliação de Repositórios de Medição visando ao Controle Estatístico de Processos. 2023. Processo ou técnica"]
        pt = ProcessoOuTecnica("id123", partesDoItem, False)
        self.assertEqual(pt.ano, "2023")

        # Variation 2: Year missing (should be empty string, not 0)
        partesDoItem = [None, "BARCELLOS, M. P. Instrumento de Avaliação de Repositórios de Medição visando ao Controle Estatístico de Processos. Processo ou técnica"]
        pt = ProcessoOuTecnica("id123", partesDoItem, False)
        self.assertEqual(pt.ano, "")

    def test_extraction_with_parenthesis_before_year(self):
        # Case from the user: Title (Nature). Year.
        partesDoItem = [None, "BARCELLOS, M. P.. Instrumento de Avaliação de Repositórios de Medição visando ao Controle Estatístico de Processos (IARM). 2015."]
        pt = ProcessoOuTecnica("id123", partesDoItem, False)
        self.assertEqual(pt.ano, "2015")
        self.assertEqual(pt.natureza, "IARM")
        self.assertEqual(pt.titulo, "Instrumento de Avaliação de Repositórios de Medição visando ao Controle Estatístico de Processos")

if __name__ == '__main__':
    unittest.main()
