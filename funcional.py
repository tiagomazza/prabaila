import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Display Title and Description
st.title("Shoe Inventory System")
st.markdown("View and manage shoes inventory.")

# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch existing shoes data
existing_data = conn.read(worksheet="Shoes", usecols=list(range(6)), ttl=5)
existing_data = existing_data.dropna(how="all")

# Convert "Modelo" and "Descrição" columns to string
existing_data["Modelo"] = existing_data["Modelo"].astype(str)
existing_data["Descrição"] = existing_data["Descrição"].astype(str)

# Display shoes information separately
st.header("Shoes Information")
for index, row in existing_data.iterrows():
    st.subheader(f"Sapato {index + 1}")
    st.text(f"Modelo: {row['Modelo']}")
    st.text(f"Número: {row['Número']}")
    
    # Display the image from the URL
    if row['Imagem']:
        st.image(row['Imagem'], caption=f"Imagem para '{row['Modelo']}'")
    else:
        st.text("Imagem não disponível")
    
    st.text(f"Descrição: {row['Descrição']}")
    st.text(f"Preço: R${row['Preço']}")
    st.text(f"Estoque: {row['Estoque']}")
    
    # Quantity input for adding or reducing stock
    quantity = st.number_input(f"Alterar Estoque para '{row['Modelo']}' (Digite um valor positivo para adicionar e negativo para reduzir):", value=0, step=1)
    
    # Update the inventory if quantity is provided
    if quantity != 0:
        updated_stock = row['Estoque'] + quantity
        existing_data.at[index, 'Estoque'] = updated_stock

# Update Google Sheets with the updated inventory
if st.button("Atualizar Estoque"):
    conn.update(worksheet="Shoes", data=existing_data)
    st.success("Estoque atualizado com sucesso!")

"""
google-auth==2.29.0
google-auth-oauthlib==1.2.0
greenlet==3.0.3
gspread==5.12.4
gspread-dataframe==3.3.1
gspread-formatting==1.1.2
gspread-pandas==3.3.0
st-gsheets-connection==0.0.4
streamlit==1.32.2
tenacity==8.2.3
toml==0.10.2
git+https://github.com/streamlit/gsheets-connection
st-gsheets-connection
"""