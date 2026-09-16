"""Família partidária para a comparação de ranking de lift entre 2018 e 2022.

`norm_partido`/`ALIAS_BANCADA` (cap3_taa_features.py) só corrigem grafia e usam
a sigla contemporânea de cada ano — não consolidam fusões substantivas
(ex.: DEM+PSL -> UNIÃO em 2021). O comentário no código-fonte é explícito:
adicionar essas fusões ali quebraria o merge com a bancada da Câmara.

Este módulo é deliberadamente separado e usado só nesta análise (comparação
de ranking de lift por partido entre eleições), nunca no cálculo de Mp/TAA.

FAMILIA_PARTIDARIA mapeia sg_partido_norm -> rótulo de família. Partidos que
não aparecem aqui têm família = a própria sigla (ver `familia`).

Fontes: renomeações e fusões registradas no TSE, 2018-2022.
"""

FAMILIA_PARTIDARIA = {
    # DEM + PSL fundiram-se em UNIÃO BRASIL (2022).
    "DEM": "UNIAO",
    "PSL": "UNIAO",
    "UNIAO": "UNIAO",
    # PR renomeado para PL (aprovado TSE, vigente desde 2022).
    "PR": "PL",
    "PL": "PL",
    # PRB renomeado para REPUBLICANOS (2019).
    "PRB": "REPUBLICANOS",
    "REPUBLICANOS": "REPUBLICANOS",
    # PPS renomeado para CIDADANIA (2019).
    "PPS": "CIDADANIA",
    "CIDADANIA": "CIDADANIA",
    # PTC renomeado para AGIR (2022).
    "PTC": "AGIR",
    "AGIR": "AGIR",
    # PATRI (sigla usada em 2018) e PATRIOTA (sigla usada em 2022) são o
    # mesmo partido (ex-PEN); diferença é só de formatação da sigla na base.
    # PRP fundiu-se ao Patriota (confirmado pelo autor, 2026-09-15).
    "PATRI": "PATRIOTA",
    "PATRIOTA": "PATRIOTA",
    "PRP": "PATRIOTA",
    # PPL foi incorporado ao PC do B (confirmado pelo autor, 2026-09-15).
    "PPL": "PC DO B",
    "PC DO B": "PC DO B",
}

# Caso levantado mas NÃO incluído acima:
#   - UP (só 2022): partido novo, sem antecessor em 2018. Família própria.


def familia(sg_partido_norm: str) -> str:
    """Rótulo de família partidária; default = a própria sigla normalizada."""
    return FAMILIA_PARTIDARIA.get(sg_partido_norm, sg_partido_norm)
