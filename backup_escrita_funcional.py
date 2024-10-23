
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


conn = st.connection("gsheets", type=GSheetsConnection)
pagina_selecionada = st.sidebar.radio("", ["✍🏽Marcação de Ponto"])

dados = conn.read(worksheet="Dados", usecols=["Pin", "Nome"], ttl=5)

if pagina_selecionada == "✍🏽Marcação de Ponto":
    st.title("✍🏽Marcação de Ponto")

    pin_digitado = st.text_input("Digite o seu PIN:",type="password")

    if str(pin_digitado):
        dados = conn.read(worksheet="Dados", usecols=["Pin", "Nome"], ttl=5)
        try:
            pin_int = int(float(pin_digitado))
            if pin_int in dados["Pin"].tolist():
                nome = dados.loc[dados["Pin"] == pin_int, "Nome"].iloc[0]

                st.write(f"😀 Bem-vindo, {nome}!")
                st.write("")

                if st.button("☕ Entrada Manhã"):
                                current_time = datetime.now()
                                one_hour_after = current_time + timedelta(hours=1)
                                submission_datetime = one_hour_after.strftime("%Y-%m-%d %H:%M:%S")
                                new_data = pd.DataFrame({
                                    "Name": [nome],
                                    "Button": ["Entrada Manhã"],
                                    "SubmissionDateTime": [submission_datetime]
                                })

                                existing_data_reservations = conn.read(worksheet="Folha")
                                existing_data_reservations = existing_data_reservations.dropna(how='all').reset_index(drop=True)

                                first_empty_index = existing_data_reservations.index[existing_data_reservations.isnull().all(axis=1)].min()
                                
                                if pd.isna(first_empty_index):
                                    first_empty_index = len(existing_data_reservations)

                                existing_data_reservations.loc[first_empty_index] = new_data.iloc[0]
                                conn.update(worksheet="Folha", data=existing_data_reservations)

                                st.success("Dados registrados com sucesso!")

                                existing_data_reservations = conn.read(worksheet="Folha")
                                existing_data_reservations = existing_data_reservations.dropna(how='all').reset_index(drop=True)

                                first_empty_index = existing_data_reservations.index[existing_data_reservations.isnull().all(axis=1)].min()
                                
                                if pd.isna(first_empty_index):
                                    first_empty_index = len(existing_data_reservations)

                                existing_data_reservations.loc[first_empty_index] = new_data.iloc[0]
                                conn.update(worksheet="Folha", data=existing_data_reservations)

                                st.success("Dados registrados com sucesso!")
            else:
                st.warning("Pin incorreto.")
        except ValueError:
            st.warning("Utilize somente numeros")                     

