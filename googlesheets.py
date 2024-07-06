import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import plotly.express as px
from woocommerce import API
from datetime import datetime, timedelta

wcapi = API(
            url="https://shop.quintaclandestina.pt",  # Substitua pelo URL da sua loja
            consumer_key="ck_326fe2832e12ff0ee0f2dd4a32e87ee0ceada496",   # Substitua pela sua Consumer Key
            consumer_secret="cs_44ad7b5fc9a38d6212240cbded4119636d003545",
            version="wc/v3"
        )
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
   existing_data = conn.read(worksheet=worksheet_name, usecols=list(range(13)), ttl=5)
   return existing_data.dropna(how="all")

# Função para exibir os dados existentes
def display_existing_data(existing_data):
   st.subheader("Existing Reservations")
   if not existing_data.empty:
       st.write(existing_data)
   else:
       st.write("No existing reservations.")

# Página Active Reservations

   st.title("Active Reservations")

   # Proteger a página com uma senha apenas se a página selecionada for "Active Reservations"
   if protected_page():
       # Carregar os dados existentes
       existing_data = load_existing_data("Reservations")

       # Exibir os dados existentes
       display_existing_data(existing_data)

def analysis_page():
    st.title("Análise dos Dados de Reservations")
    
    if protected_page():
        existing_data = load_existing_data("Reservations")
        
        # Certifique-se de que a coluna 'Movimentação de Stock' está carregada como numérica
        existing_data['Movimentação de Stock'] = pd.to_numeric(existing_data['Movimentação de Stock'], errors='coerce')
        
        # Filtrar os dados que têm 'Tipo de Movimentação' e 'Products' não nulos
        existing_data.dropna(subset=["Tipo de Movimentação", "Products"], inplace=True)
        
        # Converter a coluna 'SubmissionDateTime' para datetime
        existing_data['SubmissionDateTime'] = pd.to_datetime(existing_data['SubmissionDateTime'])
        
        # Filtrar por tipo de movimentação
        all_movement_types = existing_data["Tipo de Movimentação"].unique()
        default_movement_types = ["Venda", "Entrada"]  # Inclua todos os tipos de movimentação padrão que você deseja exibir
        selected_movement_type = st.sidebar.multiselect("Filtrar por Tipo de Movimentação", 
                                                        all_movement_types, 
                                                        default=[x for x in default_movement_types if x in all_movement_types])
        filtered_data = existing_data[existing_data["Tipo de Movimentação"].isin(selected_movement_type)]
        
        # Filtrar por data
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        start_date = st.sidebar.date_input("Data de Início", value=start_date)
        end_date = st.sidebar.date_input("Data de Fim", value=end_date)
        
        if start_date and end_date:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date) + timedelta(days=1) - timedelta(seconds=1)  # Inclui o dia final completo
            filtered_data = filtered_data[(filtered_data["SubmissionDateTime"] >= start_date) & 
                                          (filtered_data["SubmissionDateTime"] <= end_date)]
        
        # Filtrar por nome dos artigos
        all_article_names = existing_data["Products"].unique()
        selected_article_names = st.sidebar.multiselect("Nome dos Artigos", 
                                                        all_article_names, 
                                                        default=all_article_names.tolist())
        if selected_article_names:
            filtered_data = filtered_data[filtered_data["Products"].isin(selected_article_names)]
        
        # Filtrar por numeração
        all_sizes = existing_data["Size"].dropna().astype(int).unique()
        selected_numbers = st.sidebar.multiselect("Filtrar por Numeração", 
                                                  all_sizes, 
                                                  default=all_sizes.tolist())
        if selected_numbers:
            filtered_data = filtered_data[filtered_data["Size"].astype(int).isin(selected_numbers)]
        
        # Cálculos
        total_articles_sold = filtered_data["Movimentação de Stock"].sum()
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


# Função para obter o ID correspondente com base no modelo e número
def get_id_from_shoes(modelo, numero):
   existing_data_shoes = load_existing_data("Shoes")
   id_ = existing_data_shoes[(existing_data_shoes["Modelo"] == modelo) & (existing_data_shoes["Número"] == numero)]["ID"]
   if not id_.empty:
       return id_.iloc[0]
   else:
       return None

def register_page():
    st.title("Registro")
    # Proteger a página com uma senha
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
                
                # Transformar os valores de "Venda", "Oferta" e "Reserva" em números negativos
                if movimentacao_type in ["Venda", "Oferta", "Reserva"]:
                    movimentacao = -abs(movimentacao)

                # Obter o ID correspondente com base no modelo e número selecionados
                selected_model = products[0]  # Assumindo apenas um produto é selecionado
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

                # Adiciona a nova linha à lista de dicionários
                new_rows = existing_data_reservations.to_dict(orient="records")
                new_rows.append(new_row)

                # Atualiza a planilha com todas as informações
                conn.update(worksheet="Reservations", data=new_rows)

                st.success("Details successfully submitted!")

                # Atualiza o estoque no WooCommerce após a atualização da planilha
                try:
                    if existing_data_shoes is not None:
                        row_shoes = existing_data_shoes[existing_data_shoes["ID"] == selected_id].iloc[0]
                        id_produto = row_shoes["ID WooCommerce"]
                        estoque_atual = row_shoes["Stock"] + movimentacao

                        if id_produto:
                            wcapi.put(f"products/{int(id_produto)}", 
                                      {"stock_quantity": estoque_atual, "manage_stock": True})
                            st.success(f"Estoque do produto ID {id_produto} atualizado com sucesso no WooCommerce!")
                        else:
                            st.warning("ID do produto WooCommerce não encontrado.")
                except Exception as e:
                    st.error(f"Erro ao atualizar o estoque no WooCommerce: {e}")

def sync_woocommerce_stock():
    st.title("WooCommerce Sync")
    if protected_page():
        existing_data_shoes = load_existing_data("Shoes")
        st.write(existing_data_shoes)

        def update_woocommerce_stock():
            if existing_data_shoes is not None:
                try:
                    for _, row in existing_data_shoes.iterrows():
                        id_produto = row["ID WooCommerce"]
                        estoque = row["Stock"]
                        if pd.notna(id_produto):  # Verifica se o ID do produto não é NaN
                            wcapi.put(f"products/{int(id_produto)}", 
                                      {"stock_quantity": int(estoque), "manage_stock": True})
                    st.success("Estoque atualizado com sucesso no WooCommerce!")
                except Exception as e:
                    st.error(f"Erro ao atualizar o estoque no WooCommerce: {e}")

        # Adicionar um botão para atualizar o estoque no WooCommerce
        if st.button("Atualizar Estoque no WooCommerce"):
            update_woocommerce_stock()

# Roteamento de páginas
PAGES = {
    "Active Reservations": protected_page,
    "Registro": register_page,
    "Analysis": analysis_page,
    "WooCommerce Sync": sync_woocommerce_stock,
}

def main():
    st.sidebar.title("Menu")
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))
    page = PAGES[selection]
    page()

if __name__ == "__main__":
    main()
