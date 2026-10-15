import pytest

from scriptLattes.parserLattes import ParserLattes


@pytest.mark.parametrize('padding', [5, 6])
def test_extracts_all_awards_and_stops_at_next_section(padding):
    html = f'''
    <div class="title-wrapper"><h1>Prêmios e títulos</h1></div>
    <div class="layout-cell layout-cell-12 data-cell">
        <div class="layout-cell layout-cell-3 text-align-right">
            <div class="layout-cell-pad-{padding} text-align-right"><b>2026</b></div>
        </div>
        <div class="layout-cell layout-cell-9">
            <div class="layout-cell-pad-5">Prêmio Sócio Destaque, SBC.</div>
        </div>
        <div class="layout-cell layout-cell-3 text-align-right">
            <div class="layout-cell-pad-{padding} text-align-right"><b>2025</b></div>
        </div>
        <div class="layout-cell layout-cell-9">
            <div class="layout-cell-pad-5">Homenagem Mulheres na Ciência, PUCRS.</div>
        </div>
        <div class="layout-cell layout-cell-3 text-align-right">
            <div class="layout-cell-pad-{padding} text-align-right"><b>2025</b></div>
        </div>
        <div class="layout-cell layout-cell-9">
            <div class="layout-cell-pad-5">Recognition of Service, ACM.</div>
        </div>
    </div>
    <div class="title-wrapper"><h1>Formação acadêmica/titulação</h1></div>
    <div class="layout-cell layout-cell-12 data-cell">
        <div class="layout-cell layout-cell-3 text-align-right">
            <div class="layout-cell-pad-{padding} text-align-right"><b>2000</b></div>
        </div>
        <div class="layout-cell layout-cell-9">
            <div class="layout-cell-pad-5">Doutorado em Ciência da Computação.</div>
        </div>
    </div>
    '''

    parser = ParserLattes(49, html)

    assert [(award.ano, award.descricao) for award in parser.listaPremioOuTitulo] == [
        ('2026', 'Prêmio Sócio Destaque, SBC.'),
        ('2025', 'Homenagem Mulheres na Ciência, PUCRS.'),
        ('2025', 'Recognition of Service, ACM.'),
    ]
    assert len(parser.listaFormacaoAcademica) == 1

    next_cv = html[html.index('<div class="title-wrapper"><h1>Formação'):]
    next_parser = ParserLattes(50, next_cv)

    assert next_parser.listaPremioOuTitulo == []
    assert len(next_parser.listaFormacaoAcademica) == 1
    assert len(parser.listaPremioOuTitulo) == 3
