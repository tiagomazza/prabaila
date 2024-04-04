import os
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Carrega as credenciais do ambiente
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

# URL da planilha
url = "https://docs.google.com/spreadsheets/d/1j0iFYpsSh3JwQu9ej6g8C9oCfVseQsu2beEPvj512rw/edit#gid=0"

# Conexão com o Google Sheets
conn = GSheetsConnection("gsheets")

# Leitura dos dados da planilha
data = conn.read(
    spreadsheet_url=url,
    worksheet="Pag",
    credentials=credentials
)

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
    
    # Verificando o valor de 'Estoque' antes de passá-lo para st.number_input()
    st.write(f"Estoque: {row['Estoque']}")
    
    # Verificando se 'Estoque' é um número inteiro
    if isinstance(row['Estoque'], int):
        estoque_atualizado = st.number_input(f'Estoque atual: {row["Estoque"]}. Quantidade ({row["Modelo"]} - {row["Número"]})', min_value=-10, max_value=10, step=1, value=row['Estoque'])
    else:
        estoque_atualizado = st.number_input(f'Estoque atual: {row["Estoque"]}. Quantidade ({row["Modelo"]} - {row["Número"]})', min_value=-10, max_value=10, step=1, value=0)  # Default value
    
    data_filtrada.loc[index, 'Estoque'] = estoque_atualizado

# Botão para atualizar o estoque
if st.button("Atualizar Estoque"):
    gc = service_account.Credentials.from_service_account_info(credentials)
    spreadsheet = gc.open_by_url(url)
    worksheet = spreadsheet.worksheet("Pag")

    # Atualizar estoque em lotes de 100 linhas e 26 colunas
    batch_size = 100
    num_rows = data_filtrada.shape[0]
    num_cols = data_filtrada.shape[1]

    for i in range(0, num_rows, batch_size):
        for j in range(0, num_cols, 26):
            batch_data = data_filtrada.iloc[i:i+batch_size, j:j+26]
            if not batch_data.empty:
                start_row = i + 2  # Leva em consideração o cabeçalho
                start_col = j + 1  # Leva em consideração o cabeçalho
                cell_range = f"{worksheet.get_addr_int(start_row, start_col)}:{worksheet.get_addr_int(start_row+len(batch_data)-1, min(start_col+25, num_cols))}"
                batch_values = batch_data.values.tolist()
                worksheet.update(cell_range, batch_values)

    st.success('Estoque atualizado com sucesso!')