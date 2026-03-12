import streamlit as st
import requests
import time
import zipfile
import io
import PyPDF2

# 1. Configuração inicial da página (Dark Mode)
st.set_page_config(page_title="ZPL CONVERSOR MAX - DARK EDITION", page_icon="🖨️", layout="centered")

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
    
    /* Fundo Dark e Fonte Profissional */
    body, .stApp {{
        background-color: #1e1e1e;
        color: #e0e0e0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}

    /* Título Discreto e Elegante */
    .titulo-max {{
        text-align: center;
        font-size: 28px;
        font-weight: 300;
        color: #00bcd4; /* Azul Neon */
        letter-spacing: 3px;
        margin-bottom: 30px;
        text-transform: uppercase;
    }}

    /* Estilo da área de Upload (Card Flutuante Compacto) */
    section[data-testid="stFileUploadDropzone"] {{
        background-color: #2d2d2d;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #444;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: 0.3s;
    }}
    section[data-testid="stFileUploadDropzone"]:hover {{
        border-color: #00bcd4;
        box-shadow: 0 6px 10px rgba(0, 188, 212, 0.2);
    }}
    
    /* Tradução visual e customização do botão Browse files */
    section[data-testid="stFileUploadDropzone"] button {{
        font-size: 0px !important;
        background-color: transparent !important;
        border: 2px solid #00bcd4 !important;
        color: #00bcd4 !important;
        border-radius: 30px !important;
        padding: 10px 20px !important;
        width: auto !important;
        margin: 10px auto !important;
        display: block !important;
    }}
    section[data-testid="stFileUploadDropzone"] button::after {{
        content: "☁️ SELECIONAR ARQUIVOS";
        font-size: 16px;
        font-weight: bold;
    }}
    section[data-testid="stFileUploadDropzone"] button:hover {{
        background-color: #00bcd4 !important;
        color: #1e1e1e !important;
    }}

    /* Estilo do Texto de Instrução (Compacto) */
    section[data-testid="stFileUploadDropzone"] p {{
        font-size: 14px;
        color: #aaa;
        text-align: center;
        margin: 5px 0;
    }}

    /* Botão Converter (Azul Neon Brilhante) */
    div.stButton > button:first-child {{
        background-color: transparent;
        color: #00bcd4;
        width: 100%;
        border-radius: 8px;
        height: 50px;
        font-size: 18px;
        font-weight: bold;
        border: 2px solid #00bcd4;
        transition: 0.3s;
        margin-top: 20px;
    }}
    div.stButton > button:first-child:hover {{
        background-color: #00bcd4;
        color: #1e1e1e;
        box-shadow: 0 0 15px rgba(0, 188, 212, 0.5);
    }}

    /* Botão Download (Verde Sucesso Brilhante) */
    div.stDownloadButton > button {{
        background-color: transparent !important;
        color: #28a745 !important;
        width: 100%;
        border-radius: 8px;
        height: 55px;
        font-size: 20px;
        font-weight: bold;
        border: 2px solid #28a745 !important;
        transition: 0.3s;
    }}
    div.stDownloadButton > button:hover {{
        background-color: #28a745 !important;
        color: white !important;
        box-shadow: 0 0 15px rgba(40, 167, 69, 0.5);
    }}

    /* Spinner e Mensagens de Erro/Sucesso */
    .stSpinner {{
        color: #00bcd4;
    }}
    .stAlert {{
        background-color: #2d2d2d;
        color: #e0e0e0;
        border-radius: 8px;
        border: 1px solid #444;
    }}

    /* Rodapé Discreto */
    .rodape-links {{
        text-align: center;
        font-size: 14px;
        color: #888;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #444;
    }}
    .rodape-links a {{
        color: #00bcd4;
        text-decoration: none;
        margin: 0 10px;
    }}
    .rodape-links a:hover {{
        text-decoration: underline;
    }}
    </style>
""", unsafe_allow_html=True)

# 4. Interface Principal
st.markdown('<p class="titulo-max">ZPL CONVERSOR MAX</p>', unsafe_allow_html=True)

# Só mostra o seletor se ainda não processamos nada
if not st.session_state.processado:
    arquivos = st.file_uploader("", accept_multiple_files=True, type=['zpl', 'txt', 'zip'], key=f"uploader_{st.session_state.reset_key}")

    if arquivos:
        if st.button("🚀 CONVERTER PARA PDF ÚNICO"):
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
    st.success("✅ Conversor concluído com sucesso!")
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
st.markdown(f"""
    <div class="rodape-links">
        📦 <b>Suprimentos Sugeridos:</b>
        <a href="LINK_DA_AMAZON_IMPRESSORA" target="_blank">Impressora Térmica</a> |
        <a href="LINK_DA_AMAZON_ETIQUETAS" target="_blank">Etiquetas 10x15</a>
    </div>
""", unsafe_allow_html=True)
st.caption("<center>🔒 Site 100% Seguro: Seus arquivos são processados na memória e não ficam salvos.</center>", unsafe_allow_html=True)
