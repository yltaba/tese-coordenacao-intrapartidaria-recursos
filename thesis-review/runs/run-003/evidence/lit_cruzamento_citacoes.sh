#!/bin/sh
# Cruza chaves citadas no Cap. 2 com o references.bib (literature-reviewer, run-003)
cd "$(dirname "$0")/../../../.."
Q=tese/02-literatura.qmd; B=tese/references.bib
grep -o "@[a-zA-Z_]*[0-9a-z_]*" $Q | grep -v "^@sec" | sed 's/^@//' | sort -u > /tmp/lit_cited.txt
grep -o "^@[a-zA-Z]*{[^,]*" $B | sed 's/.*{//' | sort > /tmp/lit_bib_all.txt
sort -u /tmp/lit_bib_all.txt > /tmp/lit_bib.txt
echo "## citadas ausentes do bib"; comm -23 /tmp/lit_cited.txt /tmp/lit_bib.txt
echo "## chaves duplicadas no bib"; uniq -d /tmp/lit_bib_all.txt
echo "## no bib mas nao citadas no Cap.2"; comm -13 /tmp/lit_cited.txt /tmp/lit_bib.txt
