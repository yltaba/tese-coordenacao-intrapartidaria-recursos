"""Regressão: origem partidária não pode ser substituída pela fonte FEFC/FP."""
import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "2_gold"))
from cap3_survival_features import (
    ORIGEM_PARTIDO, calcular_dias_maior_receita,
    selecionar_receitas_partido, tratar_df_receita, recalcular_primeiro_repasse,
)
from cap4_lift_semanal import receitas_partido_por_semana


def receitas_exemplo(ano):
    # Mesma candidatura, dia e fonte: a agregação deve preservar a origem.
    linhas = [
        ("16/08", ORIGEM_PARTIDO, "OUTROS RECURSOS", "100,00"),
        ("16/08", ORIGEM_PARTIDO, "FUNDO ESPECIAL", "50,00"),
        ("16/08", "Recursos de outros candidatos", "FUNDO ESPECIAL", "900,00"),
        ("17/08", ORIGEM_PARTIDO, "FUNDO PARTIDARIO", "120,00"),
        ("17/08", "Recursos de outros candidatos", "FUNDO PARTIDARIO", "800,00"),
        ("15/08", ORIGEM_PARTIDO, "FUNDO ESPECIAL", "500,00"),
        ("10/10", ORIGEM_PARTIDO, "FUNDO ESPECIAL", "600,00"),
    ]
    return pd.DataFrame([
        dict(ds_cargo="Deputado Federal", sg_uf="SP", sg_partido="PT",
             nr_candidato="1300", ds_origem_receita=origem,
             ds_fonte_receita=fonte, dt_receita=f"{dia}/{ano}", vr_receita=valor)
        for dia, origem, fonte, valor in linhas
    ])


class OrigemPartidariaTest(unittest.TestCase):
    def test_origem_preservada_e_qualquer_fonte_incluida(self):
        for ano in (2018, 2022):
            with self.subTest(ano=ano):
                dados = tratar_df_receita(receitas_exemplo(ano), ano)
                partido = selecionar_receitas_partido(dados)
                self.assertEqual(partido.vr_receita.sum(), 270)
                self.assertEqual(set(partido.ds_origem_receita), {ORIGEM_PARTIDO})
                maior = calcular_dias_maior_receita(partido).iloc[0]
                self.assertEqual(maior.dias_maior_receita, 0)
                self.assertEqual(maior.vr_maior_receita, 150)
                semanal = receitas_partido_por_semana(dados)
                self.assertEqual(semanal.vr_receita.sum(), 270)
                self.assertEqual(semanal.semana.tolist(), [1])

    def test_origem_2014_normalizada(self):
        dados = receitas_exemplo(2014).rename(columns={"ds_origem_receita": "tipo receita"})
        partido = selecionar_receitas_partido(tratar_df_receita(dados, 2014))
        # Em 2014 a campanha começa em julho, incluindo o repasse de 15/08.
        self.assertEqual(partido.vr_receita.sum(), 770)
        self.assertEqual(set(partido.ds_origem_receita), {ORIGEM_PARTIDO})

    def test_sigla_patriota_liga_receitas_a_candidatura_em_2018(self):
        dados = receitas_exemplo(2018).assign(sg_partido="PATRIOTA", nr_candidato="5100")
        receitas = tratar_df_receita(dados, 2018)
        rrd = pd.DataFrame([dict(ano_eleicao=2018, sg_uf="SP", sg_partido="PATRI",
                                 nr_candidato="5100", dias_desde_inicio=float("nan"),
                                 dt_receita=pd.NaT)])
        corrigido = recalcular_primeiro_repasse(rrd, receitas)
        self.assertEqual(corrigido.dias_desde_inicio.iloc[0], 0)
        self.assertEqual(corrigido.dt_receita.iloc[0], pd.Timestamp("2018-08-16"))
        self.assertTrue(rrd.dias_desde_inicio.isna().all())


if __name__ == "__main__":
    unittest.main()
