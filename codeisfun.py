import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.title("Google Sheets as a DataBase")

# Function to create a DataFrame from user input
def create_custom_dataframe():
    order_id = st.text_input("Order ID")
    customer_name = st.text_input("Customer Name")
    product_list = st.text_input("Product List (comma separated)")
    total_price = st.number_input("Total Price")
    order_date = st.date_input("Order Date")
    
    if st.button("Add Order"):
        order_data = {
            'OrderID': [order_id],
            'CustomerName': [customer_name],
            'ProductList': [product_list],
            'TotalPrice': [total_price],
            'OrderDate': [order_date.strftime('%Y-%m-%d')]
        }
        new_order_df = pd.DataFrame(order_data)
        st.success("Order Added 🎉")
        return new_order_df
    else:
        return pd.DataFrame()

# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Placeholder for orders DataFrame
orders_df = pd.DataFrame()

# Displaying the form and processing user input
st.write("Add New Order:")
new_order_df = create_custom_dataframe()
if not new_order_df.empty:
    orders_df = pd.concat([orders_df, new_order_df], ignore_index=True)

# Displaying current orders DataFrame
if not orders_df.empty:
    st.write("Current Orders:")
    st.dataframe(orders_df)

# Confirm button only appears if there are orders to confirm
if not orders_df.empty:
    if st.button("Confirm"):
        conn.create(worksheet="Orders", data=orders_df)
        st.success("Worksheet Created 🎉")
