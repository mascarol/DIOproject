from unittest.mock import Base

import pandas as pd
import os

# ==========================================
# 1. EXTRAÇÃO (Extract)
# ==========================================
print("Iniciando a extração dos dados do ecossistema Xbox...")

# DEFINE O NOME DO SEU ARQUIVO EXCEL ORIGINAL AQUI:
# Se o seu arquivo tiver outro nome (ex: 'base.xlsx'), mude o texto abaixo:
ARQUIVO_EXCEL = 'Bases.csv'

# Sistema inteligente para encontrar o arquivo onde quer que ele esteja
caminho_final = None
pastas_para_buscar = ['.', 'xbox_bases']

for pasta in pastas_para_buscar:
    caminho_teste = os.path.join(pasta, 'Bases.csv')
    if os.path.exists(caminho_teste):
        caminho_final = caminho_teste
        break

if not caminho_final:
    # Segunda tentativa caso tenha renomeado para 'base.xlsx'
    for pasta in pastas_para_buscar:
        caminho_teste = os.path.join(pasta, 'base.xlsx')
        if os.path.exists(caminho_teste):
            caminho_final = caminho_teste
            break

if not caminho_final:
    print(f"\n❌ ERRO: Não encontrei o arquivo '{Base.csv}' nem 'base.xlsx'.")
    print("Certifique-se de que o arquivo Excel está dentro da pasta 'dio.projeto' ou 'xbox_bases'.")
    exit()

# DICA DE OURO: Usamos sheet_name=1 (segunda aba) para ignorar os caracteres invisíveis do nome "Bases"
df_xbox = pd.read_excel(caminho_final, sheet_name=1)

print(f"✔️ Sucesso! Extraídos {len(df_xbox)} registros do arquivo: {caminho_final}")
print("-" * 50)


# ==========================================
# 2. TRANSFORMAÇÃO (Transform)
# ==========================================
print("Iniciando a etapa de Transformação e Limpeza...")

# 1. Correção de cabeçalhos: Remove quebras de linha '\n' ocultas nos nomes das colunas
df_xbox.columns = df_xbox.columns.str.replace('\n', ' ').str.strip()

# 2. Padronização: Garante que os nomes dos clientes comecem sempre com letra maiúscula
df_xbox['Name'] = df_xbox['Name'].astype(str).str.title()

# 3. Regra de Negócio (Segmentação): Cria uma nova coluna categorizando o valor do cliente
def categorizar_perfil_receita(valor_total):
    if valor_total >= 50:
        return 'Premium (Alto Valor)'
    elif valor_total >= 20:
        return 'Intermediário'
    else:
        return 'Essencial (Baixo Valor)'

df_xbox['Perfil_Receita'] = df_xbox['Total Value'].apply(categorizar_perfil_receita)

# 4. Indicador de Engajamento: Identifica se o cliente usa serviços adicionais (Add-ons)
df_xbox['Usa_Addons'] = df_xbox.apply(
    lambda linha: 'Sim' if (linha['EA Play Season Pass'] == 'Yes' or linha['Minecraft Season Pass'] == 'Yes') else 'Não', 
    axis=1
)

print("✔️ Transformação concluída. Novas métricas de negócio geradas!")
print("-" * 50)


# ==========================================
# 3. CARREGAMENTO (Load)
# ==========================================
print("Iniciando a etapa de Carregamento...")

# Salvando o resultado processado em um novo CSV pronto para uso
arquivo_saida = 'Bases_Processadas_Xbox.csv'
df_xbox.to_csv(arquivo_saida, index=False)

print(f"✔️ Pipeline finalizado com sucesso absoluto!")
print(f"O arquivo limpo para o seu Dashboard foi salvo em: '{arquivo_saida}'")
