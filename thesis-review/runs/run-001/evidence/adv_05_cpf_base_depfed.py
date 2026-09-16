"""adv_05 — CPF da própria candidatura a Deputado Federal (construir_base, gerar_rrd.py:88-113).

construir_base liga resultados de Dep. Federal a candidatos.parquet por (ano, UF, nr) com
drop_duplicates(keep='first'). Em 2018/2022 há chaves de Dep. Federal com mais de um CPF
(substituições, registros indeferidos). Testa se o CPF (e portanto histórico, sexo e raça)
atribuído na base pertence a outra pessoa, comparando o nome de resultados com o nome em
candidatos.parquet do CPF escolhido.
Execute da raiz: python thesis-review/runs/run-001/evidence/adv_05_cpf_base_depfed.py
"""
from pathlib import Path
import unicodedata
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
P = ROOT / "data/processed"


def nrm(s):
    if not isinstance(s, str):
        return s
    return " ".join("".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").upper().split())


cand = pd.read_parquet(P / "candidatos.parquet", columns=["ano_eleicao", "sg_uf", "ds_cargo", "nr_candidato", "nm_candidato",
                                                          "nr_cpf_candidato", "ds_genero", "ds_situacao_candidatura"])
cand = cand[cand.ano_eleicao.isin([2018, 2022])]
cand["nr"] = cand.nr_candidato.astype(str)
first = cand.drop_duplicates(["ano_eleicao", "sg_uf", "nr_candidato"], keep="first")
df = cand[cand.ds_cargo.str.upper() == "DEPUTADO FEDERAL"]
dup = df.groupby(["ano_eleicao", "sg_uf", "nr"]).nr_cpf_candidato.nunique()
print("chaves de Dep. Federal com >1 CPF:", (dup > 1).groupby(level=0).sum().to_dict())
print("chave (ano, UF, nr) cujo 1º registro NÃO é de Dep. Federal:",
      int(first[first.nr.str.len() == 4].ds_cargo.str.upper().ne("DEPUTADO FEDERAL").sum()))

rrd = pd.read_parquet(P / "rrd_df_novo.parquet")
rrd = rrd[rrd.ano_eleicao.isin([2018, 2022])].copy()
rrd["nr"] = rrd.nr_candidato.astype(str)
m = rrd.merge(first[["ano_eleicao", "sg_uf", "nr", "nm_candidato", "ds_cargo"]].rename(columns={"nm_candidato": "nm_cand_cpf"}),
              on=["ano_eleicao", "sg_uf", "nr"], how="left")
m["nome_igual"] = m.nm_candidato.map(nrm) == m.nm_cand_cpf.map(nrm)
# nome de urna x nome civil: considerar igual se o 1º e o último token coincidem
tok = lambda s: (nrm(s).split()[0], nrm(s).split()[-1]) if isinstance(s, str) and s.strip() else None
m["tokens_iguais"] = [tok(a) == tok(b) for a, b in zip(m.nm_candidato, m.nm_cand_cpf)]
maj = ["n_eleicoes_prefeito", "n_eleicoes_deputado_estadual", "n_eleicoes_deputado_federal", "n_eleicoes_governador", "n_eleicoes_senador"]
m["comp"] = (m[maj].fillna(0).sum(axis=1) > 0) | m.alcancou_10pct_qe_hist.fillna(False).astype(bool)
m["key_dup"] = m.set_index(["ano_eleicao", "sg_uf", "nr"]).index.isin(dup[dup > 1].index)
for y, g in m.groupby("ano_eleicao"):
    bad = g[g.key_dup & ~g.nome_igual & ~g.tokens_iguais]
    print(f"{y}: chaves duplicadas na base = {int(g.key_dup.sum())}; nome do CPF atribuído difere (1º e último nome) = {len(bad)}; "
          f"dessas: votos > 0 = {int((bad.qt_votos_nominais > 0).sum())}, eleitas = {int(bad.eleito.sum())}, "
          f"competitivas = {int(bad.comp.sum())}, R>0 = {int((bad.vr_receita_recursos_partidos.fillna(0) > 0).sum())}")
    print(bad[["sg_uf", "sg_partido", "nr", "nm_candidato", "nm_cand_cpf", "qt_votos_nominais", "eleito", "comp", "vr_receita_recursos_partidos"]].head(12).to_string(index=False))
