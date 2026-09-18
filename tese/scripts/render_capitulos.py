#!/usr/bin/env python3
"""Combina um subconjunto de capitulos da tese (arquivos .qmd) em um unico
documento Quarto e renderiza (docx e/ou pdf), com as referencias ao final.

Roda a partir de qualquer diretorio; caminhos de capitulo sao relativos a
tese/. O arquivo combinado eh escrito FORA do projeto Quarto do livro
(pasta irma revisoes/, ao lado de tese/) porque renderizar dentro de
tese/ faz o Quarto validar o _quarto.yml do livro inteiro (e falha se
algum capitulo do livro ainda nao existir, ex. 05-hipoteses-alternativas).
Por isso o bibliography/csl/reference-doc do livro sao declarados
explicitamente no frontmatter do combinado, apontando de volta para tese/.

Uso:
    python scripts/render_capitulos.py
    python scripts/render_capitulos.py 02-literatura.qmd 03-medindo-coordenacao-intrapartidaria.qmd
    python scripts/render_capitulos.py --to docx,pdf
    python scripts/render_capitulos.py 04-mecanismo-causal-coordenacao.qmd --to pdf

Saida: revisoes/<data>_<capitulos>.<ext> (fonte .qmd combinada + docx/pdf).
"""
import argparse
import re
import subprocess
from datetime import date
from pathlib import Path

TESE_ROOT = Path(__file__).resolve().parents[1]  # tese/
OUT_ROOT = TESE_ROOT.parent / "revisoes"  # fora do projeto Quarto do livro
DEFAULT_CHAPTERS = [
    "02-literatura.qmd",
    "03-medindo-coordenacao-intrapartidaria.qmd",
]

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def strip_frontmatter(text: str):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return text, None
    title_m = re.search(r'^title:\s*"?(.*?)"?\s*$', m.group(1), re.MULTILINE)
    title = title_m.group(1) if title_m else None
    return text[m.end():], title


def build_combined_qmd(chapters, out_path: Path):
    parts = []
    for chap in chapters:
        chap_path = TESE_ROOT / chap
        text = chap_path.read_text(encoding="utf-8")
        body, title = strip_frontmatter(text)
        if title:
            parts.append(f"# {title}\n")
        parts.append(body.strip() + "\n")

    nomes = ", ".join(c.replace(".qmd", "") for c in chapters)
    # caminhos relativos de revisoes/ de volta para tese/
    tese_rel = "../tese"
    frontmatter = (
        "---\n"
        f'title: "Revisao — {nomes}"\n'
        'author: "Yuri Lucatelli Taba"\n'
        "lang: pt-BR\n"
        f"bibliography: {tese_rel}/references.bib\n"
        f"csl: {tese_rel}/associacao-brasileira-de-normas-tecnicas.csl\n"
        "format:\n"
        "  docx:\n"
        f"    reference-doc: {tese_rel}/reference.docx\n"
        '    reference-section-title: "Referências"\n'
        "  pdf:\n"
        "    documentclass: scrreprt\n"
        "    classoption: [oneside, open=any]\n"
        "    pdf-engine: lualatex\n"
        "    papersize: a4\n"
        "    fontsize: 12pt\n"
        "    linestretch: 1.5\n"
        "    number-sections: true\n"
        "    toc: false\n"
        "    link-citations: true\n"
        f"    include-in-header: {tese_rel}/latex/preamble.tex\n"
        "---\n\n"
    )
    out_path.write_text(frontmatter + "\n\n".join(parts), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "chapters",
        nargs="*",
        default=DEFAULT_CHAPTERS,
        help="arquivos .qmd (relativos a tese/) a combinar, na ordem desejada",
    )
    parser.add_argument(
        "--to", default="docx", help="formato(s) separados por virgula: docx,pdf"
    )
    args = parser.parse_args()

    out_dir = OUT_ROOT
    out_dir.mkdir(exist_ok=True)

    stem = "_".join(re.sub(r"\.qmd$", "", c) for c in args.chapters)
    today = date.today().isoformat()
    combined_qmd = out_dir / f"{today}_{stem}.qmd"

    build_combined_qmd(args.chapters, combined_qmd)

    for fmt in args.to.split(","):
        subprocess.run(
            ["quarto", "render", combined_qmd.name, "--to", fmt.strip()],
            cwd=out_dir,
            check=True,
        )

    print(f"OK: gerado em {out_dir}")


if __name__ == "__main__":
    main()
