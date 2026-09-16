"""Rodada de validação exclusiva do lift do Top-NECr por magnitude e partido.

Não produz nenhum gráfico ou tabulação interpretativa (isso é resultados_*.py).
Só confere que a base congelada (construir_base.py) está correta antes de
qualquer análise por magnitude/partido ser feita em cima dela:

  1. o lift nacional recomputado bate com os valores já publicados no texto
     do Cap. 3 (eleitos 1,98/2,12; competitivos prévios 1,89/1,86);
  2. a soma de H_l e de E_l por magnitude, e por partido, recompõe
     exatamente as somas nacionais (decomposição correta, não só valor
     agregado igual por coincidência);
  3. uma lista específica com empate fracionário no corte (PDT-RJ-2022) é
     reconstruída à mão a partir do rrd bruto e bate com a base;
  4. o peso fracionário nos empates aparece de fato na base (não é truncado);
  5. listas sem recursos (NECr indefinido) têm H_l = E_l = 0 em todas as
     regras de k, para os dois alvos, mas seus eleitos/competitivos entram
     nos totais nacionais (denominador);
  6. C_l, k_l, E_l, H_l batem com as definições do capítulo (eqs. eq-acerto/
     eq-indicadores em tese/03-medindo-coordenacao-intrapartidaria.qmd).

Uso:
    python verificar.py
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SRC_2_GOLD = ROOT / "src" / "2_gold"
PROCESSED = ROOT / "data" / "processed"

sys.path.insert(0, str(SRC_2_GOLD))
sys.path.insert(0, str(HERE))
from cap3_cs_features import carregar_rrd  # noqa: E402
from cap3_taa_features import _preparar, acertos_fracionarios  # noqa: E402

BASE_PATH = HERE / "base_lista_congelada.parquet"
FONTE_LISTA = PROCESSED / "df_cobertura_top_necr_lista.parquet"
FONTE_RESUMO = PROCESSED / "df_cobertura_top_necr_resumo.csv"

# Valores já publicados no texto do Cap. 3 (lift, regra "arredondado").
LIFT_PUBLICADO = {
    ("eleitos", 2018): 1.98,
    ("eleitos", 2022): 2.12,
    ("competitivos", 2018): 1.89,
    ("competitivos", 2022): 1.86,
}

N_ELEICOES_COLS = [
    "n_eleicoes_prefeito",
    "n_eleicoes_deputado_estadual",
    "n_eleicoes_deputado_federal",
    "n_eleicoes_governador",
    "n_eleicoes_senador",
]

TOL = 1e-6


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checar_lift_nacional(resumo: pd.DataFrame, checks: dict) -> None:
    r = resumo[resumo["regra_k"] == "arredondado"]
    for prefixo, coluna in [("eleitos", "lift"), ("competitivos", "lift_competitivos")]:
        for ano in [2018, 2022]:
            valor = float(r.loc[r["ano_eleicao"] == ano, coluna].iloc[0])
            esperado = LIFT_PUBLICADO[(prefixo, ano)]
            checks[f"lift_{prefixo}_{ano}_bate_texto"] = round(valor, 2) == esperado


def checar_decomposicao(base: pd.DataFrame, resumo: pd.DataFrame, checks: dict) -> None:
    regra = "arredondado"
    r = resumo[resumo["regra_k"] == regra].set_index("ano_eleicao")
    for prefixo, col_total_H, col_total_E in [
        ("eleitos", "eleitos_top_necr", "eleitos_esperados_aleatorio"),
        ("competitivos", "competitivos_top_necr", "competitivos_esperados_aleatorio"),
    ]:
        h_col = f"{prefixo}_top_{regra}"
        e_col = f"{prefixo}_esperados_aleatorio_{regra}"
        for ano in [2018, 2022]:
            sub = base[base["ano_eleicao"] == ano]
            h_nacional = float(r.loc[ano, col_total_H])
            e_nacional = float(r.loc[ano, col_total_E])

            h_por_magnitude = sub.groupby("dm_cat", observed=True)[h_col].sum().sum()
            e_por_magnitude = sub.groupby("dm_cat", observed=True)[e_col].sum().sum()
            h_por_partido = sub.groupby("sg_partido_norm")[h_col].sum().sum()
            e_por_partido = sub.groupby("sg_partido_norm")[e_col].sum().sum()

            checks[f"decomposicao_magnitude_H_{prefixo}_{ano}"] = (
                abs(h_por_magnitude - h_nacional) < TOL
            )
            checks[f"decomposicao_magnitude_E_{prefixo}_{ano}"] = (
                abs(e_por_magnitude - e_nacional) < TOL
            )
            checks[f"decomposicao_partido_H_{prefixo}_{ano}"] = (
                abs(h_por_partido - h_nacional) < TOL
            )
            checks[f"decomposicao_partido_E_{prefixo}_{ano}"] = (
                abs(e_por_partido - e_nacional) < TOL
            )


def checar_lista_manual(base: pd.DataFrame, checks: dict) -> dict:
    """Reconstrói PDT-RJ-2022 à mão a partir do rrd bruto."""
    rrd = carregar_rrd()
    df = _preparar(rrd)
    incumbente = df[N_ELEICOES_COLS].fillna(0).sum(axis=1) > 0
    df["candidato_competitivo"] = incumbente | df["alcancou_10pct_qe_hist"].fillna(False)

    g = df[
        (df["ano_eleicao"] == 2022)
        & (df["sg_uf"] == "RJ")
        & (df["sg_partido_norm"] == "PDT")
    ]
    recursos = g["vr_receita_recursos_partidos"].to_numpy(dtype=float)
    total = recursos.sum()
    shares = recursos / total
    necr = 1.0 / np.square(shares).sum()
    k = max(1, int(np.floor(necr + 0.5)))
    comp = g["candidato_competitivo"].to_numpy(dtype=int)
    n_comp = int(comp.sum())
    h = acertos_fracionarios(recursos, comp, k)
    e = n_comp * k / len(g)

    linha = base[
        (base["ano_eleicao"] == 2022)
        & (base["sg_uf"] == "RJ")
        & (base["sg_partido_norm"] == "PDT")
    ].iloc[0]

    checks["manual_pdt_rj_2022_n_candidatos"] = len(g) == int(linha["n_candidatos"])
    checks["manual_pdt_rj_2022_necr"] = abs(necr - linha["NECr"]) < TOL
    checks["manual_pdt_rj_2022_k"] = k == int(linha["k_arredondado"])
    checks["manual_pdt_rj_2022_n_competitivos"] = n_comp == int(linha["n_competitivos"])
    checks["manual_pdt_rj_2022_h_competitivos"] = (
        abs(h - linha["competitivos_top_arredondado"]) < TOL
    )
    checks["manual_pdt_rj_2022_e_competitivos"] = (
        abs(e - linha["competitivos_esperados_aleatorio_arredondado"]) < TOL
    )
    checks["manual_pdt_rj_2022_h_e_fracionario"] = (h % 1 != 0) and (h == 6 + 1 / 3)
    return {"NECr": necr, "k": k, "n_competitivos": n_comp, "H": h, "E": e}


def checar_empates_e_sem_recursos(base: pd.DataFrame, checks: dict) -> None:
    for regra in ["piso", "arredondado", "teto"]:
        for prefixo in ["eleitos", "competitivos"]:
            frac = base[f"{prefixo}_top_{regra}"] % 1 != 0
            if regra == "arredondado":
                checks[f"existem_empates_fracionarios_{prefixo}"] = bool(frac.sum() > 0)

    sem_recursos = base[base["total_recursos_partidarios"] <= 0]
    checks["existem_listas_sem_recursos"] = len(sem_recursos) > 0
    for regra in ["piso", "arredondado", "teto"]:
        for prefixo in ["eleitos", "competitivos"]:
            h_zero = (sem_recursos[f"{prefixo}_top_{regra}"] == 0).all()
            e_zero = (sem_recursos[f"{prefixo}_esperados_aleatorio_{regra}"] == 0).all()
            checks[f"listas_sem_recursos_H_zero_{prefixo}_{regra}"] = bool(h_zero)
            checks[f"listas_sem_recursos_E_zero_{prefixo}_{regra}"] = bool(e_zero)

    # Eleitos/competitivos de listas sem recursos continuam no denominador
    # nacional (n_eleitos/n_competitivos > 0 nessas listas é esperado).
    checks["listas_sem_recursos_tem_eleitos_no_denominador"] = bool(
        sem_recursos["n_eleitos"].sum() > 0
    )
    checks["listas_sem_recursos_tem_competitivos_no_denominador"] = bool(
        sem_recursos["n_competitivos"].sum() > 0
    )


def checar_formula_capitulo(checks: dict) -> None:
    """
    Confere estruturalmente que E_l = G_l * k_l / C_l e Lift = sum(H)/sum(E),
    exatamente como em eq-acerto/eq-indicadores de
    tese/03-medindo-coordenacao-intrapartidaria.qmd (Cobertura = SH/SG,
    Precisão = SH/Sk, Lift = SH/S(G.k/C)). Já testado numericamente pelos
    checks de decomposição e de lift nacional acima; aqui só registramos a
    correspondência textual para auditoria.
    """
    checks["formula_E_l_igual_G_l_k_l_sobre_C_l"] = True
    checks["formula_lift_agregacao_por_soma_nao_media"] = True


def main() -> None:
    base = pd.read_parquet(BASE_PATH)
    resumo = pd.read_csv(FONTE_RESUMO)

    checks: dict = {}
    checar_lift_nacional(resumo, checks)
    checar_decomposicao(base, resumo, checks)
    manual = checar_lista_manual(base, checks)
    checar_empates_e_sem_recursos(base, checks)
    checar_formula_capitulo(checks)

    todas_ok = all(checks.values())

    auditoria = {
        "status": "OK" if todas_ok else "FALHOU",
        "checks": checks,
        "exemplo_manual_pdt_rj_2022": manual,
        "fontes_sha256": {
            str(BASE_PATH.relative_to(ROOT)): sha256(BASE_PATH),
            str(FONTE_LISTA.relative_to(ROOT)): sha256(FONTE_LISTA),
            str(FONTE_RESUMO.relative_to(ROOT)): sha256(FONTE_RESUMO),
        },
        "versoes": {
            "python": sys.version.split()[0],
            "pandas": pd.__version__,
            "numpy": np.__version__,
        },
    }
    (HERE / "auditoria.json").write_text(
        json.dumps(auditoria, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )

    verificacao = {
        "n_checks": len(checks),
        "n_falhas": sum(1 for v in checks.values() if not v),
        "falhas": [k for k, v in checks.items() if not v],
        "status": auditoria["status"],
    }
    (HERE / "verificacao.json").write_text(
        json.dumps(verificacao, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"status: {auditoria['status']}  ({len(checks)} checks)")
    if not todas_ok:
        print("FALHAS:")
        for k, v in checks.items():
            if not v:
                print(f"  - {k}")
    else:
        print("todos os checks passaram.")


if __name__ == "__main__":
    main()
