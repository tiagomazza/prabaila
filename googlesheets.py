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
    existing_data = conn.read(worksheet=worksheet_name, usecols=list(range(12)), ttl=5)
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


def analysis_page():
    st.title("Análise dos Dados de Reservations")

    # Proteger a página com uma senha
    if protected_page():
        # Carregar os dados existentes
        existing_data = load_existing_data("Reservations")

        # Barra lateral para filtrar por tipo de movimentação
        selected_movement_type = st.sidebar.selectbox("Filtrar por Tipo de Movimentação", 
                                                      existing_data["Tipo de Movimentação"].unique())
        
        # Filtrar os dados pelo tipo de movimentação selecionado
        filtered_data = existing_data[existing_data["Tipo de Movimentação"] == selected_movement_type]

        # Número total de artigos vendidos (filtrado)
        total_articles_sold = filtered_data.shape[0]
        st.write(f"Número total de artigos vendidos: {total_articles_sold}")

        # Total vendido de cada modelo (filtrado)
        total_sold_by_model = filtered_data["Products"].str.split(", ", expand=True).stack().value_counts()
        st.write("Total vendido por modelo (filtrado):")
        st.write(total_sold_by_model)

        # Total vendido por numeração (filtrado)
        total_sold_by_size = filtered_data.groupby("Size").size()
        st.write("Total vendido por numeração (filtrado):")
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


# Imagem para exibir no menu lateral
menu_lateral_imagem = "https://acdn.mitiendanube.com/stores/003/310/899/themes/common/logo-1595099445-1706530812-af95f05363b68e950e5bd6a386042dd21706530812-320-0.webp"

# Exibir imagem no menu lateral
st.sidebar.image(menu_lateral_imagem, use_column_width=True)

# Display Title and Description
st.title("Quinta Shop🛒")

# Configuração da aplicação
pagina_selecionada = st.sidebar.radio("Página", ["Verificação de estoque","Registro","Análise"])

def get_sales_quantity(id_):
    existing_data_reservations = load_existing_data("Reservations")
    
    # Filtrar dados com base no ID e tipo de movimentação
    filtered_data = existing_data_reservations[(existing_data_reservations["ID"] == id_) &
                                               (existing_data_reservations["Tipo de Movimentação"].isin(["Venda", "Oferta","Devolução"]))]

    # Somar as quantidades de venda e oferta
    sales_quantity = filtered_data["Movimentação de Stock"].sum()

    # Filtrar dados com base no ID e tipo de movimentação para subtração
    subtraction_data = existing_data_reservations[(existing_data_reservations["ID"] == id_) &
                                                  (existing_data_reservations["Tipo de Movimentação"] == "Entrada de Material", "Reserva")]

    # Subtrair as quantidades de entrada de material
    subtraction_quantity = subtraction_data["Movimentação de Stock"].sum()

    # Calcular o total líquido
    net_quantity = sales_quantity - subtraction_quantity

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
