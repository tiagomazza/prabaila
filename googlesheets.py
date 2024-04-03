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
data = conn.read(spreadsheet_url=url, worksheet="Pag1", start_cell="A1", end_cell="E10")

# Exibir os dados
st.write(data)

# Botão para atualizar os dados
if st.button("Atualizar Dados"):
    gc = service_account.Credentials.from_service_account_info(credentials)
    spreadsheet = gc.open_by_url(url)
    worksheet = spreadsheet.worksheet("Pag1")

    # Atualizar os dados de teste
    test_data = [
        ['Novo Valor 1', 'Novo Valor 2', 'Novo Valor 3', 'Novo Valor 4', 'Novo Valor 5'],
        ['Novo Valor 6', 'Novo Valor 7', 'Novo Valor 8', 'Novo Valor 9', 'Novo Valor 10']
    ]
    
    worksheet.update('A1', test_data)

    st.success('Dados atualizados com sucesso!')
