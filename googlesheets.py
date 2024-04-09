import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from gspread_dataframe import set_with_dataframe
import datetime

# Carregar as credenciais do arquivo JSON
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

# Conectar com o Google Sheets
gc = gspread.authorize(credentials)

# Abrir a planilha
sh = gc.open_by_key("<ID_da_planilha>")

# Escolher a aba "Shoes" e converter para DataFrame
existing_data = pd.DataFrame(sh.worksheet("Shoes").get_all_records())

# Filtros
st.sidebar.header("Filtros")
modelos_filtro = st.sidebar.multiselect("Filtrar por Modelo", existing_data["Modelo"].unique(), existing_data["Modelo"].unique())
numeros_filtro = st.sidebar.multiselect("Filtrar por Número", existing_data["Número"].unique(), existing_data["Número"].unique())

# Aplicar filtros
filtered_data = existing_data[
    (existing_data["Modelo"].isin(modelos_filtro)) & 
    (existing_data["Número"].isin(numeros_filtro))
]

# Mostrar o total de estoque
total_stock = filtered_data["Estoque"].sum()
st.sidebar.header("Total de Estoque")
st.sidebar.write(str(total_stock).split('.')[0])  # Mostrar estoque sem .0

# Atualizar estoque
if st.sidebar.button("Atualizar Estoque"):
    # Atualizar a planilha "Shoes"
    sh.worksheet("Shoes").update([filtered_data.columns.values.tolist()] + filtered_data.values.tolist())
    st.success("Estoque atualizado com sucesso!")

# Adicionar campo de texto
st.sidebar.header("Registrar Venda")
modelo = st.sidebar.selectbox("Modelo", filtered_data["Modelo"].unique())
numero = st.sidebar.selectbox("Número", filtered_data[filtered_data["Modelo"] == modelo]["Número"].unique())
quantidade = st.sidebar.number_input("Quantidade", value=1, min_value=1)
texto = st.sidebar.text_input("Informações adicionais", "")

# Registrar a venda
if st.sidebar.button("Registrar Venda"):
    # Obter a data e hora atual
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Criar registro de venda
    venda = {
        "Modelo": [modelo],
        "Número": [numero],
        "Quantidade": [quantidade],
        "Data/Hora": [current_datetime],
        "Texto": [texto]
    }
    
    # Adicionar registro de venda à planilha "Vendas"
    venda_df = pd.DataFrame(venda)
    set_with_dataframe(sh.worksheet("Vendas"), venda_df, include_index=False, include_column_header=False)
    st.success("Venda registrada com sucesso!")
