import pandas as pd
import requests
import urllib.parse
import time
import re
from bs4 import BeautifulSoup
from google.colab import files

# 1. Carregar o arquivo Excel de 4 mil nomes
print("Clique no botão abaixo para carregar o seu arquivo:")
uploaded = files.upload()
nome_arquivo = list(uploaded.keys())

# 2. Ler especificamente a COLUNA 1 do Excel (índice 0)
df = pd.read_excel(nome_arquivo, header=None)
nomes_empresas = df.iloc[:, 0].dropna().astype(str).tolist()
total = len(nomes_empresas)
print(f"\nSucesso! {total} empresas carregadas da Coluna 1. Iniciando buscas...\n")

enderecos, telefones, emails = [], [], []

# Simular um navegador real para evitar bloqueios
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9"
}

# Expressões regulares para capturar dados do Brasil
regex_email = r'[a-zA-Z0-9_.-]+@[a-zA-Z0-9_.-]+\.[a-zA-Z0-9_-]+'
regex_tel = r'\(?\d{2}\)?\s?9?\d{4}[-.\s]?\d{4}'
regex_end = r'(?:Rua|Av\.|Avenida|Al\.|Alameda|Rod\.|Rodovia|Praça|Pça\.)\s[^,]+,\s?\d+'

# 3. Executar a busca de forma segura
for index, nome in enumerate(nomes_empresas):
    nome_limpo = nome.strip()
    
    if index % 10 == 0:
        print(f"Progresso: {index}/{total} empresas analisadas...")
        
    termo = f"{nome_limpo} contato telefone email endereco brasil"
    url = f"https://duckduckgo.com{urllib.parse.quote(termo)}"
    
    try:
        resposta = requests.get(url, headers=headers, timeout=8)
        if resposta.status_code == 200:
            soup = BeautifulSoup(resposta.text, 'html.parser')
            texto_pagina = soup.get_text()
            
            achou_email = re.findall(regex_email, texto_pagina)
            achou_tel = re.findall(regex_tel, texto_pagina)
            achou_end = re.findall(regex_end, texto_pagina)
            
            emails_filtrados = [e for e in achou_email if not e.endswith(('duckduckgo.com', 'w3.org', 'png', 'jpg', 'gif'))]
            
            emails.append(emails_filtrados if emails_filtrados else "Não localizado")
            telefones.append(achou_tel if achou_tel else "Não localizado")
            enderecos.append(achou_end if achou_end else "Não localizado")
        else:
            emails.append("Não localizado")
            telefones.append("Não localizado")
            enderecos.append("Não localizado")
    except:
        emails.append("Erro de conexão")
        telefones.append("Erro de conexão")
        enderecos.append("Erro de conexão")
        
    time.sleep(0.5)

# 4. Criar a nova tabela estruturada
df_resultado = pd.DataFrame({
    'Nome da Empresa': nomes_empresas,
    'Telefone Encontrado': telefones,
    'E-mail Encontrado': emails,
    'Endereço Provável': enderecos
})

# 5. Exportar o arquivo finalizado
nome_saida = "resultado_contatos_empresas.xlsx"
df_resultado.to_excel(nome_saida, index=False)
