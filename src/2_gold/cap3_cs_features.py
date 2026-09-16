"""
cap4_features.py
Engenharia de features compartilhada entre os scripts de figuras do Capítulo 4 (Seção 3.1).
Importado por cap4_plot_necr_eficiencia.py, cap4_plot_fortes_vagas.py e cap4_plot_lw_fl.py.
"""
import numpy as np
import pandas as pd
from pathlib import Path

PROCESSED_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "processed"
FIGS_PATH = Path(__file__).resolve().parents[2] / "figs"


def carregar_rrd() -> pd.DataFrame:
    return pd.read_parquet(PROCESSED_DATA_PATH / "rrd_df_novo.parquet")


def gerar_features(rrd: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona variáveis derivadas ao rrd_df para as análises do Cap. 4 (Seção 3.1):
    - prop_vr_receita_candidato, n_seats, n_cands
    - rank_votos, pos_relativa, rank_recursos
    - dm_cat, tipo_partido (via cadeiras_nacionais)
    - incumbente, candidato_competitivo (ex-ante), candidato_forte_cs (ex-post)
    """
    rrd = rrd.copy()

    # Receitas de partido: NaN → 0 (candidato não recebeu)
    rrd["vr_receita_recursos_partidos"] = rrd["vr_receita_recursos_partidos"].fillna(0)

    # Total de todos os recursos de campanha (partido + outros)
    rrd["vr_receita_total"] = (
        rrd["vr_receita_recursos_partidos"] + rrd["vr_receita_outros"].fillna(0)
    )

    # Share de recursos do partido dentro da lista (partido × uf × ano)
    if "prop_vr_receita_candidato" not in rrd.columns:
        total_lista = rrd.groupby(["ano_eleicao", "sg_uf", "sg_partido"])[
            "vr_receita_recursos_partidos"
        ].transform("sum")
        rrd["prop_vr_receita_candidato"] = np.where(
            total_lista > 0, rrd["vr_receita_recursos_partidos"] / total_lista, 0
        )

    # Vagas conquistadas e total de candidatos por lista
    rrd["n_seats"] = rrd.groupby(["ano_eleicao", "sg_uf", "sg_partido"])["eleito"].transform("sum")
    rrd["n_cands"] = rrd.groupby(["ano_eleicao", "sg_uf", "sg_partido"])["nr_candidato"].transform("count")

    # Rank por votos nominais (1 = mais votado) e posição relativa ao corte eleito/não-eleito
    rrd["rank_votos"] = (
        rrd.groupby(["ano_eleicao", "sg_uf", "sg_partido"])["qt_votos_nominais"]
        .rank(ascending=False, method="first")
        .astype(int)
    )
    rrd["pos_relativa"] = rrd["rank_votos"] - rrd["n_seats"]
    # 0=LW, -1=NLW, -2=NNLW, +1=FL, +2=SL, +3=TL

    # Rank por recursos recebidos do partido dentro da lista
    rrd["rank_recursos"] = (
        rrd.groupby(["ano_eleicao", "sg_uf", "sg_partido"])["vr_receita_recursos_partidos"]
        .rank(ascending=False, method="first", na_option="bottom")
        .astype(int)
    )

    # Magnitude do distrito
    rrd["dm_cat"] = pd.cut(
        rrd["qt_vaga"],
        bins=[0, 12, 31, 70],
        labels=["Pequeno (8–12)", "Médio (16–31)", "Grande (39–70)"],
    )

    # Competitividade do partido (cadeiras nacionais ≥ 20)
    nat_seats = (
        rrd.groupby(["ano_eleicao", "sg_partido"])["eleito"]
        .sum()
        .reset_index()
        .rename(columns={"eleito": "cadeiras_nacionais"})
    )
    rrd = rrd.merge(nat_seats, on=["ano_eleicao", "sg_partido"], how="left")
    rrd["tipo_partido"] = np.where(rrd["cadeiras_nacionais"] >= 20, "Competitivo", "Menos competitivo")

    # Incumbente: vitória prévia em qualquer cargo exceto Vereador
    n_eleicoes_cols = [
        "n_eleicoes_prefeito",
        "n_eleicoes_deputado_estadual",
        "n_eleicoes_deputado_federal",
        "n_eleicoes_governador",
        "n_eleicoes_senador",
    ]
    rrd["incumbente"] = rrd[n_eleicoes_cols].fillna(0).sum(axis=1) > 0

    # Candidato competitivo — definição EX-ANTE (canônica para a tese):
    # incumbente OU ≥10% do QE em alguma eleição ANTERIOR (critérios a+b de
    # Cheibub & Sin 2020). Usa apenas informação disponível ao partido ANTES do
    # resultado da eleição corrente. É esta a flag que deve ser usada em todas as
    # análises da tese.
    rrd["candidato_competitivo"] = (
        rrd["incumbente"]
        | rrd["alcancou_10pct_qe_hist"].fillna(False)
    )
    # Variante com QE nominal no histórico (robustez)
    rrd["candidato_competitivo_nom"] = (
        rrd["incumbente"]
        | rrd["alcancou_10pct_qe_hist_nom"].fillna(False)
    )

    # Candidato forte — replicação LITERAL de Cheibub & Sin (2020): acrescenta o
    # critério (c) ≥10% do QE na ELEIÇÃO CORRENTE, que é EX-POST. NÃO usar nas
    # análises da tese (contamina a medida com o resultado eleitoral); mantido
    # apenas para reproduzir a definição exata dos autores quando necessário.
    rrd["candidato_forte_cs"] = (
        rrd["candidato_competitivo"] | rrd["10pct_qe_eleicao_atual"]
    )
    rrd["candidato_forte_cs_nom"] = (
        rrd["candidato_competitivo_nom"] | rrd["10pct_qe_eleicao_atual"]
    )

    return rrd
