"""
Extrai a bancada de deputados federais por partido e UF nas datas
de apuração das eleições de 2018 e 2022, via API da Câmara dos Deputados.

Saída: data/processed/bancada_partido_uf.csv
"""

import time
from pathlib import Path

import pandas as pd
import requests

BASE_URL = "https://dadosabertos.camara.leg.br/api/v2/deputados"
DATAS = {
    2014: "2014-06-10",
    2018: "2018-07-20",
    2022: "2022-07-20",
}
OUTPUT = Path(__file__).resolve().parents[2] / "data" / "processed" / "bancada_partido_uf.csv"


def buscar_deputados(data: str) -> list[dict]:
    registros = []
    pagina = 1
    while True:
        resp = requests.get(
            BASE_URL,
            params={"dataInicio": data, "dataFim": data, "itens": 100, "pagina": pagina},
            timeout=30,
        )
        resp.raise_for_status()
        payload = resp.json()
        registros.extend(payload["dados"])

        tem_proxima = any(link["rel"] == "next" for link in payload.get("links", []))
        if not tem_proxima:
            break
        pagina += 1
        time.sleep(0.3)  # respeita rate limit

    return registros


def main():
    frames = []
    for ano, data in DATAS.items():
        print(f"Buscando deputados em {data}...", end=" ", flush=True)
        deputados = buscar_deputados(data)
        print(f"{len(deputados)} registros.")

        df = pd.DataFrame(deputados)[["id", "nome", "siglaPartido", "siglaUf"]]
        df["ano_eleicao"] = ano
        frames.append(df)

    deputados_df = pd.concat(frames, ignore_index=True)

    bancada = (
        deputados_df.groupby(["ano_eleicao", "siglaPartido", "siglaUf"])
        .size()
        .reset_index(name="n_deputados")
        .rename(columns={"siglaPartido": "sg_partido", "siglaUf": "sg_uf"})
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    bancada.to_csv(OUTPUT, index=False)
    print(f"\nSalvo em {OUTPUT}")
    print(bancada.groupby("ano_eleicao")["n_deputados"].sum())


if __name__ == "__main__":
    main()
