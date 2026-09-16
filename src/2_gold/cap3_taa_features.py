"""
cap3_taa_features.py
TAA — Taxa de Acerto da Alocação Partidária (indicador lista-nível, Cap. 3).

Para cada lista (partido x UF x ano), ordena os candidatos pelos recursos
partidários recebidos, toma os k = min(Mp, n_com_recursos) primeiros — o
*conjunto designado* — e mede a fração deles que foi eleita.

    TAA = |top-k por recursos do partido ∩ eleitos| / k

Mp é a bancada do partido na UF em exercício na véspera das convenções
(API da Câmara; ver src/0_bronze/bancada_por_partido_uf.py). Ranking e
denominador são integralmente EX-ANTE; o resultado eleitoral entra apenas
como desfecho avaliado, nunca como insumo da definição — o que preserva a
salvaguarda antitautológica do Cap. 3 (Bolognesi et al. 2020).

Ressalvas de nomenclatura e interpretação (não esquecer na redação):
  - Nomear como "taxa de acerto dos Mp maiores recebedores", NUNCA como
    "taxa de acerto dos candidatos que o partido esperava eleger": o ranking
    identifica quem recebeu mais, não quem a liderança projetava eleger.
  - A TAA não discrimina coordenação partidária de captura individual: um
    candidato forte que capturou recursos por conta própria também se elege.
  - A TAA não discrimina alocação top-down de ratificação bottom-up de
    pressões das bases (Hoyler & Marques 2023).

Uso:
    python src/2_gold/cap3_taa_features.py      # salva parquet + imprime tabelas
    from cap3_taa_features import construir_taa, carregar_bancada
"""
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cap3_cs_features import PROCESSED_DATA_PATH, carregar_rrd  # noqa: E402

# Colunas de incumbência "maior" — exclui vereador, como candidato_competitivo
N_ELEICOES_COLS = [
    "n_eleicoes_prefeito",
    "n_eleicoes_deputado_estadual",
    "n_eleicoes_deputado_federal",
    "n_eleicoes_governador",
    "n_eleicoes_senador",
]

# Aliases mínimos para o merge da bancada. NÃO incluir DEM→UNIÃO, PR→PL ou
# PRB→REPUBLICANOS: o snapshot da Câmara já traz a sigla contemporânea de cada
# ano, e aplicá-los quebraria o merge. Cobertura com estes 4: 99,87%.
ALIAS_BANCADA = {
    "PCDOB": "PC DO B",
    "PP**": "PP",
    "SD": "SOLIDARIEDADE",
    "PTDOB": "PT DO B",
}


def _to_ascii(s) -> str:
    """Corrige mojibake (UTF-8 lido como latin-1), remove diacríticos, maiúsculo."""
    if not isinstance(s, str):
        return str(s).upper().strip()
    try:
        fixed = s.encode("latin-1").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        fixed = s
    return "".join(
        c for c in unicodedata.normalize("NFD", fixed) if unicodedata.category(c) != "Mn"
    ).upper().strip()


def norm_partido(s) -> str:
    """Identidade da legenda para merge: ASCII + alias ortográfico."""
    k = _to_ascii(s)
    return ALIAS_BANCADA.get(k, k)


def carregar_bancada() -> pd.DataFrame:
    """
    Mp por (ano_eleicao, sg_uf, sg_partido_norm).

    Versão canônica: normaliza a sigla e soma dentro do grupo, de modo que
    fusões consolidadas na data do snapshot (p.ex. DEM+PSL → UNIÃO em 2022)
    entrem como uma bancada só.
    """
    b = pd.read_csv(PROCESSED_DATA_PATH / "bancada_partido_uf.csv")
    b["sg_partido_norm"] = b["sg_partido"].map(norm_partido)
    return (
        b.groupby(["ano_eleicao", "sg_uf", "sg_partido_norm"])["n_deputados"]
        .sum()
        .reset_index()
        .rename(columns={"n_deputados": "Mp"})
    )


def acertos_fracionarios(score, eleito, k: int, maior_melhor: bool = True) -> float:
    """
    Nº esperado de eleitos entre os k primeiros de `score`, com empates
    contados fracionariamente.

    Quando um bloco de valores idênticos cruza a fronteira do corte, em vez de
    desempatar arbitrariamente conta-se (vagas restantes × taxa de eleição
    dentro do bloco). O resultado é determinístico, independente da ordem
    física das linhas e independente do desfecho — ao contrário de um
    desempate por votos, que seria ex-post.

    NaN em `score` é tratado como pior colocado.
    """
    s = np.asarray(score, dtype=float)
    e = np.asarray(eleito, dtype=float)
    if k <= 0 or len(s) == 0:
        return np.nan

    # Ordenar de forma que menor = melhor, com NaN sempre por último
    chave = -s if maior_melhor else s
    chave = np.where(np.isnan(chave), np.inf, chave)
    ordem = np.argsort(chave, kind="mergesort")
    chave, e = chave[ordem], e[ordem]

    k = min(int(k), len(chave))
    acertos, restantes, i = 0.0, k, 0
    while i < len(chave) and restantes > 0:
        j = i
        while j < len(chave) and chave[j] == chave[i]:
            j += 1
        bloco = j - i
        if bloco <= restantes:
            acertos += e[i:j].sum()
            restantes -= bloco
        else:
            acertos += restantes * e[i:j].mean()
            restantes = 0
        i = j
    return acertos


# Bateria comparativa: nome -> (coluna de score, maior_melhor)
RANKINGS = {
    "taa": ("vr_receita_recursos_partidos", True),
    "taa_outros": ("vr_receita_outros", True),
    "taa_lag": ("prop_votos_nominais_lag", True),
    "taa_timing": ("dias_desde_inicio", False),
    "taa_exante": ("exante_score", True),
}


def _preparar(rrd: pd.DataFrame) -> pd.DataFrame:
    """Merge do Mp, scores auxiliares e tipo_partido ex-ante."""
    df = rrd.copy()
    df["sg_partido_norm"] = df["sg_partido"].map(norm_partido)
    df["vr_receita_recursos_partidos"] = df["vr_receita_recursos_partidos"].fillna(0)
    df["vr_receita_outros"] = df["vr_receita_outros"].fillna(0)

    bancada = carregar_bancada()
    df = df.merge(bancada, on=["ano_eleicao", "sg_uf", "sg_partido_norm"], how="left")
    df["Mp"] = df["Mp"].fillna(0).astype(int)

    # Ranking ex-ante puro (cf. _run_TA_v3.py): incumbência domina, voto t-1 desempata
    incumbente_major = df[N_ELEICOES_COLS].fillna(0).sum(axis=1) > 0
    df["exante_score"] = (
        incumbente_major.astype(float) * 1000.0
        + df["prop_votos_nominais_lag"].fillna(0)
    )

    # tipo_partido EX-ANTE: bancada nacional prévia >= 20 cadeiras. gerar_features
    # traz a versão ex-post (cadeiras eleitas na própria eleição), que classifica
    # o PSL 2018 como competitivo e contamina a leitura.
    banc_nac = (
        bancada.groupby(["ano_eleicao", "sg_partido_norm"])["Mp"]
        .sum()
        .reset_index()
        .rename(columns={"Mp": "bancada_nacional_previa"})
    )
    df = df.merge(banc_nac, on=["ano_eleicao", "sg_partido_norm"], how="left")
    df["bancada_nacional_previa"] = df["bancada_nacional_previa"].fillna(0).astype(int)
    df["tipo_partido_exante"] = np.where(
        df["bancada_nacional_previa"] >= 20, "Competitivo", "Menos competitivo"
    )

    df["dm_cat"] = pd.cut(
        df["qt_vaga"],
        bins=[0, 12, 31, 70],
        labels=["Pequeno (8–12)", "Médio (16–31)", "Grande (39–70)"],
    )
    return df


def construir_taa(rrd: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Dataset lista-nível com a TAA e a bateria comparativa de rankings.

    Universo: listas com Mp >= 1 e ao menos um candidato com recurso
    partidário (k >= 1). Listas com Mp = 0 têm TAA indefinida e são excluídas.
    """
    if rrd is None:
        rrd = carregar_rrd()
    df = _preparar(rrd)

    linhas = []
    for (ano, uf, partido_norm), g in df.groupby(
        ["ano_eleicao", "sg_uf", "sg_partido_norm"], sort=True
    ):
        mp = int(g["Mp"].iloc[0])
        n_cands = len(g)
        n_com_rec = int((g["vr_receita_recursos_partidos"] > 0).sum())
        n_seats = int(g["eleito"].sum())
        k = min(mp, n_com_rec)
        if mp < 1 or k < 1:
            continue

        eleito = g["eleito"].to_numpy()
        base = n_seats / n_cands

        reg = {
            "ano_eleicao": ano,
            "sg_uf": uf,
            "sg_partido": g["sg_partido"].iloc[0],
            "sg_partido_norm": partido_norm,
            "Mp": mp,
            "n_cands": n_cands,
            "n_com_recursos": n_com_rec,
            "n_seats": n_seats,
            "k": k,
            "qt_vaga": int(g["qt_vaga"].iloc[0]),
            "dm_cat": g["dm_cat"].iloc[0],
            "tipo_partido_exante": g["tipo_partido_exante"].iloc[0],
            "bancada_nacional_previa": int(g["bancada_nacional_previa"].iloc[0]),
            "base": base,
        }

        for nome, (col, maior_melhor) in RANKINGS.items():
            # timing exige ao menos k candidatos com data de primeiro repasse
            if nome == "taa_timing" and int(g["dias_desde_inicio"].notna().sum()) < k:
                reg[nome] = np.nan
                continue
            h = acertos_fracionarios(g[col], eleito, k, maior_melhor)
            reg[nome] = h / k
            if nome == "taa":
                reg["acertos"] = h

        # Variante Cox M+1
        k_mp1 = min(mp + 1, n_com_rec)
        reg["taa_mp1"] = (
            acertos_fracionarios(g["vr_receita_recursos_partidos"], eleito, k_mp1)
            / k_mp1
        )
        # Robustez ex-post: corte no nº de cadeiras efetivamente conquistadas.
        # Aqui |designados| = |eleitos|, logo precisão = recall = F1.
        reg["taa_expost_S"] = (
            acertos_fracionarios(g["vr_receita_recursos_partidos"], eleito, n_seats)
            / n_seats
            if n_seats > 0
            else np.nan
        )
        linhas.append(reg)

    out = pd.DataFrame(linhas)
    # Skill score: 0 = acaso, 1 = acerto perfeito, negativo = pior que o acaso
    out["taa_aj"] = np.where(
        out["base"] < 1, (out["taa"] - out["base"]) / (1 - out["base"]), np.nan
    )
    # Listas degeneradas: todos os candidatos foram eleitos (base == 1), logo
    # TAA = 1 por construção e o skill score é indefinido. São listas mínimas
    # (quase todas com 1 candidato) e sua frequência despenca no período —
    # 9,6% em 2014, 8,3% em 2018, 0% em 2022 —, de modo que incluí-las infla a
    # TAA bruta dos anos de coligação e exagera a queda 2014→2022. Comparações
    # entre anos na TAA bruta devem excluí-las; a TAA ajustada já as descarta
    # (taa_aj = NaN).
    out["lista_degenerada"] = out["base"] >= 1
    return out


def tabela_bateria(df: pd.DataFrame, por: list[str] | None = None) -> pd.DataFrame:
    """Médias da bateria comparativa por ano (opcionalmente cruzadas com `por`)."""
    chaves = ["ano_eleicao"] + (por or [])
    cols = ["taa", "taa_outros", "taa_lag", "taa_timing", "taa_exante", "base", "taa_aj"]
    tab = df.groupby(chaves, observed=True)[cols].mean().round(3)
    tab["n_listas"] = df.groupby(chaves, observed=True).size()
    return tab


def diagnostico_merge(rrd: pd.DataFrame | None = None) -> pd.DataFrame:
    """Deputados da bancada sem lista correspondente no rrd (órfãos do merge)."""
    if rrd is None:
        rrd = carregar_rrd()
    listas = rrd.assign(sg_partido_norm=rrd["sg_partido"].map(norm_partido))[
        ["ano_eleicao", "sg_uf", "sg_partido_norm"]
    ].drop_duplicates()
    m = carregar_bancada().merge(
        listas, on=["ano_eleicao", "sg_uf", "sg_partido_norm"], how="left", indicator=True
    )
    return m[m["_merge"] == "left_only"].drop(columns="_merge")


def main() -> None:
    rrd = carregar_rrd()

    orfaos = diagnostico_merge(rrd)
    total_dep = carregar_bancada()["Mp"].sum()
    print("=" * 72)
    print("MERGE DO Mp")
    print(
        f"cobertura: {100 * (1 - orfaos['Mp'].sum() / total_dep):.2f}% "
        f"({orfaos['Mp'].sum()} de {total_dep} deputados sem lista no rrd)"
    )
    if len(orfaos):
        print(orfaos.to_string(index=False))

    df = construir_taa(rrd)
    destino = PROCESSED_DATA_PATH / "df_taa_lista.parquet"
    df.to_parquet(destino, index=False)

    print("\n" + "=" * 72)
    print(f"TAA — {len(df)} listas | salvo em {destino}")
    print("\nListas por ano:")
    print(df.groupby("ano_eleicao").size().to_string())

    deg = df["lista_degenerada"]
    print("\nListas degeneradas (todos eleitos; TAA = 1 por construção):")
    print(df.groupby("ano_eleicao")["lista_degenerada"].agg(["sum", "mean"])
          .round(3).to_string())

    print("\n" + "=" * 72)
    print("BATERIA COMPARATIVA (médias por ano) — universo completo")
    print(tabela_bateria(df).to_string())

    print("\n" + "=" * 72)
    print("BATERIA COMPARATIVA — sem listas degeneradas")
    print("(universo comparável entre anos para a TAA bruta)")
    print(tabela_bateria(df[~deg]).to_string())

    print("\n" + "=" * 72)
    print("TAA por ano x tipo de partido (ex-ante)")
    print(
        tabela_bateria(df, ["tipo_partido_exante"])[
            ["taa", "taa_aj", "base", "n_listas"]
        ].to_string()
    )

    print("\n" + "=" * 72)
    print("TAA por ano x magnitude do distrito")
    print(
        tabela_bateria(df, ["dm_cat"])[["taa", "taa_aj", "base", "n_listas"]].to_string()
    )

    print("\n" + "=" * 72)
    print("VARIANTES DE ÂNCORA (médias por ano)")
    print(
        df.groupby("ano_eleicao")[["taa", "taa_mp1", "taa_expost_S"]]
        .mean()
        .round(3)
        .to_string()
    )


if __name__ == "__main__":
    main()
