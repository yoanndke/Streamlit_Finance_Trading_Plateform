import streamlit as st
import app_V2
import importlib
importlib.reload(app_V2)
import pandas as pd

def app(username, capital_dispo, capital_investi, capital_total):
    st.title('Historique de transactions')

    transactions_result = app_V2.view_all_transactions(username)
    clean_db = pd.DataFrame(transactions_result,
                            columns=["transac_id", "Ticker", "Name", "Position", "Statut", "Type", "Unités", "Net investi",
                                     "Ouvert", "Fermé", "G/P ($)", "Date Ouverture",
                                     "Date Fermeture"]).sort_values(by="Date Ouverture", ascending=False)
    clean_db = clean_db.fillna("")
    if clean_db.empty:
        st.warning("Aucun historique disponible")
    else:
        clean_db = clean_db.astype(str)
        st.dataframe(clean_db)

    st.markdown("""<style> .footer {
                            position: fixed; left: 0; bottom: 0; width: 100%; background-color: rgb(38, 39, 48);
                            color: white; text-align: right; padding: 30px 40px; z-index: 101;}
                            .footer-cols {display: flex; justify-content: space-between;}
                            .footer-col {flex: 1;text-align: center;border-right:solid rgb(14, 17, 23) 1px;}
                            </style>""", unsafe_allow_html=True)
    st.markdown("""<style> .footer-p {font-size: 25px !important;font-weight: bold;}</style>""", unsafe_allow_html=True)

    st.markdown('<footer class="footer"><div class="footer-cols">'
                '<div class="footer-col">Disponible : <p class="footer-p">$' + str(round(capital_dispo, 2)) + '</p></div>'
                '<div class="footer-col">Investi : <p class="footer-p">$' + str(round(capital_investi, 2)) + '</p></div>'
                '<div class="footer-col">Capital : <p class="footer-p">$' + str(round(capital_total, 2)) + '</p></div>'
                '</div></footer>', unsafe_allow_html=True)