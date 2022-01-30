import streamlit as st
import Client
import pandas as pd
import app_V2
import importlib
importlib.reload(app_V2)


def app(username):
    if username == 'admin':
        st.subheader("User Profiles")
        user_result = app_V2.view_all_users()
        clean_db = pd.DataFrame(user_result, columns=["Username", "Firstname", "Name", "Birthdate",
                                                      "Password", "Account Creation", "Capital dispo",
                                                      "Capital investi", "Capital total"])
        st.dataframe(clean_db)
    else:
        return Client