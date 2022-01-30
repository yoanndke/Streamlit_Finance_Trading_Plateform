import streamlit as st
import app_V2
import importlib
importlib.reload(app_V2)
import pandas as pd
import pandas_datareader.data as web
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import time
from plotly import graph_objs as go
from datetime import date, timedelta
from fbprophet import Prophet
from fbprophet.plot import plot_plotly


def nearest(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))

def app(username, capital_dispo, capital_investi, capital_total):
    #####Transco Ticker -> Nom + informations
    st.markdown("""<style>div.stButton > button:first-child {width : 100%;}</style>""", unsafe_allow_html=True)
    df = pd.read_csv("nasdaq_screener_1641419780590.csv", sep=",",
                     usecols=["Symbol", "Name", "Country", "Sector", "Industry"])
    df['Name'] = [i.upper() for i in df['Name']]
    st.title('Découvrir')
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>',
             unsafe_allow_html=True)
    choice_trading = ["Seul", "Multiple"]
    type_trading = st.radio("Type de Trading : ", choice_trading)

    if type_trading == "Seul":
        col1, col2 = st.columns((3, 1))
        with col1:
            #####Champ de recherche
            tick = ""
            form = st.form(key='my_form')
            rech = form.text_input(label='Recherche').upper()
            startdate = form.date_input("Startdate", min_value=pd.to_datetime("1990-1-1").date(),
                                      max_value=pd.to_datetime(date.today() - timedelta(days=1)).date(),
                                      value=pd.to_datetime("2020-1-1").date()).strftime("%d/%m/%Y")
            submit = form.form_submit_button(label='Rechercher')

            if rech == "":
                st.warning("Veuillez entrer un ticker ou un nom d'action")
            elif submit and rech == "":
                st.warning("Veuillez entrer un ticker ou un nom d'action")
            else:
                if rech in df["Symbol"].tolist():
                    tick = df[df["Symbol"] == rech]["Symbol"].to_string(index=False)
                else:
                    nb_elem = []
                    for elem in df["Name"].tolist():
                        if rech in elem:
                            nb_elem.append(elem)
                    if len(nb_elem) == 0:
                        if st.error("Aucune action à ce nom existe"):
                            return ''
                    elif len(nb_elem) == 1:
                        tick = df[df["Name"] == nb_elem[0]]["Symbol"].to_string(index=False)
                    else:
                        optn = st.selectbox('Quelle action contenant "{}" souhaitez vous regarder ?'.format(rech.lower()),
                                            (nb_elem))
                        tick = df[df["Name"] == optn]["Symbol"].to_string(index=False)
        with col2:
            st.write("")
            
        if rech != "":
            ticker = df[df["Symbol"] == tick]["Symbol"].to_string(index=False).upper()
            name = df[df["Symbol"] == tick]["Name"].to_string(index=False).title()
            st.subheader(ticker + " - " + name)

            today = date.today().strftime("%Y-%m-%d")
            ##### Récupération de donnée
            action = web.DataReader(ticker, data_source="yahoo", start=startdate, end=today)
            action['Timestamp'] = action.index

            #####Chercher la dernière date avec des données et la date à Année-1
            last_date = (action.sort_values(by="Timestamp", ascending=False).iloc[0]["Timestamp"]).strftime("%Y-%m-%d")
            date_one_year_ago = (datetime.strptime(last_date, "%Y-%m-%d") - relativedelta(years=1)).strftime("%Y-%m-%d")

            action_total = web.DataReader(ticker, data_source="yahoo",
                                          start=pd.to_datetime(datetime.strptime(date_one_year_ago, "%Y-%m-%d").date() - timedelta(days=3)).date(),
                                          end=today)
            action_total['Timestamp'] = action_total.index

            #st.dataframe(action_total)
            approx_one_year_ago = nearest(pd.to_datetime(action_total["Timestamp"].dt.strftime("%Y-%m-%d")).to_list(),
                                          pd.to_datetime(date_one_year_ago)).strftime("%Y-%m-%d")


            #####Affichage de données
            col1, col2 = st.columns((1, 1))
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=action.index, y=action["Close"], name="stock_close"))
                fig.layout.update(xaxis_rangeslider_visible=True)
                st.plotly_chart(fig)
                #st.line_chart(action["Close"])
                #st.dataframe(action.sort_values(by="Timestamp", ascending=False))
            with col2:
                st.text('')
                st.text('')
                st.text('')
                last_date_price = float(
                    (action[action["Timestamp"] == last_date]['Close'].to_string(index=False, header=False)))
                one_year_ago_price = float(
                    (action[action["Timestamp"] == approx_one_year_ago]['Close'].to_string(index=False, header=False)))
                st.write("Rendement de l’action sur 1 an : " + str(
                    round((last_date_price - one_year_ago_price) / one_year_ago_price * 100, 2)) + "%")

                start_val = float(action.sort_values(by="Timestamp", ascending=True).iloc[0]['Close'])
                final_val = float(action.sort_values(by="Timestamp", ascending=False).iloc[0]['Close'])
                st.write("Rendement de l’action sur la période {} - {} : ".format(startdate, datetime.strptime(today,
                                                                                                               "%Y-%m-%d").strftime(
                    "%d/%m/%Y")) +
                         str(round((final_val - start_val) / start_val * 100, 2)) + "%")
                st.text('')
                st.text('')
                investment = round(st.number_input("Prix ($)", value=100.0, min_value=0.0, step=50.0), 2)
                if investment > capital_dispo:
                    st.error("Vous n'avez pas assez de capital disponible")
                    return ''
                elif investment < 25:
                    st.error("Vous devez investir un minimum de 25€")

                quantity = round(investment / float(action.sort_values(by="Timestamp", ascending=False).iloc[0]['Close']),
                                 5)
                st.write("Soit : {} unités".format(quantity))
                opening_rate = float(action.sort_values(by="Timestamp", ascending=False).iloc[0]['Close'])


                if st.button('Acheter'):
                    achat = capital_dispo - investment
                    k_investi = capital_investi + investment
                    app_V2.update_capital(achat, k_investi, username)
                    app_V2.add_transaction(username, ticker, name, "Achat", "Ouvert", "Seul", quantity, investment, opening_rate)
                    st.success("Votre achat de {} pour {} a été émis".format(investment,
                                                                             df[df["Symbol"] == ticker]["Name"].to_string(
                                                                                 index=False).title()))
                    time.sleep(3)
                    st.experimental_rerun()

                if st.button('Vendre'):
                    vente = capital_dispo - investment
                    k_investi = capital_investi + investment
                    app_V2.update_capital(vente, k_investi, username)
                    app_V2.add_transaction(username, ticker, name, "Vente", "Ouvert", "Seul", quantity, investment, opening_rate)
                    st.success("Votre vente de {} pour {} a été émis".format(investment,
                                                                             df[df["Symbol"] == ticker]["Name"].to_string(
                                                                                 index=False).title()))
                    time.sleep(3)
                    st.experimental_rerun()


            ticker = df[df["Symbol"] == tick]["Symbol"].to_string(index=False).upper()
            name = df[df["Symbol"] == tick]["Name"].to_string(index=False).title()
            date_for_pred = ["6 Mois", "1 an"]
            prediction_date = st.radio("Prédire sur : ", date_for_pred)
            if prediction_date == "6 mois":
                st.header("Prédiction pour " + ticker + " - " + name + " sur {}".format(prediction_date))
            else:
                st.header("Prédiction pour " + ticker + " - " + name + " sur {}".format(prediction_date))

            today = date.today().strftime("%Y-%m-%d")

            data = web.DataReader(ticker, data_source="yahoo", start=startdate, end=today)
            data.reset_index(inplace=True)

            # Prédiction
            df_no_weekdays = data[data['Date'].dt.dayofweek < 5]  # on enlève les weekends du dataset d'entrée
            df_train = df_no_weekdays[['Date', 'Close']]  # on sélectionne la colonne Date et la Fermeture
            df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})  # on renomme les colonnes

            model = Prophet()
            model.fit(df_train)  # on entraîne notre model
            if prediction_date == "1 an":
                period = 365
            else:
                period = 180
            future = model.make_future_dataframe(periods=period, freq='d')  # on créer un nouveau dataset sur x années
            future_no_weekdays = future[future['ds'].dt.dayofweek < 5]  # on enlève les weekends du dataset prédits
            forecast = model.predict(future_no_weekdays)  # on teste le modèle

            col1, col2 = st.columns((2, 1))
            with col1:
                # Faire un graphique de la prévision
                fig1 = plot_plotly(model, forecast)
                fig1.layout.update(xaxis_rangeslider_visible=True)
                st.plotly_chart(fig1)
            with col2:
                st.write("")
                st.write("")
                st.write("Éléments de prévision")
                fig2 = model.plot_components(forecast)
                st.write(fig2)

    else:
        df["title"] = df['Symbol'] + " - " + df['Name']
        list_title = df["title"].to_list()
        options = st.multiselect(
            'Quelles sont les actions sur lesquelles vous souhaitez investir ?',
            list_title)
        if len(options) > 1:
            col1, col2 = st.columns((1, 2))
            with col1:
                st.write("")
                st.write("")
                st.write("")
                st.write("Vous avez sélectionné ces actions : ")
                tickers = []
                names = []
                today = date.today().strftime("%Y-%m-%d")
                for i in options:
                    st.write("- " + i)
                    ticker = i.split(" - ")[0].upper()
                    name = i.split(" - ")[1].title()
                    tickers.append(ticker)
                    names.append(name)

                df = web.DataReader("AAPL", data_source="yahoo", start="2018-1-1", end=today)
                df.reset_index(drop=False, inplace=True)
                df = df[["Date"]]

                for ticker in tickers:
                    data = web.DataReader(ticker, data_source="yahoo", start="2018-1-1", end=today)
                    data.reset_index(drop=False, inplace=True)
                    data = data[["Date", "Close"]]
                    data = data.rename({'Close': ticker}, axis=1)
                    df = pd.merge(df, data, how='outer', on='Date')

                investment = round(st.number_input("Prix ($)", value=100.0, min_value=0.0, step=50.0), 2)
                if investment > capital_dispo:
                    st.error("Vous n'avez pas assez de capital disponible")
                    return ''
                elif investment < 100:
                    st.error("Vous devez investir un minimum de 100€")

                if st.button('Acheter'):
                    achat = capital_dispo - investment
                    k_investi = capital_investi + investment
                    app_V2.update_capital(achat, k_investi, username)
                    j = 0
                    for i in tickers:
                        name = names[j]
                        quantity = round(investment / float(df.sort_values(by=["Date", f'{i}'], ascending=False).iloc[0][f'{i}']), 5)
                        opening_rate = float(df.sort_values(by=["Date", f'{i}'], ascending=False).iloc[0][f'{i}'])
                        app_V2.add_transaction(username, i, name, "Achat", "Ouvert", "Multiple", quantity,
                                               investment/len(tickers), opening_rate)
                        j += 1
                    st.success("Votre achat multiple de {} a été émis".format(investment))
                    time.sleep(2)
                    st.experimental_rerun()

                if st.button('Vendre'):
                    vente = capital_dispo - investment
                    k_investi = capital_investi + investment
                    app_V2.update_capital(vente, k_investi, username)
                    j = 0
                    for i in tickers:
                        name = names[j]
                        quantity = round(
                            investment / float(df.sort_values(by=["Date", f'{i}'], ascending=False).iloc[0][f'{i}']), 5)
                        opening_rate = float(df.sort_values(by=["Date", f'{i}'], ascending=False).iloc[0][f'{i}'])
                        app_V2.add_transaction(username, i, name, "Vente", "Ouvert", "Multiple", quantity,
                                               investment / len(tickers), opening_rate)
                        j += 1
                    st.success("Votre vente multiple de {} a été émis".format(investment))
                    time.sleep(2)
                    st.experimental_rerun()
            with col2:
                fig = go.Figure()
                for i in tickers:
                    fig.add_trace(go.Scatter(x=df["Date"], y=df[f"{i}"], name=f"{i}"))
                fig.layout.update(xaxis_rangeslider_visible=True)
                st.plotly_chart(fig)
        else:
            st.warning("Veuillez entrer plusieurs tickers ou plusieurs noms d'action")
            st.info("Sinon, redirigez-vous vers un type de trading 'Seul'")





    st.markdown("""<style> .footer {position: fixed; left: 0; bottom: 0; width: 100%; background-color: rgb(38, 39, 48);
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

