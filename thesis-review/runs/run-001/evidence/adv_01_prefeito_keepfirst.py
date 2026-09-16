"""adv_01 — Testa se as 'vitórias de prefeito' múltiplas de rrd_df_novo.parquet são artefato
do merge (ano, UF, nr) keep='first' de gerar_rrd.py:61-63/78, ou se há outra explicação:
 (a) granularidade de resultados.parquet (linhas por zona/município inflando contagens);
 (b) duplicação por turno (sem filtro nr_turno em _construir_resultados_select);
 (c) CPFs placeholder compartilhados;
 (d) rótulos de 'eleito' com encoding quebrado (ELEITO POR MÉDIA / MÉDIA).
Execute da raiz: python thesis-review/runs/run-001/evidence/adv_01_prefeito_keepfirst.py
"""
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[4]; P = ROOT / "data/processed"
TXT_ELEITOS = ["ELEITO", "ELEITO POR MÉDIA", "MÉDIA", "ELEITO POR QP"]

res = pd.read_parquet(P / "resultados.parquet")
cand = pd.read_parquet(P / "candidatos.parquet")
rrd = pd.read_parquet(P / "rrd_df_novo.parquet")

print("=== (d) rótulos de situação: códigos dos caracteres não-ASCII ===")
for s in res.ds_sit_tot_turno.dropna().unique():
    na = [hex(ord(c)) for c in s if ord(c) > 127]
    print(f"  {s.encode('unicode_escape').decode()!s:60s} in TXT_ELEITOS={s in TXT_ELEITOS} nonascii={na}")

print("\n=== (a) granularidade: linhas por candidatura (ano, uf, cargo, municipio, nr, turno) ===")
k = ["ano_eleicao", "sg_uf", "ds_cargo", "cd_municipio", "nr_candidato", "nr_turno"]
print("  duplicadas na chave completa:", int(res.duplicated(k).sum()), "de", len(res))

print("\n=== (b) turnos: linhas de Prefeito com nr_turno=2 e situação ===")
p2 = res[(res.ds_cargo.str.upper() == "PREFEITO")]
print(p2.groupby(["nr_turno"]).ds_sit_tot_turno.value_counts().to_string())

# reproduz o merge do pipeline
c1 = cand[["ano_eleicao", "sg_uf", "nr_candidato", "nr_cpf_candidato"]].drop_duplicates(
    ["ano_eleicao", "sg_uf", "nr_candidato"], keep="first")
sel = res[["ano_eleicao", "sg_uf", "ds_cargo", "cd_municipio", "nm_municipio", "nr_candidato", "nm_candidato",
           "nr_turno", "ds_sit_tot_turno"]].merge(c1, on=["ano_eleicao", "sg_uf", "nr_candidato"], how="left")
sel["eleito"] = sel.ds_sit_tot_turno.isin(TXT_ELEITOS).astype(int)
sel["cargo"] = sel.ds_cargo.str.upper()

print("\n=== (c) CPFs em rrd 2018/2022 que não têm 11 dígitos ===")
r = rrd[rrd.ano_eleicao.isin([2018, 2022])]
print(r.nr_cpf_candidato.astype(str)[~r.nr_cpf_candidato.astype(str).str.fullmatch(r"\d{11}")].value_counts().to_string())

print("\n=== casos extremos: de onde vêm as vitórias de prefeito atribuídas ===")
casos = r[r.n_eleicoes_prefeito.fillna(0) >= 5]
lim = {2018: 2016, 2022: 2020}
linhas = []
for _, row in casos.iterrows():
    cpf = row.nr_cpf_candidato
    v = sel[(sel.nr_cpf_candidato == cpf) & (sel.cargo == "PREFEITO") & (sel.eleito == 1) & (sel.ano_eleicao <= lim[row.ano_eleicao])]
    # nomes dos prefeitos cujas vitórias foram atribuídas a este CPF
    mesmos_nomes = (v.nm_candidato.str.upper().str.strip() == str(row.nm_candidato).upper().strip()).sum()
    # candidaturas reais do CPF em cargos municipais (candidatos.parquet)
    reais = cand[(cand.nr_cpf_candidato == cpf)]
    reais_pref = reais[reais.ds_cargo.str.upper() == "PREFEITO"][["ano_eleicao", "nm_municipio", "nr_candidato"]].drop_duplicates()
    # vitórias reais de prefeito do CPF, com chave que inclui município
    vit_reais = 0
    for _, rp in reais_pref.iterrows():
        vit_reais += int(res[(res.ano_eleicao == rp.ano_eleicao) & (res.ds_cargo.str.upper() == "PREFEITO") &
                             (res.nm_municipio == rp.nm_municipio) & (res.nr_candidato.astype(str) == str(rp.nr_candidato)) &
                             (res.ds_sit_tot_turno.isin(TXT_ELEITOS))].shape[0] > 0)
    linhas.append(dict(ano=row.ano_eleicao, uf=row.sg_uf, partido=row.sg_partido, nr=row.nr_candidato, nome=row.nm_candidato,
                       n_pref_rrd=row.n_eleicoes_prefeito, n_pref_reproduzido=len(v),
                       municipios_distintos=v.cd_municipio.nunique(), anos=",".join(map(str, sorted(v.ano_eleicao.unique()))),
                       numeros=",".join(sorted(v.nr_candidato.astype(str).unique())),
                       vitorias_com_mesmo_nome=int(mesmos_nomes), candidaturas_reais_prefeito=len(reais_pref),
                       vitorias_reais_prefeito=vit_reais))
out = pd.DataFrame(linhas)
print(out.to_string(index=False))
out.to_csv(Path(__file__).parent / "adv_01_casos_extremos.csv", index=False)

print("\n=== todos os 2018/2022 com n_eleicoes_prefeito > 0: vitórias atribuídas com nome igual ao do candidato ===")
tot = []
for _, row in r[r.n_eleicoes_prefeito.fillna(0) > 0].iterrows():
    v = sel[(sel.nr_cpf_candidato == row.nr_cpf_candidato) & (sel.cargo == "PREFEITO") & (sel.eleito == 1) & (sel.ano_eleicao <= lim[row.ano_eleicao])]
    nm = str(row.nm_candidato).upper().strip()
    tot.append(dict(ano=row.ano_eleicao, nome=nm, n=len(v), n_mesmo_nome=int((v.nm_candidato.str.upper().str.strip() == nm).sum())))
tot = pd.DataFrame(tot)
print(tot.groupby("ano").agg(candidaturas=("n", "size"), com_alguma_vitoria_mesmo_nome=("n_mesmo_nome", lambda s: int((s > 0).sum())),
                            vitorias=("n", "sum"), vitorias_mesmo_nome=("n_mesmo_nome", "sum")).to_string())
