"""mea_04 — 'Recursos partidários' (origem 'Recursos de partido político') vs 'fundos públicos'
(fonte FEFC / Fundo Partidário) em receitas.parquet, Deputado Federal 2018 e 2022.
Execute da raiz: python thesis-review/runs/run-001/evidence/mea_04_origem_vs_fonte.py
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
rec = pd.read_parquet(ROOT / "data/processed/receitas.parquet")
print(rec.columns.tolist())
rec = rec[rec.ano_eleicao.isin([2018, 2022]) & (rec.ds_cargo == "DEPUTADO FEDERAL")].copy()
rec["fonte"] = rec.ds_fonte_receita.astype(str).str.upper().str.strip()
rec["origem"] = rec.ds_origem_receita.astype(str).str.strip()
tab = rec.pivot_table(index=["ano_eleicao", "origem"], columns="fonte", values="vr_receita", aggfunc="sum", fill_value=0)
pd.set_option("display.width", 250)
print((tab / 1e6).round(2).to_string())
for y, g in rec.groupby("ano_eleicao"):
    part = g[g.origem == "Recursos de partido político"]
    pub = g[g.fonte.isin(["FUNDO ESPECIAL", "FUNDO PARTIDARIO"])]
    both = part[part.fonte.isin(["FUNDO ESPECIAL", "FUNDO PARTIDARIO"])]
    print(f"\n{y}: origem partido = R$ {part.vr_receita.sum()/1e6:,.2f} mi | fonte pública (FEFC+FP) = R$ {pub.vr_receita.sum()/1e6:,.2f} mi | interseção = R$ {both.vr_receita.sum()/1e6:,.2f} mi")
    print(f"   origem partido mas fonte NÃO pública: R$ {(part.vr_receita.sum()-both.vr_receita.sum())/1e6:,.2f} mi ({100*(1-both.vr_receita.sum()/part.vr_receita.sum()):.2f}% da medida)")
    print(f"   fonte pública mas origem NÃO partido: R$ {(pub.vr_receita.sum()-both.vr_receita.sum())/1e6:,.2f} mi ({100*(1-both.vr_receita.sum()/pub.vr_receita.sum()):.2f}% dos fundos públicos)")
    print("   fonte pública por origem (R$ mi):", (pub.groupby("origem").vr_receita.sum() / 1e6).round(2).to_dict())
