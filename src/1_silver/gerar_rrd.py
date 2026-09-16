import pandas as pd
from pathlib import Path
import numpy as np

PROCESSED_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "processed"
RAW_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "raw"

TXT_ELEITOS = ["ELEITO", "ELEITO POR MÉDIA", "MÉDIA", "ELEITO POR QP"]

# Cargos cujo nr_candidato só é exclusivo dentro do município (não da UF).
CARGOS_MUNICIPAIS = {"PREFEITO", "VICE-PREFEITO", "VEREADOR"}

JANELAS_CAMPANHA = {
    2014: ("2014-07-06", "2014-10-05"),  # Res. TSE 23.404/2014: campanha inicia em 06/07
    2018: ("2018-08-16", "2018-10-07"),
    2022: ("2022-08-16", "2022-10-02"),
}

# Harmonização de ds_fonte_receita entre os formatos pré e pós-FEFC.
# A coluna original (ds_fonte_receita) é mantida; esta tabela gera ds_fonte_receita_harm
# e fonte_primeiro_repasse no rrd.
_FONTE_HARM = {
    # 2014 (pré-FEFC) — valores originais do campo "fonte recurso"
    "Fundo Partidario":              "FUNDO_PARTIDARIO",
    "Outros Recursos nao descritos": "OUTROS_RECURSOS",
    "Nao especificado":              "OUTROS_RECURSOS",
    # 2018/2022 (pós-FEFC) — valores originais de ds_fonte_receita
    "FUNDO ESPECIAL":                "FEFC",
    "FUNDO PARTIDARIO":              "FUNDO_PARTIDARIO",
    "OUTROS RECURSOS":               "OUTROS_RECURSOS",
    "#NULO":                         "OUTROS_RECURSOS",
}


# ---------------------------------------------------------------------------
# Carregamento
# ---------------------------------------------------------------------------


def _normalizar_cpf(serie: pd.Series) -> pd.Series:
    """zfill(11) no CPF, preservando sentinelas de CPF inválido (ex.: "-1", "-4").

    Corrige I-3-001/D2: em candidatos.parquet, os CPFs de 2012 (28,6%) e 2014
    (26,4%) foram gravados sem zeros à esquerda (8-10 dígitos, contra 11 nos
    demais anos), o que quebra o merge por CPF-string para candidaturas cujo
    CPF começa com "0" — elas simplesmente não se ligam ao histórico de 2012/2014.
    """
    s = serie.astype(str).str.strip()
    numerico = s.str.fullmatch(r"\d+")
    return s.where(~numerico, s.str.zfill(11))


def _texto_ascii(serie: pd.Series) -> pd.Series:
    """Maiúsculas e sem acento (vetorizado), para comparar nomes de município
    entre resultados_ e candidatos_. Não recupera mojibake já corrompido no
    dado de origem (ex.: caractere de substituição "�" em alguns
    municípios de 2012-2022); esses casos ficam sem correspondência —
    residual pequeno (~0,7% das linhas de Prefeito), documentado em
    thesis-review."""
    s = serie.astype("string").str.normalize("NFKD")
    s = s.str.replace(r"[̀-ͯ]", "", regex=True)
    return s.str.upper().str.strip()


def _chave_cargo_municipio(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["_cargo"] = df["ds_cargo"].astype("string").str.upper()
    mun = df["nm_municipio"] if "nm_municipio" in df.columns else pd.Series([""] * len(df), index=df.index)
    df["_mun"] = _texto_ascii(mun.astype("string"))
    df["nr_candidato"] = df["nr_candidato"].astype(str)
    df["ano_eleicao"] = df["ano_eleicao"].astype(int)
    return df


def _preparar_candidatos_cpf(candidatos_: pd.DataFrame, cols_extra: list) -> pd.DataFrame:
    """Uma linha por candidatura de fato, ligando corretamente o CPF (e as
    demais colunas em cols_extra) — corrige dois defeitos de ligação
    (thesis-review/runs/run-001/synthesis/final_review.md, achado I-3-001):

      D1 — chave não exclusiva. `nr_candidato` só é exclusivo dentro do
           cargo e, em Prefeito/Vice-Prefeito/Vereador, dentro do município;
           sem isso, vitórias de dezenas de municípios (ou de outro cargo)
           acabavam creditadas a um único CPF por (ano, UF, número).
      D3 — substituição de candidato. Quando mais de um CPF aparece sob o
           mesmo número (substituição), prioriza o registro
           `ds_situacao_candidatura == "APTO"` em vez do primeiro do arquivo
           — que podia ser o candidato substituído.
    """
    cols = list(dict.fromkeys(
        ["ano_eleicao", "sg_uf", "ds_cargo", "nr_candidato", "nm_municipio",
         "ds_situacao_candidatura"] + cols_extra
    ))
    c = _chave_cargo_municipio(candidatos_[cols].copy())
    c["_prioridade"] = (c["ds_situacao_candidatura"] != "APTO").astype(int)

    is_mun = c["_cargo"].isin(CARGOS_MUNICIPAIS)
    chave_uf = ["ano_eleicao", "sg_uf", "_cargo", "nr_candidato"]
    chave_mun = chave_uf + ["_mun"]

    uf = (
        c.loc[~is_mun].sort_values(chave_uf + ["_prioridade"])
        .drop_duplicates(chave_uf, keep="first")
    )
    mun = (
        c.loc[is_mun].sort_values(chave_mun + ["_prioridade"])
        .drop_duplicates(chave_mun, keep="first")
    )
    return pd.concat([uf, mun], ignore_index=True).drop(columns=["_prioridade"])


def ligar_cpf(alvo: pd.DataFrame, candidatos_: pd.DataFrame, cols_extra: list) -> pd.DataFrame:
    """Liga cada linha de `alvo` (precisa de ano_eleicao, sg_uf, ds_cargo,
    nr_candidato, nm_municipio) à candidatura correspondente em candidatos_,
    trazendo `cols_extra`. Ver `_preparar_candidatos_cpf` para os defeitos
    corrigidos (I-3-001, D1 e D3). Substitui os antigos
    `drop_duplicates(["ano_eleicao","sg_uf","nr_candidato"], keep="first")`.
    """
    cand = _preparar_candidatos_cpf(candidatos_, cols_extra)
    a = _chave_cargo_municipio(alvo)
    is_mun_a = a["_cargo"].isin(CARGOS_MUNICIPAIS)
    is_mun_c = cand["_cargo"].isin(CARGOS_MUNICIPAIS)

    chave_uf = ["ano_eleicao", "sg_uf", "_cargo", "nr_candidato"]
    chave_mun = chave_uf + ["_mun"]

    m_uf = a.loc[~is_mun_a].merge(
        cand.loc[~is_mun_c, chave_uf + cols_extra], on=chave_uf, how="left", validate="m:1"
    )
    m_mun = a.loc[is_mun_a].merge(
        cand.loc[is_mun_c, chave_mun + cols_extra], on=chave_mun, how="left", validate="m:1"
    )
    out = pd.concat([m_uf, m_mun]).sort_index()
    return out.drop(columns=["_cargo", "_mun"])


def carregar_dados(processed_path: Path) -> dict:
    candidatos = pd.read_parquet(processed_path / "candidatos.parquet")
    candidatos["nr_cpf_candidato"] = _normalizar_cpf(candidatos["nr_cpf_candidato"])
    return {
        "resultados": pd.read_parquet(processed_path / "resultados.parquet"),
        "candidatos": candidatos,
        "receitas": pd.read_parquet(processed_path / "receitas.parquet"),
        "vagas": pd.read_parquet(processed_path / "vagas_deputado_federal.parquet"),
        "qe": pd.read_csv(processed_path / "quociente_eleitoral.csv", sep=";"),
        "votos_validos_partido": pd.read_parquet(
            processed_path / "votos_validos_partido.parquet"
        ),
    }


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------


def _construir_resultados_select(
    resultados_: pd.DataFrame, candidatos_: pd.DataFrame
) -> pd.DataFrame:
    """DataFrame auxiliar (todos os cargos/anos) com CPF e flag eleito.
    Usado internamente por adicionar_historico_eleitoral e adicionar_prop_votos_lag.
    """
    df = resultados_[
        [
            "ano_eleicao",
            "sg_uf",
            "ds_cargo",
            "sg_partido",
            "nr_candidato",
            "nm_candidato",
            "nm_municipio",
            "ds_sit_tot_turno",
            "qt_votos_nominais",
        ]
    ].reset_index(drop=True)

    df = ligar_cpf(df, candidatos_, ["nr_cpf_candidato"])
    df["eleito"] = np.where(df["ds_sit_tot_turno"].isin(TXT_ELEITOS), 1, 0)
    df["ds_cargo"] = df["ds_cargo"].str.upper()
    return df


def construir_base(
    resultados_: pd.DataFrame, candidatos_: pd.DataFrame
) -> pd.DataFrame:
    """DataFrame raiz: Deputado Federal 2018 e 2022 com CPF."""
    base = (
        resultados_.loc[
            resultados_["ano_eleicao"].isin([2014, 2018, 2022])
            & (resultados_["ds_cargo"].str.upper() == "DEPUTADO FEDERAL")
        ]
        .groupby(
            [
                "ano_eleicao",
                "sg_uf",
                "sg_partido",
                "nr_candidato",
                "nm_candidato",
                "ds_sit_tot_turno",
            ],
            as_index=False,
        )["qt_votos_nominais"]
        .sum()
    )
    base["ds_cargo"] = "DEPUTADO FEDERAL"
    base = ligar_cpf(
        base, candidatos_, ["nr_cpf_candidato", "ds_genero", "ds_cor_raca"]
    )
    # Dummies demográficas; "NÃO DIVULGÁVEL" e "NÃO INFORMADO" → NaN
    base["mulher"] = np.where(
        base["ds_genero"] == "FEMININO", 1,
        np.where(base["ds_genero"] == "MASCULINO", 0, np.nan),
    )
    base["negra"] = np.where(
        base["ds_cor_raca"].isin(["PRETA", "PARDA"]), 1,
        np.where(
            base["ds_cor_raca"].isin(["BRANCA", "AMARELA", "INDÍGENA"]), 0, np.nan
        ),
    )
    print(f"[construir_base] {len(base):,} candidatos")
    return base


# ---------------------------------------------------------------------------
# Features
# ---------------------------------------------------------------------------


def _identificar_historico_eleitoral(
    resultados_cpf: pd.DataFrame, ano_eleicao_interesse: int, ano_limite: int
) -> pd.DataFrame:
    cargos = [
        "PREFEITO",
        "VEREADOR",
        "DEPUTADO ESTADUAL",
        "DEPUTADO FEDERAL",
        "GOVERNADOR",
        "SENADOR",
        "DEPUTADO DISTRITAL",
    ]
    df = resultados_cpf.copy()
    for cargo in cargos:
        col = f"dummy_{cargo.lower().replace(' ', '_')}"
        df[col] = ((df["ds_cargo"] == cargo) & (df["eleito"] == 1)).astype(int)

    df = df.query(f"ano_eleicao <= {ano_limite}")
    cols = df.filter(like="dummy_").columns.tolist() + ["nr_cpf_candidato"]
    cpf_dummies = df[cols].groupby("nr_cpf_candidato", as_index=False).sum()

    # consolidar dep. estadual + dep. distrital (Brasília)
    cpf_dummies["dummy_deputado_estadual"] += cpf_dummies["dummy_deputado_distrital"]
    cpf_dummies = cpf_dummies.drop(columns=["dummy_deputado_distrital"])

    cpf_dummies = cpf_dummies.rename(
        columns={
            "dummy_prefeito": "n_eleicoes_prefeito",
            "dummy_vereador": "n_eleicoes_vereador",
            "dummy_deputado_estadual": "n_eleicoes_deputado_estadual",
            "dummy_deputado_federal": "n_eleicoes_deputado_federal",
            "dummy_governador": "n_eleicoes_governador",
            "dummy_senador": "n_eleicoes_senador",
        }
    )
    cpf_dummies["ano_eleicao"] = ano_eleicao_interesse
    return cpf_dummies


def adicionar_historico_eleitoral(
    df: pd.DataFrame, resultados_select: pd.DataFrame
) -> pd.DataFrame:
    """Adiciona n_eleicoes_{cargo} via CPF. CPF '-4' → NaN."""
    hist14 = _identificar_historico_eleitoral(resultados_select, 2014, 2012)
    hist18 = _identificar_historico_eleitoral(resultados_select, 2018, 2016)
    hist22 = _identificar_historico_eleitoral(resultados_select, 2022, 2020)
    historico = pd.concat([hist14, hist18, hist22], ignore_index=True)

    df = df.merge(historico, on=["ano_eleicao", "nr_cpf_candidato"], how="left")

    cols_n = df.filter(like="n_eleicoes").columns
    for col in cols_n:
        # candidatos sem histórico (não aparecem no merge) → 0; CPF inválido → NaN
        df[col] = np.where(df["nr_cpf_candidato"] == "-4", np.nan, df[col].fillna(0))

    print(f"[adicionar_historico_eleitoral] colunas: {list(cols_n)}")
    return df


def adicionar_receitas(df: pd.DataFrame, receitas_: pd.DataFrame) -> pd.DataFrame:
    """Adiciona vr_receita_recursos_partidos, vr_receita_outros, vr_receita_fefc, vr_receita_fp.

    vr_receita_fefc / vr_receita_fp decompõem vr_receita_recursos_partidos por fonte
    harmonizada. Em 2014 (pré-FEFC), vr_receita_fefc é sempre NaN.
    ds_fonte_receita original é preservado em receitas.parquet; apenas a coluna harmoniada
    é usada internamente aqui para o breakdown.
    """
    rec = receitas_.loc[receitas_["ds_cargo"] == "DEPUTADO FEDERAL"].copy()
    rec["ds_fonte_receita_harm"] = rec["ds_fonte_receita"].map(_FONTE_HARM).fillna("OUTROS_RECURSOS")

    # Total partido vs. outros (mantém semântica anterior)
    rec["_origem_cat"] = np.where(
        rec["ds_origem_receita"] != "Recursos de partido político",
        "vr_receita_outros",
        "vr_receita_recursos_partidos",
    )
    totais = (
        rec.groupby(["ano_eleicao", "sg_uf", "nr_candidato", "_origem_cat"], as_index=False)["vr_receita"]
        .sum()
        .pivot(index=["ano_eleicao", "sg_uf", "nr_candidato"], columns="_origem_cat", values="vr_receita")
        .reset_index()
    )
    totais.columns.name = None

    # Breakdown FEFC / FP dentro dos repasses de partido
    partido = rec[rec["ds_origem_receita"] == "Recursos de partido político"].copy()
    partido["_fonte_cat"] = partido["ds_fonte_receita_harm"].map(
        {"FEFC": "vr_receita_fefc", "FUNDO_PARTIDARIO": "vr_receita_fp"}
    )
    fefc_fp = (
        partido[partido["_fonte_cat"].notna()]
        .groupby(["ano_eleicao", "sg_uf", "nr_candidato", "_fonte_cat"], as_index=False)["vr_receita"]
        .sum()
        .pivot(index=["ano_eleicao", "sg_uf", "nr_candidato"], columns="_fonte_cat", values="vr_receita")
        .reset_index()
    )
    fefc_fp.columns.name = None

    totais["nr_candidato"] = totais["nr_candidato"].astype(str)
    fefc_fp["nr_candidato"] = fefc_fp["nr_candidato"].astype(str)

    df = df.merge(totais, on=["ano_eleicao", "sg_uf", "nr_candidato"], how="left")
    df = df.merge(fefc_fp, on=["ano_eleicao", "sg_uf", "nr_candidato"], how="left")

    for col in ["vr_receita_fefc", "vr_receita_fp"]:
        if col not in df.columns:
            df[col] = np.nan

    print(f"[adicionar_receitas] {len(df):,} linhas")
    return df


def adicionar_quociente_eleitoral(df: pd.DataFrame, qe: pd.DataFrame) -> pd.DataFrame:
    """Adiciona quociente eleitoral (qe) por UF × ano."""
    df = df.merge(qe, on=["ano_eleicao", "sg_uf"], how="left")
    print(f"[adicionar_quociente_eleitoral] NaN em qe: {df['qe'].isna().sum()}")
    return df


def adicionar_vagas(df: pd.DataFrame, vagas_: pd.DataFrame) -> pd.DataFrame:
    """Adiciona qt_vaga (vagas do distrito) por UF × ano."""
    df = df.merge(
        vagas_.drop(columns=["ds_cargo"]), on=["ano_eleicao", "sg_uf"], how="left"
    )
    print(f"[adicionar_vagas] NaN em qt_vaga: {df['qt_vaga'].isna().sum()}")
    return df


def _processar_receitas_2014(raw_path: Path, inicio: str, fim: str) -> pd.DataFrame:
    """Lê o arquivo raw de 2014 (pré-FEFC, esquema de colunas diferente)."""
    arquivo = raw_path / "finanças" / "receitas_candidatos_2014_brasil.txt"
    rename_map = {
        "uf": "sg_uf",
        "sigla  partido": "sg_partido",
        "numero candidato": "nr_candidato",
        "cargo": "ds_cargo",
        "data da receita": "dt_receita",
        "valor receita": "vr_receita",
        "tipo receita": "ds_origem_receita",
        "fonte recurso": "ds_fonte_receita",
    }
    rec = pd.read_csv(arquivo, sep=";", encoding="latin1", low_memory=False)
    rec.columns = rec.columns.str.strip().str.lower()
    rec = rec.rename(columns=rename_map)
    rec["nr_candidato"] = rec["nr_candidato"].astype(str)
    rec["sg_partido"] = rec["sg_partido"].astype(str)
    rec["sg_uf"] = rec["sg_uf"].astype(str)
    # Formato sem espaço: "02/10/201400:00:00" → extrair os 10 primeiros chars
    rec["dt_receita"] = pd.to_datetime(rec["dt_receita"].str[:10], format="%d/%m/%Y")
    rec["vr_receita"] = rec["vr_receita"].astype(str).str.replace(",", ".").astype(float)
    rec["ano_eleicao"] = 2014
    return rec.loc[
        (rec["ds_cargo"] == "Deputado Federal")
        & (rec["ds_origem_receita"] == "Recursos de partido político")
        & (rec["dt_receita"] >= inicio)
        & (rec["dt_receita"] <= fim)
    ].copy()


def _processar_receitas_partido_ano(raw_path: Path, ano: int) -> pd.DataFrame:
    inicio, fim = JANELAS_CAMPANHA[ano]
    if ano == 2014:
        return _processar_receitas_2014(raw_path, inicio, fim)
    arquivo = raw_path / "finanças" / f"receitas_candidatos_{ano}_BRASIL.csv"
    rec = pd.read_csv(
        arquivo,
        sep=";",
        encoding="latin1",
        low_memory=False,
        dtype={
            "NR_CANDIDATO": str,
            "ANO_ELEICAO": str,
            "SG_PARTIDO": str,
            "SG_UF": str,
        },
    )
    rec.columns = rec.columns.str.strip().str.lower()
    rec["dt_receita"] = pd.to_datetime(rec["dt_receita"], dayfirst=True)
    rec["vr_receita"] = rec["vr_receita"].str.replace(",", ".").astype(float)
    return rec.loc[
        (rec["ds_cargo"] == "Deputado Federal")
        & (rec["ds_origem_receita"] == "Recursos de partido político")
        & (rec["dt_receita"] >= inicio)
        & (rec["dt_receita"] <= fim)
    ].copy()


def adicionar_timing(df: pd.DataFrame, raw_path: Path) -> pd.DataFrame:
    """Adiciona dias_desde_inicio, dt_receita e fonte_primeiro_repasse.

    fonte_primeiro_repasse: fonte harmonizada (_FONTE_HARM) do primeiro repasse
    partidário dentro da janela de campanha. NaN para candidatos censurados.
    A coluna ds_fonte_receita original é preservada em receitas.parquet.
    """
    keys = ["ano_eleicao", "sg_uf", "sg_partido", "nr_candidato"]
    partes = []
    for ano, (inicio, _) in JANELAS_CAMPANHA.items():
        rec = _processar_receitas_partido_ano(raw_path, ano)
        rec["ds_fonte_receita_harm"] = rec["ds_fonte_receita"].map(_FONTE_HARM).fillna("OUTROS_RECURSOS")

        # idxmin garante que pegamos a linha completa da primeira transferência
        idx_min = rec.groupby(keys)["dt_receita"].idxmin()
        primeira = rec.loc[idx_min, keys + ["dt_receita", "ds_fonte_receita_harm"]].reset_index(drop=True)
        primeira = primeira.rename(columns={"ds_fonte_receita_harm": "fonte_primeiro_repasse"})
        primeira["dias_desde_inicio"] = (primeira["dt_receita"] - pd.Timestamp(inicio)).dt.days
        primeira["ano_eleicao"] = primeira["ano_eleicao"].astype(int)
        partes.append(primeira)

    timing = pd.concat(partes, ignore_index=True)
    df = df.merge(timing, on=keys, how="left")
    print(f"[adicionar_timing] com transferência: {df['dias_desde_inicio'].notna().sum():,}")
    return df


# Linhagem partidária: nomes de 2018 → nomes canônicos em 2022.
# Renames/fusões que ocorreram entre as eleições de 2018 e 2022.
# Não aplicar a outros ciclos (DEM ainda era DEM em 2018).
_LINHAGEM_2018_2022 = {
    "PR":    "PL",
    "PRB":   "REPUBLICANOS",
    "DEM":   "UNIÃO",
    "PSL":   "UNIÃO",
    "PPS":   "CIDADANIA",
    "PPL":   "PC do B",
    "PHS":   "PODE",
    "PRP":   "PATRIOTA",
    "PATRI": "PATRIOTA",
    "PTC":   "AGIR",
}


def _votos_lag_por_ciclo(
    dep_lag: pd.DataFrame, ano_lag: int, partido_map: dict | None
) -> pd.DataFrame:
    """Prop. de votos nominais intralista em `ano_lag`, com ano já adiantado em +4.

    Se `partido_map` for fornecido, traduz os nomes de partido antes de calcular
    o denominador, de modo que fusões (DEM+PSL→UNIÃO) reflictam a lista combinada.
    """
    d = dep_lag[dep_lag["ano_eleicao"] == ano_lag].copy()
    if d.empty:
        return pd.DataFrame(
            columns=["ano_eleicao", "sg_uf", "sg_partido",
                     "nr_cpf_candidato", "prop_votos_nominais"]
        )
    if partido_map:
        d["sg_partido"] = d["sg_partido"].map(partido_map).fillna(d["sg_partido"])

    total = (
        d.groupby(["ano_eleicao", "sg_uf", "sg_partido"])["qt_votos_nominais"]
        .sum()
        .rename("qt_votos_lista")
        .reset_index()
    )
    d = d.merge(total, on=["ano_eleicao", "sg_uf", "sg_partido"], how="left")
    d["prop_votos_nominais"] = d["qt_votos_nominais"] / d["qt_votos_lista"]

    out = d.groupby(
        ["ano_eleicao", "sg_uf", "sg_partido", "nr_cpf_candidato"], as_index=False
    )["prop_votos_nominais"].sum()
    out["ano_eleicao"] += 4
    return out


def adicionar_prop_votos_lag(
    df: pd.DataFrame, resultados_select: pd.DataFrame
) -> pd.DataFrame:
    """Adiciona prop_votos_nominais_lag e prop_votos_nominais_lag_candidato.

    prop_votos_nominais_lag: share de votos na lista em t-1, com linhagem
        aplicada ao ciclo 2018→2022 (PR→PL, DEM/PSL→UNIÃO…).
        Estreantes com CPF válido → 0. CPF '-4' → NaN.
    prop_votos_nominais_lag_candidato: idem, mas merge só por UF+CPF (sem
        partido) — robusto a migrações; para uso como robustez nos modelos.
    """
    dep_lag = resultados_select[
        (resultados_select["ds_cargo"] == "DEPUTADO FEDERAL")
        & (resultados_select["ano_eleicao"].isin([2010, 2014, 2018]))
    ].copy()

    # ── Variante linhagem (principal) ─────────────────────────────────────────
    votos_lag = pd.concat(
        [
            _votos_lag_por_ciclo(dep_lag, 2010, None),
            _votos_lag_por_ciclo(dep_lag, 2014, None),
            _votos_lag_por_ciclo(dep_lag, 2018, _LINHAGEM_2018_2022),
        ],
        ignore_index=True,
    ).rename(columns={"prop_votos_nominais": "prop_votos_nominais_lag"})

    df = df.merge(
        votos_lag,
        on=["ano_eleicao", "sg_uf", "sg_partido", "nr_cpf_candidato"],
        how="left",
    )

    # ── Variante candidato (UF+CPF, sem partido) ──────────────────────────────
    partes_cand = []
    for ano_lag in [2010, 2014, 2018]:
        d = dep_lag[dep_lag["ano_eleicao"] == ano_lag].copy()
        if d.empty:
            continue
        total = (
            d.groupby(["ano_eleicao", "sg_uf", "sg_partido"])["qt_votos_nominais"]
            .sum()
            .rename("qt_votos_lista")
            .reset_index()
        )
        d = d.merge(total, on=["ano_eleicao", "sg_uf", "sg_partido"], how="left")
        d["prop_votos_nominais"] = d["qt_votos_nominais"] / d["qt_votos_lista"]
        out = d.groupby(
            ["ano_eleicao", "sg_uf", "nr_cpf_candidato"], as_index=False
        )["prop_votos_nominais"].sum()
        out["ano_eleicao"] += 4
        partes_cand.append(out)

    votos_lag_cand = pd.concat(partes_cand, ignore_index=True).rename(
        columns={"prop_votos_nominais": "prop_votos_nominais_lag_candidato"}
    )
    df = df.merge(
        votos_lag_cand,
        on=["ano_eleicao", "sg_uf", "nr_cpf_candidato"],
        how="left",
    )

    # ── Imputar zero para estreantes com CPF válido ───────────────────────────
    mask_valido = df["nr_cpf_candidato"] != "-4"
    for col in ("prop_votos_nominais_lag", "prop_votos_nominais_lag_candidato"):
        df.loc[mask_valido & df[col].isna(), col] = 0.0

    print(
        f"[adicionar_prop_votos_lag] "
        f"lag NaN (CPF '-4'): {df['prop_votos_nominais_lag'].isna().sum()}, "
        f"lag_candidato NaN: {df['prop_votos_nominais_lag_candidato'].isna().sum()}"
    )
    return df


def _carregar_vagas_historicas(raw_path: Path) -> pd.DataFrame:
    anos = [1998, 2002, 2006, 2010, 2014, 2018, 2022]
    partes = []
    for ano in anos:
        f = raw_path / f"vagas/consulta_vagas_{ano}_BRASIL.csv"
        v = pd.read_csv(f, sep=";", encoding="latin1")
        v.columns = v.columns.str.lower()
        if "qt_vagas" in v.columns:
            v = v.rename(columns={"qt_vagas": "qt_vaga"})
        partes.append(v[["ano_eleicao", "sg_uf", "ds_cargo", "qt_vaga"]])
    vagas = pd.concat(partes, ignore_index=True)
    vagas["ds_cargo"] = vagas["ds_cargo"].str.upper()
    return vagas.drop_duplicates(["ano_eleicao", "sg_uf", "ds_cargo"])


def _gerar_resultados_cpf(resultados_, candidatos_):# colunas mínimas para a flag histórica
    cols_res = [
        "ano_eleicao", "sg_uf", "cd_municipio", "nm_municipio", "nr_candidato",
        "ds_cargo", "nr_turno", "qt_votos_nominais"
    ]

    # reduz o volume antes do merge
    res_base = resultados_.loc[
        resultados_["ds_cargo"].str.upper().isin(
            ["DEPUTADO FEDERAL", "DEPUTADO ESTADUAL", "GOVERNADOR", "SENADOR", "PREFEITO"]
        )
        & (resultados_["nr_turno"] == 1),
        cols_res
    ].copy()

    res_cpf = ligar_cpf(res_base, candidatos_, ["nr_cpf_candidato"])

    # opcional: reduzir memória de strings repetidas
    res_cpf["ds_cargo"] = res_cpf["ds_cargo"].astype("category")
    res_cpf["sg_uf"] = res_cpf["sg_uf"].astype("category")

    return res_cpf

# def adicionar_alcancou_10pct_qe_hist(
#     df: pd.DataFrame,
#     res_cpf: pd.DataFrame,
#     raw_path: Path,
#     votos_validos_partido: pd.DataFrame,
# ) -> pd.DataFrame:
#     """Adiciona alcancou_10pct_qe_hist: candidato atingiu >=10% QE em eleição anterior
#     (Dep. Federal, Dep. Estadual, Governador, Senador, Prefeito). CPF '-4' → NaN.

#     O denominador do QE é votos_validos (nominais + legenda) de votos_validos_partido.parquet,
#     não apenas votos nominais — evitando subestimação do QE.
#     """
#     CARGOS_FORTE = [
#         "DEPUTADO FEDERAL",
#         "DEPUTADO ESTADUAL",
#         "GOVERNADOR",
#         "SENADOR",
#         "PREFEITO",
#     ]
#     UF_CARGOS = ["DEPUTADO FEDERAL", "DEPUTADO ESTADUAL", "GOVERNADOR", "SENADOR"]

#     # Votos nominais do candidato (numerador do pct_qe)
#     res_cpf.columns = res_cpf.columns.str.lower()
#     res_cpf["ds_cargo_up"] = res_cpf["ds_cargo"].str.upper()

#     hist = res_cpf[
#         res_cpf["ds_cargo_up"].isin(CARGOS_FORTE)
#         & (res_cpf["nr_turno"] == 1)
#         & (res_cpf["nr_cpf_candidato"].astype(str) != "-4")
#     ].copy()
#     hist["nr_cpf_candidato"] = hist["nr_cpf_candidato"].astype(str)
#     hist["cd_municipio"] = hist["cd_municipio"].astype(str)

#     # Vagas por cargo/UF/ano (para QE = votos_validos / n_vagas)
#     vagas_all = _carregar_vagas_historicas(raw_path)
#     vagas_lkp = vagas_all[
#         vagas_all["ds_cargo"].isin(["DEPUTADO FEDERAL", "DEPUTADO ESTADUAL", "SENADOR"])
#     ].rename(columns={"ds_cargo": "ds_cargo_up"})

#     # Votos por distrito — duas medidas de denominador do QE
#     # votos_validos: nominais + legenda (QE oficial TSE)
#     # votos_nominais: apenas nominais (proxy de viabilidade individual do candidato)
#     vv = votos_validos_partido.copy()
#     vv["ds_cargo"] = vv["ds_cargo"].str.upper()
#     vv["cd_municipio"] = vv["cd_municipio"].astype(str)  # harmoniza tipo com hist
#     vv_uf = vv[vv["ds_cargo"].isin(UF_CARGOS)].rename(columns={"ds_cargo": "ds_cargo_up"})
#     vv_mun = vv[vv["ds_cargo"] == "PREFEITO"].rename(columns={"ds_cargo": "ds_cargo_up"})

#     VV_COLS = ["ano_eleicao", "sg_uf", "ds_cargo_up", "votos_nominais", "votos_validos"]
#     VV_MUN_COLS = ["ano_eleicao", "cd_municipio", "ds_cargo_up", "votos_nominais", "votos_validos"]

#     # --- Cargos nível UF ---
#     votos_uf = (
#         hist[hist["ds_cargo_up"].isin(UF_CARGOS)]
#         .groupby(["ano_eleicao", "sg_uf", "ds_cargo_up", "nr_cpf_candidato"])[
#             "qt_votos_nominais"
#         ]
#         .sum()
#         .reset_index()
#     )
    
#     votos_uf['ano_eleicao'] = votos_uf['ano_eleicao'].astype(int)
#     vagas_lkp['ano_eleicao'] = vagas_lkp['ano_eleicao'].astype(int)
#     vv_uf['ano_eleicao'] = vv_uf['ano_eleicao'].astype(int)
    
    
#     votos_uf = votos_uf.merge(vv_uf[VV_COLS], on=["ano_eleicao", "sg_uf", "ds_cargo_up"], how="left")
#     votos_uf = votos_uf.merge(
#         vagas_lkp[["ano_eleicao", "sg_uf", "ds_cargo_up", "qt_vaga"]],
#         on=["ano_eleicao", "sg_uf", "ds_cargo_up"],
#         how="left",
#     )
#     votos_uf["qt_vaga"] = votos_uf["qt_vaga"].fillna(1)  # Governador = 1

#     # --- Prefeito (nível município, sempre 1 vaga) ---
#     votos_mun = (
#         hist[hist["ds_cargo_up"] == "PREFEITO"]
#         .groupby(["ano_eleicao", "cd_municipio", "ds_cargo_up", "nr_cpf_candidato"])[
#             "qt_votos_nominais"
#         ]
#         .sum()
#         .reset_index()
#     )
    
#     votos_mun['ano_eleicao'] = votos_mun['ano_eleicao'].astype(int)
#     vv_mun['ano_eleicao'] = vv_mun['ano_eleicao'].astype(int)
    
#     votos_mun = votos_mun.merge(
#         vv_mun[VV_MUN_COLS], on=["ano_eleicao", "cd_municipio", "ds_cargo_up"], how="left"
#     )
#     votos_mun["qt_vaga"] = 1

#     cols = [
#         "ano_eleicao", "ds_cargo_up", "nr_cpf_candidato",
#         "qt_votos_nominais", "votos_nominais", "votos_validos", "qt_vaga",
#     ]
#     all_qe = pd.concat([votos_uf[cols], votos_mun[cols]], ignore_index=True)

#     # QE oficial (nominais + legenda) → alcancou_10pct_qe_hist
#     all_qe["qe_total"]  = all_qe["votos_validos"] / all_qe["qt_vaga"]
#     all_qe["pct_qe"]    = np.where(all_qe["qe_total"] > 0, all_qe["qt_votos_nominais"] / all_qe["qe_total"], 0)

#     # QE nominal (só nominais) → alcancou_10pct_qe_hist_nom
#     all_qe["qe_nom"]     = all_qe["votos_nominais"] / all_qe["qt_vaga"]
#     all_qe["pct_qe_nom"] = np.where(all_qe["qe_nom"] > 0, all_qe["qt_votos_nominais"] / all_qe["qe_nom"], 0)

#     # DIAGNÓSTICO TEMPORÁRIO
#     df["nr_cpf_candidato"] = df["nr_cpf_candidato"].astype(str)
#     df["alcancou_10pct_qe_hist"]     = pd.array([False] * len(df), dtype="boolean")
#     df["alcancou_10pct_qe_hist_nom"] = pd.array([False] * len(df), dtype="boolean")

#     for target_year in [2018, 2022]:
#         hist_antes = all_qe[all_qe["ano_eleicao"] < target_year]
#         mask_ano = df["ano_eleicao"] == target_year

#         cpfs_total = set(hist_antes.loc[hist_antes["pct_qe"]     >= 0.10, "nr_cpf_candidato"])
#         cpfs_nom   = set(hist_antes.loc[hist_antes["pct_qe_nom"] >= 0.10, "nr_cpf_candidato"])

#         df.loc[mask_ano & df["nr_cpf_candidato"].isin(cpfs_total), "alcancou_10pct_qe_hist"]     = True
#         df.loc[mask_ano & df["nr_cpf_candidato"].isin(cpfs_nom),   "alcancou_10pct_qe_hist_nom"] = True


#     for target_year in [2018, 2022]:
#         hist_antes = all_qe[all_qe["ano_eleicao"] < target_year]
#         fortes = hist_antes[hist_antes["pct_qe"] >= 0.10]
#         rrd_cpfs = set(df[df["ano_eleicao"] == target_year]["nr_cpf_candidato"].astype(str))
#         print(f"\nTarget {target_year} — CPFs fortes que batem no rrd_df por cargo:")
#         for cargo, grp in fortes.groupby("ds_cargo_up"):
#             cpfs_cargo = set(grp["nr_cpf_candidato"].astype(str))
#             matches = len(cpfs_cargo & rrd_cpfs)
#             print(f"  {cargo:<25} {len(cpfs_cargo):>6} CPFs únicos fortes  →  {matches:>4} no rrd_df")


#     mask_inv = df["nr_cpf_candidato"] == "-4"
#     df.loc[mask_inv, "alcancou_10pct_qe_hist"]     = pd.NA
#     df.loc[mask_inv, "alcancou_10pct_qe_hist_nom"] = pd.NA

#     print("[adicionar_alcancou_10pct_qe_hist]")
#     comp = df.groupby("ano_eleicao")[
#         ["alcancou_10pct_qe_hist", "alcancou_10pct_qe_hist_nom"]
#     ].sum().astype("Int64")
#     print(comp)
#     return df


def adicionar_alcancou_10pct_qe_hist(
    df: pd.DataFrame,
    res_cpf: pd.DataFrame,
    raw_path: Path,
    votos_validos_partido: pd.DataFrame,
) -> pd.DataFrame:
    """Adiciona alcancou_10pct_qe_hist: candidato atingiu >=10% do quociente eleitoral
    em disputa proporcional (Dep. Federal, Dep. Estadual) em eleição anterior.

    Restrito à disputa proporcional, conforme tese/03-medindo-coordenacao-intrapartidaria.qmd
    l. 68 (critério ii de "competitivo"; recomendação I-3-002 de
    thesis-review/runs/run-001/synthesis/final_review.md): Governador, Senador e Prefeito são
    disputas majoritárias e não têm quociente eleitoral — o critério de vitória (i), calculado
    em `_identificar_historico_eleitoral`, já os cobre separadamente. CPF '-4' → NaN.
    """
    CARGOS_FORTE = ["DEPUTADO FEDERAL", "DEPUTADO ESTADUAL"]
    UF_CARGOS = ["DEPUTADO FEDERAL", "DEPUTADO ESTADUAL"]

    # evita groupby com category (expansão de categorias não observadas)
    res_cpf = res_cpf.copy()
    res_cpf.columns = res_cpf.columns.str.lower()
    res_cpf["ds_cargo_up"] = res_cpf["ds_cargo"].astype("string").str.upper()

    hist = res_cpf[
        res_cpf["ds_cargo_up"].isin(CARGOS_FORTE)
        & (res_cpf["nr_turno"] == 1)
        & (res_cpf["nr_cpf_candidato"].astype(str) != "-4")
    ].copy()
    hist["nr_cpf_candidato"] = hist["nr_cpf_candidato"].astype(str)
    hist["cd_municipio"] = hist["cd_municipio"].astype(str)

    vagas_all = _carregar_vagas_historicas(raw_path)
    vagas_lkp = vagas_all[
        vagas_all["ds_cargo"].isin(UF_CARGOS)
    ].rename(columns={"ds_cargo": "ds_cargo_up"})

    vv = votos_validos_partido.copy()
    vv["ds_cargo"] = vv["ds_cargo"].astype("string").str.upper()
    vv["cd_municipio"] = vv["cd_municipio"].astype(str)

    # agrega primeiro para evitar merge m:m
    vv_uf = (
        vv[vv["ds_cargo"].isin(UF_CARGOS)]
        .rename(columns={"ds_cargo": "ds_cargo_up"})
        .groupby(["ano_eleicao", "sg_uf", "ds_cargo_up"], as_index=False, observed=True)[
            ["votos_nominais", "votos_validos"]
        ]
        .sum()
    )

    # --- Cargos nível UF (única esfera com quociente eleitoral proporcional) ---
    votos_uf = (
        hist[hist["ds_cargo_up"].isin(UF_CARGOS)]
        .groupby(
            ["ano_eleicao", "sg_uf", "ds_cargo_up", "nr_cpf_candidato"],
            as_index=False,
            observed=True,
        )["qt_votos_nominais"]
        .sum()
    )

    votos_uf["ano_eleicao"] = votos_uf["ano_eleicao"].astype(int)
    vagas_lkp["ano_eleicao"] = vagas_lkp["ano_eleicao"].astype(int)
    vv_uf["ano_eleicao"] = vv_uf["ano_eleicao"].astype(int)

    votos_uf = votos_uf.merge(
        vv_uf, on=["ano_eleicao", "sg_uf", "ds_cargo_up"], how="left", validate="m:1"
    )
    votos_uf = votos_uf.merge(
        vagas_lkp[["ano_eleicao", "sg_uf", "ds_cargo_up", "qt_vaga"]],
        on=["ano_eleicao", "sg_uf", "ds_cargo_up"],
        how="left",
        validate="m:1",
    )
    votos_uf["qt_vaga"] = votos_uf["qt_vaga"].fillna(1)

    cols = [
        "ano_eleicao", "ds_cargo_up", "nr_cpf_candidato",
        "qt_votos_nominais", "votos_nominais", "votos_validos", "qt_vaga",
    ]
    all_qe = votos_uf[cols].copy()

    all_qe["qe_total"] = all_qe["votos_validos"] / all_qe["qt_vaga"]
    all_qe["pct_qe"] = np.where(
        all_qe["qe_total"] > 0, all_qe["qt_votos_nominais"] / all_qe["qe_total"], 0
    )

    all_qe["qe_nom"] = all_qe["votos_nominais"] / all_qe["qt_vaga"]
    all_qe["pct_qe_nom"] = np.where(
        all_qe["qe_nom"] > 0, all_qe["qt_votos_nominais"] / all_qe["qe_nom"], 0
    )

    df["nr_cpf_candidato"] = df["nr_cpf_candidato"].astype(str)
    df["alcancou_10pct_qe_hist"] = pd.array([False] * len(df), dtype="boolean")
    df["alcancou_10pct_qe_hist_nom"] = pd.array([False] * len(df), dtype="boolean")

    for target_year in [2014, 2018, 2022]:
        hist_antes = all_qe[all_qe["ano_eleicao"] < target_year]
        mask_ano = df["ano_eleicao"] == target_year

        cpfs_total = set(hist_antes.loc[hist_antes["pct_qe"] >= 0.10, "nr_cpf_candidato"])
        cpfs_nom = set(hist_antes.loc[hist_antes["pct_qe_nom"] >= 0.10, "nr_cpf_candidato"])

        df.loc[mask_ano & df["nr_cpf_candidato"].isin(cpfs_total), "alcancou_10pct_qe_hist"] = True
        df.loc[mask_ano & df["nr_cpf_candidato"].isin(cpfs_nom), "alcancou_10pct_qe_hist_nom"] = True

    mask_inv = df["nr_cpf_candidato"] == "-4"
    df.loc[mask_inv, "alcancou_10pct_qe_hist"] = pd.NA
    df.loc[mask_inv, "alcancou_10pct_qe_hist_nom"] = pd.NA

    print("[adicionar_alcancou_10pct_qe_hist]")
    comp = df.groupby("ano_eleicao")[
        ["alcancou_10pct_qe_hist", "alcancou_10pct_qe_hist_nom"]
    ].sum().astype("Int64")
    print(comp)
    return df


def adicionar_10pct_qe_eleicao_atual(df: pd.DataFrame) -> pd.DataFrame:
    """Adiciona flag: candidato atingiu >=10% do QE na eleição atual."""
    df["10pct_qe_eleicao_atual"] = (df["qt_votos_nominais"] / df["qe"]) > 0.10
    print(
        f"[adicionar_10pct_qe_eleicao_atual] True: {df['10pct_qe_eleicao_atual'].sum():,}"
    )
    df["eleito"] = np.where(df["ds_sit_tot_turno"].isin(TXT_ELEITOS), 1, 0)
    return df


# ---------------------------------------------------------------------------
# Validação e saída
# ---------------------------------------------------------------------------


def validar_e_salvar(df: pd.DataFrame, processed_path: Path) -> None:
    """Valida número de eleitos por ano e salva rrd_df.parquet."""
    n_eleitos = (
        df[df["ds_sit_tot_turno"].isin(TXT_ELEITOS)]["ano_eleicao"]
        .value_counts()
        .sort_index()
    )
    print(f"[validar_e_salvar] Eleitos por ano:\n{n_eleitos}")

    esperado = 513
    anos_ok = all(n_eleitos.get(ano, 0) == esperado for ano in [2014, 2018, 2022])
    if not anos_ok:
        print(
            f"AVISO: esperado {esperado} eleitos por ano. Obtido: {n_eleitos.to_dict()}"
        )
    else:
        print("Validação OK — 513 eleitos em cada ano.")

    out = processed_path / "rrd_df_novo.parquet"
    df.to_parquet(out, index=False)
    print(f"Salvo em: {out}  ({len(df):,} linhas, {df.shape[1]} colunas)")


# ---------------------------------------------------------------------------
# Orquestração
# ---------------------------------------------------------------------------


def main():
    dados = carregar_dados(PROCESSED_DATA_PATH)

    resultados_select = _construir_resultados_select(
        dados["resultados"], dados["candidatos"]
    )

    rrd = construir_base(dados["resultados"], dados["candidatos"])
    rrd = adicionar_historico_eleitoral(rrd, resultados_select)
    rrd = adicionar_receitas(rrd, dados["receitas"])
    rrd = adicionar_quociente_eleitoral(rrd, dados["qe"])
    rrd = adicionar_vagas(rrd, dados["vagas"])
    rrd = adicionar_timing(rrd, RAW_DATA_PATH)
    rrd = adicionar_prop_votos_lag(rrd, resultados_select)
    
    res_cpf = _gerar_resultados_cpf(dados["resultados"], dados["candidatos"])
    
    rrd = adicionar_alcancou_10pct_qe_hist(
        rrd, res_cpf, RAW_DATA_PATH, dados["votos_validos_partido"]
    )
    rrd = adicionar_10pct_qe_eleicao_atual(rrd)

    validar_e_salvar(rrd, PROCESSED_DATA_PATH)


if __name__ == "__main__":
    main()
