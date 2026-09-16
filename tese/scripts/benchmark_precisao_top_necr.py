"""Benchmark nacional: razão de somas, ponderando a taxa-base pelo tamanho k."""
import numpy as np
import pandas as pd
import hashlib
import json
import platform
from pathlib import Path


def calcular_benchmark(out):
    d = pd.read_csv(out / '25_todas_nominatas.csv')
    reference = pd.read_csv(out / '15_cobertura_nacional.csv')
    reference = reference[reference['Regra de k'] == 'arredondado'].set_index('Ano')
    assert not d.duplicated(['Ano', 'UF', 'Partido']).any()
    assert d.C.gt(0).all()
    assert d.k_arredondado.between(0, d.C).all()
    detail = d[['Ano', 'UF', 'Partido', 'C', 'E', 'k_arredondado', 'eleitos_top_arredondado']].copy()
    detail['Eleitos esperados ao acaso'] = detail.k_arredondado * detail.E / detail.C
    detail['Precisão aleatória da lista'] = (detail.E / detail.C).where(detail.k_arredondado > 0)
    detail['Precisão observada da lista'] = detail.eleitos_top_arredondado / detail.k_arredondado.where(detail.k_arredondado > 0)
    detail['Peso na precisão nacional'] = detail.k_arredondado / detail.groupby('Ano').k_arredondado.transform('sum')
    rows = []
    for year, g in d.groupby('Ano'):
        k = g.k_arredondado.sum()
        seats = g.E.sum()
        hits = g.eleitos_top_arredondado.sum()
        expected = (g.k_arredondado * g.E / g.C).sum()
        r = reference.loc[year]
        assert np.allclose([k, seats, hits, expected], [r['Posições Top-k'], r['Eleitos'], r['Eleitos cobertos (fracionários)'], r['Eleitos esperados ao acaso']])
        rows.append({'Ano': year, 'Posições Top-k': k, 'Eleitos': seats,
                     'Eleitos observados no núcleo': hits, 'Eleitos esperados ao acaso': expected,
                     'Cobertura nacional (%)': 100 * hits / seats,
                     'Cobertura aleatória (%)': 100 * expected / seats,
                     'Precisão nacional (%)': 100 * hits / k,
                     'Precisão aleatória (%)': 100 * expected / k,
                     'Lift nacional': hits / expected})
    result = pd.DataFrame(rows).set_index('Ano')
    assert np.allclose(result['Precisão nacional (%)'] / result['Precisão aleatória (%)'], result['Lift nacional'])
    assert np.allclose(result['Cobertura nacional (%)'] / result['Cobertura aleatória (%)'], result['Lift nacional'])
    result.to_csv(out / 'benchmark_precisao_top_necr.csv', encoding='utf-8-sig')
    detail.to_csv(out / 'benchmark_precisao_top_necr_nominatas.csv', index=False, encoding='utf-8-sig')
    sources = [out / '25_todas_nominatas.csv', out / '15_cobertura_nacional.csv', Path(__file__)]
    manifest = {
        'status': 'OK', 'nominatas': len(d),
        'python': platform.python_version(), 'pandas': pd.__version__, 'numpy': np.__version__,
        'sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        'verificacoes': ['Chaves de nominata únicas', 'C > 0 e 0 <= k <= C',
                         'Contagens observadas e esperadas coincidem com relatório de origem',
                         'Lift de precisão = lift de cobertura = observados / esperados'],
        'formulas': {'esperados': 'sum(k_l * E_l / C_l)',
                     'precisao_aleatoria': 'sum(k_l * E_l / C_l) / sum(k_l)',
                     'precisao_observada': 'sum(eleitos_top_l) / sum(k_l)',
                     'lift': 'sum(eleitos_top_l) / sum(k_l * E_l / C_l)'},
    }
    (out / 'benchmark_precisao_top_necr_verificacao.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    return result


if __name__ == '__main__':
    print(calcular_benchmark(Path(__file__).resolve().parents[1] / 'resultados-capitulo-3').to_string())
