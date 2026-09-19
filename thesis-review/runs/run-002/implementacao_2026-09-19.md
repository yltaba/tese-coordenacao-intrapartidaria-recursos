# Implementação de I-3-001 / STA-3-001 (massa não unitária na regressão intralista)

Data: 2026-09-19. Script: `tese/scripts/regressao_fracionaria_cap3.py`.

## Decisão de estimando

Mantida a **parcela original** `s_il = R_il / R_l`, com `R_l` da lista completa, que é o mesmo denominador do NECr/Top-NECr.
Candidaturas excluídas por dados faltantes saem da amostra (2018: 4 sem proporção de votos nominais t-1, 0,09% dos recursos, 2 listas; 2022: 55 sem raça/cor e 2 com CPF "-4", 0,26% dos recursos, 12 listas), e as demais **não** são renormalizadas.
Com isso, a média perfilada é a do PPML com EF de lista: `E[s_il] = m_l · p_il`, em que `m_l = Σ_i s_il` é a massa remanescente e `p_il` é o softmax entre as retidas.
Esse é o modelo que o texto já declara ("equivale a uma regressão de Poisson da parcela com efeitos fixos de lista").

A alternativa (renormalizar `s_il / m_l`, comparação só entre remanescentes) foi descartada como especificação principal.
Ela daria peso integral a listas que perderam quase toda a massa, como DF_NOVO/2022 (m = 0,095) e RJ_PTB/2022 (m = 0,101).
Fica como sensibilidade em `tese/reports/regressao-fracionaria/sensibilidade_massa.csv`.

## Mudanças no código

- `logit_condicional_fracionario`: a Hessiana usa `m·p` e os escores do sanduíche usam `s − m·p`. O gradiente não muda, porque `Xc' s` já era `Σ (s − m p) x`.
- `_ame_vec` / `_jacobiano_numerico`: os AMEs são calculados na escala da parcela original. Nas binárias, `m·[p(1) − p(0)]`; nas contínuas, `β·m·p(1−p)`.
- `montar_base`: falha se alguma lista tiver `m_l = 0` (não ocorre hoje) e registra `listas_massa_incompleta` e `massa_minima` em `amostra.csv`.
- Nova função `sensibilidade_massa`, que gera o CSV `sensibilidade_massa.csv`.

## Validação

- Os EP corrigidos reproduzem exatamente a recomputação independente do run-002 (`evidence/sta_missing_mass_correction.csv`, `handling = mass_weighted_PPML`): diferença máxima de 0,0 em β e em EP.
- β e exp(β) ficam inalterados (|Δβ| < 1e-12). A mudança fica em EP, IC e AMEs, e a comparação completa está em `evidence/impl_massa_antes_depois.csv`:
  - EP: |Δ| ≤ 0,0005
  - AME: |Δ| ≤ 0,00055 (0,055 p.p.)
  - limites de IC das razões: |Δ| ≤ 0,009
- Massa remanescente: 2 listas em 2018 (mínimo 0,816, MG_PSB) e 12 em 2022 (mínimo 0,095, DF_NOVO). Nenhuma lista tem massa zero.
- Sensibilidade (renormalização): as razões são iguais na 2ª casa decimal, exceto competitivo/R1/2022 (4,58 → 4,59) e mulher/R2/2022 (1,32 → 1,33).

## Efeito no Cap. 3 (`tese/03-medindo-coordenacao-intrapartidaria.qmd`)

Dois números mudaram no arredondamento e foram trocados no texto. O corpo foi conferido com `tools/verificar_corpo.py`, sem nenhuma outra alteração fora dos comentários.

| Onde | Antes | Depois | Fonte |
|---|---|---|---|
| sec-premio-credenciais, AME de competitivo/R1/2022 | 12,1 pontos | 12,0 pontos | `ames.csv` 0,1208 → 0,1203 |
| tbl-cap3-03-premio-magnitude, IC sup. Grande/2022 | 9,70 | 9,71 | `interacao_magnitude.csv` 9,6983 → 9,7073 |

Todos os demais números da seção seguem idênticos no arredondamento reportado: as razões por cargo, 2,89/1,70, 15%/11%, 8,16/4,58, 20,3, as razões e IC por magnitude, 1,44/1,32 e 0,74/0,93.
Negra/R2/2022 com cluster por lista tem p = 0,0285 (antes 0,0287); I-3-002 (cluster por partido) continua aberto e independe desta correção.
A figura `figs/cap3_regressao_fracionaria.png` foi regenerada; os rótulos mostram as razões, que não mudaram.

## Declaração do estimando (autor) — resolvido em 2026-09-19

O autor inseriu a declaração no parágrafo das covariáveis de `sec-premio-credenciais`; os números conferem (4 em 2018; 57 = 55 + 2 em 2022; 0,09% e 0,26%). Registro original do pendente:


Declarar no texto, em redação própria, o estimando após as exclusões.
Isto é: `s_il` mantém o denominador da lista completa, e as candidaturas excluídas por dados faltantes saem da amostra sem renormalização das demais.
Até isso ser feito, a issue ficava `accepted`. Agora está `resolved`.
