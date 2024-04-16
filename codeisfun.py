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
        return pd.DataFrame(order_data)
    else:
        return pd.DataFrame()

# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Placeholder for orders DataFrame
orders_df = pd.DataFrame()

# Taking actions based on user input
if st.button("New Order"):
    new_order_df = create_custom_dataframe()
    if not new_order_df.empty:
        orders_df = pd.concat([orders_df, new_order_df], ignore_index=True)
        st.success("Order Added 🎉")

# Displaying current orders DataFrame
if not orders_df.empty:
    st.write("Current Orders:")
    st.dataframe(orders_df)

if st.button("Calculate Total Orders Sum"):
    sql = 'SELECT SUM("TotalPrice") as "TotalOrdersPrice" FROM Orders;'
    total_orders = conn.query(sql=sql)  # default ttl=3600 seconds / 60 min
    st.dataframe(total_orders)

if st.button("Clear Orders"):
    conn.clear(worksheet="Orders")
    orders_df = pd.DataFrame()
    st.success("Orders Cleared 🧹")
