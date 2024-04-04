import streamlit as st
from streamlit_gsheets import GSheetsConnection
from google.oauth2 import service_account
import os

# Ler as credenciais do ambiente
credentials = {
    "type": os.environ.get("GSHEETS_TYPE"),
    "project_id": os.environ.get("GSHEETS_PROJECT_ID"),
    "private_key_id": os.environ.get("GSHEETS_PRIVATE_KEY_ID"),
    "private_key": os.environ.get("GSHEETS_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.environ.get("GSHEETS_CLIENT_EMAIL"),
    "client_id": os.environ.get("GSHEETS_CLIENT_ID"),
    "auth_uri": os.environ.get("GSHEETS_AUTH_URI"),
    "token_uri": os.environ.get("GSHEETS_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.environ.get("GSHEETS_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.environ.get("GSHEETS_CLIENT_X509_CERT_URL")
}

# Conectar-se ao Google Sheets
gc = service_account.Credentials.from_service_account_info(credentials)

# URL da planilha
url = os.environ.get("GSHEETS_SPREADSHEET")

# Conexão com o Google Sheets
conn = GSheetsConnection("gsheets")

# Leitura dos dados da planilha
data = conn.read(spreadsheet_url=url, worksheet=os.environ.get("GSHEETS_WORKSHEET"))

# Filtragem por modelo
modelos = data['Modelo'].unique()
modelo_filtro = st.sidebar.multiselect('Filtrar por Modelo', modelos, default=modelos)

# Filtragem por número
numeros = data['Número'].unique()
default_numeros = [numero for numero in numeros if numero in numeros]
numero_filtro = st.sidebar.multiselect('Filtrar por Número', numeros, default=default_numeros)

# Aplicação dos filtros
filtro = (data['Modelo'].isin(modelo_filtro)) & (data['Número'].isin(numero_filtro))
data_filtrada = data[filtro]

# Exibição dos dados e atualização do estoque
for index, row in data_filtrada.iterrows():
    st.write(f"Modelo: {row['Modelo']} - Número: {row['Número']}")
    st.write(f"Descrição: {row['Descrição']}")
    st.write(f"Preço: R${row['Preço']}")
    st.write(f"Estoque: {row['Estoque']}")
    
    # Atualizar estoque
    novo_estoque = st.number_input(f'Estoque atual: {row["Estoque"]}. Quantidade ({row["Modelo"]} - {row["Número"]})', min_value=-10, max_value=10, step=1, value=row['Estoque'])
    data_filtrada.loc[index, 'Estoque'] = novo_estoque

# Botão para atualizar o estoque
if st.button("Atualizar Estoque"):
    spreadsheet = gc.open_by_url(url)
    worksheet = spreadsheet.worksheet(os.environ.get("GSHEETS_WORKSHEET"))

    # Atualizar estoque em lotes de 100 linhas
    batch_size = 100
    for i in range(0, data_filtrada.shape[0], batch_size):
        batch_data = data_filtrada.iloc[i:i+batch_size]
        batch_values = batch_data.values.tolist()
        start_row = i + 2  # Leva em consideração o cabeçalho
        cell_range = f"A{start_row}:Z{start_row + len(batch_data)}"
        worksheet.update(cell_range, batch_values)

    st.success('Estoque atualizado com sucesso!')
