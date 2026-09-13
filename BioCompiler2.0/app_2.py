from collections import Counter

import pandas as pd
import streamlit as st

from biocompiler_2 import (
    BUG_BRANCH,
    BUG_CARACTERE,
    BUG_SITIO_3,
    BUG_SITIO_5,
    CAP_5,
    CORRETO,
    TAMANHO_POLI_A,
    splicing,
)

st.set_page_config(
    page_title="BioCompiler 2.0 — RNA Processor",
    page_icon="🧬",
    layout="wide",
)

ETAPAS = [
    "Bases válidas (A/U/C/G)",
    "Sítio 5′ (GU) localizado",
    "Sítio 3′ (AG) localizado após o GU",
    "Branch point (A) entre 10 e 30 nt antes do AG",
    "Splicing: íntron removido e éxons unidos",
    f"CAP 5′ ({CAP_5}) adicionada",
    f"Cauda poli-A ({TAMANHO_POLI_A} A) adicionada",
]

ETAPA_DA_FALHA = {
    BUG_CARACTERE: 0,
    BUG_SITIO_5: 1,
    BUG_SITIO_3: 2,
    BUG_BRANCH: 3,
}

SITUACAO_DO_SINAL = {"ok": "OK", "falhou": "AUSENTE", "pendente": "NÃO VERIFICADO"}

CASOS = pd.DataFrame(
    [
        {"Caso": 1, "Situação": "GU … A … AG com branch point válido", "Resposta esperada": CORRETO},
        {"Caso": 2, "Situação": "AG sem GU anterior compatível", "Resposta esperada": BUG_SITIO_5},
        {"Caso": 3, "Situação": "GU sem AG posterior compatível", "Resposta esperada": BUG_SITIO_3},
        {"Caso": 4, "Situação": "Nenhum A entre 10 e 30 nt antes do AG", "Resposta esperada": BUG_BRANCH},
    ]
)

EXEMPLO_ENTRADA = (
    "CCUAUGGCUGUAACCUUUAACUAACAAGAUGGCCUAC\n"
    "CCUAUGGCUCUAACCUUUAAACCUAACAGGAUGGCCUAC\n"
    "CCUAUGGCUGUCCUUUCCUUCCUUCCAGGAUGGCCUAC"
)


def etapas_da_sequencia(resultado_texto):
    falha = ETAPA_DA_FALHA.get(resultado_texto)
    status = []
    for i in range(len(ETAPAS)):
        if falha is None or i < falha:
            status.append("ok")
        elif i == falha:
            status.append("falhou")
        else:
            status.append("pendente")
    return status


def situacao_do_sinal(resultado_texto, bug_do_sinal):
    situacao = etapas_da_sequencia(resultado_texto)[ETAPA_DA_FALHA[bug_do_sinal]]
    return SITUACAO_DO_SINAL[situacao]


def ler_sequencias(texto):
    return [linha.strip() for linha in texto.splitlines() if linha.strip()]


def processar(sequencias):
    linhas = []
    for i, seq in enumerate(sequencias, start=1):
        resultado_texto, mrna = splicing(seq)
        linhas.append(
            {
                "linha": i,
                "entrada": seq,
                "status": "OK" if resultado_texto == CORRETO else "ERRO",
                "resultado": resultado_texto,
                "mRNA_maduro": mrna if mrna else "NÃO GERADO",
            }
        )
    return linhas


def gerar_arquivo_resultados(linhas):
    partes = ["linha;status;resultado;mRNA_maduro"]
    for l in linhas:
        partes.append(f"{l['linha']};{l['status']};{l['resultado']};{l['mRNA_maduro']}")
    return ("\n".join(partes) + "\n").encode("utf-8")


def gerar_relatorio_tela(linhas):
    partes = ["=" * 40, "BIOCOMPILER 2.0 - RNA PROCESSOR", "=" * 40]
    for l in linhas:
        partes.append(f"ENTRADA: {l['linha']}")
        if l["status"] == "OK":
            partes += [
                "STATUS: CORRETO",
                "Sítio 5': OK",
                "Branch point: OK",
                "Sítio 3': OK",
                "Splicing: OK",
                "CAP 5': ADICIONADA",
                f"Cauda poli-A: {TAMANHO_POLI_A} A",
            ]
        else:
            partes += [
                "STATUS: ERRO",
                f"DIAGNÓSTICO: {l['resultado']}",
                f"Sítio 5': {situacao_do_sinal(l['resultado'], BUG_SITIO_5)}",
                f"Branch point: {situacao_do_sinal(l['resultado'], BUG_BRANCH)}",
                f"Sítio 3': {situacao_do_sinal(l['resultado'], BUG_SITIO_3)}",
                "Splicing: NÃO REALIZADO",
                "CAP 5': NÃO ADICIONADA",
                "Cauda poli-A: NÃO ADICIONADA",
            ]
        partes.append(f"mRNA MADURO: {l['mRNA_maduro']}")
        partes.append("-" * 40)
    return "\n".join(partes)


if "linhas" not in st.session_state:
    st.session_state.linhas = None
    st.session_state.sequencias_processadas = None

st.title("🧬 BioCompiler 2.0")
st.caption("RNA Processor — reconhece o íntron no pré-mRNA, realiza o splicing e gera o mRNA maduro.")

passo_cols = st.columns(7)
etapas_topo = [
    "📄 pré-mRNA", "→", "🔎 Sinais GU · A · AG",
    "→", "✂️ Splicing · CAP 5′ · poli-A", "→", "🧬 mRNA maduro",
]
for col, texto in zip(passo_cols, etapas_topo):
    with col:
        st.markdown(f"<div style='text-align:center; padding-top:6px'>{texto}</div>", unsafe_allow_html=True)

st.divider()

with st.sidebar:
    st.header("Sobre o BioCompiler 2.0")
    st.markdown(
        "Simula, de forma didática, a **Fase II** da expressão gênica: a "
        "maturação do pré-mRNA em mRNA maduro.\n\n"
        "- **Íntron válido:** `GU … A … AG`\n"
        "- **Branch point:** um `A` entre 10 e 30 nt antes do `AG`\n"
        "- **Splicing:** remove do `GU` ao `AG` (inclusive) e une os éxons\n"
        f"- **CAP 5′:** `{CAP_5}` no início\n"
        f"- **Cauda poli-A:** {TAMANHO_POLI_A} adeninas no final"
    )

    st.header("Casos reconhecidos")
    st.dataframe(CASOS, hide_index=True, width="stretch")
    st.caption(f"Sequências com caracteres fora de A/U/C/G retornam `{BUG_CARACTERE}`.")

    st.header("Formato de entrada")
    st.markdown(
        "- Arquivo **.txt**, uma sequência de pré-mRNA por linha\n"
        "- Apenas as bases **A, U, C, G**\n"
        "- Sem espaços ou separadores internos"
    )
    st.code(EXEMPLO_ENTRADA, language=None)

st.subheader("1. Envie as sequências")
tab_arquivo, tab_texto = st.tabs(["📁 Upload de arquivo (.txt)", "✍️ Colar sequências"])

with tab_arquivo:
    arquivo = st.file_uploader("Arquivo .txt com uma sequência de pré-mRNA por linha", type=["txt"])

with tab_texto:
    texto_colado = st.text_area(
        "Uma sequência de pré-mRNA por linha",
        placeholder=EXEMPLO_ENTRADA,
        height=150,
    )

sequencias = []
origem = None
if arquivo is not None:
    try:
        sequencias = ler_sequencias(arquivo.getvalue().decode("utf-8-sig"))
        origem = "arquivo"
    except UnicodeDecodeError:
        st.error("Não foi possível ler o arquivo: ele precisa estar codificado em UTF-8.")
elif texto_colado.strip():
    sequencias = ler_sequencias(texto_colado)
    origem = "texto colado"

if sequencias:
    st.info(f"**{len(sequencias)}** sequência(s) pronta(s) para análise (origem: {origem}).")
elif origem == "arquivo":
    st.warning("O arquivo enviado não contém nenhuma sequência.")
elif arquivo is None:
    st.info("Envie um arquivo .txt ou cole as sequências acima para começar.")

st.subheader("2. Execute o processamento")
if st.button("🧬 Executar BioCompiler 2.0", type="primary", disabled=not sequencias):
    st.session_state.linhas = processar(sequencias)
    st.session_state.sequencias_processadas = sequencias

# Resultados de uma entrada anterior deixam de ser exibidos quando a entrada muda.
linhas = st.session_state.linhas
if st.session_state.sequencias_processadas != sequencias:
    linhas = None

if linhas:
    st.divider()
    st.subheader("3. Resultados")

    total = len(linhas)
    corretos = sum(1 for l in linhas if l["status"] == "OK")
    erros = total - corretos

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total analisado", total, border=True)
    m2.metric("Corretas", corretos, border=True)
    m3.metric("Com erro", erros, border=True)
    m4.metric("Taxa de sucesso", f"{corretos / total * 100:.0f}%", border=True)

    contagem = Counter(l["resultado"] for l in linhas)
    resumo_df = pd.DataFrame(
        [{"Diagnóstico": k, "Quantidade": v} for k, v in contagem.items()]
    ).sort_values("Quantidade", ascending=False)
    st.dataframe(resumo_df, hide_index=True, width="stretch")

    tabela_df = pd.DataFrame(linhas)[["linha", "entrada", "status", "resultado", "mRNA_maduro"]]
    st.dataframe(tabela_df, hide_index=True, width="stretch")

    st.download_button(
        "⬇️ Baixar resultados.txt",
        data=gerar_arquivo_resultados(linhas),
        file_name="resultados.txt",
        mime="text/plain",
        type="primary",
        on_click="ignore",
    )

    with st.expander("📄 Relatório no formato da especificação"):
        st.code(gerar_relatorio_tela(linhas), language=None, height=400)

    mostrar_detalhes = st.toggle("🔍 Mostrar diagnóstico detalhado por entrada")
    if mostrar_detalhes:
        for l in linhas:
            icone = "✅" if l["status"] == "OK" else "❌"
            with st.expander(f"{icone} Entrada {l['linha']} — {l['resultado']}"):
                st.caption("pré-mRNA")
                st.code(l["entrada"], language=None, wrap_lines=True)
                for etapa, situacao in zip(ETAPAS, etapas_da_sequencia(l["resultado"])):
                    marcador = {"ok": "✅", "falhou": "❌", "pendente": "➖"}[situacao]
                    st.markdown(f"{marcador} {etapa}")
                if l["status"] == "OK":
                    mrna = l["mRNA_maduro"]
                    exons = mrna[len(CAP_5):len(mrna) - TAMANHO_POLI_A]
                    st.success("Íntron removido, éxons unidos, CAP 5′ e cauda poli-A adicionadas.")
                    st.markdown(
                        f"**CAP 5′** `{CAP_5}` + **éxons unidos** `{exons}` + "
                        f"**cauda poli-A** {TAMANHO_POLI_A} × `A`"
                    )
                    st.code(mrna, language=None, wrap_lines=True)
                else:
                    st.error(f"mRNA maduro: {l['mRNA_maduro']}")
