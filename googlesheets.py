import streamlit as st
from streamlit_gsheets import GSheetsConnection
from google.oauth2 import service_account

# URL da planilha
url = "https://docs.google.com/spreadsheets/d/1j0iFYpsSh3JwQu9ej6g8C9oCfVseQsu2beEPvj512rw/edit#gid=0"

# Conexão com o Google Sheets
conn = GSheetsConnection("gsheets")

# Leitura dos dados da planilha
data = conn.read(spreadsheet_url=url, worksheet="Pag")

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
    
    estoque_atualizado = st.number_input(f'Estoque atual: {row["Estoque"]}. Quantidade ({row["Modelo"]} - {row["Número"]})', min_value=-10, max_value=10, step=1, value=row['Estoque'])

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
