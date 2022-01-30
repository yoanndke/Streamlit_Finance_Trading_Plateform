import streamlit as st
import app_V2
import importlib
importlib.reload(app_V2)
import time


def app(username, firstname, name, birthdate, account_creation, capital_dispo, capital_investi, capital_total):
    st.title('Mon Compte')
    st.write("Nom d'utilisateur : {}".format(username))
    st.write("Nom : {0} {1}".format(firstname, name.upper()))
    st.write("Date de naissance : {}".format(birthdate))
    st.write("Date de création du compte : {}".format(account_creation))
    col1, col2, col3 = st.columns((2,2,7))
    with col1:
        depot = st.number_input("Dépôt", min_value=50.0, step=20.0)
    with col2:
        st.write("")
        st.write("")
        if st.button('Déposer des fonds'):
            st.success("Votre dépôt de {} a été crédité sur votre compte".format(depot))
            depot_K_tot = capital_total + depot
            depot_K_avai = capital_dispo + depot
            app_V2.add_capital(depot_K_tot, depot_K_avai, username, depot)
            time.sleep(3)
            st.experimental_rerun()
    with col3:
        st.write("")

    st.markdown("""<style> .footer {
                        position: fixed; left: 0; bottom: 0; width: 100%; background-color: rgb(38, 39, 48);
                        color: white; text-align: right; padding: 30px 40px; z-index: 101;}
                        .footer-cols {display: flex; justify-content: space-between;}
                        .footer-col {flex: 1;text-align: center;border-right:solid rgb(14, 17, 23) 1px;}
                        </style>""", unsafe_allow_html=True)
    st.markdown("""<style> .footer-p {font-size: 25px !important;font-weight: bold;}</style>""", unsafe_allow_html=True)

    st.markdown('<footer class="footer"><div class="footer-cols">'
                '<div class="footer-col">Disponible : <p class="footer-p">$' + str(round(capital_dispo,2)) + '</p></div>'
                '<div class="footer-col">Investi : <p class="footer-p">$' + str(round(capital_investi,2)) + '</p></div>'
                '<div class="footer-col">Capital : <p class="footer-p">$' + str(round(capital_total,2)) + '</p></div>'
                '</div></footer>', unsafe_allow_html=True)


