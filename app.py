import streamlit as st
import requests
import zipfile
import io
import PyPDF2

# 1. Configuração inicial da página (Dark Mode)
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

# 3. Visual e Estilo (CSS - Dark Mode Elegante)
st.markdown(f"""
    <style>
    /* Esconde menus e rodapés nativos */
    #MainMenu, footer, header {{visibility: hidden;}}
    
    /* Fundo Dark */
    body, .stApp {{
        background-color: #121212;
        color: #e0e0e0;
    }}

    /* Título Neon */
    .titulo-max {{
        text-align: center;
        font-size: 32px;
        font-weight: 700;
        color: #00e5ff;
        letter-spacing: 2px;
        margin-bottom: 10px;
    }}

    /* Estilo das Colunas de Instrução */
    .instrucao-card {{
        text-align: center;
        padding: 10px;
        border-radius: 10px;
        background: #1e1e1e;
        border: 1px solid #333;
    }}
    .instrucao-icon {{
        font-size: 24px;
        margin-bottom: 5px;
    }}
    .instrucao-texto {{
        font-size: 14px;
        color: #bbb;
    }}

    /* Customização do Uploader para Português */
    section[data-testid="stFileUploadDropzone"] {{
        background-color: #1e1e1e;
        border: 2px dashed #333;
        border-radius: 15px;
        padding: 20px;
    }}
    
    /* Esconde o texto original em inglês e insere o novo */
    section[data-testid="stFileUploadDropzone"] button {{
        font-size: 0px !important;
    }}
    section[data-testid="stFileUploadDropzone"] button::after {{
        content: "SELECIONAR ARQUIVOS";
        font-size: 16px;
        font-weight: bold;
        color: #00e5ff;
    }}
    
    /* Botão Converter (Azul Neon) */
    div.stButton > button:first-child {{
        background-color: transparent;
        color: #00e5ff;
        width: 100%;
        border-radius: 10px;
        height: 50px;
        border: 2px solid #00e5ff;
        font-weight: bold;
        transition: 0.3s;
    }}
    div.stButton > button:first-child:hover {{
        background-color: #00e5ff;
        color: #121212;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.4);
    }}

    /* Botão Download (Verde) */
    div.stDownloadButton > button {{
        background-color: #28a745 !important;
        color: white !important;
        width: 100%;
        border-radius: 10px;
        height: 60px;
        font-size: 20px;
        font-weight: bold;
        border: none;
    }}
    </style>
""", unsafe_allow_html=True)

# 4. Cabeçalho e Instruções
st.markdown('<p class="titulo-max">ZPL CONVERSOR MAX</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="instrucao-card"><div class="instrucao-icon">📁</div><div class="instrucao-texto">1. Envie seus ZPL ou ZIP</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="instrucao-card"><div class="instrucao-icon">⚙️</div><div class="instrucao-texto">2. Clique em Converter</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="instrucao-card"><div class="instrucao-icon">✅</div><div class="instrucao-texto">3. Baixe o PDF Único</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 5. Interface de Upload
if not st.session_state.processado:
    arquivos = st.file_uploader("", accept_multiple_files=True, type=['zpl', 'txt', 'zip'], key=f"uploader_{st.session_state.reset_key}")

    if arquivos:
        if st.button("🚀 INICIAR CONVERSÃO"):
            todas_as_etiquetas = []
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
                with st.spinner("Gerando PDF..."):
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

# 6. Finalização e Reset
else:
    st.success("Tudo pronto! Seu PDF foi gerado.")
    st.download_button(
        label="⬇️ BAIXAR PDF E LIMPAR TELA",
        data=st.session_state.pdf_final,
        file_name="etiquetas_concluidas.pdf",
        mime="application/pdf",
        on_click=resetar_sistema
    )
    if st.button("Voltar"):
        resetar_sistema()

# Rodapé Discreto
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("<center>📦 <b>Suprimentos:</b> <a href='#'>Impressora Térmica</a> | <a href='#'>Etiquetas 10x15</a></center>", unsafe_allow_html=True)
