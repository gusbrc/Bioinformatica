import pandas as pd
import streamlit as st
from biocompiler_1 import validar_sequencia

st.set_page_config(page_title="BioCompiler 1.0", layout="wide")

st.title("BioCompiler 1.0")

formato = st.radio("Formato do campo de entrada", options=["CSV", "TXT"], horizontal=True)

df = None

if formato == "CSV":
    st.markdown(
        "Envie um arquivo CSV contendo uma coluna chamada **`entrada`** com as "
        "sequências de RNA a serem validadas."
    )
    arquivo = st.file_uploader("Arquivo CSV", type=["csv"])
 
    if arquivo is not None:
        try:
            df = pd.read_csv(arquivo, encoding="utf-8-sig")
        except Exception as e:
            st.error(f"Não foi possível ler o CSV: {e}")
            df = None
            
else:
    st.markdown(
        "Envie um arquivo TXT contendo **uma sequência de RNA por linha**, "
        "sem cabeçalho."
    )
    arquivo = st.file_uploader("Arquivo TXT", type=["txt"])
 
    if arquivo is not None:
        try:
            conteudo = arquivo.read().decode("utf-8-sig")
        except Exception as e:
            st.error(f"Não foi possível ler o TXT: {e}")
            conteudo = None
 
        if conteudo is not None:
            linhas = [linha.strip() for linha in conteudo.splitlines()]
            linhas = [linha for linha in linhas if linha]
 
            if not linhas:
                st.error("O TXT enviado está vazio ou não contém sequências válidas.")
            else:
                df = pd.DataFrame({"entrada": linhas})



if arquivo is not None:
    if df is not None:
        st.success(f"{len(df)} sequência(s) carregada(s).")

        if st.button("Executar validação"):
            status_list = []
            pre_mrna_list = []

            for RNA in df["entrada"]:
                status, pre_mRNA = validar_sequencia(str(RNA))
                status_list.append(status)
                pre_mrna_list.append(pre_mRNA if pre_mRNA else "")

            resultado = df.copy()
            resultado["status"] = status_list
            resultado["pre_mRNA"] = pre_mrna_list

            st.subheader("Resultados")
            st.dataframe(resultado, use_container_width=True)

            st.subheader("Resumo")
            contagem = resultado["status"].value_counts().reset_index()
            contagem.columns = ["status", "quantidade"]
            st.dataframe(contagem, use_container_width=True)

            csv_saida = resultado.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "Baixar resultados em CSV",
                data=csv_saida,
                file_name="biocompiler_resultados.csv",
                mime="text/csv",
            )