import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

conn = st.experimental_connection("gsheets", type=GSheetsConnection)

# Função para proteger a página com senha
def protected_page():
    st.sidebar.title("Senha de Acesso")
    password_input = st.sidebar.text_input("Digite a senha:", type="password")

    if password_input == st.secrets["SENHA"]:
        return True
    else:
        st.error("Digite a senha no sidebar.")
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

# Imagem para exibir no menu lateral
menu_lateral_imagem = "https://acdn.mitiendanube.com/stores/003/310/899/themes/common/logo-1595099445-1706530812-af95f05363b68e950e5bd6a386042dd21706530812-320-0.webp"

# Exibir imagem no menu lateral
st.sidebar.image(menu_lateral_imagem, use_column_width=True)

# Display Title and Description
st.title("🌟Loja da Quinta🌵")
st.markdown("Sistema de controle de modelos.")

# Configuração da aplicação
pagina_selecionada = st.sidebar.radio("Página", ["Stock", "Registro", "Reservation & Discount", "Active Reservations"])

# Determinar qual página exibir com base na seleção do usuário
if pagina_selecionada == "Stock":
    # Código para a página de estoque
    pass

elif pagina_selecionada == "Registro":
    # Página Registro
    st.title("Registro")

    conn = st.experimental_connection("gsheets", type=GSheetsConnection)

    existing_data_reservations = conn.read(worksheet="Reservations", usecols=list(range(6)), ttl=5)
    existing_data_reservations = existing_data_reservations.dropna(how="all")

    # Carregar os dados existentes de Shoes para obter a coluna "Modelo"
    existing_data_shoes = conn.read(worksheet="Shoes", usecols=list(range(6)), ttl=5)
    existing_data_shoes = existing_data_shoes.dropna(how="all")

    # Lista de modelos existentes
    modelos_existentes = existing_data_shoes["Modelo"].unique()

    with st.form(key="vendor_form"):
        name = st.text_input(label="Name*")
        email = st.text_input("E-mail")
        whatsapp = st.text_input("WhatsApp with international code")
        products = st.multiselect("Wished shoes", options=modelos_existentes)
        size = st.slider("Numeração", 34, 45, 34)
        method_of_payment = st.selectbox("Method of Payment", ["Credit Card", "Cash", "Bank Transfer"])
        value = st.slider("Valor (€)", 5, 10, 5, step=5)
        additional_info = st.text_area(label="Additional Notes")

        # Marcar campos obrigatórios
        st.markdown("**required*")

        submit_button = st.form_submit_button(label="Submit Details")

        # Se o botão de envio for pressionado
        if submit_button:
            # Verificar se todos os campos obrigatórios foram preenchidos
            if not name:
                st.warning("Ensure all mandatory fields are filled.")
                st.stop()
            elif existing_data_reservations["Name"].astype(str).str.contains(name).any():
                st.warning("This name already exists.")
                st.stop()
            else:
                # Obter a data/hora atual
                submission_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Criar uma nova linha de dados do fornecedor
                vendor_data = pd.DataFrame(
                    [
                        {
                            "Name": name,
                            "Email": email,
                            "Whatsapp": whatsapp,
                            "Products": ", ".join(products),
                            "Size": size,
                            "Method of Payment": method_of_payment,
                            "Value": value,
                            "AdditionalInfo": additional_info,
                            "SubmissionDateTime": submission_datetime,  # Adicionar a data/hora da submissão
                        }
                    ]
                )

                # Adicionar os novos dados do fornecedor aos dados existentes
                updated_df = pd.concat([existing_data_reservations, vendor_data], ignore_index=True)

                # Atualizar o Google Sheets com os novos dados do fornecedor
                conn.update(worksheet="Reservations", data=updated_df)

                st.success("Details successfully submitted!")

                # Limpar os campos do formulário após o envio
                name = ""
                email = ""
                whatsapp = ""
                products = []
                size = 34
                method_of_payment = ""
                value = 5
                additional_info = ""

elif pagina_selecionada == "Reservation & Discount":
    # Código para a página de reservas e descontos
    pass

elif pagina_selecionada == "Active Reservations":
    # Exibir a página de reservas ativas
    active_reservations_page()
