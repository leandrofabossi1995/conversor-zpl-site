import streamlit as st
import requests
import time
import zipfile
import io
import PyPDF2

# 1. Configuração inicial da página
st.set_page_config(page_title="ZPL CONVERSOR MAX", page_icon="🖨️", layout="centered")

# 2. Inicialização da memória do sistema (Session State)
if 'processado' not in st.session_state:
    st.session_state.processado = False
if 'pdf_final' not in st.session_state:
    st.session_state.pdf_final = None
if 'reset_key' not in st.session_state:
    st.session_state.reset_key = 0

# Função para limpar tudo e voltar ao início
def resetar_sistema():
    st.session_state.processado = False
    st.session_state.pdf_final = None
    st.session_state.reset_key += 1
    st.rerun()

# 3. Visual e Estilo (CSS)
st.markdown(f"""
    <style>
    /* Esconde menus e rodapés */
    #MainMenu, footer, header {{visibility: hidden;}}
    
    /* Título Discreto */
    .titulo-max {{
        text-align: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 24px;
        font-weight: 300;
        color: #333;
        letter-spacing: 2px;
        margin-bottom: 20px;
    }}

    /* Estilo da área de Upload (Compacta) */
    section[data-testid="stFileUploadDropzone"] {{
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #ddd;
    }}
    
    /* Tradução visual do botão Browse files */
    section[data-testid="stFileUploadDropzone"] button {{
        font-size: 0px !important;
    }}
    section[data-testid="stFileUploadDropzone"] button::after {{
        content: "Selecionar Arquivos";
        font-size: 16px;
    }}

    /* Botão Converter (Azul) */
    div.stButton > button:first-child {{
        background-color: #0066cc;
        color: white;
        width: 100%;
        border-radius: 5px;
        height: 45px;
        border: none;
    }}

    /* Botão Download (Verde) */
    div.stDownloadButton > button {{
        background-color: #28a745 !important;
        color: white !important;
        width: 100%;
        border-radius: 5px;
        height: 50px;
        font-weight: bold;
        border: none;
    }}
    </style>
""", unsafe_allow_html=True)

# 4. Interface Principal
st.markdown('<p class="titulo-max">ZPL CONVERSOR MAX</p>', unsafe_allow_html=True)

# Só mostra o seletor se ainda não processamos nada
if not st.session_state.processado:
    arquivos = st.file_uploader("", accept_multiple_files=True, type=['zpl', 'txt', 'zip'], key=f"uploader_{st.session_state.reset_key}")

    if arquivos:
        if st.button("🚀 Converter para PDF Único"):
            todas_as_etiquetas = []
            
            # Lógica de extração (ZPL/TXT/ZIP)
            for f in arquivos:
                if f.name.lower().endswith('.zip'):
                    with zipfile.ZipFile(f, 'r') as z:
                        for nome in z.namelist():
                            if nome.lower().endswith(('.zpl', '.txt')):
                                texto = z.read(nome).decode('utf-8', errors='ignore')
                                partes = texto.replace('^xz', '^XZ').replace('^xa', '^XA').split('^XZ')
                                todas_as_etiquetas.extend([p + '^XZ' for p in partes if '^XA' in p])
                else:
                    texto = f.read().decode('utf-8', errors='ignore')
                    partes = texto.replace('^xz', '^XZ').replace('^xa', '^XA').split('^XZ')
                    todas_as_etiquetas.extend([p + '^XZ' for p in partes if '^XA' in p])

            if todas_as_etiquetas:
                with st.spinner("Processando etiquetas..."):
                    merger = PyPDF2.PdfMerger()
                    for zpl in todas_as_etiquetas:
                        res = requests.post('http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/', 
                                          headers={'Accept': 'application/pdf'}, data=zpl)
                        if res.status_code == 200:
                            merger.append(io.BytesIO(res.content))
                    
                    pdf_out = io.BytesIO()
                    merger.write(pdf_out)
                    merger.close()
                    pdf_out.seek(0)
                    
                    st.session_state.pdf_final = pdf_out.getvalue()
                    st.session_state.processado = True
                    st.rerun()
            else:
                st.error("Nenhuma etiqueta válida encontrada.")

# 5. Tela de Download e Limpeza
else:
    st.success("✅ Conversão concluída com sucesso!")
    st.download_button(
        label="⬇️ BAIXAR E FINALIZAR",
        data=st.session_state.pdf_final,
        file_name="etiquetas_concluidas.pdf",
        mime="application/pdf",
        on_click=resetar_sistema
    )
    if st.button("Cancelar e Voltar"):
        resetar_sistema()

# 6. Rodapé de Afiliados (Discreto)
st.markdown("---")
st.caption("📦 **Suprimentos Sugeridos:** [Impressora Térmica](LINK) | [Etiquetas 10x15](LINK)")
