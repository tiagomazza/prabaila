import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from google.oauth2 import service_account

# Segredo do Google Sheets
secret_info = {
  "type": "service_account",
  "project_id": "estoque-419114",
  "private_key_id": "f677783283e52d4a78e70d756ec39f5f0207ec8a",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC/ixUhV8aQNsDc\nWyE59KMOJqd3oxspKRmGMQIDSfjNLgZIEbv34b3gQqPCAmTGXrWMLvqr7axBvZTE\nsX2zRiltUC7qg3SBHVrtYOW7+L5+pe/Qh3S1HmbLjZikgppTm9f0uqmQh9Trz3Iu\nKwQy9UCFFYyZcKlhTSpow9r7CstTTERbymOsC9TUPnk1Nl4n+m1VEL2qjjY6JiZA\nggNLlQccQ0GSZY71rqofZmVqao3Sh8anlQnurwPYcETxKse5Q24vlKNwx+39XaPc\nrYminu/L+PIhvJIkaLypzFSCDHs0EPcv3S7xj+Z3Xt7RRR7MPZzyHMHjroUk8Onp\ndYS2K1z/AgMBAAECggEAQAMtJp19AIkr3vidnA7Dx2DnqrXZx+GyZARQ1eSMv5VY\nCBHVLbxFhoL+00GViC3yoky4/WhKnxXKeAmRJq6V/bBEXZ9c+iFjV92AKVex4gV2\npcv/FuB4HiLOFnyHMtXsUB9pt6GNaNlFIWTC3HzV+SQAfu8FzDzLpYN+1VMALG/F\n6mHsJHeAP3SPjYV7v11XyzAxCtOgWMAslbbRm8PqR41Zjcj8T40k9qGih2PbJLdU\nbfYPow7kW00miYrGZthW5luw/xY+zOyc8VJ4e0nke0P6mkrZ1gteKTIC9pcLvYKS\nLU0gIc9OkIHNzWE4zgtVDt9Pty6PiQFZmgSz7Y3dIQKBgQDzBdMzTqb1zssOkZS0\nz2hD10CI4e2WACBadot/wUnTJqBB8xwEEwzJcPZjgM1j/rns3hFKqKmAGtPpSNzP\n0CKwjT9OxOfWrMKFH0+evOcg1yf8t6/HmbpOGfoyR44iFxAQ5JuSzupBrnOaudTx\nloh66npg64zRGm+mmwXp6WUoZwKBgQDJxYWYOUHwE0HSjGH90e5M1MCEgqEaY8SD\nIot6pnHwGkvEO1JOxu/nUrMh21N/JW452dltlOmKEtM/sMxkIGfPNJJyBgx8LB8b\nfbfxs+vBJoKT3AS/f1Rbwp3icwrE38af7l1jY4Y+g2RUxM/5Co1hHx+sANMaFgry\nDklKZ2QnqQKBgHVuNyPvuZXFmzEq/6RvJH7DoJeENH3rCbcs2TOefsHdREsZ4kvF\nuMQOJcDnGFhdWhIvLEPbRCx2yjdL0gdJF7ogRpsVYsHFMSmKe7rEpRqlXNktGW9l\nxTTAMLnjAbdPVaAUF2jVOzUJyyrU6STkDIb4jrIOoDjagWEMP8tL0Gm5AoGAEgd0\nSIXVPn56AzZIC0YW5QadrTl+67y+cnlDvVHiHHI9Euu6Dw/3n9Pj7cKLU3EkyEaP\nBxunQo8sESTbHpdGr10jOM0RkIbgwLQbG53YEwo94LhoNDRMdWaOdQ2SiMT2GpRS\nA++Ar1VOQcTUUIyA1YzSZ6wrMMmHcNmV8vAKIwECgYEAy3DVVZvk5vp9bwwenoka\n2o+31DQgWxVUL4kiSvKdSaycLueqMtQ+Zeeq28+bm1q4/fV6ZDV7V3p/Di5ItrsQ\nN1kYpfblyxcfZpiAvENQtHVaf3AThqVuBryKGZMZJKrxqU3Uh/si8qPELmPq/DFd\n4qBtb1mrK3IlM2WhevdFhg0=\n-----END PRIVATE KEY-----\n",
  "client_email": "gsheets-python-access@estoque-419114.iam.gserviceaccount.com",
  "client_id": "100589640925253361309",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/gsheets-python-access%40estoque-419114.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# Conexão com o Google Sheets
conn = GSheetsConnection(
    type=secret_info["type"],
    project_id=secret_info["project_id"],
    private_key_id=secret_info["private_key_id"],
    private_key=secret_info["private_key"],
    client_email=secret_info["client_email"],
    client_id=secret_info["client_id"],
    auth_uri=secret_info["auth_uri"],
    token_uri=secret_info["token_uri"],
    auth_provider_x509_cert_url=secret_info["auth_provider_x509_cert_url"],
    client_x509_cert_url=secret_info["client_x509_cert_url"],
    universe_domain=secret_info["universe_domain"]
)

# URL da planilha
url = "https://docs.google.com/spreadsheets/d/1j0iFYpsSh3JwQu9ej6g8C9oCfVseQsu2beEPvj512rw/edit?usp=drive_link"

# Leitura dos dados da planilha
data = conn.read(spreadsheet=url, usecols=[0, 1, 2, 3, 4, 5])

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
    gc = service_account.Credentials.from_service_account_info(secret_info)
    spreadsheet = gc.open_by_url(url)
    worksheet = spreadsheet.get_worksheet(0)

    for i, (index, row) in enumerate(estoque_atualizado.iterrows()):
        worksheet.update_cell(index + 2, 6, row['Estoque'])

    st.success('Estoque atualizado com sucesso!')
