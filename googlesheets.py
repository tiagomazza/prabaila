import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Display Title and Description
st.title("Inventário Prábaila Quinta Clandestina")
st.markdown("Sistema de controle de modelos.")

# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch existing shoes data
existing_data = conn.read(worksheet="Shoes", usecols=list(range(6)), ttl=5)
existing_data = existing_data.dropna(how="all")

# Convert "Modelo" and "Descrição" columns to string
existing_data["Modelo"] = existing_data["Modelo"].astype(str)
existing_data["Descrição"] = existing_data["Descrição"].astype(str)

# Display shoes information separately
for index, row in existing_data.iterrows():
    st.subheader(f"{row['Modelo']}")
    st.text(f"Número: {row['Número']}")
    
    # Display the image from the URL
    if row['Imagem']:
        st.image(row['Imagem'])
    else:
        st.text("Imagem não disponível")
    
    st.text(f"Descrição: {row['Descrição']}")
    st.text(f"Preço: R${row['Preço']}")
    st.text(f"Estoque: {row['Estoque']}")
    
    # Quantity input for adding or reducing stock
    
    quantity = st.number_input(f"Alterar Estoque para '{row['Modelo']}'", value=0, step=1)

    # Update the inventory if quantity is provided
    if quantity != 0:
        updated_stock = row['Estoque'] + quantity
        existing_data.at[index, 'Estoque'] = updated_stock

# Update Google Sheets with the updated inventory
if st.button("Atualizar Estoque"):
    conn.update(worksheet="Shoes", data=existing_data)
    st.success("Estoque atualizado com sucesso!")
