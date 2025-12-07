import pytest
import re
from scriptLattes.producoesUnitarias.atuacaoProfissional import AtuacaoProfissional

# Helper to create an instance with given HTML snippet

def make_atp(html_snippet):
    # The parser expects the full item string; we can pass directly
    atp = AtuacaoProfissional(idMembro='test', partesDoItem=['', html_snippet])
    return atp

def test_institution_extracted_from_div():
    html = "<div class=\"inst_back\"><b>Universidade XYZ</b></div> Vínculo: Colaborador"
    atp = make_atp(html)
    assert atp.instituicao == "Universidade XYZ"
    assert atp.vinculo == "Colaborador"

def test_institution_extracted_before_vinculo_when_no_div():
    html = "Universidade ABC Vínculo: Professor"
    atp = make_atp(html)
    assert atp.instituicao == "Universidade ABC"
    assert atp.vinculo == "Professor"

def test_institution_extracted_before_vinculo_malformed_encoding():
    html = "Instituto DEF VÃ­nculo: Pesquisador"
    atp = make_atp(html)
    assert atp.instituicao == "Instituto DEF"
    assert atp.vinculo == "Pesquisador"

def test_missing_institution_results_none():
    html = "Vínculo: Colaborador"
    atp = make_atp(html)
    # Fallback should result in empty string or None depending on implementation
    assert atp.instituicao == "" or atp.instituicao is None
    assert atp.vinculo == "Colaborador"
