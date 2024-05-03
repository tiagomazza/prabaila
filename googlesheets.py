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
st.title("Quinta Shop🛒")
st.subheader("Busca de modelos disponíveis")

# Configuração da aplicação
pagina_selecionada = st.sidebar.radio("Página", ["Verificação de estoque","Stock", "Registro", "Reservation & Discount", "Active Reservations","Análise"])


if pagina_selecionada == "Verificação de estoque":
    # Fetch existing shoes data
    existing_data = conn.read(worksheet="Shoes", usecols=["Modelo", "Número", "Imagem", "Descrição", "Preço", "Estoque", "Numero Brasileiro", "Deslize", "Amortecimento", "Cor da sola"], ttl=6)
    existing_data.dropna(subset=["Modelo", "Número", "Imagem", "Descrição", "Preço", "Estoque", "Numero Brasileiro", "Deslize", "Amortecimento", "Cor da sola"], inplace=True)

    # Sidebar filters
    st.sidebar.header("Filtros")
    
    numeros = existing_data["Número"].unique()
    #numeros_filtro = st.sidebar.multiselect("Filtrar por Número", numeros.astype(int), default=numeros.astype(int))

    modelos = existing_data["Modelo"].unique()
    modelos_filtro = st.sidebar.multiselect("Filtrar por Modelo", modelos.astype(str), default=modelos.astype(str))
    
    deslize_opcoes = existing_data["Deslize"].unique()
    deslize_filtro = st.sidebar.multiselect("Filtrar por Deslize", deslize_opcoes, default=deslize_opcoes)

    amortecimento_opcoes = existing_data["Amortecimento"].unique()
    amortecimento_filtro = st.sidebar.multiselect("Filtrar por Amortecimento", amortecimento_opcoes, default=amortecimento_opcoes)

    cor_sola_opcoes = existing_data["Cor da sola"].unique()
    cor_sola_filtro = st.sidebar.multiselect("Filtrar por Cor da sola", cor_sola_opcoes, default=cor_sola_opcoes)

    filtered_data = existing_data[
        (existing_data["Modelo"].isin(modelos_filtro)) & 
        (existing_data["Número"].isin(numeros)) &
        #(existing_data["Número"].isin(numeros_filtros)) &
        (existing_data["Deslize"].isin(deslize_filtro)) &
        (existing_data["Amortecimento"].isin(amortecimento_filtro)) &
        (existing_data["Cor da sola"].isin(cor_sola_filtro))
    ]
        

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
        
        preco = row.get('Preço')
        if preco is not None:
            st.markdown(f"🏷 **Preço:**  {int(row['Preço'])}")
        else:
            st.markdown("Preço não disponível")
        st.markdown(f"🏂🏽 **Deslize:** {(row['Deslize'])}")  # Remove .0 and make 
        st.markdown(f"🎿🦘 **Amortecimento:** {(row['Amortecimento'])}")  # Remove .0 and make 
        st.markdown(f"👟 **Cor da sola:** {(row['Cor da sola'])}")  # Remove .0 and make 
        st.markdown(f"📦 **Unidades em estoque:** {int(row['Estoque'])}")  # Remove .0 and make 
        st.markdown(f"🇧🇷 **Numero:** {int(row['Numero Brasileiro'])}")  # Remove .0 and make 
        st.markdown(f"📝 **Descrição:** {row['Descrição']}")  # Make bold

    # Adicionar botão com link para o WhatsApp
        modelo_formatado = row['Modelo'].replace(" ", "%20")
        whatsapp_link = f"https://wa.me/351914527565?text=Tenho%20interesse%20no%20{modelo_formatado}%20{int(row['Número'])}"
        
        st.subheader(f"Gostou deste modelo? Converse connosco pelo [WhatsApp](%s)" % whatsapp_link)

        # Quantity input for adding or reducing stock
        quantity = st.number_input(f"Ajuste de stock do {row['Modelo']}", value=0, step=1, key=index)  # Unique key

        # Update the inventory if quantity is provided
        if quantity != 0:
            updated_stock = row['Estoque'] + quantity
            existing_data.at[index, 'Estoque'] = updated_stock

    # Update Google Sheets with the updated inventory
    if st.sidebar.button("Atualizar Estoque"):  # Moved button to sidebar
        conn.update(worksheet="Shoes", data=existing_data)
        st.success("Estoque atualizado com sucesso!")
        # Reload the page after updating the inventory
        st.experimental_rerun()


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

    # Número total de artigos vendidos
    total_articles_sold = existing_data.shape[0]
    st.write(f"Número total de artigos vendidos: {total_articles_sold}")

    # Total vendido de cada modelo
    total_sold_by_model = existing_data["Products"].str.split(", ", expand=True).stack().value_counts()
    st.write("Total vendido por modelo:")
    st.write(total_sold_by_model)

    # Total vendido por numeração
    total_sold_by_size = existing_data.groupby("Size").size()
    st.write("Total vendido por numeração:")
    st.write(total_sold_by_size)

    # Total de cada tipo de movimentação de stock
    st.write("Total de cada tipo de movimentação de stock:")
    total_stock_movements = existing_data["Tipo de Movimentação"].value_counts()
    st.write(total_stock_movements)

    # Total de valores recebidos
    total_values_received = existing_data["Value"].sum()
    st.write(f"Total de valores recebidos: {total_values_received}")

    # Movimentação por forma de pagamento
    st.write("Movimentação por forma de pagamento:")
    total_by_payment_method = existing_data.groupby("Method of Payment")["Value"].sum()
    st.write(total_by_payment_method)
