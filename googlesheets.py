import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta

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


# Função para obter a quantidade vendida
def get_sales_quantity(id_):
    existing_data_reservations = load_existing_data("Reservations")

    if existing_data_reservations is None or id_ not in existing_data_reservations["ID"].values:
        return 0

    sales_data = existing_data_reservations[
        (existing_data_reservations["ID"] == id_) &
        (existing_data_reservations["Tipo de Movimentação"].isin(["Venda", "Oferta"]))
    ]

    sales_quantity = sales_data["Movimentação de Stock"].sum()

    addition_data = existing_data_reservations[
        (existing_data_reservations["ID"] == id_) &
        (existing_data_reservations["Tipo de Movimentação"] == "Entrada de Material")
    ]

    addition_quantity = addition_data["Movimentação de Stock"].sum()

    net_quantity = sales_quantity - addition_quantity

    return int(net_quantity)


# Página de verificação de estoque
def stock_verification_page():
    st.subheader("Busca de modelos disponíveis")
    existing_data = conn.read(worksheet="Shoes", usecols=["ID", "Modelo", "Número", "Imagem", "Descrição", "Preço", "Estoque", "Numero Brasileiro", "Deslize", "Amortecimento", "Cor da sola"], ttl=6)
    existing_data.dropna(subset=["ID", "Modelo", "Número", "Imagem", "Descrição", "Preço", "Estoque", "Numero Brasileiro", "Deslize", "Amortecimento", "Cor da sola"], inplace=True)

    st.sidebar.header("Filtros")
    
    modelos = existing_data["Modelo"].unique()
    modelos_filtro = st.sidebar.multiselect("Filtrar por Modelo", modelos.astype(str), default=modelos.astype(str))

    deslize_opcoes = existing_data["Deslize"].unique()
    deslize_filtro = st.sidebar.multiselect("Filtrar por Deslize", deslize_opcoes, default=deslize_opcoes)

    amortecimento_opcoes = existing_data["Amortecimento"].unique()
    amortecimento_filtro = st.sidebar.multiselect("Filtrar por Amortecimento", amortecimento_opcoes, default=amortecimento_opcoes)

    cor_sola_opcoes = existing_data["Cor da sola"].unique()
    cor_sola_filtro = st.sidebar.multiselect("Filtrar por Cor da sola", cor_sola_opcoes, default=cor_sola_opcoes)

    numeros_disponiveis = existing_data[existing_data["Modelo"].isin(modelos_filtro)]["Número"].unique()
    numeros_europeus_selecionados = st.multiselect("Quais números europeus deseja consultar?", numeros_disponiveis.astype(int), default=[])

    filtered_data = existing_data[
        (existing_data["Modelo"].isin(modelos_filtro)) & 
        (existing_data["Número"].isin(numeros_europeus_selecionados)) &
        (existing_data["Deslize"].isin(deslize_filtro)) &
        (existing_data["Amortecimento"].isin(amortecimento_filtro)) &
        (existing_data["Cor da sola"].isin(cor_sola_filtro))
    ]

    filtered_data["Número"] = filtered_data["Número"].astype(int)
    
    show_zero_stock = st.sidebar.checkbox("Mostrar sem stock")

    if not show_zero_stock:
        filtered_data = filtered_data[filtered_data["Estoque"] > 0]

    total_stock = filtered_data["Estoque"].sum()
    st.sidebar.header("Total do Estoque:")
    st.sidebar.write(str(total_stock).split('.')[0])

    for index, row in filtered_data.iterrows():
        id_unico = row["ID"]
        st.subheader(f"{row['Modelo']}")
        st.markdown(f"🇪🇺 **Número:** {int(row['Número'])}")
        if row['Imagem']:
            st.image(row['Imagem'])
        else:
            st.text("Imagem não disponível")

        sales_quantity = get_sales_quantity(id_unico)
        stock_after_sales = int(row["Estoque"]) - sales_quantity

        st.markdown(f"🏂🏽 **Deslize:** {row['Deslize']}")
        st.markdown(f"🦘 **Amortecimento:** {row['Amortecimento']}")
        st.markdown(f"👟 **Cor da sola:** {row['Cor da sola']}")
        st.markdown(f"📦 **Unidades em estoque:** {stock_after_sales}")
        st.markdown(f"🇧🇷 **Numero:** {int(row['Numero Brasileiro'])}")
        preco = row.get('Preço')
        if preco is not None:
            st.markdown(f"🏷 **Preço:**  {int(row['Preço'])}€")
        else:
            st.markdown("Preço não disponível")

        st.markdown(f"📝 **Observações:** {row['Descrição']}")
        st.markdown("---")


# Exibir imagem no menu lateral
menu_lateral_imagem = "https://shop.quintaclandestina.pt/wp-content/uploads/2024/05/logo-2.png"
st.sidebar.image(menu_lateral_imagem, use_column_width=True)

# Display Title and Description
st.title("Quinta Shop🛒")

# Configuração da aplicação
pagina_selecionada = st.sidebar.radio("Página", ["Verificação de estoque", "Registro", "Análise", "Teste"])

if pagina_selecionada == "Verificação de estoque":
    stock_verification_page()
elif pagina_selecionada == "Registro":
    register_page()
elif pagina_selecionada == "Active Reservations":
    active_reservations_page()
elif pagina_selecionada == "Análise":
    analysis_page()
elif pagina_selecionada == "Teste":
    test_page()
