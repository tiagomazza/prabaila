import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.title("Google Sheets as a DataBase")

# Function to write data to "Reservas" sheet
def write_to_reservas(data):
    try:
        # Get the number of rows in the "Reservas" sheet
        reservas_sheet = conn.get(worksheet="Reservas")
        num_rows = len(reservas_sheet)

        # Append data to the next row
        conn.append(worksheet="Reservas", data=data, index=num_rows + 1)
        st.success("Data written to Reservas Sheet 🎉")
    except Exception as e:
        st.error(f"Error: {e}")

# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Placeholder for form data
form_data = {}

# Displaying the form
st.write("Reservas Form:")
form_data['Name'] = st.text_input("Name")
form_data['Email'] = st.text_input("Email")
form_data['Check-in Date'] = st.date_input("Check-in Date")
form_data['Check-out Date'] = st.date_input("Check-out Date")
form_data['Room Type'] = st.selectbox("Room Type", ["Single", "Double", "Suite"])

# Button to submit form data to "Reservas" sheet
if st.button("Submit"):
    data_df = pd.DataFrame(form_data, index=[0])  # Convert form data to DataFrame
    write_to_reservas(data_df)
