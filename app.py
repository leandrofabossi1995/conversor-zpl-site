import streamlit as st
import requests
import time
import zipfile
import io
import PyPDF2

st.set_page_config(page_title="Conversor ZPL para PDF Ultra", layout="centered")

st.info("💡 **Dica de Vendedor:** Economize tempo e fita! [Veja as melhores Impressoras Térmicas em oferta na Amazon](https://sua-url-de-afiliado.com)")

st.title("📄 Conversor ZPL para PDF Gratuito")
st.write("Suba seus arquivos **.ZPL, .TXT** ou um **.ZIP** com várias etiquetas e baixe tudo em **1 ÚNICO PDF**!")

arquivos_zpl = st.file_uploader("Arraste seus arquivos aqui", accept_multiple_files=True, type=['zpl', 'txt', 'zip'])

if arquivos_zpl:
    if st.button("Converter e Juntar em 1 PDF"):
        arquivos_para_processar = []
        
        # 1. Abre os ZIPs ou lê os arquivos soltos
        for file in arquivos_zpl:
            if file.name.lower().endswith('.zip'):
                with zipfile.ZipFile(file, 'r') as z:
                    for nome_arquivo in z.namelist():
                        if nome_arquivo.lower().endswith(('.zpl', '.txt')):
                            conteudo = z.read(nome_arquivo).decode('utf-8', errors='ignore')
                            arquivos_para_processar.append({'nome': nome_arquivo, 'conteudo': conteudo})
            else:
                conteudo = file.read().decode('utf-8', errors='ignore')
                arquivos_para_processar.append({'nome': file.name, 'conteudo': conteudo})

        total_arquivos = len(arquivos_para_processar)
        
        if total_arquivos == 0:
            st.error("Nenhuma etiqueta ZPL ou TXT encontrada.")
        else:
            progress_bar = st.progress(0)
            merger = PyPDF2.PdfMerger() # Inicia o "grampeador" de PDFs
            teve_sucesso = False
            
            for idx, item in enumerate(arquivos_para_processar):
                url = 'http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/'
                headers = {'Accept': 'application/pdf'}
                
                tentativas = 0
                sucesso_neste = False
                
                while tentativas < 10:
                    try:
                        resp = requests.post(url, headers=headers, data=item['conteudo'])
                        
                        if resp.status_code == 200:
                            # Adiciona a página da etiqueta atual no PDF principal
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
                    
                if not sucesso_neste:
                    st.warning(f"Erro ao converter a etiqueta: {item['nome']}")
                    
                progress_bar.progress((idx + 1) / total_arquivos)
                
            # Se pelo menos 1 etiqueta deu certo, libera o botão de download
            if teve_sucesso:
                st.success(f"✅ {total_arquivos} etiqueta(s) processada(s) e unidas com sucesso!")
                
                # Prepara o arquivo final unificado para baixar
                pdf_final_bytes = io.BytesIO()
                merger.write(pdf_final_bytes)
                merger.close()
                pdf_final_bytes.seek(0)
                
                st.download_button(
                    label="⬇️ Baixar Todas as Etiquetas em 1 PDF",
                    data=pdf_final_bytes,
                    file_name="etiquetas_unidas.pdf",
                    mime="application/pdf",
                    type="primary" # Deixa o botão vermelho/destacado
                )

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

st.caption("Site 100% Seguro: Seus arquivos são processados e não ficam salvos em nosso servidor.")
