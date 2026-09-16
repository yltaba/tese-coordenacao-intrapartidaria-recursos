"""adv_02 — Decompõe o efeito dos defeitos de ligação do histórico eleitoral sobre a flag
'competitivo' e sobre cobertura/precisão/lift do Top-NECr.

Dois defeitos independentes em gerar_rrd.py:
 D1 (MEA-3-001): merge candidatos<->resultados por (ano, UF, nr) com keep='first'
     (gerar_rrd.py:61-63, 78; 510-524) -> vitórias/votos municipais atribuídos ao 1º CPF.
 D2 (NÃO reportado pelos especialistas): em candidatos.parquet, 2012 e 2014 têm CPF sem zeros
     à esquerda (strings de 7-10 dígitos), enquanto rrd 2018/2022 usa 11 dígitos -> histórico
     de 2012 (prefeitos) e 2014 (dep. federal/estadual, governador, senador) de candidatos com
     CPF iniciado em '0' (~32-34 % das candidaturas) não é ligado.
     A recomputação de MEA (mea_02:58) filtra CPFs com 11 dígitos e herda D2.

Regras: 'cod' = vitórias Pref/DE+DD/DF/Gov/Sen até 2016|2020 e >=10% QE em DF/DE/Gov/Sen/Pref
antes de y; 'cod_semQEpref' = idem sem o critério de 10% em Prefeito; 'txt' = vitórias
Gov/Sen/DF/DE/Pref até 2016|2018 e >=10% QE só em DF/DE (definição da l. 68).
Métricas: cobertura, precisão, lift (sorteio entre C_l) e lift_rec (sorteio entre recebedores).
Execute da raiz: python thesis-review/runs/run-001/evidence/adv_02_flag_variantes.py
"""
from pathlib import Path
import unicodedata
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
P = ROOT / "data/processed"
OUT = Path(__file__).resolve().parent
TXT_ELEITOS = ["ELEITO", "ELEITO POR MÉDIA", "MÉDIA", "ELEITO POR QP"]
ALIAS = {"PCDOB": "PC DO B", "PP**": "PP", "SD": "SOLIDARIEDADE", "PTDOB": "PT DO B"}


def nrm(s):
    if not isinstance(s, str):
        return s
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").upper().strip()


res = pd.read_parquet(P / "resultados.parquet", columns=["ano_eleicao", "nr_turno", "sg_uf", "cd_municipio", "nm_municipio",
                                                          "ds_cargo", "nr_candidato", "ds_sit_tot_turno", "qt_votos_nominais"])
res["cargo"] = res.ds_cargo.str.upper()
res["nr"] = res.nr_candidato.astype(str).str.strip()
res["eleito"] = res.ds_sit_tot_turno.isin(TXT_ELEITOS).astype(int)
CARG = ["PREFEITO", "DEPUTADO ESTADUAL", "DEPUTADO DISTRITAL", "DEPUTADO FEDERAL", "GOVERNADOR", "SENADOR"]
res_all = res
res = res[res.cargo.isin(CARG)].copy()
res["mun"] = res.nm_municipio.map(nrm)

cand = pd.read_parquet(P / "candidatos.parquet", columns=["ano_eleicao", "sg_uf", "ds_cargo", "nr_candidato", "nr_cpf_candidato", "nm_municipio"])
cand["cargo"] = cand.ds_cargo.str.upper()
cand["nr"] = cand.nr_candidato.astype(str).str.strip()
cand["cpf_raw"] = cand.nr_cpf_candidato.astype(str).str.strip()
cand["cpf_z"] = np.where(cand.cpf_raw.str.fullmatch(r"\d{7,11}"), cand.cpf_raw.str.zfill(11), None)
cand["cpf_raw11"] = np.where(cand.cpf_raw.str.fullmatch(r"\d{11}"), cand.cpf_raw, None)
print("Parcela de CPFs com 7-10 dígitos por ano (candidatos.parquet):")
print(cand.assign(curto=cand.cpf_raw.str.fullmatch(r"\d{7,10}")).groupby("ano_eleicao").curto.mean().round(3).to_string())


def link(cpfcol, keyfix):
    if keyfix:
        cu = cand[cand.cargo.isin(CARG) & (cand.cargo != "PREFEITO")].drop_duplicates(["ano_eleicao", "sg_uf", "cargo", "nr"])
        cm = cand[cand.cargo == "PREFEITO"].assign(mun=lambda d: d.nm_municipio.map(nrm)).drop_duplicates(["ano_eleicao", "sg_uf", "cargo", "mun", "nr"])
        a = res[res.cargo != "PREFEITO"].merge(cu[["ano_eleicao", "sg_uf", "cargo", "nr", cpfcol]], on=["ano_eleicao", "sg_uf", "cargo", "nr"], how="left")
        b = res[res.cargo == "PREFEITO"].merge(cm[["ano_eleicao", "sg_uf", "cargo", "mun", "nr", cpfcol]], on=["ano_eleicao", "sg_uf", "cargo", "mun", "nr"], how="left")
        h = pd.concat([a, b], ignore_index=True)
    else:  # como gerar_rrd: (ano, uf, nr) keep first sobre todo candidatos.parquet
        c1 = cand.drop_duplicates(["ano_eleicao", "sg_uf", "nr"], keep="first")
        h = res.merge(c1[["ano_eleicao", "sg_uf", "nr", cpfcol]], on=["ano_eleicao", "sg_uf", "nr"], how="left")
    h = h.rename(columns={cpfcol: "cpf"})
    return h[h.cpf.notna()].copy()


vv = pd.read_parquet(P / "votos_validos_partido.parquet")
vv["cargo"] = vv.ds_cargo.str.upper()
vv_uf = vv[vv.cargo.isin(["DEPUTADO FEDERAL", "DEPUTADO ESTADUAL", "GOVERNADOR", "SENADOR"])].groupby(["ano_eleicao", "sg_uf", "cargo"], as_index=False)[["votos_validos"]].sum()
seats = res[res.cargo.isin(["DEPUTADO FEDERAL", "DEPUTADO ESTADUAL", "SENADOR"]) & (res.nr_turno == 1)].groupby(["ano_eleicao", "sg_uf", "cargo"]).eleito.sum().rename("seats").reset_index()
vv_uf = vv_uf.merge(seats, on=["ano_eleicao", "sg_uf", "cargo"], how="left")
vv_uf["seats"] = vv_uf.seats.fillna(1).clip(lower=1)
vv_uf["qe"] = vv_uf.votos_validos / vv_uf.seats
qe_csv = pd.read_csv(P / "quociente_eleitoral.csv", sep=";").rename(columns={"qe": "qe_csv"})
vv_uf = vv_uf.merge(qe_csv, on=["ano_eleicao", "sg_uf"], how="left")
vv_uf["qe"] = np.where((vv_uf.cargo == "DEPUTADO FEDERAL") & vv_uf.qe_csv.notna(), vv_uf.qe_csv, vv_uf.qe)
vv_mun = vv[vv.cargo == "PREFEITO"].groupby(["ano_eleicao", "cd_municipio"], as_index=False)[["votos_validos"]].sum().rename(columns={"votos_validos": "qe"})
vv_mun["cd_municipio"] = vv_mun.cd_municipio.astype(str)


def pct(h):
    h1 = h[h.nr_turno == 1]
    u = h1[h1.cargo.isin(["DEPUTADO FEDERAL", "DEPUTADO ESTADUAL", "GOVERNADOR", "SENADOR"])].groupby(["ano_eleicao", "sg_uf", "cargo", "cpf"], as_index=False).qt_votos_nominais.sum()
    u = u.merge(vv_uf[["ano_eleicao", "sg_uf", "cargo", "qe"]], on=["ano_eleicao", "sg_uf", "cargo"], how="left")
    m = h1[h1.cargo == "PREFEITO"].groupby(["ano_eleicao", "cd_municipio", "cargo", "cpf"], as_index=False).qt_votos_nominais.sum()
    m["cd_municipio"] = m.cd_municipio.astype(str)
    m = m.merge(vv_mun, on=["ano_eleicao", "cd_municipio"], how="left")
    q = pd.concat([u, m], ignore_index=True)
    q["pct"] = np.where(q.qe > 0, q.qt_votos_nominais / q.qe, 0)
    return q


def flag(h, q, y, regra):
    if regra == "txt":
        vit_c = ["GOVERNADOR", "SENADOR", "DEPUTADO FEDERAL", "DEPUTADO ESTADUAL", "PREFEITO"]
        vlim = {2018: 2016, 2022: 2018}[y]
        qe_c = ["DEPUTADO FEDERAL", "DEPUTADO ESTADUAL"]
        qlim = vlim
    else:
        vit_c = CARG
        vlim = {2018: 2016, 2022: 2020}[y]
        qlim = y - 1
        qe_c = ["DEPUTADO FEDERAL", "DEPUTADO ESTADUAL", "GOVERNADOR", "SENADOR"] + ([] if regra == "cod_semQEpref" else ["PREFEITO"])
    v = set(h[h.cargo.isin(vit_c) & (h.eleito == 1) & (h.ano_eleicao <= vlim)].cpf)
    e = set(q[q.cargo.isin(qe_c) & (q.pct >= 0.10) & (q.ano_eleicao <= qlim)].cpf)
    return v | e


L = {}
for nome, cpfcol, keyfix in [("keepfirst_raw", "cpf_raw11", False), ("keepfirst_zfill", "cpf_z", False),
                             ("chave_raw", "cpf_raw11", True), ("chave_zfill", "cpf_z", True)]:
    h = link(cpfcol, keyfix)
    L[nome] = (h, pct(h))
    print(f"ligação {nome}: linhas de resultados com CPF = {len(h)} de {len(res)}")

rrd = pd.read_parquet(P / "rrd_df_novo.parquet")
rrd = rrd[rrd.ano_eleicao.isin([2018, 2022])].copy()
rrd["lista"] = rrd.sg_partido.map(lambda s: ALIAS.get(nrm(s), nrm(s)))
rrd["R"] = rrd.vr_receita_recursos_partidos.fillna(0.0)
rrd["cpf"] = rrd.nr_cpf_candidato.astype(str)
maj = ["n_eleicoes_prefeito", "n_eleicoes_deputado_estadual", "n_eleicoes_deputado_federal", "n_eleicoes_governador", "n_eleicoes_senador"]
rrd["base"] = ((rrd[maj].fillna(0).sum(axis=1) > 0) | rrd.alcancou_10pct_qe_hist.fillna(False).astype(bool))


def pesos(R, k):
    if k <= 0:
        return np.zeros(len(R))
    q = np.sort(R)[::-1][k - 1]
    above, tied = R > q, R == q
    return above.astype(float) + tied * ((k - above.sum()) / tied.sum())


ws = np.zeros(len(rrd)); ks = np.zeros(len(rrd), int)
grp = ["ano_eleicao", "sg_uf", "lista"]
for _, idx in rrd.groupby(grp).indices.items():
    R = rrd.R.to_numpy()[idx]; t = R.sum()
    k = int(np.floor(1 / ((R / t) ** 2).sum() + 0.5)) if t > 0 else 0
    ws[idx] = pesos(R, k); ks[idx] = k
rrd["w"] = ws; rrd["k"] = ks
rrd["C"] = rrd.groupby(grp).R.transform("size")
rrd["rec"] = rrd.R > 0
rrd["n_rec"] = rrd.groupby(grp).rec.transform("sum")

variantes = {"base (rrd_df_novo)": None}
for lk in L:
    for regra in ["cod", "cod_semQEpref", "txt"]:
        variantes[f"{regra} | {lk}"] = (lk, regra)

rows = []
flags_out = {}
for y in [2018, 2022]:
    g = rrd[rrd.ano_eleicao == y].copy()
    for nome, spec in variantes.items():
        if spec is None:
            f = g.base.to_numpy()
        else:
            h, q = L[spec[0]]
            f = g.cpf.isin(flag(h, q, y, spec[1])).to_numpy() & (g.cpf != "-4").to_numpy()
        flags_out[(y, nome)] = f
        g["f"] = f.astype(float)
        agg = g.assign(h=g.w * g.f, frec=g.f * g.rec).groupby(["sg_uf", "lista"]).agg(
            G=("f", "sum"), H=("h", "sum"), k=("k", "first"), C=("C", "first"), Grec=("frec", "sum"), nrec=("n_rec", "first"))
        A0 = (agg.G * agg.k / agg.C).sum()
        A0r = (agg.Grec * agg.k / agg.nrec.where(agg.nrec > 0)).fillna(0).sum()
        rows.append(dict(ano=y, variante=nome, G=int(agg.G.sum()), cobertura=round(agg.H.sum() / agg.G.sum(), 4),
                         precisao=round(agg.H.sum() / agg.k.sum(), 4), lift=round(agg.H.sum() / A0, 3),
                         lift_rec=round(agg.H.sum() / A0r, 3), iguais_base=int((f == g.base.to_numpy()).sum())))
tab = pd.DataFrame(rows)
pd.set_option("display.width", 220)
print(tab.to_string(index=False))
tab.to_csv(OUT / "adv_02_metricas_variantes.csv", index=False)

# deputados federais eleitos em 2014 que concorrem em 2018 e não são competitivos na base
h, q = L["chave_zfill"]
e14 = set(h[(h.ano_eleicao == 2014) & (h.cargo == "DEPUTADO FEDERAL") & (h.eleito == 1)].cpf)
g18 = rrd[rrd.ano_eleicao == 2018]
inc = g18[g18.cpf.isin(e14)]
nc = inc[~inc.base]
print(f"\n2018: candidaturas de dep. federais eleitos em 2014 = {len(inc)}; competitivas na base = {int(inc.base.sum())}; "
      f"NÃO competitivas = {len(nc)}; dessas, eleitas em 2018 = {int(nc.eleito.sum())}; com w>0 no Top-NECr = {int((nc.w > 0).sum())}; "
      f"CPF iniciado em 0 = {int(nc.cpf.str[0].eq('0').sum())}")
cols = ["sg_uf", "sg_partido", "nm_candidato", "cpf", "eleito", "w", "R"]
print(nc[cols].to_string(index=False))
nc[cols].to_csv(OUT / "adv_02_incumbentes_2014_nao_competitivos.csv", index=False)

# eleitos em 2014 para qualquer cargo da regra (DF/DE/DD/Gov/Sen) não reconhecidos na base, 2018 e 2022
for y in [2018, 2022]:
    e = set(h[(h.ano_eleicao == 2014) & h.cargo.isin(CARG) & (h.eleito == 1)].cpf)
    gy = rrd[rrd.ano_eleicao == y]
    x = gy[gy.cpf.isin(e)]
    print(f"{y}: candidaturas com vitória em 2014 (qualquer cargo da regra) = {len(x)}; não competitivas na base = {int((~x.base).sum())}")
