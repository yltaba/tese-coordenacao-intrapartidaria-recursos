#!/usr/bin/env python3
"""Verifica que uma edição de revisão (comentários HTML +/- reordenação de
parágrafos) não alterou o texto do capítulo fora dos comentários.

Uso:
    python verificar_corpo.py <backup.qmd> <atual.qmd> [--reordenado]

Sem --reordenado: exige que a sequência de parágrafos (com comentários
removidos) seja idêntica entre os dois arquivos.

Com --reordenado: exige apenas que o MULTICONJUNTO de parágrafos seja
idêntico (a ordem pode mudar). Reporta qualquer parágrafo que exista em um
arquivo e não no outro.

Também checa, em ambos os modos:
- todo comentário abre e fecha (mesmo número de '<!--' e '-->');
- nenhum comentário contém '--' em seu conteúdo (quebraria o HTML).
"""
import argparse
import collections
import re
import sys


def strip_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def paragraphs(text):
    body = strip_comments(text)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return [p.strip() for p in body.split("\n\n") if p.strip()]


def check_comment_hygiene(text, label):
    problems = []
    if text.count("<!--") != text.count("-->"):
        problems.append(f"{label}: número de '<!--' ({text.count('<!--')}) "
                         f"difere de '-->' ({text.count('-->')})")
    for m in re.finditer(r"<!--(.*?)-->", text, flags=re.S):
        inner = m.group(1)
        if "--" in inner:
            snippet = inner.strip()[:60]
            problems.append(f"{label}: comentário contém '--' interno: {snippet!r}")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("backup")
    ap.add_argument("atual")
    ap.add_argument("--reordenado", action="store_true",
                     help="permite reordenação de parágrafos (compara multiconjunto)")
    args = ap.parse_args()

    a = open(args.backup, encoding="utf-8").read()
    b = open(args.atual, encoding="utf-8").read()

    problems = check_comment_hygiene(a, "backup") + check_comment_hygiene(b, "atual")

    pa, pb = paragraphs(a), paragraphs(b)

    if args.reordenado:
        ca, cb = collections.Counter(pa), collections.Counter(pb)
        only_a = list((ca - cb).elements())
        only_b = list((cb - ca).elements())
        if only_a or only_b:
            problems.append("Parágrafos presentes só no backup (podem ter sido cortados):")
            for p in only_a:
                problems.append("  - " + p[:120])
            problems.append("Parágrafos presentes só no atual (podem ter sido adicionados):")
            for p in only_b:
                problems.append("  - " + p[:120])
    else:
        if pa != pb:
            problems.append("Sequência de parágrafos difere (use --reordenado se a ordem mudou de propósito).")
            import difflib
            for line in difflib.unified_diff(pa, pb, lineterm="", n=0):
                problems.append("  " + line[:200])

    if problems:
        print("FALHOU")
        for p in problems:
            print(p)
        sys.exit(1)
    else:
        print("OK — corpo do texto preservado" +
              (" (permitindo reordenação)" if args.reordenado else ""))


if __name__ == "__main__":
    main()
