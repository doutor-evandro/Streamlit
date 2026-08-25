"""Geracao da base de exemplo do painel.

Este modulo existe para separar "de onde vem o dado" de "como o dado e
exibido". Quando voce tiver dados reais, basta reescrever a funcao
`carregar_execucoes` para ler um Excel, um CSV ou um banco de dados --
o arquivo main.py continua funcionando sem nenhuma alteracao.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# Cada robo tem um perfil proprio: com que frequencia roda, quanto tempo
# leva, quanto ele economiza e qual a chance de dar problema.
ROBOS = {
    "Conciliacao bancaria": dict(exec_dia=4, dur_media=95, economia=22, p_falha=0.05),
    "Emissao de notas": dict(exec_dia=9, dur_media=38, economia=7, p_falha=0.03),
    "Backup de planilhas": dict(exec_dia=2, dur_media=210, economia=15, p_falha=0.08),
    "Relatorio diario": dict(exec_dia=1, dur_media=140, economia=45, p_falha=0.02),
    "Importacao de pedidos": dict(exec_dia=6, dur_media=72, economia=12, p_falha=0.11),
}

STATUS = ["Sucesso", "Alerta", "Falha"]


def carregar_execucoes(dias: int = 90, semente: int = 42) -> pd.DataFrame:
    """Devolve um DataFrame com o historico de execucoes dos robos.

    A `semente` fixa o sorteio: rodando de novo, os numeros sao os mesmos.
    Isso evita que os graficos mudem a cada atualizacao da pagina.
    """
    rng = np.random.default_rng(semente)
    fim = pd.Timestamp.today().normalize()
    inicio = fim - pd.Timedelta(days=dias - 1)

    linhas = []
    for dia in pd.date_range(inicio, fim, freq="D"):
        # Fim de semana tem menos movimento que dia util.
        fator_dia = 0.35 if dia.weekday() >= 5 else 1.0

        for robo, perfil in ROBOS.items():
            n = rng.poisson(perfil["exec_dia"] * fator_dia)

            for _ in range(int(n)):
                # Sorteia o desfecho da execucao.
                p_falha = perfil["p_falha"]
                status = rng.choice(STATUS, p=[1 - p_falha - 0.06, 0.06, p_falha])

                # Execucao que falha costuma parar no meio: dura menos.
                dur = abs(rng.normal(perfil["dur_media"], perfil["dur_media"] * 0.25))
                if status == "Falha":
                    dur *= 0.4

                itens = int(abs(rng.normal(120, 45)))
                if status == "Falha":
                    itens = int(itens * 0.3)

                linhas.append(
                    {
                        "data": dia,
                        "hora": int(rng.integers(0, 24)),
                        "robo": robo,
                        "status": status,
                        "duracao_seg": round(dur, 1),
                        "itens": itens,
                        # So economiza tempo a execucao que chegou ao fim.
                        "min_economizados": 0 if status == "Falha" else perfil["economia"],
                    }
                )

    df = pd.DataFrame(linhas)
    return df.sort_values(["data", "hora"]).reset_index(drop=True)
