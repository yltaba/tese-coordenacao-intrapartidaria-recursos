# Mescla os claims dos especialistas do run-003 (Cap. 2) em IDs canônicos (conflicts.md §2) e gera o bloco
# a anexar em thesis-review/claims/claims.yaml. Regra: status mais conservador; concerns unidos; decisões do chair
# registradas em nota_status.
import json, yaml
ORD = ["supported", "partially_supported", "unverifiable", "unsupported", "contradicted"]
# 'unverifiable' não é mais nem menos conservador que 'partially'; tratado como intermediário só para desempate.
ORD_CONS = {"supported": 0, "partially_supported": 1, "unverifiable": 1.5, "unsupported": 2, "contradicted": 3}
CONF = {"baixa": 0, "media": 1, "alta": 2}
AG = {"theory": "theory-reviewer", "literature": "literature-reviewer", "methodology": "methodology-reviewer", "writing": "writing-reviewer"}
MAP = {  # (agente, id de origem) -> canônico
 ("theory","C2.4.01"):"C2.4.07", ("theory","C2.4.02"):"C2.4.08", ("theory","C2.4.03"):"C2.4.04",
 ("theory","C2.6.01"):"C2.6.07", ("methodology","C2.6.04"):"C2.6.07",
 ("methodology","C2.6.01"):"C2.6.08", ("methodology","C2.6.02"):"C2.6.09",
 ("theory","C2.7.01"):"C2.7.01", ("methodology","C2.7.01"):"C2.7.01",
 ("theory","C2.7.02"):"C2.7.02", ("methodology","C2.7.02"):"C2.7.02",
 ("theory","C2.7.03"):"C2.7.03", ("methodology","C2.7.08"):"C2.7.03",
 ("theory","C2.7.04"):"C2.7.04", ("theory","C2.7.05"):"C2.7.05",
 ("theory","C2.7.06"):"C2.7.06", ("methodology","C2.7.11"):"C2.7.06",
 ("theory","C2.7.07"):"C2.7.07", ("literature","C2.7.01"):"C2.7.07", ("methodology","C2.7.09"):"C2.7.07",
 ("theory","C2.7.08"):"C2.7.08", ("methodology","C2.7.12"):"C2.7.08", ("writing","C2.7.50"):"C2.7.08",
 ("literature","C2.7.02"):"C2.7.09", ("methodology","C2.7.03"):"C2.7.09",
 ("literature","C2.7.03"):"C2.7.10", ("methodology","C2.7.07"):"C2.7.10",
 ("literature","C2.7.04"):"C2.7.11", ("methodology","C2.7.05"):"C2.7.11",
 ("literature","C2.7.05"):"C2.7.12", ("methodology","C2.7.04"):"C2.7.13",
 ("methodology","C2.7.06"):"C2.7.14", ("methodology","C2.7.10"):"C2.7.15",
}
# Decisões do chair (pass 2) que sobrepõem a regra conservadora, com a razão.
OVR = {
 "C2.4.04": ("supported", "alta", "Chair (pass 2): verificado na fonte primária. Fiva et al., resumo ('the trade-off is weaker for more popular parties') e seção 4 (revisoes/fontes-discussao-capitulo3/fiva.txt L26-37, L930-934). Falta localizador na L93 (I-2-018)."),
 "C2.4.03": ("partially_supported", "alta", "Chair (pass 2): conteúdo confirmado (resumo: 'the moral hazard concern is real'), mas o localizador 'p. 100' não existe; o artigo é o nº 105133 e tem 13 páginas de PDF (fiva.txt L2)."),
 "C2.3.08": ("supported", "alta", "Chair (pass 2): o resumo de Janusz et al. lista número de urna, apoio financeiro e tempo de TV e chama isso de 'resource gatekeeping' (janusz.txt L10-15). O rótulo e os instrumentos da L65 conferem."),
 "C2.6.06": ("supported", "alta", "Chair (pass 2): conferido em janusz.txt (L18, L528-540). Ressalva: dados de 2014, VD em nível de R$ com EF de partido estadual; a L151 não diz o ano (I-2-023)."),
 "C2.7.12": ("supported", "alta", "Chair (pass 2): Janusz et al. classificam a experiência só com cargos e candidaturas anteriores (janusz.txt L449-462), ou seja, ex-ante. O problema é outro: eles testam a mesma hipótese (I-2-005)."),
}
EXTRA_CONCERNS = {
 "C2.7.10": ["Chair (pass 2): a justificativa informacional da L204 já está em Janusz et al. (2021, p. 2-3 do PDF; janusz.txt L180-213), com a mesma hipótese testada em 2014. O 'porque' não é testado pelo desenho (I-2-001) e não é original (I-2-005)."],
 "C2.7.03": ["Chair (pass 2): E1 também é prevista por captura, barganha, força do candidato e foco em marginais; a divisão igualitária é rejeitada pelo desenho (NECr/C mediano 0,47/0,52; adv_rivais_cap2.out bloco B)."],
 "C2.7.02": ["Chair (pass 2): passa a partially_supported se o capítulo adotar a definição comportamental de coordenação (Cox 1997; Cheibub & Sin) e trocar 'constitui' por 'pode operar como' (I-2-004)."],
 "C2.7.06": ["Adversarial/chair: a correção núcleo → credencial é de uma palavra; o que fica é a falta de expectativa temporal e a rival da prontidão (I-2-003)."],
}
ext = json.load(open("evidence/chair_claims_extraidos.json", encoding="utf-8"))
issues = yaml.safe_load(open("issues.yaml", encoding="utf-8"))
cl2iss = {}
for i in issues:
    for c in i["claims"]:
        cl2iss.setdefault(c, []).append(i["issue_id"])
merged = {}
for d in ext:
    ag = d["_agent"]; cid = MAP.get((ag, d["claim_id"]), d["claim_id"])
    m = merged.setdefault(cid, {"items": []})
    m["items"].append(d)
out = []
for cid, m in merged.items():
    items = m["items"]
    base = max(items, key=lambda x: (ORD_CONS[x["assessment"]["status"]], -CONF.get(x["assessment"].get("confidence","media"),1)))
    status = base["assessment"]["status"]; conf = base["assessment"].get("confidence")
    concerns = []
    for x in items:
        for c in (x.get("concerns") or []):
            if c not in concerns: concerns.append(c)
    concerns += EXTRA_CONCERNS.get(cid, [])
    e = {
      "claim_id": cid, "capitulo": 2, "secao": base.get("secao"),
      "claim": base["claim"],
      "localizacao": {"arquivo": "tese/02-literatura.qmd", "linha": base["localizacao"].get("linha")},
      "evidencia": base.get("evidencia"),
      "assessment": {"status": status, "confidence": conf},
    }
    if cid in OVR:
        s, c, n = OVR[cid]
        e["assessment"] = {"status": s, "confidence": c}
        e["nota_status"] = n
    elif len({x["assessment"]["status"] for x in items}) > 1:
        e["nota_status"] = "Status divergente entre agentes (" + "; ".join(f"{AG[x['_agent']].split('-')[0]}: {x['assessment']['status']}" for x in items) + "); mantido o mais conservador."
    e["concerns"] = concerns
    e["agent"] = ", ".join(dict.fromkeys(AG[x["_agent"]] for x in items))
    e["ids_origem"] = {x["_agent"]: x["claim_id"] for x in items}
    e["issues"] = sorted(set(cl2iss.get(cid, [])))
    e["runs"] = ["run-003"]
    e["versao_capitulo"] = "f4ba3b00"
    out.append(e)
def key(e):
    s, q = e["claim_id"][3:].split(".")
    return (int(s), int(q))
out.sort(key=key)
txt = yaml.dump(out, allow_unicode=True, sort_keys=False, width=110, default_flow_style=None)
txt = "\n".join("  " + l if l else l for l in txt.splitlines())
hdr = "\n\n  # ================================================================ Cap. 2 (run-003, sha f4ba3b00)\n  # Seções: 1 Primeira/segunda gerações · 2 Cânone · 3 Segunda geração · 4 Partidos heterogêneos · 5 Competição e gastos ·\n  # 6 Financiamento · 7 Argumento. Correspondência de IDs: runs/run-003/synthesis/conflicts.md §2 e evidence/chair_mesclar_claims.py.\n"
open("evidence/chair_claims_cap2_bloco.yaml", "w", encoding="utf-8").write(hdr + txt + "\n")
print(len(out), "claims")
from collections import Counter; print(Counter(e["assessment"]["status"] for e in out))
