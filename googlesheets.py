import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import plotly.express as px
from woocommerce import API

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

from datetime import datetime, timedelta

def analysis_page():
   st.title("Análise dos Dados de Reservations")

   # Proteger a página com uma senha
   if protected_page():
       # Carregar os dados existentes
       existing_data = load_existing_data("Reservations")

       # Remover NaN do Tipo de Movimentação e Nome dos artigos
       existing_data.dropna(subset=["Tipo de Movimentação", "Products"], inplace=True)

       # Convertendo a coluna 'SubmissionDateTime' para datetime
       existing_data['SubmissionDateTime'] = pd.to_datetime(existing_data['SubmissionDateTime'])

       # Barra lateral para filtrar por tipo de movimentação
       selected_movement_type = st.sidebar.multiselect("Filtrar por Tipo de Movimentação", 
                                                     existing_data["Tipo de Movimentação"].unique(), default=["Venda"])
       
       # Filtrar os dados pelo tipo de movimentação selecionado
       filtered_data = existing_data[existing_data["Tipo de Movimentação"].isin(selected_movement_type)]

       # Filtro por intervalo de datas
       end_date = datetime.now().date()
       start_date = end_date - timedelta(days=30)

       start_date = st.sidebar.date_input("Data de Início", value=start_date)
       end_date = st.sidebar.date_input("Data de Fim", value=end_date)

       if start_date and end_date:
           start_date = pd.to_datetime(start_date)
           end_date = pd.to_datetime(end_date)
           filtered_data = filtered_data[(filtered_data["SubmissionDateTime"] >= start_date) & (filtered_data["SubmissionDateTime"] <= end_date)]

       # Filtro por nome dos artigos
       article_names = st.sidebar.multiselect("Nome dos Artigos", existing_data["Products"].unique(), default=existing_data["Products"].unique())

       if article_names:
           filtered_data = filtered_data[filtered_data["Products"].isin(article_names)]

       # Filtro por numeração
       selected_numbers = st.sidebar.multiselect("Filtrar por Numeração", existing_data["Size"].dropna().astype(int).unique(), default=existing_data["Size"].dropna().astype(int).unique())

       if selected_numbers:
           filtered_data = filtered_data[filtered_data["Size"].astype(float).isin(selected_numbers)]

       # Número total de artigos vendidos (filtrado)
       total_articles_sold = int(filtered_data["Movimentação de Stock"].sum())
       st.write(f"Número total de artigos vendidos: {total_articles_sold}")

       # Total vendido por numeração (filtrado)
       total_sold_by_model = filtered_data.groupby("Products")["Movimentação de Stock"].sum()
       st.write(total_sold_by_model)

       # Total vendido por numeração (filtrado)
       total_sold_by_size = filtered_data.groupby("Size")["Movimentação de Stock"].sum()
       st.write(total_sold_by_size)

       # Total de valores recebidos (filtrado)
       total_values_received = filtered_data["Value"].sum()
       st.write(f"Total de valores recebidos (filtrado): {total_values_received}")

       # Movimentação por forma de pagamento (filtrado)
       st.write("Movimentação por forma de pagamento (filtrado):")
       total_by_payment_method = filtered_data.groupby("Method of Payment")["Value"].sum()
       st.write(total_by_payment_method)

       # Mostrar a tabela de dados filtrada
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

# Atualização da função register_page() para incluir o ID correspondente no novo registro
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
           method_of_payment = st.selectbox("Method of Payment", ["Dinheiro", "Mbway", "Transferência","Wise","Revolut","Paypal"])
           value = st.slider("Valor (€)", 0, 150, 5, step=5)
           movimentacao = st.slider("Movimentação de Stock", 0, 10, 0)
           movimentacao_type = st.selectbox("Tipo de Movimentação", movimentacao_options)
           additional_info = st.text_area(label="Additional Notes")

           st.markdown("**required*")

           submit_button = st.form_submit_button(label="Submit Details")

           if submit_button:
               submission_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
               
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

# Configuração da API do WooCommerce
    wcapi = API(
        url="https://shop.quintaclandestina.pt",  # Substitua pelo URL da sua loja
        consumer_key="ck_326fe2832e12ff0ee0f2dd4a32e87ee0ceada496",   # Substitua pela sua Consumer Key
        consumer_secret="cs_44ad7b5fc9a38d6212240cbded4119636d003545",
        version="wc/v3"
    )

    st.title("Gerenciamento de Estoque WooCommerce")

    # Formulário para entrada de dados
    product_id = st.text_input("ID do Produto")
    variation_id = st.text_input("ID da Variação (deixe em branco se não for uma variação)")

    if product_id:
        # Recupera o estoque atual
        if variation_id:
            endpoint = f"products/{product_id}/variations/{variation_id}"
        else:
            endpoint = f"products/{product_id}"
        
        response = wcapi.get(endpoint).json()
        
        if "stock_quantity" in response:
            current_stock = response["stock_quantity"]
            st.write(f"Estoque atual: {current_stock}")
        else:
            st.error(f"Erro ao obter estoque atual: {response.get('message', 'Erro desconhecido')}")
            current_stock = None
    else:
        current_stock = None

    new_stock = st.number_input("Novo Estoque", min_value=0, step=1)

    if st.button("Atualizar Estoque"):
        if product_id and new_stock is not None and current_stock is not None:
            if variation_id:
                # Atualiza o estoque de uma variação de produto no WooCommerce
                endpoint = f"products/{product_id}/variations/{variation_id}"
            else:
                # Atualiza o estoque de um produto simples no WooCommerce
                endpoint = f"products/{product_id}"
            
            # Dados para atualização do estoque
            data = {
                "stock_quantity": new_stock
            }
            
            # Envia a solicitação para atualizar o produto ou variação
            response = wcapi.put(endpoint, data).json()
            
            if "id" in response:
                st.success(f"Estoque do produto {'variação ' + variation_id if variation_id else product_id} atualizado de {current_stock} para {new_stock}.")
            else:
                st.error(f"Erro ao atualizar estoque: {response.get('message', 'Erro desconhecido')}")
        else:
            st.warning("Por favor, insira um ID de produto válido e quantidade de estoque.")


    
          


# Imagem para exibir no menu lateral
menu_lateral_imagem = "https://shop.quintaclandestina.pt/wp-content/uploads/2024/05/logo-2.png"

# Exibir imagem no menu lateral
st.sidebar.image(menu_lateral_imagem, use_column_width=True)

# Display Title and Description
st.title("Quinta Shop🛒")

# Configuração da aplicação
pagina_selecionada = st.sidebar.radio("Página", ["Verificação de estoque","Registro","Análise","Teste"])

def get_sales_quantity(id_):
   existing_data_reservations = load_existing_data("Reservations")
   
   # Verificar se os dados existem e se o ID está presente
   if existing_data_reservations is None or id_ not in existing_data_reservations["ID"].values:
       return 0
   
   # Filtrar dados com base no ID e tipo de movimentação
   filtered_data = existing_data_reservations[(existing_data_reservations["ID"] == id_) &
                                              (existing_data_reservations["Tipo de Movimentação"].isin(["Venda", "Oferta"]))]

   # Somar as quantidades de venda e oferta
   sales_quantity = filtered_data["Movimentação de Stock"].sum()

   # Filtrar dados com base no ID e tipo de movimentação para subtração
   subtraction_data = existing_data_reservations[(existing_data_reservations["ID"] == id_) &
                                                 (existing_data_reservations["Tipo de Movimentação"] == "Entrada de Material")]

   # Verificar se existem dados de subtração
   if not subtraction_data.empty:
       # Subtrair as quantidades de entrada de material
       subtraction_quantity = subtraction_data["Movimentação de Stock"].sum()

       # Calcular o total líquido
       net_quantity = sales_quantity - subtraction_quantity
   else:
       # Se não houver dados de subtração, a quantidade líquida é igual à quantidade de vendas e ofertas
       net_quantity = sales_quantity

   return int(net_quantity)  # Convertendo para inteiro para remover o .0


# Atualização da página de verificação de estoque para subtrair a quantidade de venda da quantidade disponível
if pagina_selecionada == "Verificação de estoque":
   # Fetch existing shoes data
   st.subheader("Busca de modelos disponíveis")
   existing_data = conn.read(worksheet="Shoes", usecols=["ID", "Modelo", "Número", "Imagem", "Descrição", "Preço", "Estoque", "Numero Brasileiro", "Deslize", "Amortecimento", "Cor da sola"], ttl=6)
   existing_data.dropna(subset=["ID", "Modelo", "Número", "Imagem", "Descrição", "Preço", "Estoque", "Numero Brasileiro", "Deslize", "Amortecimento", "Cor da sola"], inplace=True)

   # Sidebar filters
   st.sidebar.header("Filtros")
   
   modelos = existing_data["Modelo"].unique()
   modelos_filtro = st.sidebar.multiselect("Filtrar por Modelo", modelos.astype(str), default=modelos.astype(str))

   deslize_opcoes = existing_data["Deslize"].unique()
   deslize_filtro = st.sidebar.multiselect("Filtrar por Deslize", deslize_opcoes, default=deslize_opcoes)

   amortecimento_opcoes = existing_data["Amortecimento"].unique()
   amortecimento_filtro = st.sidebar.multiselect("Filtrar por Amortecimento", amortecimento_opcoes, default=amortecimento_opcoes)

   cor_sola_opcoes = existing_data["Cor da sola"].unique()
   cor_sola_filtro = st.sidebar.multiselect("Filtrar por Cor da sola", cor_sola_opcoes, default=cor_sola_opcoes)

   # Números disponíveis com base nos filtros aplicados
   numeros_disponiveis = existing_data[existing_data["Modelo"].isin(modelos_filtro)]["Número"].unique()
   numeros_europeus_selecionados = st.multiselect("Quais números europeus deseja consultar?", numeros_disponiveis.astype(int), default=[])

   # Aplicar os filtros selecionados aos dados existentes
   filtered_data = existing_data[
       (existing_data["Modelo"].isin(modelos_filtro)) & 
       (existing_data["Número"].isin(numeros_europeus_selecionados)) &
       (existing_data["Deslize"].isin(deslize_filtro)) &
       (existing_data["Amortecimento"].isin(amortecimento_filtro)) &
       (existing_data["Cor da sola"].isin(cor_sola_filtro))
   ]

   # Remover o ".0" dos dados consultados
   filtered_data["Número"] = filtered_data["Número"].astype(int)
       

   # Add a toggle button to show/hide shoes with zero stock
   show_zero_stock = st.sidebar.checkbox("Mostrar sem stock")

   # Apply filter to show/hide shoes with zero stock
   if not show_zero_stock:
       filtered_data = filtered_data[filtered_data["Estoque"] > 0]

   # Display total stock count in the sidebar
   total_stock = filtered_data["Estoque"].sum()
   st.sidebar.header("Total do Estoque:")
   st.sidebar.write(str(total_stock).split('.')[0])  # Displaying stock without .0

   # Display shoes information separately
   for index, row in filtered_data.iterrows():
       id_unico = f"{row['Modelo']}_{int(row['Número'])}"  # Criar um ID único combinando modelo e número
       st.subheader(f"{row['Modelo']}")
       st.markdown(f"🇪🇺 **Número:** {int(row['Número'])}")  # Remove .0 and make bold
       # Display the image from the URL
       if row['Imagem']:
           st.image(row['Imagem'])
       else:
           st.text("Imagem não disponível")
       
               # Subtrair a quantidade de venda da quantidade disponível
       id_ = row["ID"]
       sales_quantity = get_sales_quantity(id_)
       stock_after_sales = int(row["Estoque"]) - sales_quantity

       st.markdown(f"🏂🏽 **Deslize:** {(row['Deslize'])}")  # Remove .0 and make 
       st.markdown(f"🦘 **Amortecimento:** {(row['Amortecimento'])}")  # Remove .0 and make 
       st.markdown(f"👟 **Cor da sola:** {(row['Cor da sola'])}")  # Remove .0 and make 
       st.markdown(f"📦 **Unidades em estoque:** {stock_after_sales}")  # Remove .0 and make 
       st.markdown(f"🇧🇷 **Numero:** {int(row['Numero Brasileiro'])}")  # Remove .0 and make 
       preco = row.get('Preço')
       if preco is not None:
           st.markdown(f"🏷 **Preço:**  {int(row['Preço'])}€")
       else:
           st.markdown("Preço não disponível")

       st.markdown(f"📝 **Observações:** {row['Descrição']}")  # Make bold



       
       st.markdown("---")

# Página Registro
elif pagina_selecionada == "Registro":
   register_page()

elif pagina_selecionada == "Active Reservations":
   # Exibir a página de reservas ativas
   active_reservations_page()

elif pagina_selecionada == "Análise":
   analysis_page()

elif pagina_selecionada == "Teste":
       
    wcapi = API(
    url="https://sua-loja.com",  # Substitua pelo URL da sua loja
    consumer_key="ck_xxxxxxx",   # Substitua pela sua Consumer Key
    consumer_secret="cs_xxxxxxx",  # Substitua pelo seu Consumer Secret
    version="wc/v3"
    )
    # Formulário para entrada de dados
    product_id = st.text_input("ID do Produto")
    new_stock = st.number_input("Novo Estoque", min_value=0, step=1)

    if st.button("Atualizar Estoque"):
        if product_id and new_stock is not None:
            # Atualiza o estoque do produto no WooCommerce
            data = {
                "stock_quantity": new_stock
            }
            response = wcapi.put(f"products/{product_id}", data).json()
            
            if "id" in response:
                st.success(f"Estoque do produto {product_id} atualizado para {new_stock}.")
            else:
                st.error(f"Erro ao atualizar estoque: {response.get('message', 'Erro desconhecido')}")
        else:
            st.warning("Por favor, insira um ID de produto válido e quantidade de estoque.")
            
            