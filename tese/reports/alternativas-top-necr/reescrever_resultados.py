"""Gera e insere a seção de resultados a partir das tabelas auditadas."""
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
chapter = HERE.parent / '03-medindo-coordenacao-intrapartidaria.qmd'
s = pd.read_csv(HERE/'resumo_nacional.csv')
l = pd.read_csv(HERE/'listas.csv')
a = pd.read_csv(HERE/'concordancia.csv')
labels = {'top_necr':'Top-NECr','nucleo_80':'Top-80%','acima_divisao_igual':'Acima da divisão igualitária'}
kcols = ['k_top_necr','k_80','k_acima_igual']


def fmt(x, decimals=1):
    return f'{x:,.{decimals}f}'.replace(',', '_').replace('.', ',').replace('_', '.')


def table(headers, rows, caption, label):
    lines = ['| '+' | '.join(headers)+' |', '| '+' | '.join([':---']+['---:']*(len(headers)-1))+' |']
    lines += ['| '+' | '.join(map(str,row))+' |' for row in rows]
    return '\n'.join(lines)+f'\n\n: {caption} {{#{label}}}\n'


sizes = []
for year,g in l.groupby('ano_eleicao'):
    for rule,k in zip(labels,kcols):
        sizes.append([year,labels[rule],fmt(g[k].sum(),0),fmt(100*g[k].sum()/g.C.sum()),fmt(g[k].mean(),2),fmt(g[k].median(),0),f'{fmt(g[k].quantile(.25),0)}–{fmt(g[k].quantile(.75),0)}'])
t_sizes = table(['Ano','Regra','Posições','% das candidaturas','Média por lista','Mediana','Q1–Q3'],sizes,'Tamanho dos grupos nas três operacionalizações, incluindo listas sem recursos. Percentual nacional = soma das posições / soma das candidaturas; média, mediana e quartis atribuem peso igual a cada lista. Fonte: elaboração própria com base nos dados do TSE.','tbl-tamanhos-tres-regras')

prior,prior_null,election = [],[],[]
for year in [2018,2022]:
    for rule,label in labels.items():
        p = s[(s.ano_eleicao==year)&(s.regra==rule)&(s.desfecho=='competitividade')].iloc[0]
        e = s[(s.ano_eleicao==year)&(s.regra==rule)&(s.desfecho=='eleicao')].iloc[0]
        prior.append([year,label,fmt(p.cobertura*100),fmt(p.precisao*100),fmt(p.proporcao_perfil_fora*100)])
        prior_null.append([year,label,fmt(p.cobertura_acaso*100),fmt(p.precisao_acaso*100),fmt(p.lift,2)])
        election.append([year,label,fmt(e.cobertura*100),fmt(e.cobertura_acaso*100),fmt(e.precisao*100),fmt(e.precisao_acaso*100),fmt(e.lift,2)])
t_prior = table(['Ano','Regra','Competitivos incluídos (%)','Competitivos no grupo (%)','Competitivos fora (%)'],prior,'Competitividade prévia: cobertura do perfil e composição dentro e fora dos grupos. Denominadores válidos: 7.626 candidaturas em 2018 e 9.672 em 2022. Pertencimento fracionário nos empates do Top-NECr e do Top-80%. Fonte: elaboração própria com base nos dados do TSE.','tbl-competitividade-tres-regras')
t_prior_null = table(['Ano','Regra','Cobertura ao acaso (%)','Composição ao acaso (%)','Lift'],prior_null,'Benchmark intralista para competitividade prévia. As expectativas preservam as posições do grupo entre os registros válidos de cada lista; os indicadores nacionais são razões de somas. Fonte: elaboração própria com base nos dados do TSE.','tbl-acaso-competitividade')
t_election = table(['Ano','Regra','Cobertura (%)','Cobertura ao acaso (%)','Precisão (%)','Precisão ao acaso (%)','Lift'],election,'Correspondência eleitoral das três operacionalizações. Cobertura: fração dos 513 eleitos de cada ano incluída no grupo; precisão: fração das posições do grupo ocupada por eleitos. Fonte: elaboração própria com base nos dados do TSE.','tbl-eleicao-tres-regras')
agree=[]
for year in [2018,2022]:
    for pair in ['top_necr__nucleo_80','top_necr__acima_divisao_igual','nucleo_80__acima_divisao_igual']:
        x=a[(a.ano_eleicao==year)&(a.par==pair)].iloc[0]
        ra,rb=pair.split('__')
        agree.append([year,labels[ra]+' × '+labels[rb],fmt(x.comum,0),fmt(x.jaccard_agregado,3),fmt(x.A_contida_B*100),fmt(x.B_contida_A*100)])
t_agree=table(['Ano','A × B','Posições comuns','Jaccard','A contido em B (%)','B contido em A (%)'],agree,'Sobreposição nacional dos grupos. Interseção = soma dos menores pesos individuais; união = soma dos maiores pesos. Jaccard = interseção / união. A e B seguem a ordem da comparação. Fonte: elaboração própria com base nos dados do TSE.','tbl-concordancia-tres-regras')

text = r'''## Resultados

### Amplitude das nominatas e concentração dos recursos

A comparação entre 2018 e 2022 revela uma ampliação do universo de candidaturas acompanhada de crescimento da presença de competitivos prévios. O total de candidaturas a deputado federal passou de 7.630 para 9.675, um aumento de 26,8%. No mesmo período, o número de candidaturas com o perfil de competitividade definido no capítulo passou de 886 para 1.287, crescimento de 45,3%. Essas candidaturas representam aproximadamente 11,6% e 13,3% dos respectivos universos. Na avaliação desse perfil, quatro registros de 2018 e três de 2022 têm informação insuficiente e permanecem fora dos denominadores válidos; continuam, contudo, na definição dos grupos financeiros e na avaliação dos resultados eleitorais.

As candidaturas estão distribuídas em 859 listas partido × UF em 2018 e 711 em 2022. Dessas, respectivamente, 73 e 63 não registram recursos partidários e recebem grupo vazio nas três regras. As comparações nacionais incluem essas listas, de modo que sua ausência de financiamento não retira candidaturas ou eleitos do universo analisado.

O NECr permite examinar a dimensão efetiva da distribuição antes de converter o indicador em pertencimento individual. Entre as listas com recursos partidários, sua mediana passou de 1,88 para 4,81 candidaturas equivalentes em financiamento. A média da razão NECr/C, entretanto, permaneceu próxima: 56,18% em 2018 e 55,40% em 2022. Portanto, o aumento do número efetivo de candidaturas financiadas ocorreu sem expansão correspondente dessa medida relativa à extensão das listas. Essa razão descreve a concentração dos recursos; não corresponde diretamente ao percentual de candidaturas incluídas em um dos grupos.

### Tamanho dos grupos nas três operacionalizações

A @tbl-tamanhos-tres-regras mostra como a distribuição financeira se traduz em subconjuntos de candidaturas. Em 2018, o Top-NECr reuniu 2.318 posições e o Top-80%, 2.305, aproximadamente 30% do universo nacional em ambos os casos. Em 2022, esses totais passaram a 3.824 e 3.759 posições, respectivamente, ou 39,5% e 38,9% das candidaturas. As duas regras também apresentam a mesma mediana por lista em cada ano: duas posições em 2018 e quatro em 2022.

@@SIZES@@

A regra acima da divisão igualitária é mais restritiva no agregado. Seleciona 1.772 candidaturas em 2018, ou 23,2% do universo, e 2.688 em 2022, ou 27,8%. A mediana aumenta de uma para três candidaturas por lista. Assim, a expansão do grupo financeiro entre as duas eleições aparece sob os três critérios, embora sua extensão dependa da definição adotada.

As medidas não impõem a mesma condição para pertencer ao grupo. O Top-80% fixa a parcela de recursos a acumular, enquanto a regra igualitária exige que cada integrante receba acima da média de sua lista. Em uma distribuição perfeitamente igual, o Top-NECr inclui toda a nominata, o Top-80% ocupa o menor número inteiro de posições necessário para alcançar 80% dos recursos e a regra acima da divisão igualitária não seleciona ninguém. A inclusão em um grupo que concentra o orçamento, portanto, não implica necessariamente diferenciação financeira em relação aos demais copartidários.

No Top-NECr e no Top-80%, os empates no corte recebem pesos fracionários que preservam o número de posições. Em 2018, há empates desse tipo em 49 listas no Top-NECr e em 67 no Top-80%; em 2022, são 108 em cada regra. Por isso, as contagens de perfis dentro e fora desses grupos podem apresentar decimais. As médias da tabela incluem listas sem recursos, enquanto os indicadores de NECr/C apresentados anteriormente se referem apenas às listas financiadas; além disso, o percentual nacional de posições dá maior peso às listas com mais candidaturas.

### Correspondência com a competitividade prévia

A seleção financeira reúne a maioria das candidaturas competitivas prévias sob as três operacionalizações (@tbl-competitividade-tres-regras). O Top-NECr apresenta a maior cobertura desse perfil: 80,9% em 2018 e 82,7% em 2022. O Top-80% inclui 78,4% e 81,4%, respectivamente. A regra acima da divisão igualitária cobre uma parcela menor, de 69,5% e 73,6%, acompanhando seu menor tamanho agregado.

@@PRIOR@@

A composição dos grupos revela outra dimensão da focalização. Em 2018, competitivos prévios ocupavam 30,9% das posições do Top-NECr e 30,2% das posições do Top-80%; em 2022, esses percentuais ficaram próximos de 27,8% e 27,9%. No grupo acima da divisão igualitária, a presença de competitivos é maior e permanece próxima entre eleições: 34,8% e 35,3%. Entre as candidaturas que ficam fora dos respectivos grupos, a incidência de competitividade prévia varia apenas de 3,2% a 4,6% em 2018 e de 3,8% a 4,9% em 2022.

Há, assim, uma associação entre posição na distribuição de recursos e credenciais eleitorais anteriores: os grupos financeiros abrangem a maioria dos competitivos e apresentam maior incidência desse perfil do que seus complementos. Ao mesmo tempo, em todas as regras e nos dois anos, a maioria dos integrantes não preenche o critério operacional de competitividade prévia. A alocação financeira não reproduz integralmente a classificação pelo histórico eleitoral; a ausência dessa credencial tampouco demonstra ausência de outros recursos políticos.

O benchmark da @tbl-acaso-competitividade considera a expectativa de inclusão de competitivos ao preservar o tamanho do grupo dentro de cada lista. Para os registros com informação válida, a expectativa é dada pelo produto entre a massa de posições do grupo e a proporção de competitivos na lista. As expectativas são somadas nacionalmente antes do cálculo das taxas. Esse procedimento distingue a correspondência observada daquela esperada apenas pela extensão dos grupos e pela distribuição dos competitivos entre as listas.

@@PRIOR_NULL@@

As três regras apresentam correspondência superior à expectativa aleatória nos dois anos. No Top-NECr, o lift de competitividade é de 1,87 em 2018 e 1,89 em 2022; no Top-80%, de 1,93 e 1,98. A regra acima da divisão igualitária apresenta os maiores valores, 2,34 e 2,36. Seu menor alcance sobre o total de competitivos acompanha uma maior concentração relativa desse perfil nas posições selecionadas. O resultado preserva a associação descritiva entre financiamento e credenciais anteriores sob diferentes definições do grupo, sem identificar quem determinou os repasses ou demonstrar que o histórico eleitoral tenha sido o critério utilizado nessa decisão.

### Correspondência com o resultado eleitoral

A avaliação dos eleitos apresenta o mesmo contraste entre abrangência e seletividade (@tbl-eleicao-tres-regras). O Top-NECr inclui 445 dos 513 eleitos de 2018, cobertura de 86,7%, e uma contagem ponderada de 475,19 em 2022, cobertura de 92,6%. O Top-80% reúne 432 e 471,67 eleitos, correspondentes a 84,2% e 91,9%. A regra acima da divisão igualitária inclui 392 eleitos em 2018 e 461 em 2022, com coberturas de 76,4% e 89,9%.

@@ELECTION@@

A cobertura aumenta de 2018 para 2022 nas três regras, enquanto a precisão diminui. No Top-NECr, a proporção de eleitos entre as posições selecionadas cai de 19,2% para 12,4%; no Top-80%, de 18,7% para 12,5%; e na regra acima da divisão igualitária, de 22,1% para 17,2%. Como o total de eleitos permanece em 513 por ano, a ampliação dos grupos financeiros incorpora mais vencedores, mas também mais candidaturas não eleitas. Cobertura crescente e precisão decrescente expressam, nesse caso, dimensões distintas da mudança na extensão dos grupos.

O benchmark eleitoral preserva o tamanho $k$ de cada grupo e o número de eleitos $E$ entre as $C$ candidaturas de cada lista. A expectativa de acertos é $kE/C$; a cobertura aleatória nacional divide a soma dessas expectativas pelo total de eleitos, e a precisão aleatória divide a mesma soma pelo total de posições. O lift, comum às duas taxas, é a razão entre a soma dos acertos observados e a soma dos esperados.

Em 2018, as coberturas esperadas ao acaso são de 43,8% para o Top-NECr, 41,5% para o Top-80% e 30,8% para a regra acima da divisão igualitária. Em 2022, são de 43,7%, 39,3% e 32,0%. A correspondência observada com a eleição supera essas referências em todas as comparações. O lift do Top-NECr passa de 1,98 para 2,12; o do Top-80%, de 2,03 para 2,34; e o da regra igualitária, de 2,48 para 2,81. Portanto, a queda da precisão bruta entre eleições não é acompanhada de queda da correspondência relativa ao acaso: as precisões esperadas também diminuem.

O Top-NECr apresenta a maior cobertura eleitoral nas duas eleições, mas a regra acima da divisão igualitária apresenta maior precisão e maior lift. O Top-80% fica próximo do Top-NECr em cobertura e tamanho agregado, com lift superior nos dois anos. Não há uma regra que maximize simultaneamente todos os indicadores. A comparação explicita o que cada operacionalização privilegia: abranger mais vencedores ou reunir um grupo menor com maior incidência de eleitos em relação ao seu tamanho e à composição das listas.

Esses resultados descrevem correspondência eleitoral da alocação registrada. Como os recursos representam totais da campanha, a ausência do resultado eleitoral na fórmula de seleção não transforma a classificação em previsão realizada antes da eleição. Da mesma forma, candidaturas financiadas que não venceram não constituem automaticamente erros partidários, e a presença de eleitos fora dos grupos não demonstra ausência de apoio partidário. Nenhuma dessas comparações identifica o efeito causal dos recursos sobre a vitória.

### Concordância e robustez da operacionalização

A proximidade entre os tamanhos do Top-NECr e do Top-80% não implica identidade entre seus integrantes. A @tbl-concordancia-tres-regras apresenta a interseção dos grupos, o Jaccard nacional e as duas proporções de contenção. Nos empates, a interseção soma o menor peso atribuído a cada candidatura pelas duas regras; a união soma o maior. O Jaccard agregado divide essas duas somas, sem contar ausências conjuntas como concordância.

@@AGREE@@

Top-NECr e Top-80% compartilham 2.130 posições em 2018 e 3.444 em 2022, com Jaccard de 0,854 e 0,832. Aproximadamente 92% e 90% das posições do Top-NECr estão contidas no Top-80%, respectivamente. No nível das listas financiadas, os pesos de pertencimento são idênticos em 602 das 786 listas de 2018 (76,6%) e em 288 das 648 listas de 2022 (44,4%). A sobreposição nacional permanece elevada, embora a identidade dos cortes por lista seja menos frequente em 2022.

As comparações com a regra acima da divisão igualitária apresentam Jaccard agregado entre 0,659 e 0,680. Essa distância decorre em parte de seu menor tamanho. Considerando a contenção na direção inversa, 92,7% das candidaturas acima da divisão igualitária estão no Top-NECr em 2018 e 96,2% em 2022; em relação ao Top-80%, são 92,9% e 97,1%. A regra mais restritiva no agregado seleciona, portanto, sobretudo candidaturas também contempladas pelos outros critérios, mas não constitui um subconjunto fixo deles em todas as listas.

As três regras ordenam candidaturas pelos mesmos recursos e estabelecem fronteiras nesse ordenamento. Dentro de cada lista, seus cortes são aninhados, embora a ordem dos tamanhos possa mudar de uma lista para outra. Por essa razão, a sobreposição é parcialmente uma consequência da construção das medidas. A evidência de robustez está na persistência da associação com competitividade prévia e eleição, acima das expectativas intralista, mesmo quando a fronteira do grupo muda. A concordância entre as classificações não constitui validação independente da existência de um núcleo político nem demonstra uma intenção comum por trás dos repasses. Os resultados delimitam um padrão de priorização financeira observada cuja extensão e seletividade variam conforme a operacionalização.

'''
for marker,value in {'SIZES':t_sizes,'PRIOR':t_prior,'PRIOR_NULL':t_prior_null,'ELECTION':t_election,'AGREE':t_agree}.items():
    text=text.replace('@@'+marker+'@@',value.strip())
original=chapter.read_text(encoding='utf-8')
before,tail=original.split('## Resultados\n',1)
old,after=tail.split('## Discussão\n',1)
# Arquivo separado preserva o trecho substituído para revisão e recuperação.
backup=HERE/'resultados-antes-reescrita.qmd'
if not backup.exists():
    backup.write_text('## Resultados\n'+old,encoding='utf-8')
chapter.write_text(before+text+'## Discussão\n'+after,encoding='utf-8')
assert chapter.read_text(encoding='utf-8').split('## Resultados\n')[0]==before
assert chapter.read_text(encoding='utf-8').split('## Discussão\n')[1]==after
assert '@@' not in text
print(f'Seção reescrita: {chapter}; cinco tabelas geradas dos CSVs auditados.')
