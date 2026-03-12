import streamlit as st
import requests
import time
import zipfile

st.set_page_config(page_title="Conversor ZPL para PDF Ultra", layout="centered")

st.info("💡 **Dica de Vendedor:** Economize tempo e fita! [Veja as melhores Impressoras Térmicas em oferta na Amazon](https://sua-url-de-afiliado.com)")

st.title("📄 Conversor ZPL para PDF Gratuito")
st.write("Suba seus arquivos **.ZPL, .TXT** ou até mesmo um **.ZIP** com várias etiquetas!")

# Agora aceita ZIP e TXT também
arquivos_zpl = st.file_uploader("Arraste seus arquivos aqui", accept_multiple_files=True, type=['zpl', 'txt', 'zip'])

if arquivos_zpl:
    if st.button("Converter Agora"):
        st.session_state['pdfs_prontos'] = []
        
        # 1. Primeiro vamos ler todos os arquivos (descompactar os ZIPs se houver)
        arquivos_para_processar = []
        
        for file in arquivos_zpl:
            if file.name.lower().endswith('.zip'):
                # Se for ZIP, abre e extrai os arquivos lá de dentro
                with zipfile.ZipFile(file, 'r') as z:
                    for nome_arquivo in z.namelist():
                        if nome_arquivo.lower().endswith(('.zpl', '.txt')):
                            conteudo = z.read(nome_arquivo).decode('utf-8', errors='ignore')
                            arquivos_para_processar.append({'nome': nome_arquivo, 'conteudo': conteudo})
            else:
                # Se for ZPL ou TXT normal, só lê o texto
                conteudo = file.read().decode('utf-8', errors='ignore')
                arquivos_para_processar.append({'nome': file.name, 'conteudo': conteudo})

        # 2. Agora processamos tudo o que encontramos
        total_arquivos = len(arquivos_para_processar)
        
        if total_arquivos == 0:
            st.error("Nenhuma etiqueta ZPL ou TXT encontrada dentro do arquivo.")
        else:
            progress_bar = st.progress(0)
            
            for idx, item in enumerate(arquivos_para_processar):
                url = 'http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/'
                headers = {'Accept': 'application/pdf'}
                
                tentativas = 0
                sucesso = False
                
                while tentativas < 10:
                    try:
                        resp = requests.post(url, headers=headers, data=item['conteudo'])
                        
                        if resp.status_code == 200:
                            st.session_state['pdfs_prontos'].append({
                                'nome': f"{item['nome']}.pdf",
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
                    st.error(f"Erro ao converter {item['nome']}")
                    
                progress_bar.progress((idx + 1) / total_arquivos)
                
            st.success(f"✅ {total_arquivos} arquivo(s) convertido(s) com sucesso!")

# 3. Mostra os botões de Download
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
