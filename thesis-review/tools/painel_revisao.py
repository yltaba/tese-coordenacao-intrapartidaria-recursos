#!/usr/bin/env python3
"""Gera o painel interativo das pendências de revisão (comentários HTML nos .qmd).

Lê todos os comentários `<!-- ... -->` de tese/*.qmd, as listas de tarefas
(`- [ ]`) de notes/revisao-pendente/*.md e os issues do run-002, classifica cada
comentário (tipo, prioridade, resumo da ação) e escreve um HTML autocontido.

Uso (a partir da raiz do repositório):
    python thesis-review/tools/painel_revisao.py

Saída: notes/revisao-pendente/painel-revisao.html

A classificação fica no dicionário CLASSIFICACAO, indexado pelo rótulo do
comentário. Comentário novo sem entrada aparece como "Sem classificação" — basta
acrescentá-lo ao dicionário e rodar de novo. Comentário apagado do .qmd some do
painel na próxima execução.
"""
import datetime as dt
import glob
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SAIDA = ROOT / "notes" / "revisao-pendente" / "painel-revisao.html"

CAPITULOS = {
    "02-literatura.qmd": ("2", "Cap. 2 · Literatura e argumento"),
    "03-medindo-coordenacao-intrapartidaria.qmd": ("3", "Cap. 3 · Priorização na alocação"),
    "04-mecanismo-causal-coordenacao.qmd": ("4", "Cap. 4 · Timing dos repasses"),
    "apendice-a-formalizacao.qmd": ("A", "Apêndice A · Formalização"),
}

# rótulo -> (tipo, prioridade, resumo da ação). prioridade None = sem ação aberta.
CLASSIFICACAO = {
    # ── Cap. 2 ────────────────────────────────────────────────────────────
    "2.1": ("roteiro", None, "Seção 2.1 tem as quatro peças; faltam acabamentos: transição repetida, lacuna anunciada maior do que é, citação sem ligação."),
    "2.1-3": ("argumento", "media", "Acrescentar frase de amarração: o partido controla a entrada na lista, não a ordenação — é isso que abre espaço para o instrumento da tese."),
    "2.1-4": ("argumento", "media", "Fechar a classificação do Brasil em Carey & Shugart com uma frase declarativa (o pooling é peça do argumento votos × cadeiras)."),
    "2.1-5": ("estrutura", "baixa", "Mainwaring (aqui) e Samuels (seção 2.3) fazem a mesma afirmação: trocar por remissão ou justificar as duas vias."),
    "2.1-1": ("estrutura", "media", "Parágrafo repete a distinção 1ª/2ª geração pela terceira vez: cortar quase inteiro, mantendo a frase final."),
    "2.1-2": ("estrutura", "baixa", "Frase-sumário de Mershon promete três arenas e só duas aparecem: cortar ou cumprir a promessa."),
    "2.1-6": ("estrutura", "media", "Separar Cheibub & Sin (âncora do tamanho do núcleo) da literatura de distribuição territorial."),
    "2.1-7": ("estrutura", "media", "Deixar a explicação completa de resource gatekeeping (Janusz et al.) só aqui; Financiamento e Argumento remetem."),
    "2.1-8": ("argumento", "baixa", "Abrir com a lacuna ('resta observar diretamente...') e só depois situá-la como extensão da 2ª geração."),
    "2.2": ("roteiro", "media", "Fechar o dilema do gatekeeper com posição: a tese mostra uso seletivo do instrumento, não se o partido acerta o trade-off."),
    "2.2-1": ("estrutura", "media", "Decidir a formulação-âncora do argumento central e retomá-la por remissão (@sec-argumento) em vez de reformular."),
    "2.2-2": ("argumento", "alta", "Sediar aqui a justificativa teórica do timing (frente iii): por que o MOMENTO do repasse é instrumento de controle."),
    "2.2-3": ("argumento", "media", "Tomar posição sobre o dilema de Fiva et al. no Brasil; anunciar a hipótese auxiliar por tipo de partido, se for usada."),
    "2.2-4": ("correcao", "baixa", "Consertar o período iniciado por 'Enquanto' que não chega a uma oração principal."),
    "2.2-5": ("estrutura", "media", "Parágrafo-chave (gatekeeping depois da nominata): citá-lo por remissão no Argumento, que hoje reconstrói versão mais fraca."),
    "2.3": ("roteiro", "media", "A seção nunca diz por que o FEFC muda o jogo descrito por Samuels."),
    "2.3-1": ("argumento", "baixa", "Marcar a diferença institucional SNTV japonês × lista aberta com pooling antes da comparação com Samuels."),
    "2.3-2": ("argumento", "baixa", "Ligar a magnitude que degrada a informação (Samuels) aos efeitos fixos de lista do Cap. 3."),
    "2.3-3": ("argumento", "alta", "A lacuna é afirmada, não demonstrada: reformular como falta de medida direta da AÇÃO partidária (quem recebe, quanto, quando)."),
    "2.3-4": ("correcao", "media", "Moderar a antecipação sobre o FEFC e separar os anos: recursos partidários = 43,6% da receita em 2018 e 87,8% em 2022."),
    "Reestruturação": ("roteiro", None, "Registro: a ordem dos parágrafos de Financiamento mudou; nenhuma frase foi reescrita."),
    "1": ("roteiro", None, "Marcador de bloco: vertentes de Mancuso."),
    "Tensão": ("argumento", "alta", "Tratar no Argumento: 35% do FEFC e 95% do FP seguem votos, o que pode incentivar dispersão, e não só concentração."),
    "A0": ("roteiro", "alta", "Tornar visível a cadeia incentivo → restrição informacional → sinal → estratégia → implicações (i–iii) → rivais."),
    "A1": ("argumento", "alta", "Recomeçar pelo incentivo, em dois degraus: Fiva et al. dão o problema de coordenação (cadeiras × controle da seleção); a sobrevivência é o degrau brasileiro da tese, não deles."),
    "A2": ("argumento", "alta", "Resolver votos × cadeiras, nomear explicações rivais, dizer quem decide (diretório nacional × estadual); digitação 'o tese'."),
    "A3": ("estrutura", "media", "Cortar a repetição de Financiamento; usar o espaço para justificar a amostra 2018/2022 (e não 2014)."),
    "A4": ("argumento", "alta", "Cotas tornam o teste conservador; dizer que recursos partidários = FEFC + FP + outros (FP: 18,3% em 2018, 7,3% em 2022)."),
    "A5": ("argumento", "alta", "Consertar a frase quebrada ('Nestes termos,') e justificar por que o tamanho do núcleo é dado pelo número efetivo."),
    "A5, cont.": ("argumento", "media", "Explicitar o contrafactual de 'sobrerrepresentam': núcleo de mesmo tamanho, mesma lista, sem relação com o histórico."),
    "A6": ("estrutura", "media", "A ideia central abre três vezes; fixar uma formulação cedo, dar a Cheibub & Sin o papel de justificar o tamanho do núcleo."),
    "A7": ("argumento", "alta", "A frase mais importante do capítulo: estilo, 'porque' causal, por que credenciais e não candidatos marginais, terminologia."),
    "A8": ("correcao", "media", "Páginas para Silva & Cervi e Cheibub & Sin; dizer em que consiste a adaptação; uniformizar 'ex ante'."),
    "A9": ("argumento", "alta", "Frente (iii) sem justificativa teórica; fixar 'núcleo priorizado'; numerar (i) (ii) (iii)."),
    "A10": ("correcao", "baixa", "Trocar 'capítulo 3/4' por referências cruzadas do Quarto."),
    # ── Cap. 3 ────────────────────────────────────────────────────────────
    "3.0": ("argumento", "alta", "Formular o mecanismo como padrão 'compatível com', não como mecanismo demonstrado (THE-3-001)."),
    "3.0-1": ("correcao", "baixa", "Antecipar na introdução os achados de robustez (Top-X%) e da validação com eleitos."),
    "3.1": ("verificado", None, "Universo, listas, listas sem recursos e eleitos nelas conferem com rrd_df_novo.parquet."),
    "3.1-2": ("correcao", "media", "Horizonte do histórico: vitórias até o ciclo anterior, não 'retroagindo até 1998'; lista de cargos inclui Presidente."),
    "3.2": ("argumento", "media", "Justificar o arredondamento do NECr (fica entre piso e teto: 82,6% / 86,7% / 87,7% de cobertura de eleitos em 2018)."),
    "3.2-1": ("correcao", "baixa", "Notação: $R_i$ → $R_{il}$; dizer como as listas sem recursos entram nos indicadores nacionais."),
    "3.3": ("roteiro", "media", "Mencionar que Presidente não está implementado e qual é o horizonte temporal do histórico."),
    "3.3-1": ("correcao", "media", "Critério de vitória lista Presidente (não implementado) e omite deputado distrital (implementado)."),
    "3.4": ("metodo", "media", "Declarar a regra de agregação nacional: razão de somas, não média por lista (precisão 33,94% × 41,65% em 2018)."),
    "3.5": ("verificado", None, "Competitivos 12,75% / 13,99% e crescimento 27% / 39% conferem."),
    "3.6": ("verificado", None, "Cobertura e precisão dos eleitos conferem com 15_cobertura_nacional.csv."),
    "3.6-1": ("correcao", "media", "Nota curta: 33,9% / 28,6% são razões de somas nacionais, não a precisão de uma lista típica."),
    "3.6-2": ("verificado", None, "Lift por magnitude (competitivos): os seis valores conferem."),
    "3.7": ("metodo", "alta", "Corrigir a massa não unitária na regressão intralista e regenerar figura e CSVs (I-3-001, MAJOR)."),
    "3.7-1": ("verificado", None, "Equação e cancelamento do denominador comum estão corretos."),
    "3.7-2": ("metodo", "media", "Nomear os pontos percentuais como efeito médio previsto da mudança individual, não conversão da razão (STA-3-004)."),
    "3.7-3": ("correcao", "media", "Fechar o parágrafo com a lista explícita de cargos estimados (sem Presidente)."),
    "3.7-4": ("correcao", "media", "'Vitórias para todos os cargos' excede os cargos estimados; números por cargo conferem."),
    "3.7-5": ("verificado", None, "Votação anterior: +15% por 10 p.p. em 2018 confere."),
    "3.7-6": ("verificado", None, "Razões 8,16 / 4,58 conferem; AMEs sujeitos a I-3-001 e STA-3-004."),
    "3.7-7": ("verificado", None, "Tabela por magnitude reproduz o texto; sujeita a reestimação se I-3-001 for corrigido."),
    "3.7-8": ("verificado", None, "Mulher 1,44 / 1,32 confere."),
    "3.7-9": ("metodo", "media", "Qualificar 'distinguível da paridade' (negra, 2022): não resiste a cluster por partido (p≈0,09)."),
    "3.8": ("roteiro", None, "Seção de robustez cumpre a função; só ajustes de legenda."),
    "3.6-3, ver também 3.9": ("verificado", None, "86,7% / 92,6% dos eleitos conferem."),
    "3.8-1": ("correcao", "baixa", "Dar título às três tabelas de magnitude (a legenda renderizada fica vazia)."),
    "3.8-2": ("correcao", "baixa", "Dizer que o Top-X% tende a gerar núcleos maiores que o Top-NECr (explica a cobertura crescente)."),
    "3.8-3": ("correcao", "baixa", "Nomear na legenda a linha do Top-NECr e o destaque em 80% da figura Top-X%."),
    "3.D": ("rascunho", None, "Proposta de Discussão do Cap. 3, gerada por IA, para reescrita do próprio punho."),
    # ── Cap. 4 ────────────────────────────────────────────────────────────
    "4.0": ("metodo", "alta", "Decidir as extensões do piloto: incluir o lift semanal (recomendado); não substituir o corte por Top-NECr."),
    "4.0-1": ("estrutura", "alta", "Levar a justificativa do timing para o Cap. 2 (ponto [2.2-2]); hoje ela só aparece no capítulo empírico."),
    "4.1": ("argumento", "media", "Justificar por que o corte temporal é a credencial e não o Top-NECr."),
    "4.1-1": ("estrutura", "media", "Remissão: cláusula de barreira (2018 × 2022) é o mesmo incentivo de sobrevivência discutido em Financiamento."),
    "4.1-2": ("estrutura", "baixa", "A conclusão da seção aparece antes das figuras: movê-la para depois, como síntese."),
    "4.1-3": ("correcao", "baixa", "Usar 47,8 p.p. em vez de 'quase 48'; números da seção não foram recomputados."),
    "4.1-4": ("argumento", "media", "Se o lift semanal entrar, usá-lo aqui como síntese numérica (≈2,0 na 1ª semana, ≈1,9 no fim)."),
    "4.2": ("estrutura", "baixa", "Antecipar na seção do KM por que ele vem antes do Cox."),
    "4.2-1": ("estrutura", "baixa", "Anunciar aqui a operacionalização alternativa por Top-NECr, se ela for incluída."),
    "4.2-2": ("metodo", "alta", "Recomputar os números do Kaplan-Meier contra regenerar_figuras_cap4.py antes da versão final."),
    "4.3": ("argumento", "alta", "Amarrar o Cox à regressão intralista do Cap. 3: as mesmas credenciais afetam parcela E momento."),
    "4.3-1": ("argumento", "alta", "Dizer explicitamente a convergência: dep. federal 2,00→1,55 (parcela) e HR 1,55→1,36 (timing)."),
    "4.3-2": ("metodo", None, "Conferir se df_cox_survival.parquet está atualizado em relação à base."),
    "4.D": ("rascunho", None, "Proposta de Discussão do Cap. 4, gerada por IA, para reescrita do próprio punho."),
    # ── Apêndice A ────────────────────────────────────────────────────────
    "RASCUNHO PARA EDIÇÃO": ("roteiro", "baixa", "Texto duplicado do Cap. 3 com rótulos de equação repetidos: cortar do capítulo quando decidir."),
    "PENDÊNCIAS": ("metodo", "media", "Se as fórmulas saírem do corpo, dizer em prosa: razão de somas, referência somada lista a lista, pesos fracionários; corrigir vírgula em eq-referencia-aleatoria/eq-lift."),
}

# Atualizações feitas depois de o comentário ter sido escrito.
ATUALIZACOES = {
    "A1": "Corrigido em 18/09/2026: a versão anterior do comentário atribuía a sobrevivência partidária a Fiva, Izzo & Tukiainen (2024), o que eles não formulam.",
    "4.3-2": "Checado em 18/09/2026: df_cox_survival.parquet (17/09) é posterior a rrd_df_novo.parquet (14/09) — está atualizado. O comentário pode ser apagado.",
}

TIPOS = {
    "argumento": "Argumento",
    "estrutura": "Estrutura e remissões",
    "correcao": "Correção pontual",
    "metodo": "Método e dados",
    "roteiro": "Roteiro da seção",
    "verificado": "Conferido",
    "rascunho": "Rascunho IA",
    "sem": "Sem classificação",
}

# Achados dos especialistas → issue arbitrado no run-002.
ACHADO_PARA_ISSUE = {
    "STA-3-001": "I-3-001", "STA-3-002": "I-3-002", "STA-3-003": "I-3-003",
    "STA-3-004": "I-3-003", "MEA-3-001": "I-3-004", "MEA-3-002": "I-3-005",
    "THE-3-001": "I-3-006", "WRI-3-001": "I-3-007", "WRI-3-002": "I-3-007",
}

# Cadeia das três frentes (00-coerencia-caps-2-3-4.md, seção 1, e comentários).
FRENTES = [
    {"frente": "(i)", "nome": "Composição do núcleo priorizado",
     "anunciada": ["ok", "Argumento, l. 248"],
     "justificada": ["parcial", "Tamanho do núcleo = NECr não é justificado", "A5"],
     "testada": ["ok", "Cap. 3 · Top-NECr, cobertura/precisão/lift"],
     "conectada": ["ok", "Cap. 3 cita @sec-argumento"]},
    {"frente": "(ii)", "nome": "Prêmio intralista por credencial",
     "anunciada": ["ok", "Argumento, l. 248"],
     "justificada": ["parcial", "Por que credenciais e não candidatos marginais?", "A7"],
     "testada": ["alerta", "Cap. 3 · sec-premio-credenciais — I-3-001 (MAJOR) aberto", "3.7"],
     "conectada": ["ok", "Explícita"]},
    {"frente": "(iii)", "nome": "Priorização temporal",
     "anunciada": ["alerta", "Redigida como 'ao núcleo de priorizados', mas testada por credencial", "3.D"],
     "justificada": ["lacuna", "Sem justificativa teórica no Cap. 2", "A9"],
     "testada": ["ok", "Cap. 4 · fluxo, Kaplan-Meier, Cox"],
     "conectada": ["lacuna", "Cap. 4 nunca diz 'esta é a frente (iii)'", "4.0-1"]},
]


def rotulo_de(texto):
    t = texto.strip()
    m = re.match(r"(?:ROTEIRO(?: DA REVISÃO)? )?\[([^\]]+)\]", t)
    if m:
        return m.group(1)
    m = re.match(r"PROPOSTA DE DISCUSSÃO \[([^\]]+)\]", t)
    if m:
        return m.group(1)
    if t.startswith("ROTEIRO DA REVISÃO"):
        return "A0"
    for chave in ("Reestruturação", "Tensão", "RASCUNHO PARA EDIÇÃO", "PENDÊNCIAS"):
        if t.startswith(chave):
            return chave
    return t[:24]


def secao_em(linhas, n):
    """Título (## ou ###) mais próximo acima da linha n (1-indexada)."""
    for i in range(n - 1, -1, -1):
        m = re.match(r"^(#{1,3})\s+(.*?)\s*(\{#.*\})?\s*$", linhas[i])
        if m:
            return m.group(2).replace("*", "")
    return "(início do arquivo)"


def blocos_de_codigo(texto):
    """Intervalos (início, fim) de caracteres dentro de chunks ```{...}```."""
    return [(m.start(), m.end()) for m in re.finditer(r"```\{.*?```", texto, flags=re.S)]


def ler_comentarios():
    itens, problemas = [], []
    for caminho in sorted(glob.glob(str(ROOT / "tese" / "*.qmd"))):
        nome = Path(caminho).name
        if nome not in CAPITULOS:
            continue
        cap, cap_nome = CAPITULOS[nome]
        texto = Path(caminho).read_text(encoding="utf-8")
        linhas = texto.split("\n")
        chunks = blocos_de_codigo(texto)
        if texto.count("<!--") != texto.count("-->"):
            problemas.append(f"{nome}: '<!--' e '-->' em número diferente")
        for m in re.finditer(r"<!--(.*?)-->", texto, flags=re.S):
            corpo = m.group(1).strip()
            linha = texto[: m.start()].count("\n") + 1
            if any(a <= m.start() < b for a, b in chunks):
                problemas.append(f"{nome}:{linha}: comentário dentro de chunk de código")
            rot = rotulo_de(corpo)
            tipo, prio, resumo = CLASSIFICACAO.get(rot, ("sem", "media", corpo[:140]))
            achados = sorted(set(re.findall(r"\b(?:STA|MEA|THE|WRI|RES|MET|LIT)-3-\d{3}\b", corpo)))
            issues = set(re.findall(r"\bI-3-\d{3}\b", corpo))
            issues |= {ACHADO_PARA_ISSUE[a] for a in achados if a in ACHADO_PARA_ISSUE}
            refs = sorted(set(re.findall(r"\[((?:A\d+)|(?:\d\.\d(?:-\d+)?)|(?:\d\.D))\]", corpo)) - {rot})
            item = {
                "id": f"{cap}:{rot}",
                "cap": cap, "capNome": cap_nome, "arquivo": f"tese/{nome}", "linha": linha,
                "secao": secao_em(linhas, linha), "rotulo": rot, "tipo": tipo,
                "prioridade": prio, "resumo": resumo, "texto": corpo,
                "achados": achados, "issues": sorted(issues), "refs": refs,
                "atualizacao": ATUALIZACOES.get(rot),
            }
            if tipo == "rascunho":
                partes = re.split(r"=== (?:RASCUNHO|NOTAS \(fora do rascunho\)) ===", corpo)
                item["cabecalho"] = partes[0].strip()
                item["rascunho"] = [p.strip() for p in partes[1].strip().split("\n\n") if p.strip()] if len(partes) > 1 else []
                item["notas"] = [p.strip() for p in partes[2].strip().split("\n\n") if p.strip()] if len(partes) > 2 else []
                item["palavras"] = sum(len(p.split()) for p in item["rascunho"])
            itens.append(item)
    return itens, problemas


def ler_tarefas_notas():
    tarefas = []
    for caminho in sorted(glob.glob(str(ROOT / "notes" / "revisao-pendente" / "*.md"))):
        nome = Path(caminho).name
        for i, l in enumerate(Path(caminho).read_text(encoding="utf-8").split("\n"), 1):
            m = re.match(r"^- \[( |x)\] (.*)$", l)
            if m:
                refs = re.findall(r"\[((?:A\d+)|(?:\d\.\d(?:-\d+)?))\]", m.group(2))
                tarefas.append({"id": f"{nome}:{i}", "arquivo": nome, "linha": i,
                                "feita": m.group(1) == "x", "texto": m.group(2), "refs": refs})
    return tarefas


def rotulos_citados_nas_notas():
    citados = {}
    for caminho in sorted(glob.glob(str(ROOT / "notes" / "revisao-pendente" / "*.md"))):
        nome = Path(caminho).name
        for r in re.findall(r"\[((?:A\d+)|(?:\d\.\d(?:-\d+)?))\]", Path(caminho).read_text(encoding="utf-8")):
            citados.setdefault(r, set()).add(nome)
    return citados


def ler_issues():
    p = ROOT / "thesis-review" / "runs" / "run-002" / "issues.yaml"
    if not p.exists():
        return []
    dados = yaml.safe_load(p.read_text(encoding="utf-8")) or []
    return [{"id": d.get("issue_id"), "titulo": d.get("titulo"), "severidade": d.get("severidade_final"),
             "status": d.get("status"), "recomendacao": d.get("recomendacao"), "achados": d.get("findings", [])}
            for d in dados]


def main():
    itens, problemas = ler_comentarios()
    tarefas = ler_tarefas_notas()
    presentes = {i["rotulo"] for i in itens}
    orfaos = [{"rotulo": r, "notas": sorted(n)} for r, n in sorted(rotulos_citados_nas_notas().items())
              if r not in presentes and not (r == "A0")]
    sem = [i["rotulo"] for i in itens if i["tipo"] == "sem"]
    dados = {
        "geradoEm": dt.datetime.now().strftime("%d/%m/%Y %H:%M"),
        "itens": itens, "tarefas": tarefas, "issues": ler_issues(), "frentes": FRENTES,
        "tipos": TIPOS, "orfaos": orfaos, "problemas": problemas, "semClassificacao": sem,
    }
    html = MODELO.replace("__DADOS__", json.dumps(dados, ensure_ascii=False).replace("</", "<\\/"))
    SAIDA.write_text(html, encoding="utf-8")
    abertas = sum(1 for i in itens if i["prioridade"])
    print(f"{len(itens)} comentários ({abertas} com ação aberta), {len(tarefas)} tarefas das notas, "
          f"{len(orfaos)} rótulos órfãos, {len(problemas)} problemas, {len(sem)} sem classificação")
    print(f"-> {SAIDA.relative_to(ROOT)}")


MODELO = Path(__file__).with_name("painel_revisao_modelo.html").read_text(encoding="utf-8")

if __name__ == "__main__":
    main()
