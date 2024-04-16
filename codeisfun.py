import streamlit as st
from streamlit_gsheets import GSheetsDB

st.title("Google Sheets as a DataBase")

# Create a connection to Google Sheets
db = GSheetsDB()

if st.button("New Entry"):
    new_entry = {}
    new_entry['OrderID'] = st.number_input("OrderID", min_value=0)
    new_entry['CustomerName'] = st.text_input("CustomerName")
    new_entry['ProductList'] = st.text_input("ProductList")
    new_entry['TotalPrice'] = st.number_input("TotalPrice", min_value=0)
    new_entry['OrderDate'] = st.date_input("OrderDate")

    # Write new entry to Google Sheets
    db.write(new_entry, "Orders")
    st.success("New Entry Added 🎉")

if st.button("Calculate Total Orders Sum"):
    # Query the total sum of TotalPrice from the Orders worksheet
    total_orders = db.query("SELECT SUM(TotalPrice) FROM Orders;")
    st.write("Total Orders Price:", total_orders)

if st.button("Clear Worksheet"):
    # Clear the Orders worksheet
    db.clear("Orders")
    st.success("Worksheet Cleared 🧹")
