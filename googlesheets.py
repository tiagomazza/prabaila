import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from woocommerce import API

wcapi = API(
    url="https://shop.quintaclandestina.pt",
    consumer_key="ck_326fe2832e12ff0ee0f2dd4a32e87ee0ceada496",
    consumer_secret="cs_44ad7b5fc9a38d6212240cbded4119636d003545",
    version="wc/v3"
)
conn = st.experimental_connection("gsheets", type=GSheetsConnection)

def protected_page():
    st.sidebar.title("Senha de Acesso")
    password_input = st.sidebar.text_input("Digite a senha:", type="password")

    if password_input == st.secrets["SENHA"]:
        return True
    else:
        st.error("Digite a senha no sidebar.")
        return False

def load_existing_data(worksheet_name):
    existing_data = conn.read(worksheet=worksheet_name, usecols=list(range(13)), ttl=5)
    return existing_data.dropna(how="all")

def display_existing_data(existing_data):
    st.subheader("Existing Reservations")
    if not existing_data.empty:
        st.write(existing_data)
    else:
        st.write("No existing reservations.")

def active_reservations_page():
    st.title("Active Reservations")

    if protected_page():
        existing_data = load_existing_data("Reservations")
        display_existing_data(existing_data)

def analysis_page():
    st.title("Análise dos Dados de Reservations")
    if protected_page():
        existing_data = load_existing_data("Reservations")
        existing_data.dropna(subset=["Tipo de Movimentação", "Products"], inplace=True)
        existing_data['SubmissionDateTime'] = pd.to_datetime(existing_data['SubmissionDateTime'])

        selected_movement_type = st.sidebar.multiselect("Filtrar por Tipo de Movimentação", existing_data["Tipo de Movimentação"].unique(), default=["Venda"])
        filtered_data = existing_data[existing_data["Tipo de Movimentação"].isin(selected_movement_type)]

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)

        start_date = st.sidebar.date_input("Data de Início", value=start_date)
        end_date = st.sidebar.date_input("Data de Fim", value=end_date)

        if start_date and end_date:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            filtered_data = filtered_data[(filtered_data["SubmissionDateTime"] >= start_date) & (filtered_data["SubmissionDateTime"] <= end_date)]

        article_names = st.sidebar.multiselect("Nome dos Artigos", existing_data["Products"].unique(), default=existing_data["Products"].unique())
        if article_names:
            filtered_data = filtered_data[filtered_data["Products"].isin(article_names)]

        selected_numbers = st.sidebar.multiselect("Filtrar por Numeração", existing_data["Size"].dropna().astype(int).unique(), default=existing_data["Size"].dropna().astype(int).unique())
        if selected_numbers:
            filtered_data = filtered_data[filtered_data["Size"].astype(float).isin(selected_numbers)]

        total_articles_sold = int(filtered_data["Movimentação de Stock"].sum())
        st.write(f"Número total de artigos vendidos: {total_articles_sold}")

        total_sold_by_model = filtered_data.groupby("Products")["Movimentação de Stock"].sum()
        st.write(total_sold_by_model)

        total_sold_by_size = filtered_data.groupby("Size")["Movimentação de Stock"].sum()
        st.write(total_sold_by_size)

        total_values_received = filtered_data["Value"].sum()
        st.write(f"Total de valores recebidos (filtrado): {total_values_received}")

        st.write("Movimentação por forma de pagamento (filtrado):")
        total_by_payment_method = filtered_data.groupby("Method of Payment")["Value"].sum()
        st.write(total_by_payment_method)

        st.write("Dados filtrados:")
        st.write(filtered_data)

def get_id_from_shoes(modelo, numero):
    existing_data_shoes = load_existing_data("Shoes")
    id_ = existing_data_shoes[(existing_data_shoes["Modelo"] == modelo) & (existing_data_shoes["Número"] == numero)]["ID"]
    if not id_.empty:
        return id_.iloc[0]
    else:
        return None

def register_page():
    st.title("Registro")
    if protected_page():
        existing_data_reservations = load_existing_data("Reservations")
        existing_data_shoes = load_existing_data("Shoes")
        modelos_existentes = existing_data_shoes["Modelo"].unique()
        movimentacao_options = ["Venda", "Oferta", "Reserva", "Devolução", "Entrada de Material"]

        with st.form(key="vendor_form"):
            name = st.text_input(label="Name*")
            email = st.text_input("E-mail")
            whatsapp = st.text_input("WhatsApp with international code")
            products = st.multiselect("Shoes", options=modelos_existentes)
            size = st.slider("Numeração", 36, 45, 34)
            method_of_payment = st.selectbox("Method of Payment", ["Dinheiro", "Mbway", "Transferência", "Wise", "Revolut", "Paypal"])
            value = st.slider("Valor (€)", 0, 150, 5, step=5)
            movimentacao = st.slider("Movimentação de Stock", 0, 10, 0)
            movimentacao_type = st.selectbox("Tipo de Movimentação", movimentacao_options)
            additional_info = st.text_area(label="Additional Notes")

            st.markdown("**required*")

            submit_button = st.form_submit_button(label="Submit Details")

            if submit_button:
                submission_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if movimentacao_type in ["Venda", "Oferta", "Reserva"]:
                    movimentacao = -abs(movimentacao)

                selected_model = products[0]
                selected_id = get_id_from_shoes(selected_model, size)

                new_row = {
                    "ID": selected_id,
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

                new_rows = existing_data_reservations.to_dict(orient="records")
                new_rows.append(new_row)

                conn.update(worksheet="Reservations", data=new_rows)

                st.success("Details successfully submitted!")

                try:
                    if existing_data_shoes is not None:
                        row_shoes = existing_data_shoes[existing_data_shoes["ID"] == selected_id].iloc[0]
                        id_produto = int(row_shoes["ID_Produto"])
                        id_variacao = int(row_shoes["ID_Variação"]) if not pd.isna(row_shoes["ID_Variação"]) and row_shoes["ID_Variação"] != "" else None
                        stock = int(row_shoes["Estoque"])
                        new_stock = stock + movimentacao
                        data = {
                            'stock_quantity': new_stock
                        }
                        if id_variacao is None:
                            response = wcapi.put(f"products/{id_produto}", data).json()
                            st.success(f"Estoque atualizado para o produto ID {id_produto}: {new_stock}")
                        else:
                            response = wcapi.put(f"products/{id_produto}/variations/{id_variacao}", data).json()
                            st.success(f"Estoque atualizado para a variação ID {id_variacao} do produto ID {id_produto}: {new_stock}")
                    else:
                        st.error("Erro ao carregar dados dos produtos para atualização do estoque.")
                except ValueError as ve:
                    st.error(f"Erro ao converter valores para int: {ve}")
                except Exception as e:
                    st.error(f"Erro ao atualizar o estoque no WooCommerce: {e}")

def get_sales_quantity(id_):
    existing_data_reservations = load_existing_data("Reservations")

    if existing_data_reservations is None or id_ not in existing_data_reservations["ID"].values:
        return 0

    filtered_data = existing_data_reservations[(existing_data_reservations["ID"] == id_) &
                                               (existing_data_reservations["Tipo de Movimentação"].isin(["Venda", "Oferta"]))]

    sales_quantity = filtered_data["Movimentação de Stock"].sum()

    subtraction_data = existing_data_reservations[(existing_data_reservations["ID"] == id_) &
                                                  (existing_data_reservations["Tipo de Movimentação"] == "Entrada de Material")]

    if not subtraction_data.empty:
        subtraction_quantity = subtraction_data["Movimentação de Stock"].sum()
        sales_quantity -= subtraction_quantity

    return sales_quantity

def shoes_page():
    st.title("Shoes Inventory")
    if protected_page():
        existing_data = load_existing_data("Shoes")
        if existing_data is not None:
            st.write(existing_data)

        with st.form(key="shoes_form"):
            id_ = st.number_input(label="ID")
            modelo = st.text_input(label="Modelo*")
            numero = st.number_input(label="Numeração", min_value=34, max_value=45)
            estoque = st.number_input(label="Estoque")
            id_produto = st.text_input(label="ID do Produto")
            id_variacao = st.text_input(label="ID da Variação", value="")
            submit_button = st.form_submit_button(label="Registrar sapatos")

            if submit_button:
                sales_quantity = get_sales_quantity(id_)
                new_row = {
                    "ID": id_,
                    "Modelo": modelo,
                    "Número": numero,
                    "Estoque": estoque - sales_quantity,
                    "ID_Produto": id_produto,
                    "ID_Variação": id_variacao,
                }

                new_rows = existing_data.to_dict(orient="records")
                new_rows.append(new_row)

                conn.update(worksheet="Shoes", data=new_rows)

                st.success("Details successfully submitted!")

pages = {
    "Active Reservations": active_reservations_page,
    "Análise de Dados": analysis_page,
    "Registro": register_page,
    "Estoque de Sapatos": shoes_page,
}

selected_page = st.sidebar.selectbox("Select a page", options=list(pages.keys()))

pages[selected_page]()
