import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("Reservation system")
st.markdown("Type your data to be advised about new arrivals")

conn = st.experimental_connection("gsheets", type=GSheetsConnection)

existing_data = conn.read(worksheet="Reservations", usecols=list(range(6)), ttl=5)
existing_data = existing_data.dropna(how="all")

# List of Business Types and Products

PRODUCTS = [
    "Light Palha",
    "Chuteirinha Vegana Preta",
]

with st.form(key="vendor_form"):
    name = st.text_input(label="Name*")
    email = st.text_input("e-mail")
    whatsapp = st.text_input("whatsapp with international code")
    products = st.multiselect("Wished shoes", options=PRODUCTS)
    size = st.slider("Years in Business", 34, 45, 34)
    additional_info = st.text_area(label="Additional Notes")

    # Mark mandatory fields
    st.markdown("**required*")

    submit_button = st.form_submit_button(label="Submit Details")

    # If the submit button is pressed
    if submit_button:
        # Check if all mandatory fields are filled
        if not name:
            st.warning("Ensure all mandatory fields are filled.")
            st.stop()
        elif existing_data["Name"].astype(str).str.contains(name).any():
            st.warning("This name already exists.")
            st.stop()
        else:
            # Create a new row of vendor data
            vendor_data = pd.DataFrame(
                [
                    {
                        "Name": name,
                        "Email": email,
                        "Whatsapp": whatsapp,
                        "Products": ", ".join(products),
                        "Size": size,
                        "AdditionalInfo": additional_info,
                    }
                ]
            )

            # Add the new vendor data to the existing data
            updated_df = pd.concat([existing_data, vendor_data], ignore_index=True)

            # Update Google Sheets with the new vendor data
            conn.update(worksheet="Reservations", data=updated_df)

            st.success("Details successfully submitted!")

            # Clear the form fields after submission
            name = ""
            email = ""
            whatsapp = ""
            products = []
            size = 34
            additional_info = ""

# Display existing reservation data
st.subheader("Existing Reservations")
if not existing_data.empty:
    st.write(existing_data)
else:
    st.write("No existing reservations.")
