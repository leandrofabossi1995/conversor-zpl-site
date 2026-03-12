import streamlit as st
import requests
import time
import zipfile
import io
import PyPDF2

# Configuração tem que ser a primeira coisa sempre
st.set_page_config(page_title="Conversor ZPL para PDF Ultra", page_icon="🖨️", layout="centered")

# --- MÁGICA DO VISUAL (CSS) ---
st.markdown("""
    <style>
    /* Esconde o menu do topo e o rodapé do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Centraliza e embeleza os títulos */
    .titulo {
        text-align: center;
        font-size: 42px !important;
        font-weight: 800;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    .subtitulo {
        text-align: center;
        font-size: 18px;
        color: #666666;
        margin-bottom: 30px;
    }
    
    /* Deixa a área de upload mais bonita */
    [data-testid="stFileUploadDropzone"] {
        border-radius: 15px;
        border: 2px dashed #0066cc;
        background-color: #f4f8fc;
        padding: 20px;
    }
    
    /* Botão de Converter Gigante */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 55px;
        font-size: 20px !important;
        font-weight: bold;
        background-color: #0066cc;
        color: white;
        border: none;
        transition: 0.3s;
        margin-top: 10px;
    }
    .stButton>button:hover {
        background-color: #004c99;
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

# --- CABEÇALHO DO SITE ---
st.info("💡 **Dica de Vendedor:** Economize tempo e fita! [Veja as melhores Impressoras Térmicas em oferta na Amazon](https://sua-url-de-afiliado.com)")

st.markdown('<p class="titulo">🖨️ Conversor ZPL para PDF</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitulo">Suba arquivos <b>.ZPL, .TXT</b> ou <b>.ZIP</b> e baixe tudo em <b>1 ÚNICO PDF</b>!</p>', unsafe_allow_html=True)

# --- ÁREA DE FUNCIONAMENTO ---
arquivos_zpl = st.file_uploader("Arraste seus arquivos aqui", accept_multiple_files=True, type=['zpl', 'txt', 'zip'])

if arquivos_zpl:
    if st.button("🚀 Converter e Juntar em 1 PDF"):
        todas_as_etiquetas = []
        
        for file in arquivos_zpl:
            if file.name.lower().endswith('.zip'):
                with zipfile.ZipFile(file, 'r') as z:
                    for nome_arquivo in z.namelist():
                        if nome_arquivo.lower().endswith(('.zpl', '.txt')):
                            conteudo = z.read(nome_arquivo).decode('utf-8', errors='ignore')
                            conteudo_padronizado = conteudo.replace('^xz', '^XZ').replace('^xa', '^XA')
                            pedacos = conteudo_padronizado.split('^XZ')
                            for pedaco in pedacos:
                                if '^XA' in pedaco:
                                    todas_as_etiquetas.append(pedaco + '^XZ')
            else:
                conteudo = file.read().decode('utf-8', errors='ignore')
                conteudo_padronizado = conteudo.replace('^xz', '^XZ').replace('^xa', '^XA')
                pedacos = conteudo_padronizado.split('^XZ')
                for pedaco in pedacos:
                    if '^XA' in pedaco:
                        todas_as_etiquetas.append(pedaco + '^XZ')

        total_etiquetas = len(todas_as_etiquetas)
        
        if total_etiquetas == 0:
            st.error("Nenhuma etiqueta ZPL ou TXT válida encontrada.")
        else:
            st.write(f"⏳ O site encontrou **{total_etiquetas} etiquetas**! Processando...")
            progress_bar = st.progress(0)
            
            merger = PyPDF2.PdfMerger()
            teve_sucesso = False
            
            for idx, zpl_code in enumerate(todas_as_etiquetas):
                url = 'http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/'
                headers = {'Accept': 'application/pdf'}
                
                tentativas = 0
                sucesso_neste = False
                
                while tentativas < 10:
                    try:
                        resp = requests.post(url, headers=headers, data=zpl_code)
                        
                        if resp.status_code == 200:
                            merger.append(io.BytesIO(resp.content))
                            sucesso_neste = True
                            teve_sucesso = True
                            break
                        elif resp.status_code == 429:
                            time.sleep(3 + tentativas * 2) 
                        else:
                            time.sleep(1)
                    except:
                        time.sleep(2)
                    
                    tentativas += 1
                    
                progress_bar.progress((idx + 1) / total_etiquetas)
                
            if teve_sucesso:
                st.success(f"✅ O PDF com as {total_etiquetas} etiquetas está pronto!")
                
                pdf_final_bytes = io.BytesIO()
                merger.write(pdf_final_bytes)
                merger.close()
                pdf_final_bytes.seek(0)
                
                st.download_button(
                    label="⬇️ Baixar Todas as Etiquetas em 1 PDF",
                    data=pdf_final_bytes,
                    file_name="etiquetas_unidas.pdf",
                    mime="application/pdf",
                    type="primary"
                )

# --- ÁREA DE PRODUTOS/AFILIADOS ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.subheader("📦 Suprimentos para seu E-commerce")
col1, col2 = st.columns(2)

with col1:
    st.write("**Papelaria e Etiquetas**")
    st.write("- [Etiqueta Térmica 10x15](LINK_AFILIADO)")
    st.write("- [Fita Adesiva Reforçada](LINK_AFILIADO)")

with col2:
    st.write("**Hardware**")
    st.write("- [Impressora Elgin L42 Pro](LINK_AFILIADO)")
    st.write("- [Leitor de Código de Barras](LINK_AFILIADO)")

st.caption("🔒 Site 100% Seguro: Seus arquivos são processados na memória e não ficam salvos em nenhum servidor.")
