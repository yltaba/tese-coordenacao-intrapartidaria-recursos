"""Script de validação preditiva do NECr — equivalente ao notebook 3_validacao_preditiva_necr.ipynb."""
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from scipy.stats import spearmanr, kendalltau
import warnings
warnings.filterwarnings('ignore')

pd.set_option('display.float_format', '{:.3f}'.format)

# ── 1. Cadeiras conquistadas ──────────────────────────────────────────────────
print("=" * 70)
print("1. CADEIRAS CONQUISTADAS")
print("=" * 70)

res = pd.read_parquet('data/processed/resultados.parquet')
ANOS_ALVO = [2014, 2018, 2022]

frames = []
for ano in ANOS_ALVO:
    r = res[
        (res.ano_eleicao == ano) &
        (res.ds_cargo == 'Deputado Federal') &
        (res.nr_turno == 1)
    ].drop_duplicates(subset=['nr_candidato', 'sg_partido', 'sg_uf'])

    eleito_mask = (
        ~r['ds_sit_tot_turno'].isin(['SUPLENTE']) &
        ~r['ds_sit_tot_turno'].str.startswith('N')
    )
    cadeiras = (
        r[eleito_mask]
        .groupby(['sg_partido', 'sg_uf'])
        .size()
        .reset_index(name='cadeiras')
        .assign(ano_eleicao=ano)
    )
    frames.append(cadeiras)

seats = pd.concat(frames, ignore_index=True)
check = seats.groupby('ano_eleicao')['cadeiras'].sum()
print('Cadeiras totais por ano (deve ser 513 cada):')
print(check.to_string())

# ── 2. NECr por lista ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("2. NECr POR LISTA")
print("=" * 70)

# 2018/2022 via rrd
rrd = pd.read_parquet('data/processed/rrd_df_novo.parquet')

def agg_rrd(g):
    total = g['vr_receita_recursos_partidos'].sum()
    if total == 0:
        return pd.Series({'NECr': np.nan, 'vr_total': 0.0, 'n_cands': len(g)})
    props = g['vr_receita_recursos_partidos'] / total
    sum_sq = (props ** 2).sum()
    return pd.Series({
        'NECr':     (1 / sum_sq) if sum_sq > 0 else np.nan,
        'vr_total': total,
        'n_cands':  len(g),
    })

necr_1822 = (
    rrd[rrd.ano_eleicao.isin([2018, 2022])]
    .groupby(['ano_eleicao', 'sg_partido', 'sg_uf'], observed=True)
    .apply(agg_rrd, include_groups=False)
    .reset_index()
)
print(f'2018/2022: {len(necr_1822)} listas')

# 2014 via receitas
rec = pd.read_parquet('data/processed/receitas.parquet')
r14 = rec[
    (rec.ano_eleicao == 2014) &
    (rec.ds_cargo == 'DEPUTADO FEDERAL') &
    rec['ds_origem_receita'].str.startswith('Recursos de partido') &
    (rec['dt_receita'] <= pd.Timestamp('2014-10-05'))
].copy()

total_lista = (
    r14.groupby(['sg_partido', 'sg_uf'])['vr_receita']
    .sum().reset_index().rename(columns={'vr_receita': 'vr_total_lista'})
)
cand_rec = (
    r14.groupby(['sg_partido', 'sg_uf', 'nr_candidato'])['vr_receita']
    .sum().reset_index().rename(columns={'vr_receita': 'vr_cand'})
)
cand_rec = cand_rec.merge(total_lista, on=['sg_partido', 'sg_uf'])
cand_rec['prop'] = cand_rec['vr_cand'] / cand_rec['vr_total_lista']

def agg14(g):
    sum_sq = (g['prop'] ** 2).sum()
    return pd.Series({
        'NECr':     (1 / sum_sq) if sum_sq > 0 else np.nan,
        'vr_total': g['vr_cand'].sum(),
        'n_cands':  len(g),
    })

necr_14 = (
    cand_rec
    .groupby(['sg_partido', 'sg_uf'])
    .apply(agg14, include_groups=False)
    .reset_index()
    .assign(ano_eleicao=2014)
)
print(f'2014: {len(necr_14)} listas')

necr_all = pd.concat([necr_14, necr_1822], ignore_index=True)
necr_all['log_vr_total'] = np.log1p(necr_all['vr_total'])

# ── 3. Bancada anterior ────────────────────────────────────────────────────────
ban = pd.read_csv('data/processed/bancada_partido_uf.csv')

# 2010 para B_prev de 2014
r10 = res[
    (res.ano_eleicao == 2010) &
    (res.ds_cargo == 'Deputado Federal') &
    (res.nr_turno == 1)
].drop_duplicates(subset=['nr_candidato', 'sg_partido', 'sg_uf'])

eleito10 = r10[
    ~r10['ds_sit_tot_turno'].isin(['SUPLENTE']) &
    ~r10['ds_sit_tot_turno'].str.startswith('N')
]
ban10 = (
    eleito10
    .groupby(['sg_partido', 'sg_uf'])
    .size().reset_index(name='n_deputados')
    .assign(ano_eleicao=2010)
)

ban_full = pd.concat([ban10, ban], ignore_index=True)
ano_prev_map = {2014: 2010, 2018: 2014, 2022: 2018}

frames_prev = []
for ano_alvo, ano_prev in ano_prev_map.items():
    sub = ban_full[ban_full.ano_eleicao == ano_prev][['sg_partido', 'sg_uf', 'n_deputados']].copy()
    sub['ano_eleicao'] = ano_alvo
    sub = sub.rename(columns={'n_deputados': 'bancada_prev'})
    frames_prev.append(sub)

bprev = pd.concat(frames_prev, ignore_index=True)

# ── 4. Dataset analítico ───────────────────────────────────────────────────────
df = necr_all.merge(seats, on=['ano_eleicao', 'sg_partido', 'sg_uf'], how='left')
df['cadeiras'] = df['cadeiras'].fillna(0)
df = df.merge(bprev, on=['ano_eleicao', 'sg_partido', 'sg_uf'], how='left')
df['bancada_prev'] = df['bancada_prev'].fillna(0)

vagas = pd.read_parquet('data/processed/vagas_deputado_federal.parquet')
df = df.merge(vagas[['ano_eleicao', 'sg_uf', 'qt_vaga']], on=['ano_eleicao', 'sg_uf'], how='left')
df = df[df['NECr'].notna()].copy()

print("\n" + "=" * 70)
print("4. DATASET ANALÍTICO")
print("=" * 70)
print(df.groupby('ano_eleicao').agg(
    n_listas=('NECr', 'count'),
    cadeiras_total=('cadeiras', 'sum'),
    NECr_mediana=('NECr', 'median'),
    bprev_mediana=('bancada_prev', 'median'),
).round(2).to_string())

# ── 5. Correlações ─────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("5. CORRELAÇÕES DE PEARSON")
print("=" * 70)
for ano in ANOS_ALVO:
    sub = df[df.ano_eleicao == ano]
    r_necr  = sub['NECr'].corr(sub['cadeiras'])
    r_bprev = sub['bancada_prev'].corr(sub['cadeiras'])
    r_logvr = sub['log_vr_total'].corr(sub['cadeiras'])
    r_necr_bprev = sub['NECr'].corr(sub['bancada_prev'])
    print(f'{ano}:  NECr×S={r_necr:.3f}  B_prev×S={r_bprev:.3f}  '
          f'logVR×S={r_logvr:.3f}  NECr×B_prev={r_necr_bprev:.3f}')

# ── 6. Modelos OLS ─────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("6. AJUSTE IN-SAMPLE (OLS, erros HC3)")
print("=" * 70)

resultados_modelos = []
for ano in ANOS_ALVO:
    sub = df[df.ano_eleicao == ano].dropna(subset=['NECr', 'bancada_prev', 'cadeiras', 'log_vr_total'])
    y = sub['cadeiras'].values
    for label, xvars in [
        ('(1) NECr',           ['NECr']),
        ('(2) B_prev',         ['bancada_prev']),
        ('(3) B_prev+NECr+VR', ['bancada_prev', 'NECr', 'log_vr_total']),
    ]:
        X = sm.add_constant(sub[xvars].values)
        model = sm.OLS(y, X).fit(cov_type='HC3')
        yhat = model.fittedvalues
        resultados_modelos.append({
            'Ano': ano, 'Modelo': label, 'N': len(sub),
            'R²': model.rsquared, 'R²_adj': model.rsquared_adj,
            'MAE': mean_absolute_error(y, yhat),
            'RMSE': root_mean_squared_error(y, yhat),
        })

tab_modelos = pd.DataFrame(resultados_modelos)
print(tab_modelos.round(3).to_string(index=False))

# Coeficientes modelo (3)
print("\n--- Coeficientes modelo (3) completo ---")
for ano in ANOS_ALVO:
    sub = df[df.ano_eleicao == ano].dropna(subset=['NECr', 'bancada_prev', 'cadeiras', 'log_vr_total'])
    y = sub['cadeiras'].values
    X = sm.add_constant(sub[['bancada_prev', 'NECr', 'log_vr_total']].values)
    model = sm.OLS(y, X).fit(cov_type='HC3')
    coef = model.params
    pval = model.pvalues
    nomes = ['const', 'bancada_prev', 'NECr', 'log_vr_total']
    print(f'\n{ano} (N={len(sub)}, R²={model.rsquared:.3f}):')
    for i, v in enumerate(nomes):
        stars = '***' if pval[i] < 0.001 else '**' if pval[i] < 0.01 else '*' if pval[i] < 0.05 else '  '
        print(f'  {v:<15} b={coef[i]:+.4f}  p={pval[i]:.3f} {stars}')

# ── 7. Calibração cardinal ─────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("7. CALIBRAÇÃO CARDINAL: E[cadeiras | NECr ≈ k]")
print("=" * 70)
df['NECr_round'] = df['NECr'].round(0).clip(1, 20)
for ano in ANOS_ALVO:
    sub = df[(df.ano_eleicao == ano) & (df['NECr_round'] <= 12)]
    cal = (
        sub.groupby('NECr_round')
        .agg(n=('cadeiras', 'count'),
             cadeiras_media=('cadeiras', 'mean'),
             cadeiras_mediana=('cadeiras', 'median'))
        .reset_index()
    )
    cal['razao_S_NECr'] = cal['cadeiras_media'] / cal['NECr_round']
    print(f'\n{ano}:')
    print(cal[cal.n >= 3].round(2).to_string(index=False))

# ── 8. Validação cruzada temporal ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("8. VALIDAÇÃO CRUZADA TEMPORAL (OUT-OF-SAMPLE)")
print("=" * 70)

oos_results = []
pairs = [(2018, 2022), (2022, 2018), (2014, 2018), (2018, 2014)]

for train_ano, test_ano in pairs:
    train = df[df.ano_eleicao == train_ano].dropna(
        subset=['NECr', 'bancada_prev', 'cadeiras', 'log_vr_total']
    )
    test = df[df.ano_eleicao == test_ano].dropna(
        subset=['NECr', 'bancada_prev', 'cadeiras', 'log_vr_total']
    )
    for label, xvars in [
        ('(1) NECr',           ['NECr']),
        ('(2) B_prev',         ['bancada_prev']),
        ('(3) B_prev+NECr+VR', ['bancada_prev', 'NECr', 'log_vr_total']),
    ]:
        Xtr = sm.add_constant(train[xvars].values, has_constant='add')
        Xte = sm.add_constant(test[xvars].values,  has_constant='add')
        model = sm.OLS(train['cadeiras'].values, Xtr).fit()
        yhat = Xte @ model.params
        y    = test['cadeiras'].values
        oos_results.append({
            'Treino→Teste': f'{train_ano}→{test_ano}',
            'Modelo': label,
            'MAE_oos':  mean_absolute_error(y, yhat),
            'RMSE_oos': root_mean_squared_error(y, yhat),
        })

tab_oos = pd.DataFrame(oos_results)
print(tab_oos.round(3).to_string(index=False))

# ── 9. Validade ordinal ────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("9. VALIDADE ORDINAL (Spearman ρ, Kendall τ)")
print("=" * 70)
for ano in ANOS_ALVO:
    sub = df[df.ano_eleicao == ano].dropna(subset=['NECr', 'bancada_prev', 'cadeiras'])
    s_necr,  _ = spearmanr(sub['NECr'],         sub['cadeiras'])
    s_bprev, _ = spearmanr(sub['bancada_prev'],  sub['cadeiras'])
    k_necr,  _ = kendalltau(sub['NECr'],         sub['cadeiras'])
    k_bprev, _ = kendalltau(sub['bancada_prev'],  sub['cadeiras'])
    print(f'{ano}:')
    print(f'  NECr   — Spearman ρ={s_necr:.3f}, Kendall τ={k_necr:.3f}')
    print(f'  B_prev — Spearman ρ={s_bprev:.3f}, Kendall τ={k_bprev:.3f}')

print("\n" + "=" * 70)
print("CONCLUÍDO")
print("=" * 70)
