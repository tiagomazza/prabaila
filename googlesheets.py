# Importações
from pathlib import Path
from typing import Dict, List

# Carregamento das credenciais
path_credentials = Path(__file__).parent / "credentials.json"
credentials = service_account.Credentials.from_service_account_file(path_credentials)

# Conexão com a planilha
gc = gspread.authorize(credentials)
worksheet = gc.open("NOME_DA_PLANILHA").sheet1

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
