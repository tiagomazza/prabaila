import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import gspread
import json

# Convertendo a string de chave privada para um dicionário
credentials = json.loads("""
{
  "type": "service_account",
  "project_id": "estoque-419114",
  "private_key_id": "f677783283e52d4a78e70d756ec39f5f0207ec8a",
  "private_key": "-----BEGIN PRIVATE KEY-----MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC/ixUhV8aQNsDc
WyE59KMOJqd3oxspKRmGMQIDSfjNLgZIEbv34b3gQqPCAmTGXrWMLvqr7axBvZTE
sX2zRiltUC7qg3SBHVrtYOW7+L5+pe/Qh3S1HmbLjZikgppTm9f0uqmQh9Trz3Iu
KwQy9UCFFYyZcKlhTSpow9r7CstTTERbymOsC9TUPnk1Nl4n+m1VEL2qjjY6JiZA
ggNLlQccQ0GSZY71rqofZmVqao3Sh8anlQnurwPYcETxKse5Q24vlKNwx+39XaPc
rYminu/L+PIhvJIkaLypzFSCDHs0EPcv3S7xj+Z3Xt7RRR7MPZzyHMHjroUk8Onp
dYS2K1z/AgMBAAECggEAQAMtJp19AIkr3vidnA7Dx2DnqrXZx+GyZARQ1eSMv5VY
CBHVLbxFhoL+00GViC3yoky4/WhKnxXKeAmRJq6V/bBEXZ9c+iFjV92AKVex4gV2
pcv/FuB4HiLOFnyHMtXsUB9pt6GNaNlFIWTC3HzV+SQAfu8FzDzLpYN+1VMALG/F
6mHsJHeAP3SPjYV7v11XyzAxCtOgWMAslbbRm8PqR41Zjcj8T40k9qGih2PbJLdU
bfYPow7kW00miYrGZthW5luw/xY+zOyc8VJ4e0nke0P6mkrZ1gteKTIC9pcLvYKS
LU0gIc9OkIHNzWE4zgtVDt9Pty6PiQFZmgSz7Y3dIQKBgQDzBdMzTqb1zssOkZS0
z2hD10CI4e2WACBadot/wUnTJqBB8xwEEwzJcPZjgM1j/rns3hFKqKmAGtPpSNzP
0CKwjT9OxOfWrMKFH0+evOcg1yf8t6/HmbpOGfoyR44iFxAQ5JuSzupBrnOaudTx
loh66npg64zRGm+mmwXp6WUoZwKBgQDJxYWYOUHwE0HSjGH90e5M1MCEgqEaY8SD
Iot6pnHwGkvEO1JOxu/nUrMh21N/JW452dltlOmKEtM/sMxkIGfPNJJyBgx8LB8b
fbfxs+vBJoKT3AS/f1Rbwp3icwrE38af7l1jY4Y+g2RUxM/5Co1hHx+sANMaFgry
DklKZ2QnqQKBgHVuNyPvuZXFmzEq/6RvJH7DoJeENH3rCbcs2TOefsHdREsZ4kvF
uMQOJcDnGFhdWhIvLEPbRCx2yjdL0gdJF7ogRpsVYsHFMSmKe7rEpRqlXNktGW9l
xTTAMLnjAbdPVaAUF2jVOzUJyyrU6STkDIb4jrIOoDjagWEMP8tL0Gm5AoGAEgd0
SIXVPn56AzZIC0YW5QadrTl+67y+cnlDvVHiHHI9Euu6Dw/3n9Pj7cKLU3EkyEaP
BxunQo8sESTbHpdGr10jOM0RkIbgwLQbG53YEwo94LhoNDRMdWaOdQ2SiMT2GpRS
A++Ar1VOQcTUUIyA1YzSZ6wrMMmHcNmV8vAKIwECgYEAy3DVVZvk5vp9bwwenoka
2o+31DQgWxVUL4kiSvKdSaycLueqMtQ+Zeeq28+bm1q4/fV6ZDV7V3p/Di5ItrsQ
N1kYpfblyxcfZpiAvENQtHVaf3AThqVuBryKGZMZJKrxqU3Uh/si8qPELmPq/DFd
4qBtb1mrK3IlM2WhevdFhg0=
-----END PRIVATE KEY-----
""",



# Inserir CSS personalizado para estilização
st.markdown(
    """
    <style>
    body {
        background-color: #363636;
    }
    .css-1bnyegh-buttonContainer button {
        background-color: #f0ad4e !important;
        color: #000000 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

url = ("https://docs.google.com/spreadsheets/d/"
       "1j0iFYpsSh3JwQu9ej6g8C9oCfVseQsu2beEPvj512rw/edit?usp=drive_link")


conn = GSheetsConnection(url)

data = conn.read(spreadsheet=url, usecols=[0,1,2,3,4,5])

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

for index, row in data_filtrada.iterrows():
    st.write(f"Modelo: {row['Modelo']} - Número: {row['Número']}")
    st.write(f"Descrição: {row['Descrição']}")
    st.write(f"Preço: R${row['Preço']}")
    
    # Exibir o estoque atualizado
    if index in estoque_atualizado.index:
        estoque_atualizado.loc[index, 'Estoque'] = st.number_input(f'Estoque atual: {row["Estoque"]}. Quantidade ({row["Modelo"]} - {row["Número"]})', min_value=-10, max_value=10, step=1, value=0)

# Adicionar um espaço para separar os elementos
st.write("")

# Adicionar um espaço extra para separar os elementos
st.write("")

# Adicionar um botão para atualizar o estoque
if st.button("Atualizar Estoque"):
    # Atualizar os dados no Google Sheets apenas se houver confirmação
    # Atualizar os dados no Google Sheets
    

    # Abrir o arquivo do Google Sheets
    gc = gspread.service_account_from_dict(credentials)
    spreadsheet = gc.open_by_url(url)
    worksheet = spreadsheet.get_worksheet(0)

    # Atualizar as células com os novos dados
    for i, (index, row) in enumerate(estoque_atualizado.iterrows()):
        worksheet.update_cell(index + 2, 6, row['Estoque'])

    st.success('Estoque atualizado com sucesso!')

