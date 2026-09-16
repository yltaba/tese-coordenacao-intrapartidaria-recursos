"""
cap3_calibracao_features.py
Calibração NECr × S — resposta operacional à provocação do orientador: em vez de avaliar
apenas se o partido acertou a expectativa ex-ante (Mp), avalia o que o partido efetivamente
FEZ — gastou recursos para quantos candidatos viáveis (NECr) e elegeu quantos (S)? "Gastou
para 3 e elegeu 3" é um dado sobre comportamento partidário que se sustenta sozinho, sem
depender de a expectativa codificada em Mp estar certa.

Duas dimensões, deliberadamente separadas (não devem ser confundidas nem somadas):

- CALIBRAÇÃO DE ESCALA — NECr ≈ S? (gap = NECr - S; razão = NECr / S). Responde "o partido
  acertou o TAMANHO da aposta".
- DISCRIMINAÇÃO — dentre os S candidatos mais financiados, quantos se elegeram?
  (`taa_expost_S`, reaproveitado de cap3_taa_features — lá é robustez; aqui é resultado
  principal). Responde "o partido acertou EM QUEM apostar".

Ressalva antitautológica (Bolognesi et al. 2020; Guarnieri & Silva 2025): S entra como
ALVO/desfecho avaliado, nunca como preditor. Isto é material do Cap. 3 (validação da
medida) — nada aqui deve migrar para os modelos de montante/timing dos caps. 4-5, que
seguem proibidos de usar `eleito` no RHS (ver CLAUDE.md).

Uso:
    python src/2_gold/cap3_calibracao_features.py     # salva parquet + imprime tabelas
    from cap3_calibracao_features import construir_calibracao, resumo_calibracao
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cap3_cs_features import PROCESSED_DATA_PATH, carregar_rrd  # noqa: E402
from cap3_taa_features import _preparar, acertos_fracionarios  # noqa: E402
from cap3_necr_decomposicao import (  # noqa: E402
    CORTES_RELEVANCIA,
    necr_cortes,
    necr_excedente,
    necr_por_fonte,
)


def _necr(p) -> float:
    p = np.asarray(p, dtype=float)
    sum_sq = (p ** 2).sum()
    return (1 / sum_sq) if sum_sq > 0 else np.nan


def construir_calibracao(rrd: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Painel lista-nível (partido x UF x ano) com NECr (bruto + variantes decompostas de
    `cap3_necr_decomposicao`), S (cadeiras conquistadas) e a taxa de acerto ex-post
    (discriminação, de `cap3_taa_features`).

    Universo: listas com algum recurso partidário distribuído (total > 0). Ao contrário de
    `construir_taa()`, NÃO exige Mp >= 1 — aqui Mp é só referência comparativa, não
    denominador do indicador. Um partido sem bancada prévia também faz uma aposta ao
    distribuir recursos de forma desigual, e é essa aposta que a calibração avalia.
    """
    if rrd is None:
        rrd = carregar_rrd()
    df = _preparar(rrd)

    linhas = []
    for (ano, uf, partido_norm), g in df.groupby(
        ["ano_eleicao", "sg_uf", "sg_partido_norm"], sort=True
    ):
        v = g["vr_receita_recursos_partidos"].to_numpy(dtype=float)
        tot = v.sum()
        if tot <= 0:
            continue

        props = v / tot
        eleito = g["eleito"].to_numpy()
        S = int(eleito.sum())

        reg = {
            "ano_eleicao": ano,
            "sg_uf": uf,
            "sg_partido": g["sg_partido"].iloc[0],
            "sg_partido_norm": partido_norm,
            "Mp": int(g["Mp"].iloc[0]),
            "qt_vaga": int(g["qt_vaga"].iloc[0]),
            "dm_cat": g["dm_cat"].iloc[0],
            "tipo_partido_exante": g["tipo_partido_exante"].iloc[0],
            "n_cands": len(g),
            "n_com_recursos": int((v > 0).sum()),
            "S": S,
            "vr_total_lista": tot,
            "NECr": _necr(props),
        }

        # Variantes de margem extensiva x intensiva (cap3_necr_decomposicao)
        reg.update(necr_cortes(props, cortes=CORTES_RELEVANCIA))
        piso, necr_exc = necr_excedente(v)
        reg["piso_distributivo"] = piso
        reg["NECr_excedente"] = necr_exc
        if "vr_receita_fefc" in g.columns:
            reg["NECr_fefc"] = necr_por_fonte(g["vr_receita_fefc"].to_numpy(dtype=float))
        if "vr_receita_fp" in g.columns:
            reg["NECr_fp"] = necr_por_fonte(g["vr_receita_fp"].to_numpy(dtype=float))

        # Discriminação ex-post: dentre os S mais financiados, quantos se elegeram?
        reg["taa_expost_S"] = (
            acertos_fracionarios(v, eleito, S) / S if S > 0 else np.nan
        )

        linhas.append(reg)

    painel = pd.DataFrame(linhas)

    # --- Calibração de escala: gap, razão e log-razão para cada variante de NECr -----
    for variante in ["NECr", "NECr_excedente"]:
        painel[f"gap_{variante}"] = painel[variante] - painel["S"]
        painel[f"razao_{variante}"] = np.where(
            painel["S"] > 0, painel[variante] / painel["S"], np.nan
        )
        with np.errstate(divide="ignore", invalid="ignore"):
            painel[f"log_razao_{variante}"] = np.log(painel[f"razao_{variante}"])

    painel["sem_eleitos"] = painel["S"] == 0

    return painel


def calibrado(razao: pd.Series, tol_razao: tuple[float, float] = (2 / 3, 3 / 2)) -> pd.Series:
    """Flag binária: razão NECr/S dentro do intervalo de tolerância (default: ±50%)."""
    lo, hi = tol_razao
    return (razao >= lo) & (razao <= hi)


def discrimina_bem(taa_expost_s: pd.Series, limiar: float = 0.5) -> pd.Series:
    """Flag binária: ao menos `limiar` dos eleitos estavam entre os S mais financiados."""
    return taa_expost_s >= limiar


TIPOLOGIA_LABELS = {
    (True, True): "Coordenação eficaz",
    (True, False): "Acertou a escala, errou o alvo",
    (False, True): "Acertou o alvo, descalibrou a escala",
    (False, False): "Descoordenado",
}


def classificar_tipologia(
    painel: pd.DataFrame,
    variante: str = "NECr",
    tol_razao: tuple[float, float] = (2 / 3, 3 / 2),
    limiar_discrimina: float = 0.5,
) -> pd.Series:
    """
    Tipologia 2x2 (calibração de escala x discriminação), só definida para listas com
    S >= 1 (discriminação é indefinida quando o partido não elegeu ninguém — ver
    `painel["sem_eleitos"]` para tratar esse grupo à parte).
    """
    cal = calibrado(painel[f"razao_{variante}"], tol_razao)
    disc = discrimina_bem(painel["taa_expost_S"], limiar_discrimina)
    return pd.Series(
        [
            TIPOLOGIA_LABELS.get((bool(c), bool(d)), np.nan) if s > 0 else np.nan
            for c, d, s in zip(cal, disc, painel["S"])
        ],
        index=painel.index,
        name="tipologia",
    )


def resumo_calibracao(
    painel: pd.DataFrame, variante: str = "NECr", by: list[str] | None = None
) -> pd.DataFrame:
    """
    Tabela-resumo por ano (opcionalmente cruzada com colunas extras em `by`): correlação
    NECr x S, gap e razão medianos, % de listas calibradas. Restrita a S >= 1 (gap/razão
    exigem S > 0 no denominador; listas com S = 0 são descritas à parte — ver
    `painel[painel.sem_eleitos]`).
    """
    chaves = ["ano_eleicao"] + (by or [])
    sub = painel[painel["S"] > 0].copy()
    # gap/razão calculados sob demanda a partir da coluna bruta da variante — funciona para
    # qualquer NECr_* de cap3_necr_decomposicao, não só as duas pré-computadas em
    # construir_calibracao (NECr, NECr_excedente).
    sub["_gap"] = sub[variante] - sub["S"]
    sub["_razao"] = sub[variante] / sub["S"]
    sub["_calibrado"] = calibrado(sub["_razao"])

    def _agg(d: pd.DataFrame) -> pd.Series:
        return pd.Series(
            {
                "n_listas": len(d),
                "corr_NECr_S": d[variante].corr(d["S"]),
                "gap_mediano": d["_gap"].median(),
                "razao_mediana": d["_razao"].median(),
                "pct_calibrado": d["_calibrado"].mean(),
            }
        )

    return (
        sub.groupby(chaves, observed=True)
        .apply(_agg, include_groups=False)
        .reset_index()
    )


def decompor_variancia_gap(painel: pd.DataFrame, gap_col: str = "gap_NECr") -> pd.DataFrame:
    """
    Decomposição aproximada de variância do gap de calibração, por ano: R² de
    gap ~ C(sg_partido), gap ~ C(sg_uf) e gap ~ C(sg_partido) + C(sg_uf), estimados
    separadamente. Responde se o desalinhamento entre NECr e S é atributo do partido
    (nacional), do diretório estadual (UF), ou de ambos.
    """
    import statsmodels.formula.api as smf

    linhas = []
    for ano in sorted(painel["ano_eleicao"].unique()):
        sub = painel[(painel["ano_eleicao"] == ano) & painel[gap_col].notna()].copy()
        if len(sub) < 10:
            continue
        sub = sub.rename(columns={gap_col: "gap"})
        r2 = {}
        for label, formula in [
            ("R2_partido", "gap ~ C(sg_partido_norm)"),
            ("R2_uf", "gap ~ C(sg_uf)"),
            ("R2_partido_uf", "gap ~ C(sg_partido_norm) + C(sg_uf)"),
        ]:
            r2[label] = smf.ols(formula, data=sub).fit().rsquared
        linhas.append({"ano_eleicao": ano, "n_listas": len(sub), **r2})
    return pd.DataFrame(linhas)


def main() -> None:
    painel = construir_calibracao()
    destino = PROCESSED_DATA_PATH / "df_calibracao_lista.parquet"
    painel.to_parquet(destino, index=False)

    print("=" * 72)
    print(f"CALIBRAÇÃO NECr × S — {len(painel)} listas | salvo em {destino}")
    print("\nListas por ano (e % sem nenhum eleito):")
    print(
        painel.groupby("ano_eleicao")["sem_eleitos"].agg(["size", "mean"]).round(3).to_string()
    )

    print("\n" + "=" * 72)
    print("RESUMO DE CALIBRAÇÃO (NECr bruto, S >= 1)")
    print(resumo_calibracao(painel).round(3).to_string(index=False))

    print("\n" + "=" * 72)
    print("RESUMO DE CALIBRAÇÃO (NECr do excedente acima do piso distributivo)")
    print(resumo_calibracao(painel, variante="NECr_excedente").round(3).to_string(index=False))

    print("\n" + "=" * 72)
    print("TIPOLOGIA 2x2 (calibração x discriminação) — contagens por ano")
    tipo = classificar_tipologia(painel)
    print(pd.crosstab(painel["ano_eleicao"], tipo).to_string())

    print("\n" + "=" * 72)
    print("DECOMPOSIÇÃO DE VARIÂNCIA DO GAP (R² por agrupamento)")
    print(decompor_variancia_gap(painel).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
