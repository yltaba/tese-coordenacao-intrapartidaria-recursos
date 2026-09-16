"""
cap3_necr_decomposicao.py
Métricas complementares ao NECr para separar "piso distribuído" de "excedente estratégico"
sob abundância orçamentária do FEFC (2018→2022, +~144% nominal). O NECr bruto pode subir
apenas porque mais candidatos passam a receber algum recurso (margem extensiva), sem que a
concentração dos recursos eleitoralmente relevantes (margem intensiva) tenha mudado. As
funções aqui decompõem essas duas margens:

- `share_top_mpp1`: participação dos Mp+1 candidatos mais financiados no total da lista.
- `necr_cortes`: NECr recalculado ignorando candidatos abaixo de limiares de relevância
  (0%, 0,5%, 1%, 2%, 5% do total da lista) — usa as proporções originais, não renormalizadas.
- `necr_excedente`: NECr calculado sobre o excedente de cada candidato acima de um piso
  distributivo da lista (mínimo, p10 ou p25 dos valores positivos).
- `necr_por_fonte`: NECr calculado separadamente para FEFC e Fundo Partidário.

Consumido por notebooks/3_necr.ipynb e notebooks/3_necr_graficos.ipynb (Seção 13).
"""
import numpy as np
import pandas as pd

CORTES_RELEVANCIA = {"0": 0.0, "005": 0.005, "01": 0.01, "02": 0.02, "05": 0.05}


def _necr(p):
    p = np.asarray(p, dtype=float)
    sum_sq = (p ** 2).sum()
    return (1 / sum_sq) if sum_sq > 0 else np.nan


def _proporcoes(valores):
    valores = np.asarray(valores, dtype=float)
    total = valores.sum()
    return valores / total if total > 0 else np.full_like(valores, np.nan)


def share_top_mpp1(valores, mp):
    """Participação dos Mp+1 candidatos mais financiados no total de recursos da lista."""
    valores = np.asarray(valores, dtype=float)
    total = valores.sum()
    k = int(mp) + 1
    if total <= 0 or k <= 0:
        return np.nan
    top = np.sort(valores)[::-1][:k].sum()
    return top / total


def necr_cortes(props, cortes=CORTES_RELEVANCIA):
    """NECr recalculado apenas com candidatos cuja proporção >= cada limiar (props originais)."""
    props = np.asarray(props, dtype=float)
    return {
        f"NECr_{label}": (_necr(props[props >= corte]) if (props >= corte).any() else np.nan)
        for label, corte in cortes.items()
    }


def necr_por_fonte(valores):
    """NECr sobre as proporções de uma fonte específica (ex.: só FEFC) dentro da lista."""
    valores = np.nan_to_num(np.asarray(valores, dtype=float), nan=0.0)
    if valores.sum() <= 0:
        return np.nan
    return _necr(_proporcoes(valores))


def calcular_piso(positivos, piso_metodo="p10", piso_valor=None):
    if piso_metodo == "min":
        return positivos.min()
    if piso_metodo == "p10":
        return np.quantile(positivos, 0.10)
    if piso_metodo == "p25":
        return np.quantile(positivos, 0.25)
    if piso_metodo == "fixo":
        if piso_valor is None:
            raise ValueError("piso_valor é obrigatório quando piso_metodo='fixo'")
        return piso_valor
    raise ValueError(f"piso_metodo inválido: {piso_metodo}")


def necr_excedente(valores, piso_metodo="p10", piso_valor=None):
    """
    Decompõe valores em piso (mínimo distributivo da lista) + excedente, e calcula o NECr
    sobre o excedente. Retorna (piso, necr_excedente).
    """
    valores = np.asarray(valores, dtype=float)
    positivos = valores[valores > 0]
    if len(positivos) == 0:
        return np.nan, np.nan
    piso = calcular_piso(positivos, piso_metodo=piso_metodo, piso_valor=piso_valor)
    excedente = np.clip(valores - piso, 0, None)
    if excedente.sum() <= 0:
        return piso, np.nan
    return piso, _necr(_proporcoes(excedente))


def decompor_lista(g, mp_col="Mp", valor_col="vr_receita_recursos_partidos",
                    prop_col="prop_vr_receita_candidato", piso_metodo="p10",
                    cortes=CORTES_RELEVANCIA):
    """
    Métricas de decomposição do NECr para uma lista (partido × UF × ano), para uso em
    `rrd.groupby([...]).apply(decompor_lista, include_groups=False)`. Espera `g` com colunas
    `valor_col`, `prop_col`, `mp_col` e, opcionalmente, `vr_receita_fefc` / `vr_receita_fp`.
    """
    valores = g[valor_col].to_numpy(dtype=float)
    props = g[prop_col].to_numpy(dtype=float)
    mp = g[mp_col].iloc[0]

    piso, necr_exc = necr_excedente(valores, piso_metodo=piso_metodo)

    out = {
        "share_top_mpp1": share_top_mpp1(valores, mp),
        "piso": piso,
        "necr_excedente": necr_exc,
        **necr_cortes(props, cortes=cortes),
    }
    if "vr_receita_fefc" in g.columns:
        out["necr_fefc"] = necr_por_fonte(g["vr_receita_fefc"].to_numpy(dtype=float))
    if "vr_receita_fp" in g.columns:
        out["necr_fp"] = necr_por_fonte(g["vr_receita_fp"].to_numpy(dtype=float))

    return pd.Series(out)
