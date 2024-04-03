import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from google.oauth2 import service_account
import json

# Corrigindo a quebra de linha na chave privada
credentials = json.loads("""
{
  "type": "service_account",
  "project_id": "estoque-419114",
  "private_key_id": "f677783283e52d4a78e70d756ec39f5f0207ec8a",
  "private_key": "-----BEGIN PRIVATE KEY-----MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC/ixUhV8aQNsDcWyE59KMOJqd3oxspKRmGMQIDSfjNLgZIEbv34b3gQqPCAmTGXrWMLvqr7axBvZTEsX2zRiltUC7qg3SBHVrtYOW7+L5+pe/Qh3S1HmbLjZikgppTm9f0uqmQh9Trz3IuKwQy9UCFFYyZcKlhTSpow9r7CstTTERbymOsC9TUPnk1Nl4n+m1VEL2qjjY6JiZA...0WMAslbbRm8PqR41Zjcj8T40k9qGih2PbJLdUbfYPow7kW00miYrGZthW5luw/xY+zOyc8VJ4e0nke0P6mkrZ1gteKTIC9pcLvYKSLU0gIc9OkIHNzWE4zgtVDt9Pty6PiQFZmgSz7Y3dIQKBgQDzBdMzTqb1zssOkZS0z2hD10CI4e2WACBadot/wUnTJqBB8xwEEwzJcPZjgM1j/rns3hFKqKmAGtPpSNzP0CKwjT9OxOfWrMKFH0+evOcg1yf8t6/HmbpOGfoyR44iFxAQ5JuSzupBrnOaudTxloh66npg64zRGm+mmwXp6WUoZwKBgQDJxYWYOUHwE0HSjGH90e5M1MCEgqEaY8SDIot6pnHwGkvEO1JOxu/nUrMh21N/JW452dltlOmKEtM/sMxkIGfPNJJyBgx8LB8bfbfxs+vBJoKT3AS/f1Rbwp3icwrE38af7l1jY4Y+g2RUxM/5Co1hHx+sANMaFgryDklKZ2QnqQKBgHVuNyPvuZXFmzEq/6RvJH7DoJeENH3rCbcs2TOefsHdREsZ4kvFuMQOJcDnGFhdWhIvLEPbRCx2yjdL0gdJF7ogRpsVYsHFMSmKe7rEpRqlXNktGW9lxTTAMLnjAbdPVaAUF2jVOzUJyyrU6STkDIb4jrIOoDjagWEMP8tL0Gm5AoGAEgd0SIXVPn56AzZIC0YW5QadrTl+67y+cnlDvVHiHHI9Euu6Dw/3n9Pj7cKLU3EkyEaPBxunQo8sESTbHpdGr10jOM0RkIbgwLQbG53YEwo94LhoNDRMdWaOdQ2SiMT2GpRSA++Ar1VOQcTUUIyA1YzSZ6wrMMmHcNmV8vAKIwECgYEAy3DVVZvk5vp9bwwenoka2o+31DQgWxVUL4kiSvKdSaycLueqMtQ+Zeeq28+bm1q4/fV6ZDV7V3p/Di5ItrsQN1kYpfblyxcfZpiAvENQtHVaf3AThqVuBryKGZMZJKrxqU3Uh/si8qPELmPq/DFd4qBtb1mrK3IlM2WhevdFhg0=-----END PRIVATE KEY-----"
}
""")

# URL da planilha


# Conexão com o Google Sheets
conn = GSheetsConnection("gsheets")

# Leitura dos dados da planilha
data = conn.read(worksheet"Pag1")

# Filtragem por modelo
modelos = data['Modelo'].unique()
modelo_filtro = st.sidebar.multiselect('Filtrar por Modelo', modelos, default=modelos)

# Filtragem por número
numeros = data['Número'].unique()
numero_filtro = st.sidebar.multiselect('Filtrar por Número', numeros, default=numeros)

# Aplicação dos filtros
filtro = (data['Modelo'].isin(modelo_filtro)) & (data['Número'].isin(numero_filtro))
data_filtrada = data[filtro]

# DataFrame para armazenar as alterações de estoque
estoque_atualizado = data_filtrada.copy()

# Exibição dos dados e atualização do estoque
for index, row in data_filtrada.iterrows():
    st.write(f"Modelo: {row['Modelo']} - Número: {row['Número']}")
    st.write(f"Descrição: {row['Descrição']}")
    st.write(f"Preço: R${row['Preço']}")
    
    if index in estoque_atualizado.index:
        estoque_atualizado.loc[index, 'Estoque'] = st.number_input(f'Estoque atual: {row["Estoque"]}. Quantidade ({row["Modelo"]} - {row["Número"]})', min_value=-10, max_value=10, step=1, value=0)

# Botão para atualizar o estoque
if st.button("Atualizar Estoque"):
    gc = service_account.Credentials.from_service_account_info(credentials)
    spreadsheet = gc.open_by_url(url)
    worksheet = spreadsheet.get_worksheet(0)

    for i, (index, row) in enumerate(estoque_atualizado.iterrows()):
        worksheet.update_cell(index + 2, 6, row['Estoque'])

    st.success('Estoque atualizado com sucesso!')