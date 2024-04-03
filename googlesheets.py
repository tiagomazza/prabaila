import streamlit as st
from streamlit_gsheets import GSheetsConnection
from google.oauth2 import service_account
import json

# Carregar as credenciais do arquivo JSON
credentials = json.loads("""
{
  "type": "service_account",
  "project_id": "estoque-419114",
  "private_key_id": "f677783283e52d4a78e70d756ec39f5f0207ec8a",
  "private_key": "-----BEGIN PRIVATE KEY-----MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC/ixUhV8aQNsDcWyE59KMOJqd3oxspKRmGMQIDSfjNLgZIEbv34b3gQqPCAmTGXrWMLvqr7axBvZTEsX2zRiltUC7qg3SBHVrtYOW7+L5+pe/Qh3S1HmbLjZikgppTm9f0uqmQh9Trz3IuKwQy9UCFFYyZcKlhTSpow9r7CstTTERbymOsC9TUPnk1Nl4n+m1VEL2qjjY6JiZA...0WMAslbbRm8PqR41Zjcj8T40k9qGih2PbJLdUbfYPow7kW00miYrGZthW5luw/xY+zOyc8VJ4e0nke0P6mkrZ1gteKTIC9pcLvYKSLU0gIc9OkIHNzWE4zgtVDt9Pty6PiQFZmgSz7Y3dIQKBgQDzBdMzTqb1zssOkZS0z2hD10CI4e2WACBadot/wUnTJqBB8xwEEwzJcPZjgM1j/rns3hFKqKmAGtPpSNzP0CKwjT9OxOfWrMKFH0+evOcg1yf8t6/HmbpOGfoyR44iFxAQ5JuSzupBrnOaudTxloh66npg64zRGm+mmwXp6WUoZwKBgQDJxYWYOUHwE0HSjGH90e5M1MCEgqEaY8SDIot6pnHwGkvEO1JOxu/nUrMh21N/JW452dltlOmKEtM/sMxkIGfPNJJyBgx8LB8bfbfxs+vBJoKT3AS/f1Rbwp3icwrE38af7l1jY4Y+g2RUxM/5Co1hHx+sANMaFgryDklKZ2QnqQKBgHVuNyPvuZXFmzEq/6RvJH7DoJeENH3rCbcs2TOefsHdREsZ4kvFuMQOJcDnGFhdWhIvLEPbRCx2yjdL0gdJF7ogRpsVYsHFMSmKe7rEpRqlXNktGW9lxTTAMLnjAbdPVaAUF2jVOzUJyyrU6STkDIb4jrIOoDjagWEMP8tL0Gm5AoGAEgd0SIXVPn56AzZIC0YW5QadrTl+67y+cnlDvVHiHHI9Euu6Dw/3n9Pj7cKLU3EkyEaPBxunQo8sESTbHpdGr10jOM0RkIbgwLQbG53YEwo94LhoNDRMdWaOdQ2SiMT2GpRSA++Ar1VOQcTUUIyA1YzSZ6wrMMmHcNmV8vAKIwECgYEAy3DVVZvk5vp9bwwenoka2o+31DQgWxVUL4kiSvKdSaycLueqMtQ+Zeeq28+bm1q4/fV6ZDV7V3p/Di5ItrsQN1kYpfblyxcfZpiAvENQtHVaf3AThqVuBryKGZMZJKrxqU3Uh/si8qPELmPq/DFd4qBtb1mrK3IlM2WhevdFhg0=-----END PRIVATE KEY-----"
}
""")

# URL da planilha
url = "https://docs.google.com/spreadsheets/d/1j0iFYpsSh3JwQu9ej6g8C9oCfVseQsu2beEPvj512rw/edit#gid=0"

# Conexão com o Google Sheets
conn = GSheetsConnection("gsheets")

# Leitura dos dados da planilha
data = conn.read(spreadsheet_url=url, worksheet="Pag")

# Filtragem por modelo
modelos = data['Modelo'].unique()
modelo_filtro = st.sidebar.multiselect('Filtrar por Modelo', modelos, default=modelos)

# Verificar se 'numeros' é None e atribuir uma lista vazia se for
numeros = data['Número'].unique()
if numeros is None:
    numeros = []

# Filtragem por número
numero_filtro = st.sidebar.multiselect('Filtrar por Número', numeros, default=numeros)

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
