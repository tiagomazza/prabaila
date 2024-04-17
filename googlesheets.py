import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Função para proteger a página com senha
def protected_page():
    st.sidebar.title("Senha de Acesso")
    password_input = st.sidebar.text_input("Digite a senha:", type="password")

    if password_input == st.secrets["SENHA"]:
        return True
    else:
        st.error("Senha incorreta. Por favor, tente novamente.")
        return False

# Função para carregar os dados existentes
def load_existing_data(worksheet_name):
    conn = st.experimental_connection("gsheets", type=GSheetsConnection)
    existing_data = conn.read(worksheet=worksheet_name, usecols=list(range(6)), ttl=5)
    return existing_data.dropna(how="all")

# Função para exibir os dados existentes
def display_existing_data(existing_data):
    st.subheader("Existing Reservations")
    if not existing_data.empty:
        st.write(existing_data)
    else:
        st.write("No existing reservations.")

# Página Active Reservations
def active_reservations_page():
    st.title("Active Reservations")

    # Proteger a página com uma senha apenas se a página selecionada for "Active Reservations"
    if protected_page():
        # Carregar os dados existentes
        existing_data = load_existing_data("Reservations")

        # Exibir os dados existentes
        display_existing_data(existing_data)

# Configuração da aplicação
pagina_selecionada = st.sidebar.radio("Página", ["Stock", "Reservation & Discount", "Active Reservations"])

# Determinar qual página exibir com base na seleção do usuário
if pagina_selecionada == "Stock":
    # Código para a página de estoque
    pass
elif pagina_selecionada == "Reservation & Discount":
    # Código para a página de reserva e desconto
    pass
elif pagina_selecionada == "Active Reservations":
    # Exibir a página de reservas ativas
    active_reservations_page()
