import streamlit as st
import app_V2
import importlib
importlib.reload(app_V2)
import pandas as pd
import pandas_datareader.data as web
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta
import time



def app(username, capital_dispo, capital_investi, capital_total):
    today = date.today().strftime("%Y-%m-%d")
    last_date = pd.to_datetime(datetime.strptime(today, "%Y-%m-%d").date() - timedelta(days=3)).date()

    st.title('Portefeuille')
    list_gains_pertes_footer = []
    list_investment_footer = []

    transactions_result = app_V2.view_all_transactions(username)
    clean_db = pd.DataFrame(transactions_result, columns=["transac_id", "Ticker", "Name", "Position", "Statut", "Type",
                                                          "Unités", "Net investi", "Ouvert", "Fermé", "G/P ($)",
                                                          "Date Ouverture", "Date Fermeture"]).sort_values(by="Date Ouverture", ascending=False)
    clean_db = clean_db[clean_db["Statut"] == "Ouvert"]

    if clean_db.empty:
        st.warning("Pour le moment, vous n'avez investi dans aucune action.")
    else:
        if st.button("Actualiser"):
            st.experimental_rerun()

        list_multibuy = []
        multibuy = clean_db[clean_db["Type"] == "Multiple"]
        unique_value = multibuy["transac_id"].unique()
        for i in unique_value:
            list_multibuy.append(i)

        list_simplebuy = []
        simplebuy = clean_db[clean_db["Type"] == "Seul"]
        unique_value = simplebuy["transac_id"].unique()
        for i in unique_value:
            list_simplebuy.append(i)


        for i in list_multibuy:
            transactions_result = app_V2.view_specific_transactions(username, i)
            clean_db = pd.DataFrame(transactions_result,
                                        columns=["transac_id", "Ticker", "Name", "Position", "Statut", "Type",
                                                 "Unités", "Net investi", "Ouvert", "Fermé", "G/P ($)",
                                                 "Date Ouverture", "Date Fermeture"]).sort_values(by="Date Ouverture",
                                                                                                  ascending=False)
            clean_db = clean_db[clean_db["Statut"] == "Ouvert"]
            tickers = []
            names = []
            for index, row in clean_db.iterrows():
                tickers.append(row["Ticker"])
                names.append(row["Name"])
            if len(tickers) == 2:
                st.subheader("Trade Multiple : {}/{}".format(str(tickers[0]), str(tickers[1])))
            elif len(tickers) == 3:
                st.subheader("Trade Multiple : {}/{}/{}".format(str(tickers[0]), str(tickers[1]), str(tickers[2])))
            elif len(tickers) == 4:
                st.subheader("Trade Multiple : {}/{}/{}/{}".format(str(tickers[0]), str(tickers[1]), str(tickers[2]),
                                                                   str(tickers[3])))
            else:
                st.subheader("Trade Multiple : {}/{}/{}/{}/{}".format(str(tickers[0]), str(tickers[1]), str(tickers[2]),
                                                                      str(tickers[3]), str(tickers[4])))

            with st.expander("Ouvrir"):
                list_gains_pertes = []
                list_investment = []
                for index, row in clean_db.iterrows():
                    val_actuelle = web.DataReader(row["Ticker"], data_source="yahoo", start=last_date, end=today)
                    val_actuelle['Timestamp'] = val_actuelle.index
                    val_actuelle = val_actuelle.sort_values(by="Timestamp", ascending=False)

                    id_transaction = row["transac_id"]
                    ticker = row["Ticker"]
                    name = row["Name"]
                    position = row["Position"]
                    type = row["Type"]
                    quantity = row["Unités"]
                    investment = row["Net investi"]
                    open_rate = row["Ouvert"]
                    actuel = float(val_actuelle.iloc[0]["Close"])

                    st.write(ticker + " - " + name)
                    col1, col2, col3, col4, col5, col6 = st.columns(6)
                    with col1:
                        st.write("Position")
                        st.caption(position)
                    with col2:
                        st.write("Unités")
                        st.caption(str(round(quantity, 5)))
                    with col3:
                        st.write("Investi")
                        st.caption(str(investment))
                    with col4:
                        st.write("Ouvert")
                        st.caption(str(round(open_rate, 5)))
                    with col5:
                        actuel_pct = str(str(round((actuel - open_rate) / open_rate * 100, 2)) + "%")
                        st.metric(label="Actuel", value=round(actuel, 2))
                    with col6:
                        if position == "Vente":
                            gain_perte = round((open_rate - actuel) * quantity, 2)
                            gain_perte_pct = str(
                                str(round(((investment + gain_perte) - investment) / investment * 100, 2)) + "%")
                            st.metric(label="G/P ($)", value=str("$" + str(gain_perte)), delta=gain_perte_pct)
                        else:
                            gain_perte = round((actuel - open_rate) * quantity, 2)
                            gain_perte_pct = str(
                                str(round(((investment + gain_perte) - investment) / investment * 100, 2)) + "%")
                            st.metric(label="G/P ($)", value=str("$" + str(gain_perte)), delta=gain_perte_pct)
                    list_gains_pertes.append(gain_perte)
                    list_investment.append(investment)
                    list_gains_pertes_footer.append(gain_perte)
                    list_investment_footer.append(investment)
                if st.button("Clôturer la position", key=i):
                    y = 0
                    for ticker in tickers:
                        ticker = ticker
                        val_actuelle = web.DataReader(ticker, data_source="yahoo", start=last_date, end=today)
                        val_actuelle['Timestamp'] = val_actuelle.index
                        val_actuelle = val_actuelle.sort_values(by="Timestamp", ascending=False)
                        actuel = float(val_actuelle.iloc[0]["Close"])
                        gain_perte = list_gains_pertes[y]
                        app_V2.update_transaction(username, id_transaction, ticker, actuel, float(gain_perte))
                        y += 1

                    fin_trade = round(float(capital_dispo) + (float(sum(list_investment)) + float(sum(list_gains_pertes))), 2)
                    app_V2.update_capital(fin_trade, capital_investi - sum(list_investment), username)
                    st.experimental_rerun()


        for i in list_simplebuy:
            transactions_result = app_V2.view_specific_transactions(username, i)
            clean_db = pd.DataFrame(transactions_result,
                                    columns=["transac_id", "Ticker", "Name", "Position", "Statut", "Type",
                                             "Unités", "Net investi", "Ouvert", "Fermé", "G/P ($)",
                                             "Date Ouverture", "Date Fermeture"]).sort_values(by="Date Ouverture",
                                                                                              ascending=False)
            clean_db = clean_db[clean_db["Statut"] == "Ouvert"]
            for index, row in clean_db.iterrows():
                val_actuelle = web.DataReader(row["Ticker"], data_source="yahoo", start=last_date, end=today)
                val_actuelle['Timestamp'] = val_actuelle.index
                val_actuelle = val_actuelle.sort_values(by="Timestamp", ascending=False)

                id_transaction = row["transac_id"]
                ticker = row["Ticker"]
                name = row["Name"]
                position = row["Position"]
                type = row["Type"]
                quantity = row["Unités"]
                investment = row["Net investi"]
                open_rate = row["Ouvert"]
                actuel = float(val_actuelle.iloc[0]["Close"])

                st.subheader(ticker + " - " + name)
                col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
                with col1:
                    st.write("Position")
                    st.caption(position)
                with col2:
                    st.write("Unités")
                    st.caption(str(round(quantity, 5)))
                with col3:
                    st.write("Investi")
                    st.caption(str(investment))
                with col4:
                    st.write("Ouvert")
                    st.caption(str(round(open_rate, 5)))
                with col5:
                    actuel_pct = str(str(round((actuel - open_rate) / open_rate * 100, 2)) + "%")
                    st.metric(label="Actuel", value=round(actuel, 2))
                with col6:
                    if position == "Vente":
                        gain_perte = round((open_rate - actuel) * quantity, 2)
                        gain_perte_pct = str(
                            str(round(((investment + gain_perte) - investment) / investment * 100, 2)) + "%")
                        st.metric(label="G/P ($)", value=str("$" + str(gain_perte)), delta=gain_perte_pct)
                    else:
                        gain_perte = round((actuel - open_rate) * quantity, 2)
                        gain_perte_pct = str(
                            str(round(((investment + gain_perte) - investment) / investment * 100, 2)) + "%")
                        st.metric(label="G/P ($)", value=str("$" + str(gain_perte)), delta=gain_perte_pct)
                with col7:
                    if st.button("Clôturer la position", key=i):
                        app_V2.update_transaction(username, id_transaction, ticker, actuel, float(gain_perte))
                        fin_trade = round(float(capital_dispo) + (float(investment) + float(gain_perte)), 2)
                        app_V2.update_capital(fin_trade, capital_investi - investment, username)
                        st.experimental_rerun()

                list_gains_pertes_footer.append(gain_perte)
                list_investment_footer.append(investment)

    total_available_footer = capital_dispo
    total_investment_footer = capital_investi
    total_gains_pertes_footer = sum(list_gains_pertes_footer)
    total_capital_footer = capital_total + total_gains_pertes_footer


    st.markdown("""<style> .footer {
                    position: fixed; left: 0; bottom: 0; width: 100%; background-color: rgb(38, 39, 48);
                    color: white; text-align: right; padding: 30px 40px; z-index: 101;}
                    .footer-cols {display: flex; justify-content: space-between;}
                    .footer-col {flex: 1;text-align: center;border-right:solid rgb(14, 17, 23) 1px;}
                    </style>""", unsafe_allow_html=True)
    st.markdown("""<style> .footer-p {font-size: 25px !important;font-weight: bold;}</style>""", unsafe_allow_html=True)

    st.markdown('<footer class="footer"><div class="footer-cols">'
                '<div class="footer-col">Disponible : <p class="footer-p">$' + str(round(total_available_footer,2)) + '</p></div>'
                '<div class="footer-col">Investi : <p class="footer-p">$' + str(round(total_investment_footer,2)) + '</p></div>'
                '<div class="footer-col">Gains/Pertes : <p class="footer-p">$' + str(round(total_gains_pertes_footer,2)) + '</p></div>'
                '<div class="footer-col">Capital : <p class="footer-p">$' + str(round(total_capital_footer,2)) + '</p></div>'
                '</div></footer>', unsafe_allow_html=True)

