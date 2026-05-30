import pandas as pd
import requests
import time
from google.colab import files

# 1. Carregar o arquivo original de empresas
print("Selecione a sua lista de nomes em Excel:")
uploaded = files.upload()
nome_arquivo = list(uploaded.keys())[0]

# 2. Ler a primeira coluna do Excel
df = pd.read_excel(nome_arquivo, header=None)
nomes_empresas = df.iloc[:, 0].dropna().astype(str).tolist()
total = len(nomes_empresas)
print(f"\nSucesso! {total} empresas carregadas. Buscando na base oficial do CNPJ...\n")

enderecos, telefones, emails = [], [], []

# 3. Executar a busca na API oficial de empresas do Brasil
for index, nome in enumerate(nomes_empresas):
    nome_limpo = nome.strip()
    
    if index % 20 == 0:
        print(f"Progresso: {index}/{total} empresas consultadas...")
        
    url = f"https://brasilapi.com.br{nome_limpo}"
    
    try:
        resposta = requests.get(url, timeout=10)
        if resposta.status_code == 200:
            dados = resposta.json()
            
            if isinstance(dados, list) and len(dados) > 0:
                empresa = dados[0]
            elif isinstance(dados, dict):
                empresa = dados
            else:
                empresa = {}
                
            if empresa:
                rua = empresa.get('logradouro', '')
                num = empresa.get('numero', '')
                bairro = empresa.get('bairro', '')
                cidade = empresa.get('municipio', '')
                uf = empresa.get('uf', '')
                
                enderecos.append(f"{rua}, {num} - {bairro}, {cidade}/{uf}")
                telefones.append(f"({empresa.get('ddd', '')}) {empresa.get('telefone', '')}")
                emails.append(empresa.get('email', 'Não localizado'))
            else:
                enderecos.append("Não localizado")
                telefones.append("Não localizado")
                emails.append("Não localizado")
        else:
            enderecos.append("Não localizado")
            telefones.append("Não localizado")
            emails.append("Não localizado")
            
    except:
        enderecos.append("Não localizado")
        telefones.append("Não localizado")
        emails.append("Não localizado")
        
    time.sleep(0.3)

# 4. Criar a tabela estruturada
df_resultado = pd.DataFrame({
    'Nome da Empresa': nomes_empresas,
    'Telefone Encontrado': telefones,
    'E-mail Encontrado': emails,
    'Endereço Provável': enderecos
})

# 5. Filtrar imediatamente apenas a região de Sorocaba ou DDD 15
df_sorocaba = df_resultado[
    df_resultado['Endereço Provável'].astype(str).str.contains('Sorocaba', case=False, na=False) |
    df_resultado['Telefone Encontrado'].astype(str).str.contains(r'\(?15\)?', regex=True, na=False)
]

# 6. Exportar o arquivo final limpo
nome_saida = "resultado_sorocaba_oficial.xlsx"
df_sorocaba.to_excel(nome_saida, index=False)
print(f"\nFiltro concluído! Encontradas {len(df_sorocaba)} empresas na região.")
files.download(nome_saida)
