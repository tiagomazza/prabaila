import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Display Title and Description
st.title("Shoe Inventory System")
st.markdown("View shoes information from the workbook.")

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
    st.text(f"Imagem: {row['Imagem']}")
    st.text(f"Descrição: {row['Descrição']}")
    st.text(f"Preço: R${row['Preço']}")
    st.text(f"Estoque: {row['Estoque']}")
    st.write("---")
