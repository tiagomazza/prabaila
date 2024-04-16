import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("Google Sheets as a DataBase")

# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

if st.button("New Entry"):
    new_entry = {}
    new_entry['OrderID'] = st.number_input("OrderID", min_value=0)
    new_entry['CustomerName'] = st.text_input("CustomerName")
    new_entry['ProductList'] = st.text_input("ProductList")
    new_entry['TotalPrice'] = st.number_input("TotalPrice", min_value=0)
    new_entry['OrderDate'] = st.date_input("OrderDate")

    # Prepare the data for insertion
    data_to_insert = [list(new_entry.values())]

    # Write new entry to Google Sheets
    conn.append(data=data_to_insert, worksheet="reservas")
    st.success("New Entry Added 🎉")

if st.button("Calculate Total Orders Sum"):
    # Query the total sum of TotalPrice from the reservas worksheet
    sql = 'SELECT SUM("TotalPrice") as "TotalOrdersPrice" FROM reservas;'
    total_orders = conn.query(sql=sql)  # default ttl=3600 seconds / 60 min
    st.write("Total Orders Price:", total_orders)

if st.button("Clear Worksheet"):
    # Clear the reservas worksheet
    conn.clear(worksheet="reservas")
    st.success("Worksheet Cleared 🧹")
