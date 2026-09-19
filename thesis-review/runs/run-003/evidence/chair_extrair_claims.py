# Extrai blocos YAML de claims dos relatórios dos especialistas (run-003) e lista id/linha/status.
import re, yaml, json, sys
out = []
for ag in ["theory", "literature", "methodology", "writing"]:
    txt = open(f"agents/{ag}.md", encoding="utf-8").read()
    sec = txt.split("## Claims", 1)[1]
    sec = re.split(r"\n## ", sec, 1)[0]
    for b in re.findall(r"```yaml\n(.*?)```", sec, re.S):
        try:
            d = yaml.safe_load(b)
        except Exception as e:
            print("ERRO", ag, e, b[:80]); continue
        d["_agent"] = ag
        out.append(d)
json.dump(out, open("evidence/chair_claims_extraidos.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for d in out:
    loc = d.get("localizacao", {})
    print(d["_agent"][:4], d["claim_id"], loc.get("linha"), d["assessment"]["status"], d["assessment"].get("confidence"), "|", str(d["claim"])[:90])
