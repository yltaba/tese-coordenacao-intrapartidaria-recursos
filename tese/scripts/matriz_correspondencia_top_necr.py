"""Matriz de correspondência nacional, preservando os créditos do Atlas."""
from pathlib import Path

import numpy as np
import pandas as pd


def calcular():
    out = Path(__file__).resolve().parents[1] / 'resultados-capitulo-3'
    listas = pd.read_csv(out / '25_todas_nominatas.csv')
    referencia = pd.read_csv(out / '15_cobertura_nacional.csv')
    referencia = referencia[referencia['Regra de k'].eq('arredondado')].set_index('Ano')
    assert not listas.duplicated(['Ano', 'UF', 'Partido']).any()
    detalhe = listas[['Ano', 'UF', 'Partido']].copy()
    detalhe['Dentro: eleitos'] = listas.eleitos_top_arredondado
    detalhe['Dentro: não eleitos'] = listas.k_arredondado - listas.eleitos_top_arredondado
    detalhe['Fora: eleitos'] = listas.E - listas.eleitos_top_arredondado
    detalhe['Fora: não eleitos'] = listas.C - listas.E - detalhe['Dentro: não eleitos']
    celulas = detalhe.columns[3:]
    assert detalhe[celulas].ge(-1e-9).all().all()
    assert np.allclose(detalhe[celulas].sum(axis=1), listas.C)
    matriz = detalhe.groupby('Ano')[list(celulas)].sum()
    linhas = []
    for ano, r in matriz.iterrows():
        ref = referencia.loc[ano]
        dentro = r['Dentro: eleitos'] + r['Dentro: não eleitos']
        eleitos = r['Dentro: eleitos'] + r['Fora: eleitos']
        assert eleitos == 513
        assert np.allclose([r.sum(), dentro, r['Dentro: eleitos']],
                           [ref['Candidatos'], ref['Posições Top-k'], ref['Eleitos cobertos (fracionários)']])
        assert np.isclose(100 * r['Dentro: eleitos'] / eleitos, ref['Cobertura nacional (%)'])
        assert np.isclose(100 * r['Dentro: eleitos'] / dentro, ref['Precisão nacional (%)'])
        for pos in ['Dentro', 'Fora']:
            e, n = r[f'{pos}: eleitos'], r[f'{pos}: não eleitos']
            linhas.append([ano, pos + ' do Top-NECr', e, n, e + n])
        linhas.append([ano, 'Total', eleitos, r.sum() - eleitos, r.sum()])
    tabela = pd.DataFrame(linhas, columns=['Ano', 'Posição', 'Eleitos', 'Não eleitos', 'Total'])
    detalhe.to_csv(out / 'matriz_correspondencia_top_necr_nominatas.csv', index=False, encoding='utf-8-sig')
    tabela.to_csv(out / 'matriz_correspondencia_top_necr.csv', index=False, encoding='utf-8-sig')
    def fmt(v):
        return f'{v:,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.')
    texto = ['| Ano | Posição | Eleitos | Não eleitos | Total |',
             '|:---|:---|---:|---:|---:|']
    for ano, pos, e, n, total in linhas:
        texto.append(f'| {ano} | {pos} | {fmt(e)} | {fmt(n)} | {fmt(total)} |')
    texto += ['', ': Matriz de correspondência entre pertencimento ao Top-NECr e eleição, por ano. Fonte: elaboração própria com base nos dados do TSE e nas contagens por nominata do Atlas. {#tbl-matriz-top-necr}', '']
    (out / 'matriz_correspondencia_top_necr.qmd').write_text('\n'.join(texto), encoding='utf-8')
    print(tabela.to_string(index=False))
    print('Verificado: células não negativas, totais de candidatos e 513 eleitos por ano; cobertura e precisão idênticas às do Atlas.')


if __name__ == '__main__':
    calcular()
