"""Análise reproduzível: eleitos fora do Top-NECr e financiamento alternativo.
Execute: python tese/scripts/financiamento_alternativo_top_necr.py
"""
from pathlib import Path
import sys
import json
import hashlib
import html
import numpy as np
import pandas as pd
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'tese/resultados-financiamento-alternativo'
OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT / 'src/2_gold'))
from cap3_taa_features import _preparar, acertos_fracionarios
from cap3_cobertura_top_necr import calcular_cobertura_top_necr

KEY = ['ano_eleicao', 'sg_uf', 'nr_candidato']
LIST = ['ano_eleicao', 'sg_uf', 'sg_partido_norm']
B = 4999
checks = {}


def check(name, condition):
    checks[name] = bool(condition)
    assert condition, name


def membership(values, k):
    k = min(k, len(values))
    if k == 0:
        return np.zeros(len(values))
    cut = np.sort(values)[-k]
    above, tied = values > cut, values == cut
    return above.astype(float) + tied * ((k - above.sum()) / tied.sum())


def difference(high, inside):
    outside = 1 - inside
    return np.dot(high, outside) / outside.sum() - np.dot(high, inside) / inside.sum()


def inference(g, high, seed):
    """Cluster bootstrap; permutation restricted to elected within each list."""
    rng = np.random.default_rng(seed)
    w = g.top_arredondado.to_numpy()
    h = np.asarray(high, float)
    codes, labels = pd.factorize(pd.MultiIndex.from_frame(g[LIST]))
    indices = [np.flatnonzero(codes == i) for i in range(len(labels))]
    contributions = np.array([[np.dot(h[ix], 1-w[ix]), (1-w[ix]).sum(),
                               np.dot(h[ix], w[ix]), w[ix].sum()] for ix in indices])
    boot = []
    for _ in range(B):
        s = contributions[rng.integers(len(indices), size=len(indices))].sum(axis=0)
        if s[1] > 0 and s[3] > 0:
            boot.append(s[0]/s[1] - s[2]/s[3])
    informative = [ix for ix in indices if len(ix) > 1 and np.ptp(w[ix]) > 0 and np.ptp(h[ix]) > 0]
    # Keep fixed strata fixed; only shuffle high-resource labels in informative strata.
    sims = np.full(B, difference(h, w))
    for ix in informative:
        perm = np.array([rng.permutation(h[ix]) for _ in range(B)])
        coeff = (1-w[ix])/(1-w).sum() - w[ix]/w.sum()
        sims += perm @ coeff - h[ix] @ coeff
    obs = difference(h, w)
    null = float(sims.mean())
    return dict(diferenca=obs, ic95_inf=float(np.quantile(boot, .025)),
                ic95_sup=float(np.quantile(boot, .975)),
                n_listas=len(indices), listas_informativas=len(informative),
                eleitos_listas_informativas=sum(map(len, informative)),
                esperado_permutacao=null,
                p_bilateral=(1 + np.sum(np.abs(sims-null) >= abs(obs-null)-1e-12))/(B+1),
                p_unilateral_maior=(1 + np.sum(sims >= obs-1e-12))/(B+1))


def table(d):
    return '<div class="scroll">'+d.to_html(index=False, border=0, escape=True, float_format=lambda x: f'{x:,.3f}')+'</div>'


def main():
    raw = pd.read_parquet(ROOT / 'data/processed/rrd_df_novo.parquet')
    d = _preparar(raw[raw.ano_eleicao.isin([2018, 2022])]).reset_index(drop=True)
    check('Chaves de candidatos únicas', not d.duplicated(KEY).any())
    check('513 eleitos por ano', d.groupby('ano_eleicao').eleito.sum().eq(513).all())
    rec = pd.read_parquet(ROOT / 'data/processed/receitas.parquet')
    rec = rec[rec.ano_eleicao.isin([2018, 2022]) & rec.ds_cargo.eq('DEPUTADO FEDERAL')].copy()
    rec['categoria'] = np.select([
        rec.ds_origem_receita.eq('Recursos de partido político'),
        rec.ds_origem_receita.eq('Recursos próprios'),
        rec.ds_origem_receita.eq('Recursos de pessoas físicas'),
        rec.ds_origem_receita.isin(['Recursos de Financiamento Coletivo', 'Doações pela Internet'])],
        ['partido', 'proprios', 'pessoas_fisicas', 'coletivo_internet'], default='demais')
    sums = rec.groupby(KEY + ['categoria']).vr_receita.sum().unstack(fill_value=0).reset_index()
    d = d.merge(sums, on=KEY, how='left', validate='one_to_one')
    money = ['partido', 'proprios', 'pessoas_fisicas', 'coletivo_internet', 'demais']
    d[money] = d[money].fillna(0)
    d['nao_partidarios'] = d[['proprios', 'pessoas_fisicas', 'coletivo_internet', 'demais']].sum(axis=1)
    d['privado_proprio'] = d.proprios + d.pessoas_fisicas
    d['privado_ampliado'] = d.privado_proprio + d.coletivo_internet
    check('Receitas partidárias reconciliadas', np.allclose(d.partido, d.vr_receita_recursos_partidos))
    check('Receitas não partidárias reconciliadas', np.allclose(d.nao_partidarios, d.vr_receita_outros))
    check('Receitas não negativas e finitas', np.isfinite(d[money]).all().all() and d[money].ge(0).all().all())
    for rule in ['piso', 'arredondado', 'teto']:
        d['top_'+rule] = 0.
    for _, g in d.groupby(LIST):
        v = g.partido.to_numpy(float)
        necr = v.sum()**2 / np.square(v).sum() if v.sum() else np.nan
        d.loc[g.index, 'necr'] = necr
        d.loc[g.index, 'lista_sem_recursos'] = v.sum() == 0
        for rule, k in [('piso', np.floor(necr)), ('arredondado', np.floor(necr+.5)), ('teto', np.ceil(necr))]:
            k = max(1, int(k)) if np.isfinite(necr) else 0
            w = membership(v, k)
            d.loc[g.index, 'top_'+rule] = w
            assert np.isclose(w.sum(), min(k, len(v)))
            assert np.isclose(np.dot(w, g.eleito), acertos_fracionarios(v, g.eleito, k) if k else 0)
    check('Pesos no intervalo unitário', d.top_arredondado.between(0, 1).all())
    _, canonical = calcular_cobertura_top_necr(raw)
    for _, r in canonical.iterrows():
        x = d[d.ano_eleicao.eq(r.ano_eleicao)]
        check(f'Cobertura canônica {r.ano_eleicao} {r.regra_k}', np.isclose(np.dot(x.eleito, x['top_'+r.regra_k]), r.eleitos_top_necr))
    e = d[d.eleito.eq(1)].copy()
    thresholds, quadrants, sensitivity, tests = [], [], [], []
    for year, g in e.groupby('ano_eleicao'):
        all_year = d[d.ano_eleicao.eq(year)]
        for metric in ['nao_partidarios', 'privado_proprio', 'privado_ampliado']:
            median = g[metric].median()
            thresholds.append(dict(Ano=year, Medida=metric, Mediana_eleitos=median,
                                   P75_candidatos=all_year[metric].quantile(.75)))
            specifications = {
                'Principal: acima da mediana dos eleitos no ano': g[metric] > median,
                'Acima do P75 de todos os candidatos no ano': g[metric] > all_year[metric].quantile(.75),
                'Acima da mediana dos eleitos na UF/ano': g[metric] > g.groupby('sg_uf')[metric].transform('median'),
                'Acima do P75 dos eleitos no ano': g[metric] > g[metric].quantile(.75),
                'Mais de 50% do financiamento total': g[metric] > (g.partido + g.nao_partidarios)/2,
            }
            for label, high in specifications.items():
                for rule in ['piso', 'arredondado', 'teto']:
                    w = g['top_'+rule]
                    po, pi = np.dot(high, 1-w)/(1-w).sum(), np.dot(high, w)/w.sum()
                    sensitivity.append(dict(Ano=year, Medida=metric, Corte=label, Regra=rule,
                                            Fora_n=(1-w).sum(), Fora_alto_pct=100*po, Dentro_alto_pct=100*pi,
                                            Diferenca_pp=100*(po-pi), Razao_prevalencias=po/pi if pi else np.nan))
            high = g[metric] > median
            if metric != 'privado_ampliado':
                for status, weight in [('Dentro Top-NECr', g.top_arredondado), ('Fora Top-NECr', 1-g.top_arredondado)]:
                    for level, mask in [('Muitos', high), ('Poucos', ~high)]:
                        quadrants.append(dict(Ano=year, Medida=metric, Grupo=status, Recursos=level,
                                              N_ponderado=weight[mask].sum(), Percentual_grupo=100*weight[mask].sum()/weight.sum()))
                r = inference(g, high, int(year)+(1 if metric == 'privado_proprio' else 0))
                tests.append(dict(Ano=year, Medida=metric, **r))
            e.loc[g.index, 'alto_'+metric] = high
    q, s, t = pd.DataFrame(quadrants), pd.DataFrame(sensitivity), pd.DataFrame(tests)
    # Holm adjustment across the four prespecified two-sided tests.
    order = np.argsort(t.p_bilateral.to_numpy())
    adjusted = np.maximum.accumulate((len(t)-np.arange(len(t)))*t.p_bilateral.to_numpy()[order])
    t.loc[t.index[order], 'p_holm'] = np.minimum(1, adjusted)
    check('Quatro quadrantes somam 513', q.groupby(['Ano', 'Medida']).N_ponderado.sum().sub(513).abs().lt(1e-8).all())
    exports = {'quadrantes.csv': q, 'sensibilidade.csv': s, 'testes.csv': t, 'limiares.csv': pd.DataFrame(thresholds)}
    export_cols = KEY + ['nm_candidato','sg_partido_norm','eleito'] + money + ['nao_partidarios','privado_proprio','privado_ampliado','necr','lista_sem_recursos','top_piso','top_arredondado','top_teto']
    exports['candidatos.csv'] = d[export_cols]
    exports['eleitos.csv'] = e[export_cols+['alto_nao_partidarios','alto_privado_proprio']]
    for filename, frame in exports.items():
        frame.to_csv(OUT / filename, index=False, encoding='utf-8-sig')
    principal = s[s.Corte.str.startswith('Principal') & s.Regra.eq('arredondado') & ~s.Medida.eq('privado_ampliado')]
    print(principal.to_string(index=False))
    print(t.to_string(index=False))
    print('Empates eleitos:', e.top_arredondado.between(0,1,inclusive='neither').sum())
    print('Sem recursos:', e.assign(z=e.lista_sem_recursos.astype(int)).groupby('ano_eleicao').z.sum().to_dict())

    parts = ['''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Eleitos fora do Top-NECr · Financiamento alternativo</title><style>
:root{color-scheme:light}a,code{overflow-wrap:anywhere}body{margin:0;background:#f3f5f8;color:#172538;font:17px/1.65 system-ui,sans-serif}main{max-width:1150px;margin:auto;padding:32px 22px 80px}header{background:#142a42;color:white;padding:42px;border-radius:20px}h1{font-size:38px;line-height:1.15}h2{font-size:27px;margin-top:0}h3{font-size:20px}section{background:white;padding:30px;margin-top:24px;border-radius:15px}a{color:#126385}header a{color:#b8eafa}.lead{font-size:20px}.note{color:#526175;font-size:15px}.callout{border-left:5px solid #159783;padding:16px 22px;background:#edf8f5;margin:18px 0}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;padding:11px;border-bottom:1px solid #dee5ec}th{background:#eef3f8}nav{margin-top:25px}nav a{margin-right:18px}code{font-size:14px}details{margin:15px 0}input{padding:12px;width:min(90%,500px);margin:15px 0;border:1px solid #aab8c8;border-radius:8px}@media print{body{background:white}section{break-inside:avoid}header{color:#172538;background:white}input,nav{display:none}}@media(max-width:600px){h1{font-size:29px}header,section{padding:20px}}
</style><main><header><p>CAPÍTULO 3 / TESTE DE UMA EXPLICAÇÃO SUBSTANTIVA</p><h1>Eleitos fora do Top-NECr dispõem de financiamento alternativo?</h1><p class="lead">Comparação dos quatro quadrantes entre os 513 deputados federais eleitos em 2018 e os 513 eleitos em 2022.</p><nav><a href="#resultado">Resultados</a><a href="#testes">Testes</a><a href="#robustez">Robustez</a><a href="#casos">Candidatos</a><a href="#metodo">Método e arquivos</a></nav></header>''']
    parts.append('<section id="resultado"><h2>O que os dados mostram</h2>')
    for _, r in principal[principal.Medida.eq('privado_proprio')].iterrows():
        tt = t[t.Ano.eq(r.Ano) & t.Medida.eq(r.Medida)].iloc[0]
        direction = 'maior' if r.Diferenca_pp > 0 else 'menor'
        parts.append(f'<div class="callout"><strong>{r.Ano}: {r.Fora_alto_pct:.1f}% dos eleitos fora do núcleo têm muitos recursos privados/próprios, contra {r.Dentro_alto_pct:.1f}% dos eleitos dentro.</strong> A proporção é {direction} fora: diferença de {r.Diferenca_pp:+.1f} pontos percentuais; IC bootstrap de 95% [{100*tt.ic95_inf:.1f}; {100*tt.ic95_sup:.1f}].</div>')
    parts.append('<p>“Muitos” significa valor estritamente acima da mediana dos eleitos do mesmo ano. É uma régua exigente de comparação entre vencedores; os valores iguais à mediana ficam em “poucos”. O corte não altera o Top-NECr. As outras réguas aparecem na análise de sensibilidade.</p>')
    parts.append('<p><strong>Leitura substantiva:</strong> uma concentração maior fora do núcleo é compatível com financiamento alternativo compensando menor posição no ranking partidário. Ela não demonstra que o partido deliberadamente deixou de financiar quem já tinha recursos. As receitas são totais da campanha e não comprovam disponibilidade prévia; condicionar a análise à eleição também pode induzir associação entre as fontes.</p>')
    for metric, title in [('nao_partidarios', 'Todos os recursos não partidários'), ('privado_proprio', 'Recursos próprios + pessoas físicas')]:
        fig = go.Figure()
        for level, color in [('Muitos','#108777'), ('Poucos','#b9c8d8')]:
            z = q[q.Medida.eq(metric) & q.Recursos.eq(level)]
            fig.add_bar(name=level, x=[f'{r.Ano} · {r.Grupo}' for _,r in z.iterrows()], y=z.Percentual_grupo,
                        customdata=z.N_ponderado, marker_color=color,
                        text=[f'{v:.1f}%' for v in z.Percentual_grupo], textposition='inside',
                        hovertemplate='%{x}<br>%{y:.2f}% · n ponderado = %{customdata:.2f}<extra>%{fullData.name}</extra>')
        fig.update_layout(title=title,barmode='stack',template='plotly_white',height=390,yaxis_title='% dos eleitos no grupo',legend_orientation='h',margin=dict(l=50,r=15,t=60,b=80))
        parts.append(fig.to_html(full_html=False,include_plotlyjs=True if metric=='nao_partidarios' else False,config={'displaylogo':False,'responsive':True}))
    parts.append('<h3>Os quatro grupos: hipóteses, não intenções observadas</h3><table><tr><th></th><th>Muitos recursos não partidários</th><th>Poucos recursos não partidários</th></tr><tr><th>Dentro Top-NECr</th><td>Prioridade financeira relativa + capacidade própria</td><td>Maior dependência do financiamento partidário; o volume absoluto precisa ser observado</td></tr><tr><th>Fora Top-NECr</th><td>Financiamento alternativo; possível apoio partidário complementar</td><td>Caso mais consistente com baixa priorização financeira relativa</td></tr></table>')
    parts.append('<details><summary>Contagens e percentuais dos quatro quadrantes</summary>'+table(q)+'</details></section>')
    parts.append('<section id="testes"><h2>Testes e incerteza</h2><p>A diferença principal compara a porcentagem com muitos recursos fora e dentro do núcleo. O intervalo usa 4.999 reamostragens de nominatas completas por ano, preservando a dependência entre eleitos da mesma lista. Como a base abrange o universo observado, esses intervalos são uma análise de estabilidade sob reamostragem, não erros amostrais de uma pesquisa.</p><p>O teste de permutação redistribui a classificação de recursos entre os eleitos da mesma nominata, mantendo suas posições no Top-NECr. Testa associação além da composição entre listas, sob permutabilidade dentro de cada lista. Listas sem variação não contribuem para a permutação. O valor esperado sob essa permutação pode ser diferente de zero; por isso seu p-valor e o intervalo agregado respondem a perguntas distintas.</p>')
    display = t.copy()
    for c in ['diferenca','ic95_inf','ic95_sup','esperado_permutacao']:
        display[c] *= 100
    display = display.rename(columns={'diferenca':'Diferença (pp)','ic95_inf':'IC95 inferior (pp)','ic95_sup':'IC95 superior (pp)','esperado_permutacao':'Nulo condicionado (pp)'})
    parts.append(table(display))
    parts.append('<div class="callout"><strong>A associação agregada é compatível com a hipótese, mas a evidência dentro das nominatas é limitada.</strong> Para recursos privados/próprios, os p-valores bilaterais são 0,023 em 2018 e 0,029 em 2022; após Holm, ambos são 0,092. Nenhum dos quatro testes rejeita a hipótese nula a 5% após a correção. Apenas 19 e 15 listas, respectivamente, apresentam variação informativa para esses testes. Portanto, os resultados não estabelecem uma estratégia deliberada de substituição do financiamento partidário.</div>')
    parts.append('<p class="note">p_bilateral: desvio absoluto em relação à média das permutações. p_unilateral_maior: alternativa direcional de maior concentração fora. p_holm: correção dos quatro testes bilaterais (duas fontes × dois anos). Sementes fixas; 4.999 permutações, com correção +1. Empates do Top-NECr mantêm pesos fracionários; não se aplica Fisher/qui-quadrado a contagens fracionárias.</p></section>')
    parts.append('<section id="robustez"><h2>A conclusão depende da definição de “muitos”?</h2><p>São cruzadas três definições de financiamento, cinco cortes e três regras de arredondamento do NECr. As 90 especificações são descritivas, sem selecionar apenas as favoráveis. O critério “mais de 50% do total” mede dependência relativa e tende mecanicamente a favorecer quem recebe menos do partido; não deve substituir os testes de volume.</p>')
    parts.append(table(s[s.Regra.eq('arredondado')][['Ano','Medida','Corte','Fora_alto_pct','Dentro_alto_pct','Diferenca_pp']]))
    parts.append('<p><strong>A sensibilidade não é uniforme:</strong> em 2018 todas as especificações mantêm diferença positiva. Em 2022, algumas definições de recursos privados com corte no P75 de todos os candidatos produzem diferenças próximas de zero, inclusive levemente negativas. Essa régua relativamente baixa classifica muitos vencedores como bem financiados e reduz a discriminação. A conclusão principal não deve ser descrita como independente de qualquer corte.</p>')
    parts.append('<details><summary>Todas as regras: piso, arredondamento e teto</summary>'+table(s)+'</details><h3>Cortes em reais nominais do próprio ano</h3>'+table(pd.DataFrame(thresholds)))
    # Exclusion of zero-funded lists and ambiguous ties, without re-estimating annual thresholds.
    exclusions = []
    for year, g in e.groupby('ano_eleicao'):
        for label, mask in [('Excluir listas sem recursos', ~g.lista_sem_recursos.astype(bool)), ('Excluir empates fracionários', g.top_arredondado.isin([0,1]))]:
            x = g[mask]
            for metric in ['nao_partidarios','privado_proprio']:
                h = x['alto_'+metric].astype(float)
                exclusions.append(dict(Ano=year, Exclusao=label, Medida=metric, N=len(x), Diferenca_pp=100*difference(h,x.top_arredondado.to_numpy())))
    pd.DataFrame(exclusions).to_csv(OUT/'exclusoes.csv',index=False,encoding='utf-8-sig')
    parts.append('<h3>Listas sem financiamento e empates</h3><p>Os limiares anuais originais são mantidos nas exclusões abaixo.</p>'+table(pd.DataFrame(exclusions))+'</section>')
    cases = e[e.top_arredondado.lt(1)].copy().sort_values(['ano_eleicao','privado_proprio'],ascending=[True,False])
    cases['Peso fora'] = 1-cases.top_arredondado
    casecols = ['ano_eleicao','sg_uf','sg_partido_norm','nm_candidato','Peso fora','partido','proprios','pessoas_fisicas','nao_partidarios','alto_privado_proprio']
    parts.append('<section id="casos"><h2>Quem são os eleitos fora do núcleo?</h2><p>A tabela inclui candidatos inteiramente fora e empates com algum peso fora. Valores monetários em reais; “True” indica acima da mediana anual dos eleitos.</p><input id="search" placeholder="Filtrar por nome, UF, partido ou ano" aria-label="Filtrar candidatos"><div id="cases">'+table(cases[casecols])+'</div><h3>O exemplo Glauco</h3><p>Nenhum candidato com “Glauco” no nome está eleito neste recorte de deputados federais em 2018 e 2022. O exemplo permanece conceitual; é necessário identificar nome completo, cargo e eleição para verificá-lo empiricamente.</p></section>')
    parts.append('''<section id="metodo"><h2>Método, limites e reprodução</h2><p>Unidade: candidato a deputado federal; nominata = partido × UF × ano. NECr = (Σ recursos partidários)² / Σ recursos partidários². Regra principal: k = floor(NECr + 0,5), mínimo 1 nas listas financiadas; k = 0 nas listas sem recursos. Empatados no corte recebem peso igual à fração das vagas remanescentes no bloco. Peso fora = 1 − peso dentro. O resultado eleitoral não participa do ranking.</p><p>“Não partidários” reproduz vr_receita_outros: todas as origens diferentes de “Recursos de partido político”. Inclui outros candidatos, rendimentos e origens não identificadas, portanto não equivale a dinheiro privado. A definição estrita “privado/próprio” soma apenas recursos próprios e pessoas físicas; a ampliada acrescenta financiamento coletivo e doações pela internet. São classificações por origem registrada, sem rastrear a fonte última de cada repasse.</p><p>Receitas ausentes são tratadas como zero registrado, conforme o pipeline existente, e reconciliadas com a soma da base de receitas. Isso não demonstra ausência de subdeclaração. As comparações ocorrem dentro de cada ano, sem comparação de valores nominais entre 2018 e 2022. A mediana dos eleitos é uma régua descritiva ex post, não uma medida de informação disponível ao partido antes da eleição.</p><p>Não são identificados efeitos causais, sequência temporal, intenção partidária ou o contrafactual de vitória sem recursos alternativos. Fora do Top-NECr significa posição relativa abaixo do corte, não ausência de apoio. A unidade mantém partidos separados nas federações de 2022 e não agrega coligações de 2018, seguindo a análise original. O condicionamento aos vencedores, diferenças entre UFs e capacidade eleitoral prévia limitam a interpretação estratégica; a permutação por lista atenua apenas a composição entre nominatas.</p><h3>Arquivos auditáveis</h3><p>Execução: <code>python tese/scripts/financiamento_alternativo_top_necr.py</code>. Fontes locais: <code>data/processed/rrd_df_novo.parquet</code> e <code>data/processed/receitas.parquet</code>. O HTML incorpora os gráficos e funciona sem internet.</p>''')
    parts.append('<p>'+ ' · '.join(f'<a href="{f}">{f}</a>' for f in [*exports,'exclusoes.csv','verificacao.json'])+'</p>')
    parts.append('<h3>Verificações de consistência</h3>'+table(pd.DataFrame([{'Verificação':k,'Passou':v} for k,v in checks.items()])))
    parts.append('</section></main><script>document.getElementById("search").addEventListener("input",function(){const q=this.value.toLocaleLowerCase("pt-BR");document.querySelectorAll("#cases tbody tr").forEach(r=>r.hidden=!r.textContent.toLocaleLowerCase("pt-BR").includes(q));});</script></html>')
    report = OUT / 'financiamento-alternativo-top-necr.html'
    report.write_text(''.join(parts), encoding='utf-8')
    audit = {'checks':checks,'seed_base':'ano + 1 para privado_proprio','replicacoes':B,
             'n_candidatos':len(d),'n_eleitos':len(e),'empates_eleitos':int(e.top_arredondado.between(0,1,inclusive='neither').sum()),
             'fontes_sha256':{f:hashlib.sha256((ROOT/'data/processed'/f).read_bytes()).hexdigest() for f in ['rrd_df_novo.parquet','receitas.parquet']}}
    (OUT/'verificacao.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    print(report)


if __name__ == '__main__':
    main()
