import streamlit as st
import requests
import time

st.set_page_config(page_title="Conversor ZPL para PDF Ultra", layout="centered")

st.info("💡 **Dica de Vendedor:** Economize tempo e fita! [Veja as melhores Impressoras Térmicas em oferta na Amazon](https://sua-url-de-afiliado.com)")

st.title("📄 Conversor ZPL para PDF Gratuito")
st.write("Converta suas etiquetas da Shopee, Mercado Livre e outros com segurança.")

arquivos_zpl = st.file_uploader("Arraste seus arquivos .zpl aqui", accept_multiple_files=True)

# 1. Botão de Converter
if arquivos_zpl:
    if st.button("Converter Agora"):
        # Cria uma "memória" temporária para guardar os PDFs prontos
        st.session_state['pdfs_prontos'] = []
        progress_bar = st.progress(0)
        
        for idx, file in enumerate(arquivos_zpl):
            # O .decode('utf-8') garante que o arquivo não vá como "letras estranhas"
            zpl_content = file.read().decode('utf-8', errors='ignore')
            
            url = 'http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/'
            headers = {'Accept': 'application/pdf'}
            
            tentativas = 0
            sucesso = False
            
            while tentativas < 10:
                try:
                    resp = requests.post(url, headers=headers, data=zpl_content)
                    
                    if resp.status_code == 200:
                        # Salva o PDF pronto na memória em vez de mostrar o botão logo de cara
                        st.session_state['pdfs_prontos'].append({
                            'nome': f"{file.name}.pdf",
                            'dados': resp.content
                        })
                        sucesso = True
                        break
                    elif resp.status_code == 429:
                        time.sleep(3 + tentativas * 2) 
                    else:
                        time.sleep(1)
                except:
                    time.sleep(2)
                
                tentativas += 1
                
            if not sucesso:
                st.error(f"Erro ao converter {file.name}")
                
            progress_bar.progress((idx + 1) / len(arquivos_zpl))
            
        st.success("✅ Conversão finalizada com sucesso!")

# 2. Mostra os botões de Download FORA do botão de converter (Segurança do Streamlit)
if 'pdfs_prontos' in st.session_state:
    st.write("### Seus arquivos estão prontos:")
    for pdf in st.session_state['pdfs_prontos']:
        st.download_button(
            label=f"⬇️ Baixar {pdf['nome']}",
            data=pdf['dados'],
            file_name=pdf['nome'],
            mime="application/pdf"
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
