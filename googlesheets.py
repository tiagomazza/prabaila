import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import plotly.express as px

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
    existing_data = conn.read(worksheet=worksheet_name, usecols=list(range(11)), ttl=5)
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
pagina_selecionada = st.sidebar.radio("Página", ["Stock", "Registro", "Reservation & Discount", "Active Reservations","Análise"])

# Determinar qual página exibir com base na seleção do usuário
if pagina_selecionada == "Stock":
    # Código para a página de estoque
    pass

# Página Registro
elif pagina_selecionada == "Registro":
    st.title("Registro")

    existing_data_reservations = load_existing_data("Reservations")
    existing_data_shoes = load_existing_data("Shoes")
    modelos_existentes = existing_data_shoes["Modelo"].unique()
    movimentacao_options = ["Venda", "Oferta", "Reserva", "Devolução", "Chegada de Material"]

    with st.form(key="vendor_form"):
        name = st.text_input(label="Name*")
        email = st.text_input("E-mail")
        whatsapp = st.text_input("WhatsApp with international code")
        products = st.multiselect("Wished shoes", options=modelos_existentes)
        size = st.slider("Numeração", 34, 45, 34)
        method_of_payment = st.selectbox("Method of Payment", ["Dinheiro", "Mbway", "Transferência","Wise","Revolut","Paypal"])
        value = st.slider("Valor (€)", 5, 150, 5, step=5)
        movimentacao = st.slider("Movimentação de Stock", -10, 10, 0)
        movimentacao_type = st.selectbox("Tipo de Movimentação", movimentacao_options)
        additional_info = st.text_area(label="Additional Notes")

        st.markdown("**required*")

        submit_button = st.form_submit_button(label="Submit Details")

        if submit_button:
            submission_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_row = {
                "Name": name,
                "Email": email,
                "Whatsapp": whatsapp,
                "Products": ", ".join(products),
                "Size": size,
                "Method of Payment": method_of_payment,
                "Value": value,
                "Movimentação de Stock": movimentacao,
                "Tipo de Movimentação": movimentacao_type,
                "AdditionalInfo": additional_info,
                "SubmissionDateTime": submission_datetime,
            }

            # Adiciona a nova linha à lista de dicionários
            new_rows = existing_data_reservations.to_dict(orient="records")
            new_rows.append(new_row)

            # Atualiza a planilha com todas as informações
            conn.update(worksheet="Reservations", data=new_rows)

            st.success("Details successfully submitted!")

            name = ""
            email = ""
            whatsapp = ""
            products = []
            size = 34
            method_of_payment = ""
            value = 5
            movimentacao = 0
            movimentacao_type = ""
            additional_info = ""


elif pagina_selecionada == "Reservation & Discount":
    # Código para a página de reservas e descontos
    pass

elif pagina_selecionada == "Active Reservations":
    # Exibir a página de reservas ativas
    active_reservations_page()

elif pagina_selecionada == "Análise":
    st.title("Análise dos Dados de Reservations")

    # Carregar os dados existentes
    existing_data = load_existing_data("Reservations")

    # Sidebar filters
    st.sidebar.header("Filtros")
    modelo_filtro = st.sidebar.selectbox("Filtrar por Modelo", ["Todos"] + existing_data["Products"].str.split(", ", expand=True).stack().unique())
    
    # Converter os valores exclusivos da coluna "Tipo de Movimentação" em uma lista de strings
    tipo_movimentacao_unique = existing_data["Tipo de Movimentação"].dropna().astype(str).unique()
    movimentacao_filtro = st.sidebar.selectbox("Filtrar por Tipo de Movimentação", ["Todos"] + tipo_movimentacao_unique.tolist())
    
    # Converter os valores exclusivos da coluna "Method of Payment" em uma lista de strings
    pagamento_unique = existing_data["Method of Payment"].dropna().astype(str).unique()
    pagamento_filtro = st.sidebar.selectbox("Filtrar por Método de Pagamento", ["Todos"] + pagamento_unique.tolist())

    # Aplicar filtros
    filtered_data = existing_data
    if modelo_filtro != "Todos":
        filtered_data = filtered_data[filtered_data["Products"].apply(lambda x: any(modelo_filtro in item for item in x))]
    if movimentacao_filtro != "Todos":
        filtered_data = filtered_data[filtered_data["Tipo de Movimentação"] == movimentacao_filtro]
    if pagamento_filtro != "Todos":
        filtered_data = filtered_data[filtered_data["Method of Payment"] == pagamento_filtro]

    # Número total de artigos vendidos
    total_articles_sold = filtered_data.shape[0]
    st.write(f"Número total de artigos vendidos: {total_articles_sold}")

    # Total vendido de cada modelo
    total_sold_by_model = filtered_data["Products"].str.split(", ", expand=True).stack().value_counts().to_string()
    st.write("Total vendido por modelo:")
    st.write(total_sold_by_model)

    # Total de cada tipo de movimentação de stock
    st.write("Total de cada tipo de movimentação de stock:")
    total_stock_movements = filtered_data["Tipo de Movimentação"].value_counts().to_string()
    st.write(total_stock_movements)

    # Total de valores recebidos
    total_values_received = filtered_data["Value"].sum()
    st.write(f"Total de valores recebidos: {total_values_received}")

    # Movimentação por forma de pagamento
    st.write("Movimentação por forma de pagamento:")
    total_by_payment_method = filtered_data.groupby("Method of Payment")["Value"].sum().to_string()
    st.write(total_by_payment_method)
