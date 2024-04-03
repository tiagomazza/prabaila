import streamlit as st
import pandas as pd
import gspread
from google.auth import service_account
import toml

# Carregue os segredos do Streamlit Cloud
secrets = st.secrets["gsheets_credentials"]

# Carregue as credenciais do arquivo TOML
credentials = service_account.Credentials.from_service_account_info({
    "type": secrets["type"],
    "project_id": secrets["project_id"],
    "private_key_id": secrets["private_key_id"],
    "private_key": secrets["private_key"],
    "client_email": secrets["client_email"],
    "client_id": secrets["client_id"],
    "auth_uri": secrets["auth_uri"],
    "token_uri": secrets["token_uri"],
    "auth_provider_x509_cert_url": secrets["auth_provider_x509_cert_url"],
    "client_x509_cert_url": secrets["client_x509_cert_url"]
})

# URL da planilha
url = "https://docs.google.com/spreadsheets/d/1j0iFYpsSh3JwQu9ej6g8C9oCfVseQsu2beEPvj512rw/edit?usp=drive_link"

# Autorize e abra a planilha
gc = gspread.authorize(credentials)
worksheet = gc.open_by_url(url).sheet1  # ou qualquer outra planilha que você tenha

# Leitura dos dados da planilha
data = worksheet.get_all_records()

# Filtragem por modelo
modelos = pd.DataFrame(data)['Modelo'].unique()
modelo_filtro = st.sidebar.multiselect('Filtrar por Modelo', modelos, default=modelos)

# Filtragem por número
numeros = pd.DataFrame(data)['Número'].unique()
numero_filtro = st.sidebar.multiselect('Filtrar por Número', numeros, default=numeros)

# Aplicação dos filtros
data_filtrada = []
for row in data:
    if row['Modelo'] in modelo_filtro and row['Número'] in numero_filtro:
        data_filtrada.append(row)

# Exibição dos dados filtrados
for row in data_filtrada:
    st.write(f"Modelo: {row['Modelo']} - Número: {row['Número']}")
    st.write(f"Descrição: {row['Descrição']}")
    st.write(f"Preço: R${row['Preço']}")

# Botão para atualizar o estoque
if st.button("Atualizar Estoque"):
    for row in data_filtrada:
        # Suponha que 'Estoque' seja a quinta coluna
        cell = worksheet.find(row['Estoque'])
        worksheet.update_cell(cell.row, cell.col, row['Estoque'])

    st.success('Estoque atualizado com sucesso!')
