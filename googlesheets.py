import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

conn = st.connection("gsheets", type=GSheetsConnection)

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

# Inicialização da variável de estado
if "form_data" not in st.session_state:
    st.session_state.form_data = {
        "name": "",
        "email": "",
        "whatsapp": "",
        "products": [],
        "size": 34,
        "method_of_payment": "",
        "value": 5,
        "movimentacao": 0,
        "movimentacao_type": "",
        "additional_info": "",
        "submission_datetime": "",
    }

# Determinar qual página exibir com base na seleção do usuário
if pagina_selecionada == "Stock":
    # Código para a página de estoque
    pass

elif pagina_selecionada == "Registro":
    # Página Registro
    st.title("Registro")

    existing_data_reservations = load_existing_data("Reservations")

    # Carregar os dados existentes de Shoes para obter a coluna "Modelo"
    existing_data_shoes = load_existing_data("Shoes")

    # Lista de modelos existentes
    modelos_existentes = existing_data_shoes["Modelo"].unique()

    # Opções de movimentação
    movimentacao_options = ["Venda", "Oferta", "Reserva", "Devolução", "Chegada de Material"]

    with st.form(key="vendor_form"):
        st.session_state.form_data["name"] = st.text_input(label="Name*", value=st.session_state.form_data["name"])
        st.session_state.form_data["email"] = st.text_input("E-mail", value=st.session_state.form_data["email"])
        st.session_state.form_data["whatsapp"] = st.text_input("WhatsApp with international code", value=st.session_state.form_data["whatsapp"])
        st.session_state.form_data["products"] = st.multiselect("Wished shoes", options=modelos_existentes, default=st.session_state.form_data["products"])
        st.session_state.form_data["size"] = st.slider("Numeração", 34, 45, value=st.session_state.form_data["size"])
        st.session_state.form_data["method_of_payment"] = st.selectbox("Method of Payment", ["", "Credit Card", "Cash", "Bank Transfer"], index=["", "Credit Card", "Cash", "Bank Transfer"].index(st.session_state.form_data["method_of_payment"]))
        st.session_state.form_data["value"] = st.slider("Valor (€)", 5, 10, 5, step=5, value=st.session_state.form_data["value"])
        st.session_state.form_data["movimentacao"] = st.slider("Movimentação de Stock", -10, 10, 0, value=st.session_state.form_data["movimentacao"])
        st.session_state.form_data["movimentacao_type"] = st.selectbox("Tipo de Movimentação", [""] + movimentacao_options, index=[""] + movimentacao_options.index(st.session_state.form_data["movimentacao_type"]))
        st.session_state.form_data["additional_info"] = st.text_area(label="Additional Notes", value=st.session_state.form_data["additional_info"])

        # Marcar campos obrigatórios
        st.markdown("**required*")

        submit_button = st.form_submit_button(label="Submit Details")

        # Se o botão de envio for pressionado
        if submit_button:
            # Obter a data/hora atual
            submission_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Adicionar a data/hora da submissão aos dados do formulário
            st.session_state.form_data["submission_datetime"] = submission_datetime

            # Criar uma nova linha de dados do fornecedor
            vendor_data = pd.DataFrame(
                [
                    {
                        "Name": st.session_state.form_data["name"],
                        "Email": st.session_state.form_data["email"],
                        "Whatsapp": st.session_state.form_data["whatsapp"],
                        "Products": ", ".join(st.session_state.form_data["products"]),
                        "Size": st.session_state.form_data["size"],
                        "Method of Payment": st.session_state.form_data["method_of_payment"],
                        "Value": st.session_state.form_data["value"],
                        "Movimentação de Stock": st.session_state.form_data["movimentacao"],
                        "Tipo de Movimentação": st.session_state.form_data["movimentacao_type"],
                        "SubmissionDateTime": st.session_state.form_data["submission_datetime"],
                        "AdditionalInfo": st.session_state.form_data["additional_info"],
                    }
                ]
            )

            # Adicionar os novos dados do fornecedor aos dados existentes
            updated_df = pd.concat([existing_data_reservations, vendor_data], ignore_index=True)

            # Atualizar o Google Sheets com os novos dados do fornecedor
            conn.update(worksheet="Reservations", data=updated_df)

            # Mensagem de sucesso
            st.success("Details successfully submitted!")

            # Limpar os campos do formulário após a submissão
            st.session_state.form_data = {
                "name": "",
                "email": "",
                "whatsapp": "",
                "products": [],
                "size": 34,
                "method_of_payment": "",
                "value": 5,
                "movimentacao": 0,
                "movimentacao_type": "",
                "additional_info": "",
                "submission_datetime": "",
            }

elif pagina_selecionada == "Reservation & Discount":
    # Página Reservas e Descontos
    pass

elif pagina_selecionada == "Active Reservations":
    # Exibir a página de reservas ativas
    active_reservations_page()
