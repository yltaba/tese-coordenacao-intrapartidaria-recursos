"""Piloto de avaliação (18/09/2026): as duas extensões empíricas propostas pelo
autor para o Cap. 4 -- (a) lift semana a semana; (b) separar por dentro/fora do
Top-NECr em vez de competitivo/não-competitivo.

Não escreve nada em tese/. Não regenera nenhum artefato oficial do capítulo
(figs/, data/processed/df_cox_survival.parquet). Roda a partir da raiz do
repositório: python piloto_cap4_extensoes.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve()
# Ajuste manual: rodar a partir da raiz real do repo, não do scratchpad.
ROOT = Path(r"C:\Users\yuri_taba\Desktop\recursos-campanha-local")
sys.path.insert(0, str(ROOT / "src" / "2_gold"))

from cap3_survival_features import (  # noqa: E402
    gerar_features_survival, preparar_survival, carregar_receitas,
    calc_cumulative, FONTES_PARTIDO, JANELAS,
)

DATA_PATH = ROOT / "data" / "processed"
ANOS = [2018, 2022]


# ── (b) Top-NECr por candidato, com peso fracionário no empate de fronteira ──

def top_necr_por_candidato(rrd: pd.DataFrame) -> pd.DataFrame:
    """Peso de pertencimento ao Top-NECr por candidatura (0 a 1).

    Replica a regra de cap3_cobertura_top_necr.acertos_fracionarios, mas
    devolve o peso POR CANDIDATO em vez do total agregado da lista: candidatos
    estritamente acima do bloco de fronteira recebem peso 1; os do bloco de
    fronteira dividem as vagas restantes; os demais recebem peso 0.
    """
    linhas = []
    grp = rrd.groupby(["ano_eleicao", "sg_uf", "sg_partido"], sort=False)
    for (ano, uf, partido), g in grp:
        recursos = g["vr_receita_recursos_partidos"].fillna(0.0).to_numpy(dtype=float)
        total = recursos.sum()
        idx = g.index.to_numpy()
        if total <= 0:
            linhas.append(pd.DataFrame({"idx": idx, "top_necr_peso": 0.0}))
            continue
        shares = recursos / total
        necr = 1.0 / np.square(shares).sum()
        k = max(1, int(np.floor(necr + 0.5)))
        k = min(k, len(recursos))

        ordem = np.argsort(-recursos, kind="mergesort")
        recursos_ord, idx_ord = recursos[ordem], idx[ordem]

        peso = np.zeros(len(recursos_ord))
        restantes, i = k, 0
        while i < len(recursos_ord) and restantes > 0:
            j = i
            while j < len(recursos_ord) and recursos_ord[j] == recursos_ord[i]:
                j += 1
            bloco = j - i
            atribuido = min(bloco, restantes)
            peso[i:j] = atribuido / bloco
            restantes -= atribuido
            i = j
        linhas.append(pd.DataFrame({"idx": idx_ord, "top_necr_peso": peso}))

    pesos = pd.concat(linhas, ignore_index=True).set_index("idx")
    out = rrd.copy()
    out["top_necr_peso"] = pesos["top_necr_peso"].reindex(out.index).fillna(0.0)
    out["grupo_necr"] = np.where(
        out["top_necr_peso"] >= 0.5, "Dentro do Top-NECr", "Fora do Top-NECr"
    )
    return out


def carregar_rrd_com_grupos():
    rrd = pd.read_parquet(DATA_PATH / "rrd_df_novo.parquet")
    rrd["nr_candidato"] = rrd["nr_candidato"].astype(str)
    rrd["dias_primeira_receita"] = rrd["dias_desde_inicio"]
    rrd = top_necr_por_candidato(rrd)
    rrd = gerar_features_survival(rrd)
    return rrd


def lookup_grupos(rrd):
    return rrd[
        ["ano_eleicao", "sg_uf", "sg_partido", "nr_candidato",
         "candidato_competitivo", "grupo_necr", "top_necr_peso"]
    ].drop_duplicates()


def resumo_grupo(rrd, ano, col_grupo, rotulo):
    d = rrd[rrd["ano_eleicao"] == ano]
    ct = pd.crosstab(d[col_grupo], d["candidato_competitivo"])
    print(f"\n--- {rotulo}, {ano}: contingência ({col_grupo} x candidato_competitivo) ---")
    print(ct)
    n = len(d)
    n_grp = int((d[col_grupo] == d[col_grupo].cat.categories[-1]
                 if hasattr(d[col_grupo], "cat") else d[col_grupo]).astype(bool).sum()) \
        if False else None
    return ct


# ── (a) Lift semana a semana ──────────────────────────────────────────────────

def fluxo_por_grupo(rrd, lookup, col_grupo, ano):
    df_rec = carregar_receitas()
    df_rec = df_rec[df_rec["fonte_tipo"].isin(FONTES_PARTIDO)].copy()
    df_rec = df_rec[df_rec["ano_eleicao"] == ano].copy()
    df_rec["dias_campanha"] = (
        df_rec["dt_receita"] - JANELAS[ano][0]
    ).dt.days
    df_rec["semana"] = (df_rec["dias_campanha"] // 7) + 1

    m = df_rec.merge(
        lookup[lookup["ano_eleicao"] == ano],
        on=["ano_eleicao", "sg_uf", "sg_partido", "nr_candidato"], how="left",
    )
    m[col_grupo] = m[col_grupo].fillna(
        "Fora do Top-NECr" if col_grupo == "grupo_necr" else False
    )
    return calc_cumulative(m, ["ano_eleicao", col_grupo])


def lift_semanal(rrd, lookup, ano):  # noqa: C901 (piloto, não produção)
    """Lift semanal: proporção acumulada de recursos no Top-NECr / proporção
    esperada ao acaso (peso do Top-NECr no total de recursos financiados da
    lista), calculado semana a semana com o fluxo cumulativo de receitas.

    Expectativa aleatória: para cada lista, a fração de recursos que um
    conjunto do MESMO TAMANHO (k_l posições) receberia se distribuído
    proporcionalmente ao número de candidatos (k_l / C_l), aplicada ao total
    cumulativo observado até a semana w. É o análogo temporal do benchmark
    hipergeométrico usado no Cap. 3 para cobertura/precisão de recursos, mas
    aqui aplicado ao fluxo cumulativo em vez do total final.
    """
    df_rec = carregar_receitas()
    df_rec = df_rec[df_rec["fonte_tipo"].isin(FONTES_PARTIDO)].copy()
    df_rec = df_rec[df_rec["ano_eleicao"] == ano].copy()
    df_rec["dias_campanha"] = (df_rec["dt_receita"] - JANELAS[ano][0]).dt.days
    df_rec["semana"] = (df_rec["dias_campanha"] // 7) + 1

    lk = lookup[lookup["ano_eleicao"] == ano][
        ["sg_uf", "sg_partido", "nr_candidato", "top_necr_peso"]
    ]
    m = df_rec.merge(lk, on=["sg_uf", "sg_partido", "nr_candidato"], how="left")
    m["top_necr_peso"] = m["top_necr_peso"].fillna(0.0)
    m["receita_top"] = m["vr_receita"] * m["top_necr_peso"]

    max_semana = int(np.ceil((JANELAS[ano][1] - JANELAS[ano][0]).days / 7))
    linhas = []
    cum_total, cum_top = 0.0, 0.0
    for w in range(1, max_semana + 1):
        sem = m[m["semana"] == w]
        cum_total += sem["vr_receita"].sum()
        cum_top += sem["receita_top"].sum()
        prop_top_obs = cum_top / cum_total if cum_total > 0 else np.nan
        linhas.append({"semana": w, "prop_top_observada": prop_top_obs,
                        "cum_total": cum_total, "cum_top": cum_top})
    df_out = pd.DataFrame(linhas)

    # Referência ao acaso: k_l/C_l de cada lista (TODAS as candidaturas da
    # lista, não só quem recebeu receita no feed), ponderada pelo total de
    # recursos partidários FINAL da própria lista -- constante ao longo das
    # semanas, análoga ao benchmark hipergeométrico G*k/C do Cap. 3, mas
    # aplicada ao fluxo cumulativo em vez do total de fim de campanha.
    base = rrd[rrd["ano_eleicao"] == ano]
    por_lista = base.groupby(["sg_uf", "sg_partido"]).agg(
        k_l=("top_necr_peso", "sum"),
        c_l=("nr_candidato", "nunique"),
        total_l=("vr_receita_recursos_partidos", lambda s: s.fillna(0).sum()),
    )
    por_lista = por_lista[por_lista["total_l"] > 0]
    ref = (por_lista["k_l"] / por_lista["c_l"] * por_lista["total_l"]).sum() \
        / por_lista["total_l"].sum()
    df_out["prop_top_esperada_acaso"] = ref
    df_out["lift_semanal"] = df_out["prop_top_observada"] / ref
    return df_out


if __name__ == "__main__":
    rrd = carregar_rrd_com_grupos()
    lookup = lookup_grupos(rrd)

    print("=" * 70)
    print("(b) Quanto 'dentro do Top-NECr' e 'competitivo' se sobrepõem?")
    print("=" * 70)
    for ano in ANOS:
        d = rrd[rrd["ano_eleicao"] == ano]
        ct = pd.crosstab(d["grupo_necr"], d["candidato_competitivo"])
        print(f"\n{ano}:")
        print(ct)
        jaccard = ct.loc["Dentro do Top-NECr", True] / (
            ct.loc["Dentro do Top-NECr"].sum() + ct[True].sum()
            - ct.loc["Dentro do Top-NECr", True]
        )
        print(f"Índice de Jaccard (Top-NECr ∩ competitivo): {jaccard:.3f}")

    print("\n" + "=" * 70)
    print("(b) Fluxo cumulativo por grupo_necr (dentro/fora do Top-NECr)")
    print("=" * 70)
    for ano in ANOS:
        df_cum = fluxo_por_grupo(rrd, lookup, "grupo_necr", ano)
        piv = df_cum.pivot(index="semana", columns="grupo_necr", values="cum_prop")
        print(f"\n{ano} (proporção acumulada por semana):")
        print(piv.head(3).round(4))

    print("\n" + "=" * 70)
    print("(a) Lift semanal (Top-NECr no fluxo cumulativo vs. expectativa ao acaso)")
    print("=" * 70)
    for ano in ANOS:
        lf = lift_semanal(rrd, lookup, ano)
        print(f"\n{ano}:")
        print(lf[["semana", "prop_top_observada", "prop_top_esperada_acaso",
                   "lift_semanal"]].head(6).round(4))
