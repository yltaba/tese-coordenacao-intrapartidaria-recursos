"""Diagnóstico dos dados do Cap. 4 (apoio a notes/tecnico/cap4-secao-dados.md).

Não altera nada em data/ nem em tese/. Uso:
    python notes/tecnico/cap4_diagnostico_dados.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "finanças"
JANELAS = {
    2018: (pd.Timestamp("2018-08-16"), pd.Timestamp("2018-10-07")),
    2022: (pd.Timestamp("2022-08-16"), pd.Timestamp("2022-10-02")),
}
KEYS = ["ano_eleicao", "sg_uf", "sg_partido", "nr_candidato"]


def ler(ano):
    usecols = ["ANO_ELEICAO", "SG_UF", "SG_PARTIDO", "NR_CANDIDATO", "DS_CARGO",
               "DS_ORIGEM_RECEITA", "DS_FONTE_RECEITA", "DT_RECEITA", "VR_RECEITA"]
    r = pd.read_csv(RAW / f"receitas_candidatos_{ano}_BRASIL.csv", sep=";",
                    encoding="latin1", usecols=usecols, dtype=str)
    r.columns = r.columns.str.lower()
    r = r[r["ds_cargo"].str.strip().str.title() == "Deputado Federal"].copy()
    r["dt_receita"] = pd.to_datetime(r["dt_receita"], dayfirst=True)
    r["vr_receita"] = r["vr_receita"].str.replace(",", ".").astype(float)
    r["ano_eleicao"] = ano
    r["origem_partido"] = r["ds_origem_receita"].str.strip() == "Recursos de partido político"
    fonte = r["ds_fonte_receita"].str.upper()
    r["fonte_partido"] = fonte.isin(["FUNDO ESPECIAL", "FUNDO PARTIDARIO"])
    ini, fim = JANELAS[ano]
    r["posicao"] = np.select([r["dt_receita"] < ini, r["dt_receita"] > fim],
                             ["antes", "depois"], "janela")
    return r


def main():
    rrd = pd.read_parquet(ROOT / "data" / "processed" / "rrd_df_novo.parquet")
    rrd = rrd[rrd["ano_eleicao"].isin(JANELAS)].copy()
    for c in ["sg_uf", "sg_partido", "nr_candidato"]:
        rrd[c] = rrd[c].astype(str)

    for ano in JANELAS:
        print(f"\n================ {ano} ================")
        r = ler(ano)
        d = rrd[rrd["ano_eleicao"] == ano]
        n = len(d)
        R = d["vr_receita_recursos_partidos"].fillna(0) > 0
        ev = d["dias_desde_inicio"].notna()
        print(f"candidaturas={n}  R>0={R.sum()}  com evento={ev.sum()}  censuradas={n - ev.sum()}")
        print(f"R>0 sem evento={(R & ~ev).sum()}  evento sem R>0={(~R & ev).sum()}")

        # 1. Por que R>0 sem evento: posição temporal das receitas (origem partido)
        gap = d.loc[R & ~ev, ["sg_uf", "sg_partido", "nr_candidato"]].assign(ano_eleicao=ano)
        rp = r[r["origem_partido"]]
        pos = (rp.groupby(KEYS)["posicao"].agg(lambda s: "+".join(sorted(set(s))))
                 .reset_index())
        g = gap.merge(pos, on=KEYS, how="left")
        print("posição das receitas (origem partido) dos R>0 sem evento:")
        print(g["posicao"].fillna("sem receita no arquivo").value_counts().to_string())

        # 2. Volume fora da janela (origem partido)
        tot = rp.groupby("posicao")["vr_receita"].sum()
        print("R$ origem partido por posição (mi):", (tot / 1e6).round(1).to_dict(),
              f"| % fora da janela = {100 * (1 - tot.get('janela', 0) / tot.sum()):.2f}%")

        # 3. Origem x fonte, dentro da janela
        rj = r[r["posicao"] == "janela"]
        ct = rj.groupby(["origem_partido", "fonte_partido"])["vr_receita"].sum() / 1e6
        print("R$ (mi) na janela, origem_partido x fonte_partido:\n", ct.round(1).to_string())
        so_fonte = rj[rj["fonte_partido"] & ~rj["origem_partido"]]
        print("origens das receitas com fonte FP/FEFC mas origem ≠ partido:")
        print((so_fonte.groupby("ds_origem_receita")["vr_receita"].sum() / 1e6).round(1).to_string())
        cand_o = set(map(tuple, rj.loc[rj["origem_partido"], KEYS].drop_duplicates().values))
        cand_f = set(map(tuple, rj.loc[rj["fonte_partido"], KEYS].drop_duplicates().values))
        print(f"candidatos com evento: regra origem={len(cand_o)}  regra fonte={len(cand_f)}  "
              f"só origem={len(cand_o - cand_f)}  só fonte={len(cand_f - cand_o)}")

        # 4. Primeiro repasse antes do dia 0? (receitas anteriores ao início, origem partido)
        antes = rp[rp["posicao"] == "antes"]
        print(f"candidatos com repasse partidário datado antes de 16/08: "
              f"{antes[KEYS].drop_duplicates().shape[0]}  (R$ {antes['vr_receita'].sum() / 1e6:.1f} mi)")

        # 5. Listas sem recurso no universo (entram como censuradas)
        lista = d.groupby(["sg_uf", "sg_partido"])["vr_receita_recursos_partidos"].sum()
        sem = lista[lista.fillna(0) <= 0].index
        m = d.set_index(["sg_uf", "sg_partido"]).index.isin(sem)
        print(f"listas sem recurso={len(sem)}  candidaturas nelas={m.sum()}")

        # 6. Mediana de dias até o 1º repasse (entre quem tem evento), por competitividade
        if "candidato_competitivo" in d.columns:
            comp = d["candidato_competitivo"]
        else:
            import sys
            sys.path.insert(0, str(ROOT / "src" / "2_gold"))
            from cap3_survival_features import gerar_features_survival
            comp = gerar_features_survival(d)["candidato_competitivo"]
        tab = (d.assign(comp=comp.map({True: "competitivo", False: "não-competitivo"}))
                .groupby("comp")
                .agg(n=("dias_desde_inicio", "size"),
                     com_evento=("dias_desde_inicio", lambda s: s.notna().sum()),
                     mediana_dias=("dias_desde_inicio", "median"),
                     p25=("dias_desde_inicio", lambda s: s.quantile(.25)),
                     p75=("dias_desde_inicio", lambda s: s.quantile(.75))))
        tab["pct_evento"] = (100 * tab["com_evento"] / tab["n"]).round(1)
        print(tab.to_string())

        # 7. Empates no maior repasse diário (regra fonte, como em calcular_dias_maior_receita)
        rf = rj[rj["fonte_partido"]].groupby(KEYS + ["dt_receita"])["vr_receita"].sum().reset_index()
        mx = rf.groupby(KEYS)["vr_receita"].transform("max")
        emp = rf[rf["vr_receita"] == mx].groupby(KEYS).size()
        print(f"candidatos com empate no dia de maior repasse: {(emp > 1).sum()} de {len(emp)}")

        # 8. Última semana parcial
        dur = (JANELAS[ano][1] - JANELAS[ano][0]).days
        print(f"duração={dur} dias  nº semanas={dur // 7 + 1}  "
              f"última semana = dias {7 * (dur // 7)}–{dur} ({dur - 7 * (dur // 7) + 1} dias)")

    # 9. N dos modelos Cox
    cox = pd.read_parquet(ROOT / "data" / "processed" / "df_cox_survival.parquet")
    print("\ncolunas df_cox_survival:", list(cox.columns))


if __name__ == "__main__":
    main()
