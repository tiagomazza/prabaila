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
    conn.create(worksheet="Orders", data=data_to_insert)
    st.success("New Entry Added 🎉")

if st.button("Calculate Total Orders Sum"):
    # Query the total sum of TotalPrice from the Orders worksheet
    sql = 'SELECT SUM("TotalPrice") as "TotalOrdersPrice" FROM Orders;'
    total_orders = conn.query(sql=sql)  # default ttl=3600 seconds / 60 min
    st.write("Total Orders Price:", total_orders)

if st.button("Clear Worksheet"):
    # Clear the Orders worksheet
    conn.clear(worksheet="Orders")
    st.success("Worksheet Cleared 🧹")
