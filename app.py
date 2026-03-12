import streamlit as st
import requests
import time
import io

# Configuração da Página
st.set_page_config(page_title="Conversor ZPL para PDF Ultra", layout="centered")

# --- ÁREA DE MONETIZAÇÃO (BANNER SUPERIOR) ---
st.info("💡 **Dica de Vendedor:** Economize tempo e fita! [Veja as melhores Impressoras Térmicas em oferta na Amazon](https://sua-url-de-afiliado.com)")

st.title("📄 Conversor ZPL para PDF Gratuito")
st.write("Converta suas etiquetas da Shopee, Mercado Livre e outros com segurança.")

# --- COMPONENTE DE UPLOAD ---
arquivos_zpl = st.file_uploader("Arraste seus arquivos .zpl aqui", accept_multiple_files=True)

if arquivos_zpl:
    if st.button("Converter Agora"):
        progress_bar = st.progress(0)
        total_arquivos = len(arquivos_zpl)
        
        for idx, file in enumerate(arquivos_zpl):
            zpl_content = file.read()
            
            # Lógica de 10 tentativas adaptada do seu código 
            url = 'http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/'
            headers = {'Accept': 'application/pdf'}
            
            sucesso = False
            tentativas = 0
            
            while tentativas < 10: [cite: 2]
                try:
                    resp = requests.post(url, headers=headers, data=zpl_content)
                    
                    if resp.status_code == 200: [cite: 3]
                        # Disponibiliza o download individual
                        st.download_button(
                            label=f"⬇️ Baixar PDF - {file.name}",
                            data=resp.content,
                            file_name=f"{file.name}.pdf",
                            mime="application/pdf"
                        )
                        sucesso = True
                        break
                    
                    elif resp.status_code == 429: [cite: 5]
                        # Espera progressiva 
                        time.sleep(3 + tentativas * 2) 
                    
                    else:
                        time.sleep(1) [cite: 7]
                        
                except:
                    time.sleep(2) [cite: 7]
                
                tentativas += 1
            
            if not sucesso:
                st.error(f"Erro ao converter {file.name} após 10 tentativas.")
            
            # Atualiza barra de progresso
            progress_bar.progress((idx + 1) / total_arquivos)

# --- ÁREA DE MONETIZAÇÃO (BANNER INFERIOR E ADS) ---
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
