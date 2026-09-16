"""Cria a pasta de um novo run de revisão e escreve manifest.yaml.

Uso (a partir da raiz do repositório):
    python thesis-review/tools/new_run.py --chapter 3 --agents measurement,statistics,results
    python thesis-review/tools/new_run.py --chapter 4 --agents measurement,statistics,results --run run-003

Imprime o id do run criado. Não sobrescreve runs existentes.
"""
import argparse
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "thesis-review" / "runs"

CHAPTER_FILES = {
    "1": "tese/01-introducao.qmd",
    "2": "tese/02-literatura.qmd",
    "3": "tese/03-medindo-coordenacao-intrapartidaria.qmd",
    "4": "tese/04-mecanismo-causal-coordenacao.qmd",
}

# Insumos cujo hash entra no manifesto (para saber se o run é comparável com outro).
INPUTS_BY_CHAPTER = {
    "3": [
        "tese/03-medindo-coordenacao-intrapartidaria.qmd",
        "tese/03-formulas-propostas.qmd",
        "src/1_silver/gerar_rrd.py",
        "data/processed/rrd_df_novo.parquet",
        "src/2_gold/cap3_cobertura_top_necr.py",
        "src/2_gold/cap3_cs_features.py",
        "src/2_gold/cap3_taa_features.py",
        "tese/reports/resultados-capitulo-3/15_cobertura_nacional.csv",
        "tese/reports/resultados-capitulo-3/00_sintese.csv",
        "tese/reports/sensibilidade-top-x/resumo_nacional.csv",
        "data/processed/df_cobertura_top_necr_resumo.csv",
    ],
    "4": [
        "tese/04-mecanismo-causal-coordenacao.qmd",
        "src/2_gold/cap3_survival_features.py",
        "data/processed/df_cox_survival.parquet",
    ],
    "2": ["tese/02-literatura.qmd", "tese/references.bib"],
    "1": ["tese/01-introducao.qmd"],
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def next_run_id() -> str:
    RUNS.mkdir(parents=True, exist_ok=True)
    existing = sorted(p.name for p in RUNS.iterdir() if p.is_dir() and p.name.startswith("run-"))
    n = int(existing[-1].split("-")[1]) + 1 if existing else 1
    return f"run-{n:03d}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapter", required=True)
    ap.add_argument("--agents", required=True, help="lista separada por vírgula")
    ap.add_argument("--run", default=None)
    args = ap.parse_args()

    chapter = str(args.chapter)
    if chapter not in CHAPTER_FILES:
        print(f"capítulo desconhecido: {chapter}", file=sys.stderr)
        return 2
    run_id = args.run or next_run_id()
    run_dir = RUNS / run_id
    if run_dir.exists():
        print(f"{run_id} já existe", file=sys.stderr)
        return 3
    for sub in ("agents", "evidence", "synthesis"):
        (run_dir / sub).mkdir(parents=True)

    agents = [a.strip() for a in args.agents.split(",") if a.strip()]
    inputs = []
    for rel in INPUTS_BY_CHAPTER.get(chapter, [CHAPTER_FILES[chapter]]):
        p = ROOT / rel
        inputs.append((rel, sha256(p) if p.exists() else "AUSENTE"))

    lines = [
        f"run: {run_id}",
        f"capitulo: {chapter}",
        f"arquivo: {CHAPTER_FILES[chapter]}",
        f"iniciado_em: {datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')}",
        "agentes:",
        *[f"  - {a}" for a in agents],
        "insumos:",
        *[f"  - {{arquivo: {rel}, sha256: {h}}}" for rel, h in inputs],
        "concluido_em: null",
        "contagens: {CRITICAL: null, MAJOR: null, MODERATE: null, MINOR: null}",
        "gate: null",
        "",
    ]
    (run_dir / "manifest.yaml").write_text("\n".join(lines), encoding="utf-8")
    print(run_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
