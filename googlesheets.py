import streamlit as st
from streamlit_gsheets import GSheetsConnection

# URL da planilha
url = "https://docs.google.com/spreadsheets/d/1j0iFYpsSh3JwQu9ej6g8C9oCfVseQsu2beEPvj512rw/edit#gid=0"

# Conexão com o Google Sheets
conn = GSheetsConnection("gsheets")

st.title("Google Sheets as a DataBase")

with st.sidebar:
    modelo_filtro = st.multiselect('Filtrar por Modelo', data['Modelo'].unique())
    numero_filtro = st.multiselect('Filtrar por Número', data['Número'].unique())

# Carregar dados da planilha
data = conn.read(spreadsheet_url=url, worksheet="Pag")

# Filtrar dados com base nos filtros do usuário
filtro = (data['Modelo'].isin(modelo_filtro)) & (data['Número'].isin(numero_filtro))
data_filtrada = data[filtro]

# Mostrar os dados filtrados na interface do usuário
for index, row in data_filtrada.iterrows():
    st.write(f"Modelo: {row['Modelo']} - Número: {row['Número']}")
    st.write(f"Descrição: {row['Descrição']}")
    st.write(f"Preço: R${row['Preço']}")
    
    st.write(f"Estoque: {row['Estoque']}")
    
    if isinstance(row['Estoque'], int):
        estoque_atualizado = st.number_input(f'Estoque atual: {row["Estoque"]}. Quantidade ({row["Modelo"]} - {row["Número"]})', min_value=-10, max_value=10, step=1, value=row['Estoque'])
    else:
        estoque_atualizado = st.number_input(f'Estoque atual: {row["Estoque"]}. Quantidade ({row["Modelo"]} - {row["Número"]})', min_value=-10, max_value=10, step=1, value=0)  # Valor padrão
    
    data_filtrada.loc[index, 'Estoque'] = estoque_atualizado

# Botão para atualizar o estoque na planilha
if st.button("Atualizar Estoque"):
    conn.write(data_filtrada, spreadsheet_url=url, worksheet="Pag")
    st.success('Estoque atualizado com sucesso!')

st.divider()
st.write("CRUD Operations:")

# Tomando ações com base na entrada do usuário
if st.button("New Worksheet"):
    conn.create(worksheet="Orders", data=data)
    st.success("Planilha Criada 🎉")

if st.button("Calculate Total Orders Sum"):
    sql = 'SELECT SUM("TotalPrice") as "TotalOrdersPrice" FROM Orders;'
    total_orders = conn.query(sql=sql)
    st.dataframe(total_orders)

if st.button("Update Worksheet"):
    conn.update(worksheet="Orders", data=data)
    st.success("Planilha Atualizada 🤓")

if st.button("Clear Worksheet"):
    conn.clear(worksheet="Orders")
    st.success("Planilha Limpa 🧹")
