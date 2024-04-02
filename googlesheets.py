import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import gspread

# Recuperar as credenciais do Secret Manager
credentials = st.secrets["google_credentials"]

# URL do Google Sheets
url = "https://docs.google.com/spreadsheets/d/1j0iFYpsSh3JwQu9ej6g8C9oCfVseQsu2beEPvj512rw/edit?usp=drive_link"

# Conexão com o Google Sheets
conn = GSheetsConnection(url, service_account=credentials)

# Ler os dados do Google Sheets
data = conn.read(spreadsheet=url, usecols=[0, 1, 2, 3, 4, 5])

# Filtrar por modelo
modelos = data['Modelo'].unique()
modelo_filtro = st.sidebar.multiselect('Filtrar por Modelo', modelos, default=modelos)

# Filtrar por número
numeros = data['Número'].unique()
numero_filtro = st.sidebar.multiselect('Filtrar por Número', numeros, default=numeros)

# Aplicar os filtros
filtro = (data['Modelo'].isin(modelo_filtro)) & (data['Número'].isin(numero_filtro))
data_filtrada = data[filtro]

# Criar um DataFrame para armazenar as alterações de estoque
estoque_atualizado = data_filtrada.copy()

# Exibir os dados filtrados e permitir a atualização do estoque
for index, row in data_filtrada.iterrows():
    st.write(f"Modelo: {row['Modelo']} - Número: {row['Número']}")
    st.write(f"Descrição: {row['Descrição']}")
    st.write(f"Preço: R${row['Preço']}")
    
    # Exibir o estoque atualizado
    if index in estoque_atualizado.index:
        estoque_atualizado.loc[index, 'Estoque'] = st.number_input(
            f'Estoque atual: {row["Estoque"]}. Quantidade ({row["Modelo"]} - {row["Número"]})',
            min_value=-10, max_value=10, step=1, value=0
        )

# Adicionar um espaço para separar os elementos
st.write("")

# Adicionar um botão para atualizar o estoque
if st.button("Atualizar Estoque"):
    # Abrir o arquivo do Google Sheets
    gc = gspread.service_account_from_dict(credentials)
    spreadsheet = gc.open_by_url(url)
    worksheet = spreadsheet.get_worksheet(0)

    # Atualizar as células com os novos dados
    for i, (index, row) in enumerate(estoque_atualizado.iterrows()):
        worksheet.update_cell(index + 2, 6, row['Estoque'])

    st.success('Estoque atualizado com sucesso!')
