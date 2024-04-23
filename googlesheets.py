import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Conexão com a planilha
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
pagina_selecionada = st.sidebar.radio("Página", ["Stock", "Reservation & Discount", "Active Reservations"])

# Determinar qual página exibir com base na seleção do usuário
if pagina_selecionada == "Stock":
    # Fetch existing shoes data
    existing_data = load_existing_data("Shoes")

    # Convert "Modelo" and "Descrição" columns to string
    existing_data["Modelo"] = existing_data["Modelo"].astype(str)
    existing_data["Descrição"] = existing_data["Descrição"].astype(str)

    # Sidebar filters
    st.sidebar.header("Filtros")
    modelos = existing_data["Modelo"].unique()
    modelos_filtro = st.sidebar.multiselect("Filtrar por Modelo", modelos.astype(str), default=modelos.astype(str))

    numeros = existing_data["Número"].unique()
    numeros_filtro = st.sidebar.multiselect("Filtrar por Número", numeros.astype(int), default=numeros.astype(int))

    # Filter the data based on the selected filters
    filtered_data = existing_data[
        (existing_data["Modelo"].isin(modelos_filtro)) & (existing_data["Número"].isin(numeros_filtro))
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
        st.subheader(f"{row['Modelo']}")
        st.markdown(f"**Número:** {int(row['Número'])}")  # Remove .0 and make bold
        # Display the image from the URL
        if row['Imagem']:
            st.image(row['Imagem'])
        else:
            st.text("Imagem não disponível")
        st.markdown(f"**Descrição:** {row['Descrição']}")  # Make bold
        st.markdown(f"**Preço:** {int(row['Preço'])}€")  # Displaying price in € and make bold
        st.markdown(f"**Estoque:** {int(row['Estoque'])}")  # Remove .0 and make bold

        # Botão para abrir janela abaixo de cada sapato
        button_key = f"details_button_{index}"
        if st.button(f"Movimentar stock do {row['Modelo']}", key=button_key):
            form_key = f"form_{index}"
            name = st.text_input(f"Nome do {row['Modelo']}", key=f"name_{index}")
            valor_pago = st.number_input(f"Valor Pago do {row['Modelo']}", step=0.01, key=f"valor_pago_{index}")
            metodo_pagamento = st.selectbox(f"Método de Pagamento do {row['Modelo']}", ["Dinheiro", "Cartão de Crédito", "Cartão de Débito"], key=f"metodo_pagamento_{index}")

            # Menu deslizante para o preço com incremento de 5€
            preco_min = int(row['Preço'])  # Preço mínimo será o preço atual do sapato
            preco_max = preco_min + 50  # Definindo um preço máximo de 50€ a mais
            preco_step = 5  # Incremento de 5€
            novo_preco = st.slider(f"Novo Preço do {row['Modelo']}", min_value=preco_min, max_value=preco_max, step=preco_step, value=preco_min, key=f"novo_preco_{index}")

            submit_button = st.button(f"Registrar Movimentação do {row['Modelo']}", key=f"submit_button_{index}")

            if submit_button:
                # Criar uma nova entrada de movimentação de estoque
                new_entry = pd.DataFrame({
                    "Nome": [name],
                    "Valor Pago": [valor_pago],
                    "Método de Pagamento": [metodo_pagamento],
                    "Preço": [novo_preco]  # Usar o novo preço selecionado
                })

                # Adicionar a nova entrada ao DataFrame existing_data
                existing_data = existing_data.append(new_entry, ignore_index=True)

                # Atualizar a planilha com os novos dados
                conn.update(worksheet="Shoes", data=existing_data)

                st.success("Movimentação de estoque registrada com sucesso!")

elif pagina_selecionada == "Reservation & Discount":
    # Página Reservas
    st.title("Reservation system")
    st.markdown("Type your data to be advised about new arrivals")

    existing_data = load_existing_data("Reservations")

    # List of Business Types and Products
    PRODUCTS = [
        "Light Palha",
        "Chuteirinha Vegana Preta",
    ]

    with st.form(key="vendor_form"):
        name = st.text_input(label="Name*")
        email = st.text_input("e-mail")
        whatsapp = st.text_input("whatsapp with international code")
        products = st.multiselect("Wished shoes", options=PRODUCTS)
        size = st.slider("Numeração", 34, 45, 34)
        additional_info = st.text_area(label="Additional Notes")

        # Mark mandatory fields
        st.markdown("**required*")

        submit_button = st.form_submit_button(label="Submit Details")

        if submit_button:
            # Check if all mandatory fields are filled
            if not name:
                st.warning("Ensure all mandatory fields are filled.")
                st.stop()
            elif existing_data["Name"].astype(str).str.contains(name).any():
                st.warning("This name already exists.")
                st.stop()
            else:
                # Create a new row of vendor data
                vendor_data = pd.DataFrame(
                    [
                        {
                            "Name": name,
                            "Email": email,
                            "Whatsapp": whatsapp,
                            "Products": ", ".join(products),
                            "Size": size,
                            "AdditionalInfo": additional_info,
                        }
                    ]
                )

                # Add the new vendor data to the existing data
                updated_df = pd.concat([existing_data, vendor_data], ignore_index=True)

                # Update Google Sheets with the new vendor data
                conn.update(worksheet="Reservations", data=updated_df)

                st.success("Details successfully submitted!")

                # Clear the form fields after submission
                name = ""
                email = ""
                whatsapp = ""
                products = []
                size = 34
                additional_info = ""

elif pagina_selecionada == "Active Reservations":
    # Exibir a página de reservas ativas
    active_reservations_page()
