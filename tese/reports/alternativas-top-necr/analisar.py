"""Execute da raiz: python tese/alternativas-top-necr/analisar.py."""
from pathlib import Path
import sys
import hashlib
import json
from itertools import combinations
from decimal import Decimal
import numpy as np
import pandas as pd
import plotly.express as px

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
sys.path.insert(0, str(ROOT / 'src/2_gold'))
sys.path.insert(0, str(ROOT / 'tese/scripts'))
from cap3_cobertura_top_necr import calcular_cobertura_top_necr
from cap3_taa_features import acertos_fracionarios
from financiamento_alternativo_top_necr import membership

LK = ['ano_eleicao', 'sg_uf', 'sg_partido_norm']
CK = ['ano_eleicao', 'sg_uf', 'nr_candidato']
RULES = {'top_necr': 'Top-NECr', 'nucleo_80': 'Núcleo 80%', 'acima_divisao_igual': 'Acima da divisão igualitária'}
KCOL = dict(zip(RULES, ['k_top_necr', 'k_80', 'k_acima_igual']))
checks = {}


def check(label, value):
    checks[label] = bool(value)
    assert value, label


def divide(a, b):
    return a / b if b else np.nan


def grupo_acumulado(v, limiar=80):
    """Menor k para acumular limiar% dos recursos, com empates canônicos."""
    if not 0 < limiar <= 100:
        raise ValueError('O limiar deve estar no intervalo (0, 100].')
    v = np.asarray(v, float)
    amounts = [Decimal(str(x)) for x in v]
    total = sum(amounts, Decimal(0))
    k, cumulative = 0, Decimal(0)
    if total > 0:
        target = Decimal(str(limiar)) / Decimal(100) * total
        for amount in sorted(amounts, reverse=True):
            k += 1
            cumulative += amount
            if cumulative >= target:
                break
    return membership(v, k), k


def select(v, k_top):
    """Somente recursos e k canônico; empates exatos, sem arredondar dinheiro."""
    v = np.asarray(v, float)
    # Decimal da representação round-trip: não arredonda a centavos e evita
    # classificar igualdade como superior por erro de soma binária.
    amounts = [Decimal(str(x)) for x in v]
    total = sum(amounts, Decimal(0))
    shares = np.array([float(x/total) for x in amounts]) if total > 0 else np.zeros(len(v))
    w80, k80 = grupo_acumulado(v, 80)
    return shares, {'top_necr': membership(v, k_top),
                    'nucleo_80': w80,
                    'acima_divisao_igual': np.array([int(x*len(v) > total) for x in amounts])}, k80


def evaluate(w, y):
    valid = np.isfinite(y)
    n, k, f = valid.sum(), w[valid].sum(), y[valid].sum()
    hits = w[valid] @ y[valid]
    return dict(n=n, k=k, total=f, hits=hits, expected=divide(k*f, n))


def table(d):
    return '<div class="scroll">' + d.to_html(index=False, border=0, na_rep='—', float_format=lambda x: f'{x:.3f}') + '</div>'


def main():
    source = ROOT / 'tese/resultados-exploracao-nucleo/base_analitica.csv'
    raw = ROOT / 'data/processed/rrd_df_novo.parquet'
    old_audit = json.loads((source.parent/'auditoria.json').read_text(encoding='utf-8'))
    check('Hash da base primária auditada', hashlib.sha256(raw.read_bytes()).hexdigest() == old_audit['fontes_sha256']['data/processed/rrd_df_novo.parquet'])
    d = pd.read_csv(source, float_precision='round_trip', low_memory=False)
    check('Universo 2018=7630 e 2022=9675', d.groupby('ano_eleicao').size().to_dict() == {2018:7630, 2022:9675})
    check('Chave única de candidatura', not d.duplicated(CK).any())
    major = ['n_eleicoes_'+x for x in ['prefeito','deputado_estadual','deputado_federal','governador','senador']]
    known = d[major].notna().all(axis=1) & d.voto_relevante.notna() & d.vitoria_qualquer.notna()
    d['competitivo_previo'] = (d[major].gt(0).any(axis=1) | d.voto_relevante.eq(1)).astype(float).where(known)
    canonical, national = calcular_cobertura_top_necr(pd.read_parquet(raw))
    canonical = canonical.set_index(LK)
    check('Mesmas listas da função canônica', len(canonical) == d.groupby(LK).ngroups)
    check('Recursos finitos e não negativos', np.isfinite(d.vr_receita_recursos_partidos).all() and d.vr_receita_recursos_partidos.ge(0).all())
    rows, evaluations, overlaps = [], [], []
    # Casos sintéticos exercitam fronteiras com e sem empate, igualdade e zero.
    check('Exemplo 40+25+10+8 requer quatro', select([40,25,10,8,7,5,5],3)[2] == 4)
    check('Exatos 80% requerem uma candidatura', select([80,20],1)[2] == 1)
    check('Divisão igualitária não seleciona ninguém', not select([10]*5,5)[1]['acima_divisao_igual'].any())
    check('Empate preserva menor k e pesos iguais', np.allclose(select([10]*5,5)[1]['nucleo_80'], .8))
    check('Zero produz três grupos vazios', all(w.sum()==0 for w in select([0,0],0)[1].values()))
    for keys, g in d.groupby(LK, sort=True):
        ref = canonical.loc[keys]
        v = g.vr_receita_recursos_partidos.to_numpy(float)
        c = len(g)
        check(f'Reconciliação base {keys}', c == ref.n_candidatos and np.isclose(v.sum(),ref.total_recursos_partidarios) and g.eleito.sum()==ref.n_eleitos)
        s, weights, k80 = select(v, int(ref.k_arredondado))
        ks = {r:int(round(w.sum())) for r,w in weights.items()}
        reg = dict(zip(LK,keys)) | dict(C=c, NECr=ref.NECr, total_recursos_partidarios=v.sum(), lista_sem_recursos=v.sum()==0, E=int(g.eleito.sum()))
        # A ordem dentro de empates serve apenas para exibir ranking/acumulado.
        order = g.assign(_position=np.arange(c)).sort_values(['vr_receita_recursos_partidos','nr_candidato'], ascending=[False,True])._position.to_numpy()
        rank = np.empty(c,int); rank[order] = np.arange(1,c+1)
        cum = np.empty(c); cum[order] = np.cumsum(s[order])
        for name, values in {'rank_recursos_partidarios':rank,'share_recursos_partidarios':s,'share_acumulado':cum,'share_igualitaria':1/c,'razao_share_igual':c*s,'lista_sem_recursos':v.sum()==0,'C':c,'NECr':ref.NECr}.items():
            d.loc[g.index,name] = values
        for rule,w in weights.items():
            d.loc[g.index,rule] = w
            d.loc[g.index,KCOL[rule]] = ks[rule]
            reg[KCOL[rule]] = ks[rule]
            reg['proporcao_'+rule] = ks[rule]/c
            reg['empate_corte_'+rule] = bool(((w>0)&(w<1)).any())
            check(f'Pesos e ordem {keys} {rule}', np.isclose(w.sum(),ks[rule]) and np.allclose(select(v[::-1],ks['top_necr'])[1][rule][::-1],w))
            for outcome,col in [('competitividade','competitivo_previo'),('eleicao','eleito')]:
                ev = evaluate(w,g[col].to_numpy(float))
                evaluations.append(dict(zip(LK,keys)) | dict(regra=rule,desfecho=outcome) | ev)
            if rule != 'acima_divisao_igual' and ks[rule]:
                check(f'Acertos fracionários {keys} {rule}', np.isclose(w@g.eleito.to_numpy(), acertos_fracionarios(v,g.eleito,ks[rule])))
        check(f'Top original {keys}', np.allclose(weights['top_necr'],g.top))
        if v.sum()>0:
            ordered = np.sort(v)[::-1]
            check(f'Mínimo 80% {keys}', ordered[:k80].sum() >= .8*v.sum()-1e-8 and (k80==1 or ordered[:k80-1].sum() < .8*v.sum()))
        for a,b in combinations(RULES,2):
            wa,wb = weights[a],weights[b]
            inter,union = np.minimum(wa,wb).sum(),np.maximum(wa,wb).sum()
            pair = a+'__'+b
            metrics = dict(comum=inter,uniao=union,jaccard=divide(inter,union), A_contida_B=divide(inter,ks[a]), B_contida_A=divide(inter,ks[b]), pesos_identicos=np.allclose(wa,wb), concordancia_candidaturas=1-np.abs(wa-wb).sum()/c)
            reg.update({pair+'__'+m:x for m,x in metrics.items()})
            overlaps.append(dict(zip(LK,keys)) | dict(par=pair,k_A=ks[a],k_B=ks[b],C=c,lista_sem_recursos=v.sum()==0) | metrics)
        rows.append(reg)
    lists = pd.DataFrame(rows)
    ev = pd.DataFrame(evaluations)
    summary = []
    for (year,rule,outcome),g in ev.groupby(['ano_eleicao','regra','desfecho']):
        n,k,f,h,e = g[['n','k','total','hits','expected']].sum()
        summary.append(dict(ano_eleicao=year,regra=rule,desfecho=outcome,N_valido=n,ausentes=int(d.ano_eleicao.eq(year).sum()-n),k_valido=k,total_perfil=f,observados=h,esperados_acaso=e,cobertura=divide(h,f),precisao=divide(h,k),proporcao_perfil_fora=divide(f-h,n-k),cobertura_acaso=divide(e,f),precisao_acaso=divide(e,k),proporcao_perfil_fora_acaso=divide(f-e,n-k),lift=divide(h,e)))
    summary = pd.DataFrame(summary)
    for _,r in national[national.regra_k.eq('arredondado')].iterrows():
        x = summary.query('ano_eleicao == @r.ano_eleicao and regra == "top_necr" and desfecho == "eleicao"').iloc[0]
        check(f'Reprodução nacional canônica {r.ano_eleicao}', np.allclose([x.observados,x.esperados_acaso,x.k_valido,x.total_perfil],[r.eleitos_top_necr,r.eleitos_esperados_aleatorio,r.n_posicoes_top_necr,r.eleitos_total]))
    old = pd.read_csv(ROOT/'tese/resultados-validacao-top-necr/exante_por_corte.csv')
    for _,r in old[old.Regra.eq('Arredondado')].iterrows():
        x = summary.query('ano_eleicao == @r.Ano and regra == "top_necr" and desfecho == "competitividade"').iloc[0]
        check(f'Competitividade reproduz relatório atual {r.Ano}', np.allclose([x.N_valido,x.observados,x.esperados_acaso],[r['N válido'],r['Perfil no núcleo'],r['Esperado intralista']]))
    ov = pd.DataFrame(overlaps)
    agreement = []
    for (year,pair),g in ov.groupby(['ano_eleicao','par']):
        agreement.append(dict(ano_eleicao=year,par=pair,listas=len(g),listas_sem_recursos=int(g.lista_sem_recursos.sum()),pares_vazios=int(g.uniao.eq(0).sum()),comum=g.comum.sum(),jaccard_agregado=divide(g.comum.sum(),g.uniao.sum()),jaccard_medio_listas=g.jaccard.mean(),jaccard_mediano=g.jaccard.median(),A_contida_B=divide(g.comum.sum(),g.k_A.sum()),B_contida_A=divide(g.comum.sum(),g.k_B.sum()),listas_identicas=int(g.pesos_identicos.sum()),listas_financiadas_identicas=int((g.pesos_identicos & ~g.lista_sem_recursos).sum()),concordancia_candidaturas=1-((g.uniao-g.comum).sum()/g.C.sum())))
    agreement = pd.DataFrame(agreement)
    long = lists.melt(id_vars=LK+['C'],value_vars=list(KCOL.values()),var_name='regra_k',value_name='k')
    dist = long.groupby(['ano_eleicao','regra_k']).k.describe(percentiles=[.25,.5,.75,.9]).reset_index()
    freq = long.groupby(['ano_eleicao','regra_k','k']).size().rename('listas').reset_index()
    candcols = CK+['sg_partido_norm','nm_candidato','vr_receita_recursos_partidos','C','NECr','lista_sem_recursos','rank_recursos_partidarios','share_recursos_partidarios','share_acumulado','share_igualitaria','razao_share_igual']+list(RULES)+list(KCOL.values())+['competitivo_previo','eleito']
    artifacts = {'candidaturas':d[candcols], 'listas':lists, 'resumo_nacional':summary, 'distribuicoes_k':dist, 'frequencias_k':freq, 'concordancia':agreement, 'avaliacao_por_lista':ev}
    for name,frame in artifacts.items():
        frame.to_csv(OUT/(name+'.csv'),index=False,encoding='utf-8-sig')
    d[candcols].to_parquet(OUT/'candidaturas.parquet',index=False)
    lists.to_parquet(OUT/'listas.parquet',index=False)
    parts = ['<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Alternativas ao Top-NECr</title><style>body{font:16px/1.6 system-ui;color:#18303a;background:#f4f6f8;margin:0}main{max-width:1200px;margin:auto;padding:32px}section{background:white;padding:24px;margin:20px 0;border-radius:12px}h1,h2{line-height:1.2}a{color:#126c93}.scroll{overflow:auto}table{border-collapse:collapse;font-size:13px;white-space:nowrap}td,th{padding:9px;border-bottom:1px solid #dde4e8;text-align:right}th{background:#eaf0f4}.note{border-left:4px solid #c78e31;padding:14px;background:#fff7e7}code{overflow-wrap:anywhere}li{margin:8px 0}</style><main><h1>Três regras de priorização financeira</h1><p>Deputados federais · 2018 e 2022 · Robustez da operacionalização</p>']
    parts.append('<section><h2>Resultados substantivos</h2><p>Taxas nas tabelas abaixo em porcentagem; lift em múltiplos do acaso. As avaliações usam razão de somas nacional e mantêm listas sem recursos nos denominadores.</p>')
    for outcome,title in [('competitividade','Competitividade prévia'),('eleicao','Eleição')]:
        z = summary[summary.desfecho.eq(outcome)].copy()
        z.regra = z.regra.map(RULES)
        cols = ['ano_eleicao','regra','k_valido','total_perfil','observados','esperados_acaso','cobertura','precisao','proporcao_perfil_fora','cobertura_acaso','precisao_acaso','lift','ausentes']
        for col in ['cobertura','precisao','proporcao_perfil_fora','cobertura_acaso','precisao_acaso']: z[col] *= 100
        z = z[cols].rename(columns={'ano_eleicao':'Ano','regra':'Regra','k_valido':'Posições válidas','total_perfil':'Total com perfil','observados':'Perfil no grupo','esperados_acaso':'Esperados ao acaso','cobertura':'Cobertura %','precisao':'Precisão / composição %','proporcao_perfil_fora':'Perfil fora %','cobertura_acaso':'Cobertura acaso %','precisao_acaso':'Precisão acaso %','lift':'Lift','ausentes':'Ausentes'})
        parts.append('<h3>'+title+'</h3>'+table(z))
    for year in [2018,2022]:
        parts.append(f'<h3>{year}</h3><ul>')
        for rule,label in RULES.items():
            x = summary.query('ano_eleicao == @year and regra == @rule and desfecho == "eleicao"').iloc[0]
            p = summary.query('ano_eleicao == @year and regra == @rule and desfecho == "competitividade"').iloc[0]
            parts.append(f'<li><strong>{label}:</strong> {x.k_valido:,.0f} posições; inclui {100*p.cobertura:.1f}% dos competitivos prévios. Competitivos compõem {100*p.precisao:.1f}% do grupo e {100*p.proporcao_perfil_fora:.1f}% de quem fica fora. Cobre {100*x.cobertura:.1f}% dos eleitos, com precisão de {100*x.precisao:.1f}% e lift de {x.lift:.2f} (cobertura esperada: {100*x.cobertura_acaso:.1f}%).</li>')
        parts.append('</ul>')
    parts.append('<p class="note">Cobertura e precisão respondem a perguntas diferentes. Um grupo maior pode cobrir mais eleitos e simultaneamente ter menor precisão. As três regras usam o mesmo ranking financeiro e produzem cortes aninhados; concordância é evidência de robustez da operacionalização, não validação independente, identificação de intenção partidária ou efeito causal do financiamento.</p></section>')
    fig = px.bar(freq,x='k',y='listas',color='regra_k',facet_row='ano_eleicao',barmode='group',labels={'listas':'Número de listas','k':'Tamanho do grupo','regra_k':'Regra'},height=650)
    parts.append('<section><h2>Distribuições dos tamanhos</h2><p>Cada lista tem peso igual; k=0 inclui grupos vazios. Os tamanhos fracionários somam um número inteiro de posições.</p>'+fig.to_html(full_html=False,include_plotlyjs=True)+table(dist)+'</section>')
    parts.append('<section><h2>Concordância e sobreposição</h2><p>Comum = Σ min(peso A, peso B); união = Σ max(peso A, peso B). Nos casos binários, são as contagens usuais. Jaccard agregado é a razão das somas; média e mediana atribuem peso igual a cada lista com união positiva. Jaccard de dois grupos vazios e contenção de um grupo vazio são indefinidos (—). Concordância por candidatura = 1 − Σ|A−B| / C, incluindo ausências conjuntas.</p>'+table(agreement)+'</section>')
    diagnostics = lists.groupby('ano_eleicao').agg(listas=('C','size'),candidatos=('C','sum'),sem_recursos=('lista_sem_recursos','sum'),empates_top=('empate_corte_top_necr','sum'),empates_80=('empate_corte_nucleo_80','sum')).reset_index()
    parts.append('<section><h2>Método e auditoria</h2>'+table(diagnostics)+'''<p>Base: a mesma base analítica auditada do relatório atual, reconciliada por lista com <code>calcular_cobertura_top_necr</code> e com hash da base primária <code>rrd_df_novo.parquet</code>. Recursos = <code>vr_receita_recursos_partidos</code>, origem “Recursos de partido político”; ausências seguem o tratamento zero do pipeline. Listas = partido normalizado × UF × eleição; partidos de federações/coligações não são agregados.</p>
<p>O NECr e o k do Top-NECr são importados diretamente da função canônica, sem modificação: k arredondado convencionalmente, 0,5 para cima. Núcleo 80%: menor k cujo acumulado dos recursos atinge 0,8 do total. Acima da divisão igualitária: comparação estrita sᵢ &gt; 1/C, sem tolerância que inclua igualdade.</p>
<p class="note">Preservação dos empates: Top-NECr e nucleo_80 têm valor 1 acima do corte, 0 abaixo e peso (vagas restantes / tamanho do bloco) no empate exato. Não existe um conjunto binário único nesse caso. O k_80 continua sendo o menor número inteiro de candidaturas necessário; os pesos representam a média dos possíveis desempates. Não se incluem todos os empatados, pois isso aumentaria k. A seleção acima da média é sempre binária. Ranking e acumulado exibidos usam número de candidatura crescente dentro de empates apenas para apresentação; esse desempate não define pertencimento nem resultados.</p>
<p>Sem recursos: NECr indefinido, três grupos vazios, shares e razão igualitária registrados como zero por convenção; share igualitária = 1/C. Esses zeros não representam uma divisão financeira observada. Em listas financiadas, razão_share_igual = C × sᵢ: 1 significa exatamente a parcela igualitária; acima de 1, acima da parcela; abaixo de 1, abaixo.</p>
<p>Competitividade prévia reproduz o relatório atual: vitória anterior para prefeito, deputado estadual/distrital, federal, governador ou senador, ou votação histórica ≥10% do QE. Usa também a mesma máscara de informação válida (histórico maior, voto relevante e vitória qualquer conhecidos); ausentes são explicitados. Eleito e competitividade só entram na avaliação, nunca na função de seleção.</p>
<p>Por lista: esperado = k × F/C, onde F é o total do perfil avaliado. Se o perfil está ausente, a avaliação de competitividade segue o relatório anterior: N válido e K válido substituem C e k. Nacionalmente: cobertura = Σacertos/ΣF; precisão = Σacertos/Σk; perfil fora = (ΣF−Σacertos)/(ΣC−Σk); benchmark substitui acertos pela expectativa. Lift = Σacertos/Σesperados, igual para cobertura e precisão. Não há simulação ou média simples de taxas de listas.</p>
<p>NECr, k do Top e blocos de empate preservam os floats originais do projeto. Nas duas alternativas, somas e comparações dos limiares usam Decimal da representação textual round-trip, sem arredondar a centavos: isso evita que a ordem da soma binária transforme igualdade em superioridade. Shares exportados são floats; a decisão estrita usa C × recurso &gt; total em Decimal. CSVs armazenam taxas entre 0 e 1. Contagens com pertencimento fracionário são massas de posições.</p>''')
    parts.append(f'<p><strong>{len(checks)} verificações concluídas:</strong> universo, fontes, reprodução canônica nacional e por lista, competitividade anterior, mínimo de 80%, empates, ordem das linhas, igualdade estrita e grupos vazios.</p><h3>Arquivos e reprodução</h3><p>Execute da raiz: <code>python tese/alternativas-top-necr/analisar.py</code>. O HTML é autossuficiente e funciona sem internet.</p><ul>')
    for f in [*(name+'.csv' for name in artifacts),'candidaturas.parquet','listas.parquet','analisar.py','auditoria.json']:
        parts.append(f'<li><a href="{f}">{f}</a></li>')
    parts.append('</ul></section></main></html>')
    (OUT/'relatorio.html').write_text(''.join(parts),encoding='utf-8')
    sources = [raw,source,Path(__file__),ROOT/'src/2_gold/cap3_cobertura_top_necr.py',ROOT/'src/2_gold/cap3_taa_features.py',ROOT/'tese/scripts/financiamento_alternativo_top_necr.py',ROOT/'tese/scripts/validacao_mensuracao_top_necr.py']
    (OUT/'auditoria.json').write_text(json.dumps({'checks':checks,'fontes_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},'versoes':{'python':sys.version,'numpy':np.__version__,'pandas':pd.__version__}},ensure_ascii=False,indent=2),encoding='utf-8')
    print(summary.to_string(index=False))
    print(diagnostics.to_string(index=False))
    print(f'{len(checks)} verificações OK. HTML: {OUT / "relatorio.html"}')


if __name__ == '__main__':
    main()
