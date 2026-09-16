"""mea_02 — Recomputa a flag 'competitivo' com a definição do capítulo TAL COMO ESCRITA
(tese/03-medindo-coordenacao-intrapartidaria.qmd, linhas 64 e 68) e compara com
`candidato_competitivo` (cap3_cs_features.gerar_features sobre rrd_df_novo.parquet).

Definição do texto (l. 68): candidatura em y é competitiva se, antes de y, o candidato
 (i) venceu para Presidente, Governador, Senador, Dep. Federal, Dep. Estadual ou Prefeito
     [janela: 1998-2016 para 2018; 1998-2018 para 2022]; ou
 (ii) obteve >= 10% do quociente eleitoral em disputa proporcional para Dep. Federal ou
     Dep. Estadual.
Definição do código (gerar_rrd.py): (i) vitórias em Prefeito, Dep. Estadual (+Distrital),
 Dep. Federal, Governador, Senador com ano <= 2016 (2018) / <= 2020 (2022); (ii) >= 10% do
 QE em Dep. Federal, Dep. Estadual, Governador, Senador ou Prefeito, com ano < y.
 Não há coluna de Presidente (resultados.parquet não contém o cargo).

Também reconstrói o CPF do histórico com chave que inclui o município para cargos
municipais, porque gerar_rrd.py faz o merge candidatos<->resultados por
(ano, uf, nr_candidato) com drop_duplicates(keep='first'), chave não única para
prefeito/vereador.

Execute da raiz: python thesis-review/runs/run-001/evidence/mea_02_competitivo_como_escrito.py
"""
from pathlib import Path
import unicodedata
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
P = ROOT / "data/processed"
TXT_ELEITOS = ["ELEITO", "ELEITO POR MÉDIA", "MÉDIA", "ELEITO POR QP"]


def norm(s):
    if not isinstance(s, str):
        return s
    try:
        s = s.encode("latin-1").decode("utf-8")
    except Exception:
        pass
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").upper().strip()


res = pd.read_parquet(P / "resultados.parquet",
                      columns=["ano_eleicao", "nr_turno", "sg_uf", "cd_municipio", "nm_municipio", "ds_cargo",
                               "nr_candidato", "ds_sit_tot_turno", "qt_votos_nominais"])
res = res[res.nr_turno == 1].copy()
res["cargo"] = res.ds_cargo.map(norm)
res["nr"] = res.nr_candidato.astype(str).str.strip()
res["mun"] = res.nm_municipio.map(norm)
res["eleito"] = res.ds_sit_tot_turno.map(norm).isin([norm(x) for x in TXT_ELEITOS]).astype(int)
MUNICIPAL = {"PREFEITO", "VEREADOR"}

cand = pd.read_parquet(P / "candidatos.parquet",
                       columns=["ano_eleicao", "sg_uf", "ds_cargo", "nr_candidato", "nr_cpf_candidato", "nm_municipio"])
cand["cargo"] = cand.ds_cargo.map(norm)
cand["nr"] = cand.nr_candidato.astype(str).str.strip()
cand["mun"] = cand.nm_municipio.map(norm)
cand = cand[cand.nr_cpf_candidato.astype(str).str.fullmatch(r"\d{11}")]

# --- CPF correto: chave com cargo (+ município para cargos municipais) ---------
k_uf = ["ano_eleicao", "sg_uf", "cargo", "nr"]
k_mun = k_uf + ["mun"]
c_uf = cand[~cand.cargo.isin(MUNICIPAL)].drop_duplicates(k_uf, keep="first")
c_mun = cand[cand.cargo.isin(MUNICIPAL)].drop_duplicates(k_mun, keep="first")
print("candidatos: chaves UF duplicadas antes do dedup:", cand[~cand.cargo.isin(MUNICIPAL)].duplicated(k_uf).sum(),
      "| chaves municipais duplicadas:", cand[cand.cargo.isin(MUNICIPAL)].duplicated(k_mun).sum())
r_uf = res[~res.cargo.isin(MUNICIPAL)].merge(c_uf[k_uf + ["nr_cpf_candidato"]], on=k_uf, how="left")
r_mun = res[res.cargo.isin(MUNICIPAL)].merge(c_mun[k_mun + ["nr_cpf_candidato"]], on=k_mun, how="left")
hist = pd.concat([r_uf, r_mun], ignore_index=True)
print("taxa de CPF encontrado por cargo:")
print(hist.groupby("cargo").nr_cpf_candidato.apply(lambda s: s.notna().mean()).round(4).to_string())
hist = hist[hist.nr_cpf_candidato.notna()].copy()

# --- CPF 'como o código faz': chave (ano, uf, nr) keep first, sem cargo/município --
c_code = cand.drop_duplicates(["ano_eleicao", "sg_uf", "nr"], keep="first")
hist_code = res.merge(c_code[["ano_eleicao", "sg_uf", "nr", "nr_cpf_candidato"]], on=["ano_eleicao", "sg_uf", "nr"], how="left")
hist_code = hist_code[hist_code.nr_cpf_candidato.notna()].copy()

# --- quociente eleitoral por (ano, uf, cargo) ----------------------------------
vv = pd.read_parquet(P / "votos_validos_partido.parquet")
vv["cargo"] = vv.ds_cargo.map(norm)
vv_uf = vv[vv.cargo.isin(["DEPUTADO FEDERAL", "DEPUTADO ESTADUAL", "GOVERNADOR", "SENADOR"])].groupby(
    ["ano_eleicao", "sg_uf", "cargo"], as_index=False)[["votos_nominais", "votos_validos"]].sum()
seats = res[res.cargo.isin(["DEPUTADO FEDERAL", "DEPUTADO ESTADUAL", "SENADOR"])].groupby(
    ["ano_eleicao", "sg_uf", "cargo"]).eleito.sum().rename("seats").reset_index()
vv_uf = vv_uf.merge(seats, on=["ano_eleicao", "sg_uf", "cargo"], how="left")
vv_uf["seats"] = vv_uf.seats.fillna(1).clip(lower=1)
vv_uf["qe"] = vv_uf.votos_validos / vv_uf.seats
qe_csv = pd.read_csv(P / "quociente_eleitoral.csv", sep=";")
chk = vv_uf[vv_uf.cargo == "DEPUTADO FEDERAL"].merge(qe_csv, on=["ano_eleicao", "sg_uf"], suffixes=("", "_csv"))
print("QE dep. federal: validos/eleitos vs quociente_eleitoral.csv — desvio relativo max:",
      ((chk.qe - chk.qe_csv).abs() / chk.qe_csv).max().round(4), " (n =", len(chk), ")",
      "| mediana:", ((chk.qe - chk.qe_csv).abs() / chk.qe_csv).median().round(4))
# Para Deputado Federal usa-se o QE auditado do pipeline (quociente_eleitoral.csv).
vv_uf = vv_uf.merge(qe_csv.rename(columns={"qe": "qe_csv"}), on=["ano_eleicao", "sg_uf"], how="left")
vv_uf["qe"] = np.where((vv_uf.cargo == "DEPUTADO FEDERAL") & vv_uf.qe_csv.notna(), vv_uf.qe_csv, vv_uf.qe)
vv_mun = vv[vv.cargo == "PREFEITO"].groupby(["ano_eleicao", "cd_municipio", "cargo"], as_index=False)[["votos_validos"]].sum()
vv_mun["qe"] = vv_mun.votos_validos  # qt_vaga = 1 no código


def pct_qe(h):
    """razão votos nominais / QE por (ano, uf|municipio, cargo, cpf) como em gerar_rrd."""
    uf = h[h.cargo.isin(["DEPUTADO FEDERAL", "DEPUTADO ESTADUAL", "GOVERNADOR", "SENADOR"])].groupby(
        ["ano_eleicao", "sg_uf", "cargo", "nr_cpf_candidato"], as_index=False).qt_votos_nominais.sum()
    uf = uf.merge(vv_uf[["ano_eleicao", "sg_uf", "cargo", "qe"]], on=["ano_eleicao", "sg_uf", "cargo"], how="left")
    mun = h[h.cargo == "PREFEITO"].groupby(["ano_eleicao", "cd_municipio", "cargo", "nr_cpf_candidato"], as_index=False).qt_votos_nominais.sum()
    mun = mun.merge(vv_mun[["ano_eleicao", "cd_municipio", "cargo", "qe"]], on=["ano_eleicao", "cd_municipio", "cargo"], how="left")
    q = pd.concat([uf, mun], ignore_index=True)
    q["pct"] = np.where(q.qe > 0, q.qt_votos_nominais / q.qe, 0)
    return q


q_ok = pct_qe(hist)
q_code = pct_qe(hist_code)

rrd = pd.read_parquet(P / "rrd_df_novo.parquet")
rrd = rrd[rrd.ano_eleicao.isin([2018, 2022])].copy()
maj = ["n_eleicoes_prefeito", "n_eleicoes_deputado_estadual", "n_eleicoes_deputado_federal", "n_eleicoes_governador", "n_eleicoes_senador"]
rrd["comp_rrd"] = (rrd[maj].fillna(0).sum(axis=1) > 0) | rrd.alcancou_10pct_qe_hist.fillna(False).astype(bool)
rrd["cpf"] = rrd.nr_cpf_candidato.astype(str)

CARGOS_TEXTO = ["PRESIDENTE", "GOVERNADOR", "SENADOR", "DEPUTADO FEDERAL", "DEPUTADO ESTADUAL", "PREFEITO"]
CARGOS_CODIGO_VIT = ["PREFEITO", "DEPUTADO ESTADUAL", "DEPUTADO DISTRITAL", "DEPUTADO FEDERAL", "GOVERNADOR", "SENADOR"]
QE_TEXTO = ["DEPUTADO FEDERAL", "DEPUTADO ESTADUAL"]
QE_CODIGO = ["DEPUTADO FEDERAL", "DEPUTADO ESTADUAL", "GOVERNADOR", "SENADOR", "PREFEITO"]
JANELA_TEXTO = {2018: 2016, 2022: 2018}
JANELA_CODIGO_VIT = {2018: 2016, 2022: 2020}

linhas = []
for y in [2018, 2022]:
    m = rrd[rrd.ano_eleicao == y].copy()
    def cpfs_vit(h, cargos, lim):
        return set(h[(h.cargo.isin(cargos)) & (h.eleito == 1) & (h.ano_eleicao <= lim)].nr_cpf_candidato)
    def cpfs_qe(q, cargos, lim):
        return set(q[(q.cargo.isin(cargos)) & (q.pct >= 0.10) & (q.ano_eleicao <= lim)].nr_cpf_candidato)
    m["vit_texto"] = m.cpf.isin(cpfs_vit(hist, CARGOS_TEXTO, JANELA_TEXTO[y]))
    m["qe_texto"] = m.cpf.isin(cpfs_qe(q_ok, QE_TEXTO, JANELA_TEXTO[y]))
    m["comp_texto"] = m.vit_texto | m.qe_texto
    # código com CPF correto
    m["vit_cod_ok"] = m.cpf.isin(cpfs_vit(hist, CARGOS_CODIGO_VIT, JANELA_CODIGO_VIT[y]))
    m["qe_cod_ok"] = m.cpf.isin(cpfs_qe(q_ok, QE_CODIGO, y - 1))
    m["comp_cod_ok"] = m.vit_cod_ok | m.qe_cod_ok
    # código com CPF 'keep first' (reprodução do merge de gerar_rrd)
    m["vit_cod_kf"] = m.cpf.isin(cpfs_vit(hist_code, CARGOS_CODIGO_VIT, JANELA_CODIGO_VIT[y]))
    m["qe_cod_kf"] = m.cpf.isin(cpfs_qe(q_code, QE_CODIGO, y - 1))
    m["comp_cod_kf"] = m.vit_cod_kf | m.qe_cod_kf
    # componentes isolados
    m["vit_prefeito_ok"] = m.cpf.isin(cpfs_vit(hist, ["PREFEITO"], JANELA_CODIGO_VIT[y]))
    m["vit_prefeito_rrd"] = m.n_eleicoes_prefeito.fillna(0) > 0
    m["vit_prefeito_2020"] = m.cpf.isin(cpfs_vit(hist[hist.ano_eleicao == 2020], ["PREFEITO"], 2020)) if y == 2022 else False
    m["vit_distrital"] = m.cpf.isin(cpfs_vit(hist, ["DEPUTADO DISTRITAL"], JANELA_CODIGO_VIT[y]))
    m["qe_majoritario"] = m.cpf.isin(cpfs_qe(q_ok, ["GOVERNADOR", "SENADOR", "PREFEITO"], y - 1))
    m["qe_prop_ok"] = m.cpf.isin(cpfs_qe(q_ok, QE_TEXTO, y - 1))
    m["qe_rrd"] = m.alcancou_10pct_qe_hist.fillna(False).astype(bool)
    m["vit_maior_rrd"] = m[maj].fillna(0).sum(axis=1) > 0

    def n(col): return int(m[col].sum())
    ct = pd.crosstab(m.comp_rrd, m.comp_texto)
    print(f"\n===== {y} (N={len(m)}) =====")
    print("competitivo rrd (candidato_competitivo):", n("comp_rrd"))
    print("competitivo TEXTO (como escrito, CPF correto):", n("comp_texto"), "| vitória:", n("vit_texto"), "| QE prop.:", n("qe_texto"))
    print("competitivo CÓDIGO (regras do código, CPF correto):", n("comp_cod_ok"), "| vitória:", n("vit_cod_ok"), "| QE:", n("qe_cod_ok"))
    print("competitivo CÓDIGO (regras do código, CPF keep-first como gerar_rrd):", n("comp_cod_kf"), "| vitória:", n("vit_cod_kf"), "| QE:", n("qe_cod_kf"))
    print("cruzamento rrd x texto:\n", ct)
    print("só rrd:", int((m.comp_rrd & ~m.comp_texto).sum()), "| só texto:", int((~m.comp_rrd & m.comp_texto).sum()))
    print("cruzamento rrd x código-CPF-correto: iguais =", int((m.comp_rrd == m.comp_cod_ok).sum()), "de", len(m),
          "| só rrd:", int((m.comp_rrd & ~m.comp_cod_ok).sum()), "| só cod_ok:", int((~m.comp_rrd & m.comp_cod_ok).sum()))
    print("cruzamento rrd x código-CPF-keepfirst: iguais =", int((m.comp_rrd == m.comp_cod_kf).sum()),
          "| só rrd:", int((m.comp_rrd & ~m.comp_cod_kf).sum()), "| só kf:", int((~m.comp_rrd & m.comp_cod_kf).sum()))
    print("-- componentes --")
    print(" vitória prefeito: rrd =", n("vit_prefeito_rrd"), "| CPF correto =", n("vit_prefeito_ok"),
          "| concordam =", int((m.vit_prefeito_rrd == m.vit_prefeito_ok).sum()), "| só rrd =", int((m.vit_prefeito_rrd & ~m.vit_prefeito_ok).sum()),
          "| só correto =", int((~m.vit_prefeito_rrd & m.vit_prefeito_ok).sum()))
    if y == 2022:
        print(" vitória prefeito em 2020 (fora da janela do texto):", n("vit_prefeito_2020"),
              "| dessas, competitivas só por isso:", int((m.vit_prefeito_2020 & ~m.comp_texto).sum()))
    print(" vitória dep. distrital (fora do texto):", n("vit_distrital"), "| competitivas só por isso:", int((m.vit_distrital & ~m.comp_texto).sum()))
    print(" QE>=10% majoritário gov/sen/pref (fora do texto):", n("qe_majoritario"), "| competitivas só por isso:", int((m.qe_majoritario & ~m.comp_texto).sum()))
    print(" QE prop. rrd =", n("qe_rrd"), "| QE prop. CPF correto =", n("qe_prop_ok"), "| QE código CPF correto =", n("qe_cod_ok"))
    print(" vitória maior rrd =", n("vit_maior_rrd"), "| vitória código CPF correto =", n("vit_cod_ok"))
    print(" competitivas com vitória prévia FEDERAL (rrd) =", int((m.n_eleicoes_deputado_federal.fillna(0) > 0).sum()))
    linhas.append(dict(ano=y, N=len(m), comp_rrd=n("comp_rrd"), comp_texto=n("comp_texto"), comp_codigo_cpf_ok=n("comp_cod_ok"),
                       comp_codigo_keepfirst=n("comp_cod_kf"), so_rrd=int((m.comp_rrd & ~m.comp_texto).sum()),
                       so_texto=int((~m.comp_rrd & m.comp_texto).sum()), vit_prefeito_rrd=n("vit_prefeito_rrd"),
                       vit_prefeito_ok=n("vit_prefeito_ok"), vit_prefeito_2020=n("vit_prefeito_2020"), vit_distrital=n("vit_distrital"),
                       qe_majoritario=n("qe_majoritario"), qe_rrd=n("qe_rrd"), qe_prop_ok=n("qe_prop_ok")))
    m[["ano_eleicao", "sg_uf", "sg_partido", "nr_candidato", "nm_candidato", "comp_rrd", "comp_texto", "comp_cod_ok", "comp_cod_kf",
       "vit_texto", "qe_texto", "vit_prefeito_rrd", "vit_prefeito_ok", "vit_distrital", "qe_majoritario", "qe_rrd", "qe_prop_ok",
       "eleito", "vr_receita_recursos_partidos"]].to_csv(OUT / f"mea_02_flags_{y}.csv", index=False)
pd.DataFrame(linhas).to_csv(OUT / "mea_02_resumo.csv", index=False)
print("\n", pd.DataFrame(linhas).to_string(index=False))
